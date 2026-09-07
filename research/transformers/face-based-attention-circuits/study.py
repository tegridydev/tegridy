"""Grouped operand evaluation with gate swaps and a labelled layout shift."""
from pathlib import Path
import numpy as np
import torch
from experiment import Model,dataset
from study_support import fit,predict,classification


def run(seed,data_seed,profile,output):
    output=Path(output);train,dev,final=dataset(data_seed)
    steps=2 if profile=='smoke' else 500
    metrics={}
    shifted=final[0].clone()
    shifted[:,1:3]=final[0][:,3:5]
    shifted[:,3:5]=final[0][:,1:3]
    np.savez_compressed(output/'data.npz',train_x=train[0].numpy(),train_y=train[1].numpy(),dev_x=dev[0].numpy(),dev_y=dev[1].numpy(),final_x=final[0].numpy(),final_y=final[1].numpy(),layout_shift_x=shifted.numpy())
    for condition in ['base','dense','static','fbac']:
        torch.manual_seed(seed);model=Model(condition)
        fit(model,train,dev,seed,steps,output,condition)
        for split,x in [('final',final[0]),('layout_shift',shifted)]:
            logits=predict(model,x)
            metrics.update({condition+'.'+split+'.'+k:v for k,v in classification(logits,final[1]).items()})
            np.save(output/(condition+'-'+split+'-logits.npy'),logits.numpy())
            for mode in range(4):metrics[condition+'.'+split+'.mode'+str(mode)]=float((logits.argmax(-1)[x[:,0]==32+mode]==final[1][x[:,0]==32+mode]).float().mean())
        metrics[condition+'.parameters']=sum(p.numel() for p in model.parameters())
        if condition=='fbac':
            within=torch.arange(len(final[0]))
            for mode in range(4):
                idx=torch.where(final[0][:,0]==32+mode)[0];within[idx]=idx.roll(1)
            with torch.no_grad():
                for name,permutation in [('within_mode_swap',within),('cross_mode_swap',torch.arange(len(within)).roll(1))]:
                    logits=model(final[0],permutation)
                    metrics['fbac.'+name+'.accuracy']=classification(logits,final[1])['accuracy']
                    np.save(output/(name+'-logits.npy'),logits.numpy())
    return dict(scope='Grouped 1024 operand pairs, per-mode and layout-shift evaluation, five-run initialisation comparison when default seeds are used. Swap effects are not a matched-magnitude causal identification result.',metrics=metrics,seed=seed,data_seed=data_seed,steps=steps,split_pairs=[768,128,128])
