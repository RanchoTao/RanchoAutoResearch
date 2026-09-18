"""Outcome-blind ARC-007R geometry comparison and match freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ARC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ARC_ROOT.parents[1]
ARC007 = ARC_ROOT.parent / "arc_20260826_5060_007"
RUNS = [2, 3, 5, 6, 8]
BOOT_SEED = 20260827
BOOT_DRAWS = 100_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_geometry() -> tuple[pd.DataFrame, list[dict]]:
    rows, manifest = [], []
    for path in sorted((ARC007 / "raw" / "geometry").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        before = len(rows)
        for checkpoint in payload["checkpoints"]:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"harness failure: {path.name}")
            rows.extend(checkpoint["geometry_rows"])
        manifest.append({"path":str(path.relative_to(REPO_ROOT)).replace("\\","/"),
                         "sha256":sha256(path),"rows":len(rows)-before,"status":"verified"})
    frame = pd.DataFrame(rows)
    if len(frame)!=300 or frame[["target_id","family"]].duplicated().any():
        raise RuntimeError("geometry family grain failure")
    if frame.target_id.nunique()!=150 or set(frame.family)!={"block","noise"}:
        raise RuntimeError("geometry cell/family coverage failure")
    if frame.drop_duplicates("target_id").match_class.value_counts().to_dict()!={"A":103,"B":31,"C":16}:
        raise RuntimeError("geometry match-class failure")
    if float((frame.delta_margin_mean-frame.delta_b_mean).abs().max())>1e-8:
        raise RuntimeError("anchored margin identity failure")
    return frame, manifest


def add_margin_std(frame: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for path in sorted((ARC007/"raw"/"per_example").glob("seed*_step*.npz")):
        stem=path.stem
        run_id=int(stem.split("_step")[0].replace("seed",""))
        step=int(stem.split("_step")[1])
        with np.load(path) as payload:
            values=payload["intact_margin"].astype(float)
        rows.append({"run_id":run_id,"step":step,"intact_margin_std":float(values.std(ddof=0)),
                     "array_sha256":sha256(path)})
    margins=pd.DataFrame(rows)
    if len(margins)!=15 or margins[["run_id","step"]].duplicated().any():
        raise RuntimeError("margin array coverage failure")
    return frame.merge(margins,on=["run_id","step"],validate="many_to_one")


def bootstrap(values: np.ndarray) -> list[float]:
    rng=np.random.default_rng(BOOT_SEED)
    draws=rng.choice(np.asarray(values,float),size=(BOOT_DRAWS,len(values)),replace=True).mean(axis=1)
    return [float(x) for x in np.quantile(draws,[.025,.975])]


def comparison(pairs: pd.DataFrame, column: str) -> dict:
    run=pairs.groupby("run_id")[column].median().reindex(RUNS)
    values=run.to_numpy(float); mean=float(values.mean()); sign=-1 if mean<0 else 1
    layer=pairs.groupby("layer")[column].mean()
    return {"metric":column,"paired_cell_mean":float(pairs[column].mean()),
            "mean_run_median":mean,"run_medians":{str(int(k)):float(v) for k,v in run.items()},
            "bootstrap_95_ci":bootstrap(values),
            "same_sign_runs":int((np.sign(values)==sign).sum()),
            "same_sign_layers":int((np.sign(layer.to_numpy())==sign).sum()),
            "layers":int(len(layer))}


def main() -> None:
    frame, source_manifest=load_geometry()
    frame=add_margin_std(frame)
    safe_columns=["target_id","run_id","step","layer","match_class","selected_beta","family",
        "kl","nll_damage","delta_b_mean","delta_b_median","delta_b_q10","delta_b_q25",
        "delta_b_q75","delta_b_q90","delta_margin_mean","delta_margin_identity_max_abs",
        "logit_delta_norm_mean","logit_delta_norm_median","cosine_alignment_mean",
        "abs_cosine_alignment_mean","intact_margin_mean","intact_margin_median",
        "intact_margin_std","intact_margin_q10","intact_margin_q25","intact_margin_q75",
        "intact_margin_q90","baseline_nll"]
    blind=frame[safe_columns].copy()
    primary=blind[blind.match_class=="A"]
    identity=["target_id","run_id","step","layer","match_class"]
    wide=primary.pivot(index=identity,columns="family",
        values=["delta_b_mean","logit_delta_norm_mean","abs_cosine_alignment_mean"]).reset_index()
    wide.columns=["_".join([str(x) for x in col if str(x)]) if isinstance(col,tuple) else col for col in wide.columns]
    wide=wide.rename(columns={"target_id_":"target_id","run_id_":"run_id","step_":"step",
                              "layer_":"layer","match_class_":"match_class"})
    wide["delta_boundary_difference"]=wide["delta_b_mean_noise"]-wide["delta_b_mean_block"]
    wide["logit_norm_difference"]=wide["logit_delta_norm_mean_noise"]-wide["logit_delta_norm_mean_block"]
    wide["absolute_cosine_difference_signed"]=wide["abs_cosine_alignment_mean_noise"]-wide["abs_cosine_alignment_mean_block"]
    wide["absolute_log_norm_ratio"]=(np.log(wide.logit_delta_norm_mean_noise)-np.log(wide.logit_delta_norm_mean_block)).abs()
    pooled=float(primary.delta_b_mean.std(ddof=0))
    wide["delta_b_standardized_difference"]=wide.delta_boundary_difference.abs()/pooled
    wide["absolute_cosine_difference"]=wide.absolute_cosine_difference_signed.abs()
    wide["pass_delta_b"]=wide.delta_b_standardized_difference<=.5
    wide["pass_norm"]=wide.absolute_log_norm_ratio<=np.log(1.25)
    wide["pass_cosine"]=wide.absolute_cosine_difference<=.10
    wide["geometry_match"]=wide.pass_delta_b&wide.pass_norm&wide.pass_cosine
    reasons=[]
    for row in wide.itertuples():
        failed=[]
        if not row.pass_delta_b: failed.append("delta_boundary")
        if not row.pass_norm: failed.append("log_norm")
        if not row.pass_cosine: failed.append("abs_cosine")
        reasons.append(";".join(failed))
    wide["failure_reason"]=reasons

    old=pd.read_csv(ARC007/"geometry_match_manifest.csv")
    check=wide.merge(old[["target_id","geometry_match"]].rename(columns={"geometry_match":"old_match"}),
                     on="target_id",validate="one_to_one")
    if not (check.geometry_match==check.old_match).all():
        raise RuntimeError("outcome-blind match reproduction failure")
    selected=wide[wide.geometry_match]
    coverage_run=selected.groupby("run_id").size().reindex(RUNS,fill_value=0)
    coverage_step=selected.groupby("step").size().reindex([14000,72000,143000],fill_value=0)
    quality={"class_a_cells":103,"matched_cells":int(len(selected)),"coverage":float(len(selected)/103),
             "pooled_delta_boundary_sd":pooled,
             "calipers":{"delta_boundary_standardized_difference":.5,
                         "absolute_log_norm_ratio":float(np.log(1.25)),"absolute_cosine_difference":.10},
             "coverage_by_run":{str(int(k)):int(v) for k,v in coverage_run.items()},
             "coverage_by_step":{str(int(k)):int(v) for k,v in coverage_step.items()},
             "support_adequate":bool(len(selected)>=30 and coverage_run.min()>=3 and coverage_step.min()>=5),
             "historical_subset_exactly_reproduced":True}
    comparisons=[comparison(wide,"delta_boundary_difference"),comparison(wide,"logit_norm_difference"),
                 comparison(wide,"absolute_cosine_difference_signed")]
    systematic=[row["metric"] for row in comparisons if (row["bootstrap_95_ci"][0]>0 or row["bootstrap_95_ci"][1]<0) and row["same_sign_runs"]>=4]
    result={"arc":"ARC-20260827-5060-007R","outcome_blind":True,
            "family_comparisons":comparisons,"systematic_metrics":systematic,
            "matching":quality,"source_manifest":source_manifest}
    ARC_ROOT.mkdir(parents=True,exist_ok=True)
    blind.to_csv(ARC_ROOT/"geometry_blinded.csv",index=False)
    wide.to_csv(ARC_ROOT/"geometry_pair_blinded.csv",index=False)
    wide[["target_id","run_id","step","layer","geometry_match","delta_b_standardized_difference",
          "absolute_log_norm_ratio","absolute_cosine_difference","pass_delta_b","pass_norm",
          "pass_cosine","failure_reason"]].to_csv(ARC_ROOT/"geometry_match_manifest.csv",index=False)
    (ARC_ROOT/"outcome_blind_summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
