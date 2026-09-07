"""Train a query projection through detached, causally eligible episodic memory."""
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from memory import Memory


class Reader(nn.Module):
    def __init__(self,mode):
        super().__init__();self.mode=mode;self.query=nn.Linear(16,16,bias=False);self.output=nn.Linear(16,16)
    def forward(self,keys,values,query):
        encoded=self.query(F.one_hot(query,16).float())
        if self.mode=='none':read=torch.zeros_like(encoded)
        elif self.mode=='attention':
            scores=torch.einsum('bi,bti->bt',encoded,F.one_hot(keys,16).float())/4
            read=torch.einsum('bt,bti->bi',scores.softmax(-1),F.one_hot(values,16).float())
        else:
            bank=Memory(batch_size=len(keys),total_capacity=4,heads=1,width=16)
            bank.gate.requires_grad_(False)
            for step in range(keys.shape[1]):bank.write(F.one_hot(keys[:,step],16).float()[:,None,:],F.one_hot(values[:,step],16).float()[:,None,:],step)
            read=bank(encoded[:,None,:],keys.shape[1])[:,0]
        return self.output(read)


def run(seed,data_seed,profile,output):
    torch.set_num_threads(2);g=torch.Generator().manual_seed(data_seed);output=Path(output)
    keys=torch.stack([torch.randperm(16,generator=g)[:8] for _ in range(2048)]);values=torch.randint(16,(2048,8),generator=g);position=torch.randint(8,(2048,),generator=g);query=keys[torch.arange(len(keys)),position];target=values[torch.arange(len(keys)),position]
    metrics={};steps=2 if profile=='smoke' else 300
    for mode in ['none','attention','fifo']:
        torch.manual_seed(seed);model=Reader(mode);optimizer=torch.optim.Adam(model.parameters(),lr=.01);generator=torch.Generator().manual_seed(seed+data_seed)
        for step in range(steps):
            idx=torch.randint(1536,(32,),generator=generator);optimizer.zero_grad();loss=F.cross_entropy(model(keys[idx],values[idx],query[idx]),target[idx]);loss.backward();optimizer.step()
        model.eval()
        with torch.no_grad():logits=torch.cat([model(keys[start:start+64],values[start:start+64],query[start:start+64]) for start in range(1536,2048,64)])
        correct=logits.argmax(-1)==target[1536:];metrics[mode+'.accuracy']=float(correct.float().mean())
        for name,mask in [('retained',position[1536:]>=4),('evicted',position[1536:]<4)]:metrics[mode+'.'+name+'.accuracy']=float(correct[mask].float().mean())
        torch.save(model.state_dict(),output/(mode+'.pt'));np.save(output/(mode+'-logits.npy'),logits.numpy())
    np.savez_compressed(output/'episodes.npz',keys=keys.numpy(),values=values.numpy(),query=query.numpy(),target=target.numpy(),position=position.numpy())
    return dict(scope='Synthetic eight-write episodic lookup with a learned query projection, no-memory, full-eight-item attention and four-slot FIFO. Capacity difference is explicit; this is not a full reflective Transformer or LRU comparison.',metrics=metrics,seed=seed,data_seed=data_seed,steps=steps)
