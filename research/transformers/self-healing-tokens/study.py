"""Grouped repair comparison across corruption severity, with raw predictions."""
import json
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from experiment import Denoiser,records,measure,POSITIONS
from repair_reference import repair


def run(seed,data_seed,profile,output):
    torch.set_num_threads(2);output=Path(output);metrics={};details={}
    count,steps=(128,2) if profile=='smoke' else (4096,500)
    train_end=int(count*.7);dev_end=int(count*.85)
    clean,noisy,mask=records(data_seed,count,.15)
    for condition in ['ordinary','gated']:
        torch.manual_seed(seed);model=Denoiser();optimizer=torch.optim.Adam(model.parameters(),lr=.001)
        generator=torch.Generator().manual_seed(seed+100000)
        trace=[];best=float('inf');state=None
        for step in range(steps):
            model.train();idx=torch.randint(train_end,(32,),generator=generator);optimizer.zero_grad()
            logits,detector=model(noisy[idx]);loss=F.cross_entropy(logits.transpose(1,2),clean[idx][:,POSITIONS])
            if condition=='gated':loss+=F.binary_cross_entropy_with_logits(detector,mask[idx].float())
            loss.backward();optimizer.step()
            if (step+1)%50==0 or step==steps-1:
                model.eval()
                with torch.no_grad():
                    logits,detector=model(noisy[train_end:dev_end]);value=float(F.cross_entropy(logits.transpose(1,2),clean[train_end:dev_end][:,POSITIONS]))
                trace.append(dict(step=step+1,development_recovery_loss=value))
                if value<best:best=value;state={k:v.detach().clone() for k,v in model.state_dict().items()}
        model.load_state_dict(state);model.eval();torch.save(state,output/(condition+'.pt'))
        threshold=0.
        with torch.no_grad():
            logits,detector=model(noisy[train_end:dev_end]);guess=logits.argmax(-1)
            if condition=='gated':
                allowed=[]
                for candidate in [i/20 for i in range(21)]+[1.1]:
                    pred=torch.where(detector.sigmoid()>=candidate,guess,noisy[train_end:dev_end][:,POSITIONS])
                    values=measure(pred,clean[train_end:dev_end][:,POSITIONS],mask[train_end:dev_end])
                    if values['clean_false_edit']<=.01:allowed.append((values['corrupt_recovery'],-candidate))
                threshold=-max(allowed)[1]
            for probability in [.15,.35,.6]:
                target,corrupted,bad=records(data_seed,count,probability)
                target,corrupted,bad=target[dev_end:],corrupted[dev_end:],bad[dev_end:]
                logits,detector=model(corrupted);pred=logits.argmax(-1)
                if condition=='gated':pred=torch.where(detector.sigmoid()>=threshold,pred,corrupted[:,POSITIONS])
                # Explicit post-filter requires repeated fields plus the preserved checksum.
                valid=(pred[:,:5]==pred[:,5:10]).all(1)&(pred[:,:5]==pred[:,10:]).all(1)&(pred[:,:5].sum(1)%16==corrupted[:,-1])
                filtered=torch.where(valid[:,None],pred,corrupted[:,POSITIONS])
                majority=[]
                for row in corrupted.tolist():
                    fixed,_,_=repair(['SEP' if v==16 else None if v==17 else v for v in row]);majority.append([17 if fixed[i] is None else fixed[i] for i in POSITIONS])
                predictions={condition:pred,condition+'_checksum':filtered,'identity':corrupted[:,POSITIONS],'majority':torch.tensor(majority)}
                for name,prediction in predictions.items():
                    values=measure(prediction,target[:,POSITIONS],bad)
                    metrics.update({f'{probability}.{name}.{k}':v for k,v in values.items() if v is not None})
                np.savez_compressed(output/f'{condition}-{probability}.npz',clean=target.numpy(),noisy=corrupted.numpy(),mask=bad.numpy(),**{name:p.numpy() for name,p in predictions.items()})
        details[condition]=dict(threshold=threshold,trace=trace,steps=steps)
    Path(output,'training.json').write_text(json.dumps(details,indent=2)+'\n')
    return dict(scope='Grouped repeated-record synthetic repair, three frozen severity levels and checksum abstention; five initialisation seeds when default runner seeds are used. No general-text repair claim.',metrics=metrics,seed=seed,data_seed=data_seed,split_rows=[train_end,dev_end-train_end,count-dev_end])
