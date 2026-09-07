"""Held-out irregular temporal episodes, shift controls and saved probabilities."""
from pathlib import Path
import numpy as np
import torch
from experiment import TemporalModel,episodes
from study_support import fit,predict,classification


def run(seed,data_seed,profile,output):
    output=Path(output);metrics={}
    counts=[64,32,32] if profile=='smoke' else [2048,512,1024]
    steps=2 if profile=='smoke' else 400
    for periodic in [False,True]:
        task='periodic' if periodic else 'switching'
        train=episodes(data_seed,counts[0],periodic)
        dev=episodes(data_seed+1,counts[1],periodic)
        final=episodes(data_seed+2,counts[2],periodic)
        shift=episodes(data_seed+3,counts[2],periodic,gaps=(19,37,83))
        np.savez_compressed(output/(task+'-data.npz'),train_x=train[0].numpy(),train_y=train[1].numpy(),dev_x=dev[0].numpy(),dev_y=dev[1].numpy(),final_x=final[0].numpy(),final_y=final[1].numpy(),shift_x=shift[0].numpy(),shift_y=shift[1].numpy())
        for condition in ['position','features','fixed','learned']:
            torch.manual_seed(seed);model=TemporalModel(condition)
            name=task+'-'+condition
            fit(model,train,dev,seed,steps,output,name,binary=True)
            for split,data in [('final',final),('shift',shift)]:
                logits=predict(model,data[0]);values=classification(logits,data[1],binary=True)
                metrics.update({name+'.'+split+'.'+k:v for k,v in values.items()})
                np.save(output/(name+'-'+split+'-logits.npy'),logits.numpy())
            if condition=='learned':
                for i,value in enumerate(torch.nn.functional.softplus(model.raw_decay).detach()):metrics[name+'.decay'+str(i)]=float(value)
        for split,data in [('final',final),('shift',shift)]:
            metrics[task+'.last_observation.'+split+'.accuracy']=float((data[0][:,-1,0]==data[1]).float().mean())
    return dict(scope='Two synthetic temporal generators, frozen final and gap-shift sets, development-selected checkpoints; no universal recency or real-arrival-process claim.',metrics=metrics,seed=seed,data_seed=data_seed,split_rows=counts,steps=steps)
