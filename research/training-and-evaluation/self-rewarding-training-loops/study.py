"""Bounded single-token preference learning with an exact arithmetic checker."""
import copy
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from preference import dpo,sequence_logprob,judge_audit


def run(seed,data_seed,profile,output):
    torch.set_num_threads(2);torch.manual_seed(seed);output=Path(output)
    inputs=torch.cartesian_prod(torch.arange(10),torch.arange(10));targets=inputs.sum(1)%10
    x=F.one_hot(inputs,10).float().reshape(-1,20)
    order=torch.randperm(100,generator=torch.Generator().manual_seed(data_seed));train,final=order[:80],order[80:]
    base=nn.Sequential(nn.Linear(20,64),nn.Tanh(),nn.Linear(64,10));reference=copy.deepcopy(base).eval()
    for parameter in reference.parameters():parameter.requires_grad_(False)
    steps=2 if profile=='smoke' else 400;metrics={};records=[]
    for condition in ['unchanged','supervised','preference']:
        model=copy.deepcopy(base);optimizer=torch.optim.Adam(model.parameters(),lr=.003);g=torch.Generator().manual_seed(seed+data_seed);accepted=0;discarded=0
        for step in range(0 if condition=='unchanged' else steps):
            idx=train[torch.randint(len(train),(32,),generator=g)];optimizer.zero_grad();logits=model(x[idx])
            if condition=='supervised':loss=F.cross_entropy(logits,targets[idx])
            else:
                candidates=torch.multinomial(logits.detach().softmax(-1),4,replacement=True,generator=g)
                good=(candidates==targets[idx,None]).any(1);bad=(candidates!=targets[idx,None]).any(1);keep=good&bad;discarded+=int((~keep).sum())
                if not keep.any():continue
                chosen=targets[idx[keep]];rejected=torch.stack([row[row!=truth][0] for row,truth in zip(candidates[keep],chosen)])
                mask=torch.ones((len(chosen),1),dtype=torch.bool);policy=logits[keep,None,:]
                with torch.no_grad():fixed=reference(x[idx[keep]])[:,None,:]
                loss=dpo(sequence_logprob(policy,chosen[:,None],mask),sequence_logprob(policy,rejected[:,None],mask),sequence_logprob(fixed,chosen[:,None],mask),sequence_logprob(fixed,rejected[:,None],mask))
                accepted+=len(chosen)
                if step%50==0:records.append(dict(step=step,operands=inputs[idx[keep]].tolist(),correct=chosen.tolist(),rejected=rejected.tolist()))
            loss.backward();optimizer.step()
        model.eval()
        with torch.no_grad():logits=model(x[final]);accuracy=float((logits.argmax(-1)==targets[final]).float().mean());loss=float(F.cross_entropy(logits,targets[final]))
        metrics.update({condition+'.accuracy':accuracy,condition+'.loss':loss,condition+'.accepted_preferences':accepted,condition+'.discarded_candidate_sets':discarded})
        torch.save(model.state_dict(),output/(condition+'.pt'));np.save(output/(condition+'-logits.npy'),logits.numpy())
    audits=[]
    for target in range(10):
        judge=lambda left,right,t=target:'left' if int(left.strip())==t else 'right' if int(right.strip())==t else 'neither'
        audits.append(judge_audit([dict(id=target,correct=' '+str(target)+' ',incorrect=str((target+1)%10))],judge))
    if not all(a['passed'] for a in audits):raise ValueError('objective checker changed with presentation order')
    np.savez_compressed(output/'data.npz',inputs=inputs.numpy(),targets=targets.numpy(),training_indices=train.numpy(),final_indices=final.numpy())
    Path(output,'preferences.json').write_text(json.dumps(dict(records=records,judge_audits=audits),indent=2)+'\n')
    return dict(scope='Single-token modulo-addition policy, on-policy candidate sampling and exact objective checking; comparison with unchanged and supervised policies on held-out operand pairs. This is not validation of a free-form self-judging language model.',metrics=metrics,seed=seed,data_seed=data_seed,steps=steps)
