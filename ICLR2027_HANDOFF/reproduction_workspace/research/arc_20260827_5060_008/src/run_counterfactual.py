"""Outcome-blind calibration and held-out counterfactual reveal for ARC-008."""

from __future__ import annotations

import argparse, csv, gc, json, math, random, time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT=Path(__file__).resolve().parents[1]

def choose(tokens,seed,count,length):
    rng=random.Random(seed); usable=len(tokens)-length-1; width=usable//count
    return torch.stack([tokens[(s:=i*width+rng.randrange(max(1,width-length))):s+length+1] for i in range(count)])

def noise_seed(direction,eval_seed,layer,batch_start): return int(direction*1_000_003+eval_seed*10_007+layer*101+batch_start)

class Inject(nn.Module):
    def __init__(self,block,kind,alpha,seed): super().__init__(); self.block=block; self.kind=kind; self.alpha=float(alpha); self.seed=int(seed); self.rel=0.; self.count=0
    def forward(self,h,*args,**kwargs):
        out=self.block(h,*args,**kwargs); base=out[0]; basef=base.float()
        if self.kind=='block': raw=h.float()-basef
        else:
            g=torch.Generator(device=base.device); g.manual_seed(self.seed); raw=torch.randn(base.shape,generator=g,device=base.device,dtype=torch.float32)
        norm=torch.linalg.vector_norm(raw,dim=-1,keepdim=True); base_norm=torch.linalg.vector_norm(basef,dim=-1,keepdim=True)
        delta=self.alpha*base_norm*raw/(norm+1e-12); changed=(basef+delta).to(base.dtype)
        actual=changed.float()-basef; self.rel+=(torch.linalg.vector_norm(actual,dim=-1)/(base_norm.squeeze(-1)+1e-12)).sum().item(); self.count+=actual.shape[0]*actual.shape[1]
        return (changed,)+out[1:]
    def relative(self): return self.rel/self.count

def replace(layers,index,wrapper): return nn.ModuleList([wrapper if i==index else b for i,b in enumerate(layers)])

def acc_new(): return {"tokens":0,"nll":0.,"kl":0.,"lognorm":0.,"abscos":0.,"flips":0,"hidden_rel":0.,"hidden_count":0}

@torch.inference_mode()
def evaluate(model,original,sequences,eval_seeds,layer,kind,alpha,direction_ids,batch_size,reveal):
    acc=acc_new()
    for eval_seed,seq in zip(eval_seeds,sequences):
        for batch_start in range(0,len(seq),batch_size):
            batch=seq[batch_start:batch_start+batch_size].to('cuda'); inputs,labels=batch[:,:-1],batch[:,1:]
            model.gpt_neox.layers=original; intact=model(inputs,use_cache=False).logits.float(); lp=intact.log_softmax(-1); probs=lp.exp(); c1=intact.argmax(-1)
            runner=intact.clone(); runner.scatter_(-1,c1.unsqueeze(-1),-torch.inf); c2=runner.argmax(-1)
            ids=[0] if kind=='block' else direction_ids
            for did in ids:
                seed=noise_seed(int(did),int(eval_seed),int(layer),batch_start) if kind=='noise' else 0
                wrapper=Inject(original[layer],kind,alpha,seed); model.gpt_neox.layers=replace(original,layer,wrapper)
                changed=model(inputs,use_cache=False).logits.float(); changed_lp=changed.log_softmax(-1); delta=changed-intact; ln=torch.linalg.vector_norm(delta,dim=-1)
                db=delta.gather(-1,c1.unsqueeze(-1)).squeeze(-1)-delta.gather(-1,c2.unsqueeze(-1)).squeeze(-1)
                count=labels.numel(); acc['tokens']+=count; acc['nll']+=F.cross_entropy(changed.reshape(-1,changed.shape[-1]),labels.reshape(-1),reduction='sum').item()
                acc['kl']+=(probs*(lp-changed_lp)).sum().item(); acc['lognorm']+=ln.sum().item(); acc['abscos']+=(db/(math.sqrt(2)*ln+1e-12)).abs().sum().item()
                if reveal: acc['flips']+=(changed.argmax(-1)!=c1).sum().item()
                acc['hidden_rel']+=wrapper.relative()*wrapper.count; acc['hidden_count']+=wrapper.count
                del wrapper,changed,changed_lp,delta,ln,db
    model.gpt_neox.layers=original
    baseline_tokens=0; baseline_nll=0.
    for seq in sequences:
        for start in range(0,len(seq),batch_size):
            batch=seq[start:start+batch_size].to('cuda'); logits=model(batch[:,:-1],use_cache=False).logits.float(); labels=batch[:,1:]
            baseline_nll+=F.cross_entropy(logits.reshape(-1,logits.shape[-1]),labels.reshape(-1),reduction='sum').item(); baseline_tokens+=labels.numel()
    return {"tokens":acc['tokens'],"kl":acc['kl']/acc['tokens'],"nll_damage":acc['nll']/acc['tokens']-baseline_nll/baseline_tokens,
            "output_logit_norm":acc['lognorm']/acc['tokens'],"output_abs_cosine":acc['abscos']/acc['tokens'],"hidden_relative_norm":acc['hidden_rel']/acc['hidden_count'],
            **({"ds":acc['flips']/acc['tokens']} if reveal else {})}

