"""Frozen observational Stage A2 analysis after Stage B support failure."""

from pathlib import Path
import json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.metrics import mean_squared_error,roc_auc_score,balanced_accuracy_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]; RUNS=[2,3,5,6,8]; BLUE='#4477AA';ORANGE='#EE7733';GOLD='#CCAA44';INK='#2B2B2B';GRID='#D9D9D9'
BASE=['mean_kl','mean_nll','delta_boundary_difference','output_log_norm_ratio','output_abs_cosine_difference']; AUG=BASE+['directional_disagreement','log_noise_block_norm_ratio']

def design(train,test,features,layer=True):
    sc=StandardScaler().fit(train[features]); a=sc.transform(train[features]);b=sc.transform(test[features])
    fixed=['step']+(['layer'] if layer else [])
    both=pd.concat([train[fixed],test[fixed]]);d=pd.get_dummies(both.astype(str),prefix=fixed,drop_first=True,dtype=float)
    da=d.iloc[:len(train)].to_numpy();db=d.iloc[len(train):].to_numpy();return np.column_stack([a,da]),np.column_stack([b,db])

def loo_reg(data,features):
    rows=[]
    for run in RUNS:
        tr=data[~data.run_id.eq(run)];te=data[data.run_id.eq(run)];x,z=design(tr,te,features);m=LinearRegression().fit(x,tr.family_residual);pred=m.predict(z)
        rows.extend({'target_id':t,'run_id':run,'truth':y,'prediction':p} for t,y,p in zip(te.target_id,te.family_residual,pred))
    out=pd.DataFrame(rows);return out,float(np.sqrt(mean_squared_error(out.truth,out.prediction)))

def loo_logit(data,features):
    rows=[]
    for run in RUNS:
        tr=data[~data.run_id.eq(run)];te=data[data.run_id.eq(run)];x,z=design(tr,te,features);m=LogisticRegression(C=1,class_weight='balanced',solver='liblinear',random_state=20260827).fit(x,tr.reversal);p=m.predict_proba(z)[:,1]
        rows.extend({'target_id':t,'run_id':run,'truth':int(y),'probability':q} for t,y,q in zip(te.target_id,te.reversal,p))
    out=pd.DataFrame(rows);auc=float(roc_auc_score(out.truth,out.probability));bal=float(balanced_accuracy_score(out.truth,out.probability>=.5));return out,auc,bal

def weighted_sd(table,col):
    x=table[col].to_numpy(float);w=table.cells.to_numpy(float);mu=np.average(x,weights=w);return float(np.sqrt(np.average((x-mu)**2,weights=w)))

def style(ax): ax.grid(True,color=GRID,alpha=.65);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False)
def blossom(fig):
    for dx,dy in [(-.006,0),(.006,0),(0,-.008),(0,.008)]:fig.add_artist(plt.Circle((.975+dx,.965+dy),.004,transform=fig.transFigure,color=GOLD,alpha=.8))

def figures(data):
    out=ROOT/'figures';out.mkdir(exist_ok=True);plt.rcParams.update({'font.size':10})
    fig,ax=plt.subplots(figsize=(7.8,4.8));groups=[data[data.run_id.eq(r)].cosine_mean for r in RUNS];ax.boxplot(groups,labels=[f'seed{r}' for r in RUNS],patch_artist=True,boxprops={'facecolor':'white','edgecolor':BLUE},medianprops={'color':INK})
    for i,g in enumerate(groups,1):ax.scatter(np.full(len(g),i)+np.random.default_rng(20260827+i).normal(0,.04,len(g)),g,s=18,facecolors='none',edgecolors=ORANGE,alpha=.6)
    ax.axhline(0,color=INK);ax.set_ylabel('Block-noise directional cosine');ax.set_title('Cross-family hidden-direction cosine by training run (103 cells)');style(ax);blossom(fig);fig.tight_layout();fig.savefig(out/'fig1_direction_cosine.png',dpi=240);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.6,4.8));
    for r,m in zip(RUNS,['o','^','s','D','P']):q=data[data.run_id.eq(r)];ax.scatter(q.directional_disagreement,q.family_residual,marker=m,s=42,alpha=.7,label=f'seed{r}')
    ax.axhline(0,color=INK);ax.set_xlabel('Directional disagreement (1 - cosine)');ax.set_ylabel('Corrected family residual');ax.set_title('Corrected residual vs hidden-direction disagreement (103 cells)');ax.legend(frameon=False,ncol=3);style(ax);blossom(fig);fig.tight_layout();fig.savefig(out/'fig2_residual_disagreement.png',dpi=240);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9.2,4.6));rev=data.reversal.astype(bool)
    for ax,col,label in [(axes[0],'directional_disagreement','Directional disagreement'),(axes[1],'log_noise_block_norm_ratio','Log noise/block norm ratio')]:
        ax.boxplot([data.loc[~rev,col],data.loc[rev,col]],labels=[f'Ordinary\n(n={(~rev).sum()})',f'Reversal\n(n={rev.sum()})'],patch_artist=True,boxprops={'facecolor':'white','edgecolor':BLUE},medianprops={'color':INK});ax.set_ylabel(label);style(ax)
    fig.suptitle('Internal direction statistics by corrected reversal status');blossom(fig);fig.tight_layout();fig.savefig(out/'fig5_reversal_direction.png',dpi=240);plt.close(fig)

