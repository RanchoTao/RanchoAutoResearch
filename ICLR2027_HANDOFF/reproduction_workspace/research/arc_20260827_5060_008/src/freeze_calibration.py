"""Select and freeze outcome-blind alpha pairs for ARC-008."""

from pathlib import Path
import json, math
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]

def rel(a,b): return abs(a-b)/(max(abs(a),abs(b),1e-12))
def ratio(a,b): return max(a/b,b/a)

def main():
    cfg=yaml.safe_load((ROOT/'config.yaml').read_text()); source=pd.read_csv((ROOT/cfg['corrected_results']).resolve(),usecols=['target_id','target_kl','target_nll_damage','run_id','step','layer','match_class']); source=source[source.match_class.eq('A')]
    candidates=pd.concat([pd.read_csv(p) for p in sorted((ROOT/'raw').glob('calibrate_seed*.csv'))],ignore_index=True)
    rows=[]
    for target in source.itertuples():
        cell=candidates[candidates.target_id.eq(target.target_id)]; block=cell[cell.family_direction.eq('block')]; noise=cell[cell.family_direction.eq('noise')]; choices=[]
        for b in block.itertuples():
            for n in noise.itertuples():
                eps=1e-12
                target_error=sum(abs(math.log(max(x,eps)/max(t,eps))) for x,t in [(b.kl,target.target_kl),(n.kl,target.target_kl),(b.nll_damage,target.target_nll_damage),(n.nll_damage,target.target_nll_damage)])
                objective=target_error+abs(math.log(max(n.kl,eps)/max(b.kl,eps)))+abs(math.log(max(n.nll_damage,eps)/max(b.nll_damage,eps)))+.5*abs(math.log(max(n.hidden_relative_norm,eps)/max(b.hidden_relative_norm,eps)))+.5*abs(math.log(max(n.output_logit_norm,eps)/max(b.output_logit_norm,eps)))+5*abs(n.output_abs_cosine-b.output_abs_cosine)
                choices.append((objective,b,n))
        objective,b,n=min(choices,key=lambda x:x[0]); c=cfg['pair_calipers']
        checks={"pass_kl":rel(b.kl,n.kl)<=c['relative_kl_difference'],"pass_nll":rel(b.nll_damage,n.nll_damage)<=c['relative_nll_difference'],
                "pass_hidden_norm":ratio(b.hidden_relative_norm,n.hidden_relative_norm)<=c['hidden_norm_ratio'],"pass_output_norm":ratio(b.output_logit_norm,n.output_logit_norm)<=c['output_norm_ratio'],
                "pass_abs_cosine":abs(b.output_abs_cosine-n.output_abs_cosine)<=c['absolute_cosine_difference']}
        rows.append({"target_id":target.target_id,"run_id":target.run_id,"step":target.step,"layer":target.layer,"block_alpha":b.alpha,"noise_alpha":n.alpha,"objective":objective,
                     "block_kl":b.kl,"noise_kl":n.kl,"block_nll":b.nll_damage,"noise_nll":n.nll_damage,"block_hidden_norm":b.hidden_relative_norm,"noise_hidden_norm":n.hidden_relative_norm,
                     "block_output_norm":b.output_logit_norm,"noise_output_norm":n.output_logit_norm,"block_abs_cosine":b.output_abs_cosine,"noise_abs_cosine":n.output_abs_cosine,
                     **checks,"calibration_pass":all(checks.values())})
    out=pd.DataFrame(rows);out.to_csv(ROOT/'calibration_manifest.csv',index=False)
    selected=out[out.calibration_pass];run=selected.groupby('run_id').size().reindex(cfg['run_ids'],fill_value=0);step=selected.groupby('step').size().reindex(cfg['checkpoint_steps'],fill_value=0)
    support=bool(len(selected)>=cfg['support']['cells'] and run.min()>=cfg['support']['per_run'] and step.min()>=cfg['support']['per_checkpoint'])
    summary={"outcome_blind":True,"cells":len(out),"passed":len(selected),"by_run":{str(k):int(v) for k,v in run.items()},"by_step":{str(k):int(v) for k,v in step.items()},"support_pass":support}
    (ROOT/'calibration_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
