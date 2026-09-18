"""Outcome-blind Stage A1 summary and activation manifest."""

from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def boot(values,level=.95):
    cfg=yaml.safe_load((ROOT/'config.yaml').read_text());rng=np.random.default_rng(cfg['bootstrap_seed']);v=np.asarray(values,float);d=rng.choice(v,(cfg['bootstrap_draws'],len(v)),replace=True).mean(1);t=(1-level)/2;return [float(x) for x in np.quantile(d,[t,1-t])]

def main():
    cfg=yaml.safe_load((ROOT/'config.yaml').read_text());paths=sorted((ROOT/'raw').glob('stage_a_seed*.csv'));data=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
    if len(data)!=103 or data.target_id.nunique()!=103 or data[['run_id','step','layer']].duplicated().any(): raise RuntimeError('Stage A grain failure')
    if data.valid_fraction.min()<.999 or not np.isfinite(data.select_dtypes(include='number')).all().all(): raise RuntimeError('Stage A validity failure')
    run=data.groupby('run_id').directional_disagreement.median().reindex(cfg['run_ids']);ci=boot(run);substantial=bool(ci[0]>.75 and (run>.75).sum()>=4)
    summary={"outcome_blind":True,"cells":len(data),"valid_fraction_min":float(data.valid_fraction.min()),"mean_cosine":float(data.cosine_mean.mean()),
             "mean_disagreement":float(data.directional_disagreement.mean()),"cell_disagreement_sd":float(data.directional_disagreement.std(ddof=0)),
             "run_median_disagreement":{str(int(k)):float(v) for k,v in run.items()},"run_bootstrap_95_ci":ci,"substantially_distinct":substantial,
             "usable_cross_cell_variation":bool(data.directional_disagreement.std(ddof=0)>=.002),
             "checkpoint_medians":{str(int(k)):float(v) for k,v in data.groupby('step').directional_disagreement.median().items()},
             "layer_medians":{str(int(k)):float(v) for k,v in data.groupby('layer').directional_disagreement.median().items()}}
    manifest=[]
    for p in sorted((ROOT/'raw').glob('stage_a_seed*.json')):
        payload=json.loads(p.read_text());
        for row in payload['checkpoints']:manifest.append({"run_id":row['run_id'],"step":row['step'],"revision":row['revision'],"commit_hash":row['commit_hash'],"targets":row['targets'],"runtime_seconds":row['runtime_seconds'],"peak_cuda_bytes":row['peak_cuda_bytes'],"source_file":p.name,"source_sha256":digest(p)})
    data.to_csv(ROOT/'direction_metrics.csv',index=False);pd.DataFrame(manifest).to_csv(ROOT/'activation_manifest.csv',index=False);(ROOT/'stageA1_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