def checkpoint(model_name,revision,step,targets,tokens,cfg,phase,selection):
    started=time.perf_counter(); torch.cuda.reset_peak_memory_stats(); model=AutoModelForCausalLM.from_pretrained(model_name,revision=revision,dtype=torch.float16,local_files_only=True).to('cuda').eval(); original=model.gpt_neox.layers
    rows=[]
    if phase=='calibrate': seeds=[int(cfg['calibration_seed'])]; count=int(cfg['calibration_sequences'])
    else: seeds=[int(x) for x in cfg['confirmatory_seeds']]; count=int(cfg['confirmatory_sequences_per_seed'])
    sequences=[choose(tokens,s,count,int(cfg['sequence_length'])) for s in seeds]
    for target in targets:
        if phase=='calibrate':
            alphas=sorted(set(float(target['selected_beta'])*float(m) for m in cfg['alpha_multipliers']))
            for kind in ['block','noise']:
                for alpha in alphas:
                    met=evaluate(model,original,sequences,seeds,int(target['layer']),kind,alpha,[int(x) for x in cfg['noise_direction_ids']],int(cfg['batch_size']),False)
                    rows.append({"target_id":target['target_id'],"run_id":int(target['run_id']),"step":int(target['step']),"layer":int(target['layer']),"family_direction":kind,"alpha":alpha,**met})
        else:
            selected=[row for row in selection if row['target_id']==target['target_id']]
            if not selected or str(selected[0]['calibration_pass']).lower()!='true': continue
            row=selected[0]
            for kind,field in [('block','block_alpha'),('noise','noise_alpha')]:
                met=evaluate(model,original,sequences,seeds,int(target['layer']),kind,float(row[field]),[int(x) for x in cfg['noise_direction_ids']],int(cfg['batch_size']),True)
                rows.append({"target_id":target['target_id'],"run_id":int(target['run_id']),"step":int(target['step']),"layer":int(target['layer']),"family_direction":kind,"alpha":float(row[field]),**met})
    meta={"step":step,"revision":revision,"commit_hash":getattr(model.config,'_commit_hash',None),"phase":phase,"rows":len(rows),"runtime_seconds":time.perf_counter()-started,"peak_cuda_bytes":int(torch.cuda.max_memory_allocated())}
    del model;gc.collect();torch.cuda.empty_cache();return rows,meta

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);ap.add_argument('--run-id',type=int,required=True);ap.add_argument('--phase',choices=['calibrate','confirm'],required=True);a=ap.parse_args()
    cfg=yaml.safe_load(a.config.read_text()); run=int(a.run_id); source=(ROOT/cfg['corrected_results']).resolve()
    allowed=['target_id','run_id','step','layer','match_class','selected_beta','target_kl','target_nll_damage']
    with source.open(newline='',encoding='utf-8') as handle: targets=[{k:row[k] for k in allowed} for row in csv.DictReader(handle) if int(row['run_id'])==run and row['match_class']=='A']
    for row in targets: row.update(run_id=int(row['run_id']),step=int(row['step']),layer=int(row['layer']),selected_beta=float(row['selected_beta']),target_kl=float(row['target_kl']),target_nll_damage=float(row['target_nll_damage']))
    if a.phase=='confirm':
        with (ROOT/'calibration_manifest.csv').open(newline='',encoding='utf-8') as handle: selection=list(csv.DictReader(handle))
    else: selection=[]
    name=f"EleutherAI/pythia-{cfg['model_scale']}m-seed{run}";tok=AutoTokenizer.from_pretrained(name,revision='main',local_files_only=True);text=(ROOT/cfg['text_file']).resolve(); tokens=tok(text.read_text(encoding='utf-8'),add_special_tokens=False,return_tensors='pt')['input_ids'][0]
    all_rows=[];meta=[]
    for revision,step in zip(cfg['revisions'],cfg['checkpoint_steps']):
        rows,m=checkpoint(name,revision,int(step),[row for row in targets if row['step']==int(step)],tokens,cfg,a.phase,selection);all_rows+=rows;meta.append(m);print(json.dumps(m),flush=True)
    raw=ROOT/'raw';raw.mkdir(exist_ok=True)
    if all_rows:
        with (raw/f'{a.phase}_seed{run}.csv').open('w',newline='',encoding='utf-8') as handle: writer=csv.DictWriter(handle,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)
    (raw/f'{a.phase}_seed{run}.json').write_text(json.dumps({"arc":cfg['arc'],"phase":a.phase,"outcome_blind":a.phase=='calibrate',"checkpoints":meta},indent=2),encoding='utf-8')

if __name__=='__main__':main()
