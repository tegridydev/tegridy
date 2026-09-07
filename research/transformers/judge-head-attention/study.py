"""64-token recall on disjoint key/value associations; post-computation gates."""
from pathlib import Path
import numpy as np
import torch
from experiment import RecallModel
from study_support import fit,predict,classification


def grouped_data(seed, counts):
    g=torch.Generator().manual_seed(seed)
    pairs=torch.cartesian_prod(torch.arange(32),torch.arange(32))
    pairs=pairs[torch.randperm(len(pairs),generator=g)]
    pools=[pairs[:768],pairs[768:896],pairs[896:]]
    result=[]
    for pool,count in zip(pools,counts):
        x=torch.full((count,64),69,dtype=torch.long);y=torch.empty(count,dtype=torch.long)
        for row in range(count):
            first=pool[torch.randint(len(pool),(1,),generator=g).item()]
            eligible=pool[pool[:,0]!=first[0]]
            second=eligible[torch.randint(len(eligible),(1,),generator=g).item()]
            x[row,0],x[row,1]=first[0],first[1]+32
            x[row,20],x[row,21]=second[0],second[1]+32
            selected=first if torch.rand((),generator=g)<.5 else second
            x[row,-1],y[row]=selected[0],selected[1]
        result.append((x,y))
    return result,pools


def run(seed,data_seed,profile,output):
    counts=[64,32,32] if profile=='smoke' else [8192,1024,2048]
    steps=2 if profile=='smoke' else 500
    (train,dev,final),pools=grouped_data(data_seed,counts)
    metrics={};output=Path(output)
    np.savez_compressed(output/'data.npz',train_x=train[0].numpy(),train_y=train[1].numpy(),dev_x=dev[0].numpy(),dev_y=dev[1].numpy(),final_x=final[0].numpy(),final_y=final[1].numpy(),train_pairs=pools[0].numpy(),dev_pairs=pools[1].numpy(),final_pairs=pools[2].numpy())
    for condition in ['ordinary','static','token','judge']:
        torch.manual_seed(seed);model=RecallModel(condition,sequence_length=64)
        selected=fit(model,train,dev,seed,steps,output,condition)
        logits=predict(model,final[0]);values=classification(logits,final[1])
        metrics.update({condition+'.'+k:v for k,v in values.items()})
        metrics[condition+'.parameters']=sum(p.numel() for p in model.parameters())
        metrics[condition+'.selected_step']=selected
        np.save(output/(condition+'-logits.npy'),logits.numpy())
    return dict(scope='64-token two-pair synthetic recall; disjoint key/value associations and development checkpoint selection. Gating computes all heads; parameter differences are reported, not claimed matched. Causal head-importance study remains separate.',metrics=metrics,seed=seed,data_seed=data_seed,steps=steps,split_rows=counts)
