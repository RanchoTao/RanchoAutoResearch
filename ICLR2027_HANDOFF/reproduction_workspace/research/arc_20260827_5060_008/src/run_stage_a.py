"""Outcome-blind extraction of internal perturbation directions for ARC-008."""

from __future__ import annotations

import argparse, csv, gc, hashlib, json, math, random, time
from pathlib import Path

import numpy as np
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng=random.Random(seed); usable=len(tokens)-length-1; width=usable//count
    starts=[i*width+rng.randrange(max(1,width-length)) for i in range(count)]
    return torch.stack([tokens[s:s+length+1] for s in starts])


def noise_seed(direction: int, eval_seed: int, layer: int, batch_start: int) -> int:
    return int(direction*1_000_003+eval_seed*10_007+layer*101+batch_start)


def summarize(values: list[np.ndarray]) -> dict:
    x=np.concatenate(values).astype(float)
    return {"mean":float(x.mean()),"median":float(np.median(x)),"q10":float(np.quantile(x,.1)),
            "q90":float(np.quantile(x,.9)),"sd":float(x.std(ddof=0)),"count":int(len(x))}


@torch.inference_mode()
def checkpoint(run_id: int, revision: str, step: int, targets: list[dict], tokens: torch.Tensor, cfg: dict) -> tuple[list[dict],dict]:
    started=time.perf_counter(); torch.cuda.reset_peak_memory_stats()
    name=f"EleutherAI/pythia-{cfg['model_scale']}m-seed{run_id}"
    model=AutoModelForCausalLM.from_pretrained(name,revision=revision,dtype=torch.float16,local_files_only=True).to('cuda').eval()
    captures={}; handles=[]; wanted=sorted(set(int(row['layer']) for row in targets))
    for layer in wanted:
        def pre(_m,args,l=layer): captures.setdefault(l,{})['pre']=args[0].detach()
        def post(_m,args,out,l=layer): captures.setdefault(l,{})['post']=(out[0] if isinstance(out,tuple) else out).detach()
        handles += [model.gpt_neox.layers[layer].register_forward_pre_hook(pre),model.gpt_neox.layers[layer].register_forward_hook(post)]
    acc={row['target_id']:{"cos":[],"block_norm":[],"noise_norm":[],"valid":0,"total":0} for row in targets}
    layer_to_target={int(row['layer']):row for row in targets}
    for eval_seed in cfg['evaluation_seeds']:
        seq=choose(tokens,int(eval_seed),int(cfg['stage_a_sequences_per_seed']),int(cfg['sequence_length']))
        for batch_start in range(0,len(seq),int(cfg['batch_size'])):
            batch=seq[batch_start:batch_start+int(cfg['batch_size']),:-1].to('cuda'); captures.clear()
            model(batch,use_cache=False)
            for layer,row in layer_to_target.items():
                before=captures[layer]['pre'].float(); after=captures[layer]['post'].float()
                block=before-after; bn=torch.linalg.vector_norm(block,dim=-1)
                for direction_id in cfg['noise_direction_ids']:
                    gen=torch.Generator(device='cuda'); gen.manual_seed(noise_seed(int(direction_id),int(eval_seed),layer,batch_start))
                    raw=torch.randn(after.shape,generator=gen,device='cuda',dtype=torch.float32)
                    rn=torch.linalg.vector_norm(raw,dim=-1); an=torch.linalg.vector_norm(after,dim=-1)
                    noise=float(row['selected_beta'])*an.unsqueeze(-1)*raw/(rn.unsqueeze(-1)+1e-12); nn=torch.linalg.vector_norm(noise,dim=-1)
                    valid=(bn>float(cfg['zero_norm_epsilon']))&(nn>float(cfg['zero_norm_epsilon']))
                    cos=(block*noise).sum(-1)/(bn*nn+1e-12)
                    item=acc[row['target_id']]; item['cos'].append(cos[valid].cpu().numpy()); item['block_norm'].append(bn[valid].cpu().numpy()); item['noise_norm'].append(nn[valid].cpu().numpy()); item['valid']+=int(valid.sum()); item['total']+=int(valid.numel())
    for h in handles: h.remove()
    rows=[]
    for row in targets:
        item=acc[row['target_id']]; c=summarize(item['cos']); b=summarize(item['block_norm']); n=summarize(item['noise_norm'])
        rows.append({"target_id":row['target_id'],"run_id":run_id,"step":step,"layer":int(row['layer']),"selected_beta":float(row['selected_beta']),
                     "valid_fraction":item['valid']/item['total'],"comparisons":item['valid'],"cosine_mean":c['mean'],"cosine_median":c['median'],
                     "cosine_q10":c['q10'],"cosine_q90":c['q90'],"cosine_sd":c['sd'],"directional_disagreement":1-c['mean'],
                     "block_norm_mean":b['mean'],"noise_norm_mean":n['mean'],"log_noise_block_norm_ratio":math.log(n['mean']/b['mean'])})
    meta={"run_id":run_id,"step":step,"revision":revision,"commit_hash":getattr(model.config,'_commit_hash',None),
          "targets":len(rows),"runtime_seconds":time.perf_counter()-started,"peak_cuda_bytes":int(torch.cuda.max_memory_allocated())}
    del model; gc.collect(); torch.cuda.empty_cache(); return rows,meta


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',type=Path,required=True); ap.add_argument('--run-id',type=int,required=True); a=ap.parse_args()
    cfg=yaml.safe_load(a.config.read_text()); run=int(a.run_id)
    if run not in cfg['run_ids'] or not torch.cuda.is_available(): raise RuntimeError('invalid run or CUDA unavailable')
    source=(ROOT/cfg['corrected_results']).resolve(); allowed=['target_id','run_id','step','layer','match_class','selected_beta']
    with source.open(newline='',encoding='utf-8') as handle: targets=[{k:row[k] for k in allowed} for row in csv.DictReader(handle) if int(row['run_id'])==run and row['match_class']=='A']
    for row in targets: row.update(run_id=int(row['run_id']),step=int(row['step']),layer=int(row['layer']),selected_beta=float(row['selected_beta']))
    name=f"EleutherAI/pythia-{cfg['model_scale']}m-seed{run}"; tok=AutoTokenizer.from_pretrained(name,revision='main',local_files_only=True)
    text=(ROOT/cfg['text_file']).resolve(); tokens=tok(text.read_text(encoding='utf-8'),add_special_tokens=False,return_tensors='pt')['input_ids'][0]
    all_rows=[]; metas=[]
    for revision,step in zip(cfg['revisions'],cfg['checkpoint_steps']):
        rows,meta=checkpoint(run,revision,int(step),[row for row in targets if row['step']==int(step)],tokens,cfg); all_rows+=rows; metas.append(meta); print(json.dumps(meta),flush=True)
    raw=ROOT/'raw'; raw.mkdir(exist_ok=True)
    with (raw/f'stage_a_seed{run}.csv').open('w',newline='',encoding='utf-8') as handle: writer=csv.DictWriter(handle,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)
    (raw/f'stage_a_seed{run}.json').write_text(json.dumps({"arc":cfg['arc'],"outcome_blind":True,"source_sha256":sha(source),"config":cfg,"checkpoints":metas},indent=2),encoding='utf-8')

if __name__=='__main__': main()
