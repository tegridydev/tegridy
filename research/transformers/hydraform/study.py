"""Train structural mutations with fixed-size and optimiser-reset controls."""
import copy
import json
from pathlib import Path
import time
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from adaptation import AdaptiveAttention


class Classifier(nn.Module):
    def __init__(self,widths=(16,16,16,16)):
        super().__init__();self.attention=AdaptiveAttention(widths);self.head=nn.Linear(64,2)
    def forward(self,x):return self.head(self.attention(x).mean(1))


def run(seed,data_seed,profile,output):
    torch.set_num_threads(2);g=torch.Generator().manual_seed(data_seed);output=Path(output)
    x=torch.randn(2048,8,64,generator=g);y=(x[:,:,0].mean(1)>0).long();train,dev,final=(x[:1536],y[:1536]),(x[1536:1792],y[1536:1792]),(x[1792:],y[1792:])
    steps=4 if profile=='smoke' else 300;metrics={};receipts=[]
    for condition in ['fixed_initial','fixed_final','reset_control','random_mutation','guided_mutation']:
        torch.manual_seed(seed);model=Classifier((20,12,16,16) if condition=='fixed_final' else (16,16,16,16));optimizer=torch.optim.Adam(model.parameters(),lr=.001);start=time.perf_counter();events=[]
        generator=torch.Generator().manual_seed(seed+100000)
        for step in range(steps):
            if step==steps//2 and condition in ['reset_control','random_mutation','guided_mutation']:
                if condition!='reset_control':
                    candidates=[]
                    for receiver,donor in [(0,1),(2,3)]:
                        candidate=copy.deepcopy(model);budget=sum(p.numel() for p in candidate.attention.parameters())
                        _,narrow=candidate.attention.mutate(donor,12,budget);_,widen=candidate.attention.mutate(receiver,20,budget)
                        with torch.no_grad():score=float(F.cross_entropy(candidate(dev[0]),dev[1]))
                        candidates.append((score,candidate,[narrow,widen]))
                    chosen=min(candidates,key=lambda c:c[0]) if condition=='guided_mutation' else candidates[seed%2]
                    model=chosen[1];events=[{k:v for k,v in event.items() if 'parameter_ids' not in k} for event in chosen[2]]
                optimizer=torch.optim.Adam(model.parameters(),lr=.001)
                if {id(p) for group in optimizer.param_groups for p in group['params']}!={id(p) for p in model.parameters()}:raise ValueError('optimizer missed mutated parameters')
            idx=torch.randint(len(train[0]),(32,),generator=generator);optimizer.zero_grad();loss=F.cross_entropy(model(train[0][idx]),train[1][idx]);loss.backward();optimizer.step()
        model.eval()
        with torch.no_grad():logits=model(final[0]);accuracy=float((logits.argmax(-1)==final[1]).float().mean())
        metrics.update({condition+'.accuracy':accuracy,condition+'.elapsed_seconds':time.perf_counter()-start,condition+'.parameters':sum(p.numel() for p in model.parameters())})
        torch.save(dict(widths=model.attention.architecture(),state=model.state_dict()),output/(condition+'.pt'));np.save(output/(condition+'-logits.npy'),logits.numpy());receipts.append(dict(condition=condition,events=events,steps=steps))
    np.savez_compressed(output/'data.npz',x=x.numpy(),y=y.numpy());Path(output,'mutations.json').write_text(json.dumps(receipts,indent=2)+'\n')
    return dict(scope='Synthetic sequence classification, equal total head width, fixed/final-size/reset controls and two-candidate development-guided mutation. Candidate evaluation time is included. Not an upstream reproduction or AG News result.',metrics=metrics,seed=seed,data_seed=data_seed)