def main():
    direction=pd.read_csv(ROOT/'direction_metrics.csv');corr=pd.read_csv(ROOT.parent/'arc_20260827_5060_006R'/'corrected_results.csv');corr=corr[corr.match_class.eq('A')]
    geo=pd.read_csv(ROOT.parent/'arc_20260827_5060_007R'/'processed'/'geometry_pairs_corrected.csv')
    source=corr[['target_id','corrected_residual','corrected_reversal','block_kl','reveal_kl','block_nll_damage','reveal_nll_damage']].copy();source['mean_kl']=(source.block_kl+source.reveal_kl)/2;source['mean_nll']=(source.block_nll_damage+source.reveal_nll_damage)/2
    geo=geo[['target_id','delta_boundary_difference','log_norm_ratio','abs_cosine_difference']].rename(columns={'log_norm_ratio':'output_log_norm_ratio','abs_cosine_difference':'output_abs_cosine_difference'})
    data=direction.merge(source,on='target_id',validate='one_to_one').merge(geo,on='target_id',validate='one_to_one');data=data.rename(columns={'corrected_residual':'family_residual','corrected_reversal':'reversal'})
    pb,rb=loo_reg(data,BASE);pa,ra=loo_reg(data,AUG);lb,ab,bb=loo_logit(data,BASE);la,aa,ba=loo_logit(data,AUG)
    # Exclude layer indicators here so heterogeneity cannot be removed mechanically.
    xb,_=design(data,data,BASE,layer=False);xa,_=design(data,data,AUG,layer=False);data['resid_base']=data.family_residual-LinearRegression().fit(xb,data.family_residual).predict(xb);data['resid_aug']=data.family_residual-LinearRegression().fit(xa,data.family_residual).predict(xa)
    layer=data.groupby('layer',as_index=False).agg(cells=('target_id','size'),raw=('family_residual','median'),baseline_residual=('resid_base','median'),augmented_residual=('resid_aug','median'))
    sdb=weighted_sd(layer,'baseline_residual');sda=weighted_sd(layer,'augmented_residual');cal=json.loads((ROOT/'calibration_summary.json').read_text())
    summary={"verdict":"DIRECTION-NONIDENTIFIABLE","stage_a":{"loo_baseline_rmse":rb,"loo_augmented_rmse":ra,"rmse_reduction":1-ra/rb,"material":bool(1-ra/rb>=.10),
                "baseline_reversal_auc":ab,"augmented_reversal_auc":aa,"auc_improvement":aa-ab,"augmented_balanced_accuracy":ba,
                "reversal_informative":bool(aa>=.70 and aa-ab>=.05),"direction_residual_correlation":float(data.directional_disagreement.corr(data.family_residual))},
             "layer":{"baseline_weighted_sd":sdb,"augmented_weighted_sd":sda,"shrinkage":1-sda/sdb,"rows":layer.to_dict('records')},
             "stage_b":{"calibration_support":cal,"heldout_ds_revealed":False,"reason":"frozen calibration support gate failed"}}
    data.to_csv(ROOT/'processed_analysis.csv',index=False);pb.to_csv(ROOT/'processed_loo_baseline.csv',index=False);pa.to_csv(ROOT/'processed_loo_augmented.csv',index=False);lb.to_csv(ROOT/'processed_reversal_baseline.csv',index=False);la.to_csv(ROOT/'processed_reversal_augmented.csv',index=False);layer.to_csv(ROOT/'processed_layer.csv',index=False)
    pd.DataFrame(columns=['target_id','run_id','step','layer','block_ds','noise_ds','direction_effect','eligible']).to_csv(ROOT/'counterfactual_results.csv',index=False)
    (ROOT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');figures(data);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
