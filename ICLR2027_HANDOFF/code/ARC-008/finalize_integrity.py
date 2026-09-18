"""Validate and seal ARC-008."""

from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
REQ=['README.md','preregistration.md','representation_site.md','resource_usage.md','activation_manifest.csv','direction_metrics.csv','stageA_analysis.md','counterfactual_protocol.md','calibration_diagnostics.md','counterfactual_results.csv','sign_reversal_analysis.md','layer_analysis.md','statistical_analysis.md','strongest_counterevidence.md','paper_implications.md','next_arc_recommendation.md','EXECUTIVE_SUMMARY.md','results.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(base,manifest):
    bad=[]
    for line in manifest.read_text().splitlines():
        if line.strip():
            expected,rel=line.split(maxsplit=1);p=base/rel.strip();
            if not p.is_file() or sha(p).lower()!=expected.lower():bad.append(rel.strip())
    return bad
def main():
    d=pd.read_csv(ROOT/'direction_metrics.csv');c=pd.read_csv(ROOT/'calibration_manifest.csv');cf=pd.read_csv(ROOT/'counterfactual_results.csv');s=json.loads((ROOT/'results.json').read_text());figs=list((ROOT/'figures').glob('*.png'))
    bad6=verify(ROOT.parent/'arc_20260827_5060_006R',ROOT.parent/'arc_20260827_5060_006R'/'final_integrity.sha256');bad7=verify(ROOT.parent/'arc_20260827_5060_007R',ROOT.parent/'arc_20260827_5060_007R'/'final_integrity.sha256')
    checks={'required':all((ROOT/x).is_file() for x in REQ),'direction_103':len(d)==103 and d.target_id.nunique()==103,'direction_finite':np.isfinite(d.select_dtypes(include='number')).all().all(),'valid_fraction':d.valid_fraction.min()>=.999,
            'calibration_103':len(c)==103,'calibration_pass_15':int(c.calibration_pass.sum())==15,'support_failed':not s['stage_b']['calibration_support']['support_pass'],'counterfactual_empty':len(cf)==0,
            'no_confirm_raw':not any((ROOT/'raw').glob('confirm_seed*')),'verdict':s['verdict']=='DIRECTION-NONIDENTIFIABLE','figures_supported':len(figs)==3 and all(p.stat().st_size>10000 for p in figs),'arc006r_seal':not bad6,'arc007r_seal':not bad7}
    checks={k:bool(v) for k,v in checks.items()};out={'pass':all(checks.values()),'checks':checks,'arc006r_failures':bad6,'arc007r_failures':bad7,'figures':[p.name for p in figs],'verdict':s['verdict']};(ROOT/'final_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');(ROOT/'final_validation.md').write_text('# Final validation\n\nOverall: **'+('PASS' if out['pass'] else 'FAIL')+'**.\n\n'+'\n'.join(f"- {'PASS' if v else 'FAIL'}: `{k}`" for k,v in checks.items())+f"\n\nFinal verdict: `{s['verdict']}`.\n",encoding='utf-8')
    if not out['pass']:raise RuntimeError(json.dumps(out,indent=2))
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='final_integrity.sha256' and '__pycache__' not in p.parts);(ROOT/'final_integrity.sha256').write_text('\n'.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in files)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
