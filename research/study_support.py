"""Small CPU training/evaluation helpers shared by the article studies."""
import json
from pathlib import Path
import torch
from torch.nn import functional as F


def predict(model, x, batch=128):
    model.eval()
    with torch.no_grad():
        return torch.cat([model(part) for part in x.split(batch)])


def fit(model, train, dev, seed, steps, output, name, binary=False):
    torch.set_num_threads(2)
    generator=torch.Generator().manual_seed(seed+100000)
    optimizer=torch.optim.Adam(model.parameters(),lr=.001)
    loss_function=F.binary_cross_entropy_with_logits if binary else F.cross_entropy
    best=float('inf'); best_step=0; trace=[]; best_state=None
    for step in range(steps):
        model.train()
        idx=torch.randint(len(train[0]),(32,),generator=generator)
        optimizer.zero_grad()
        loss=loss_function(model(train[0][idx]),train[1][idx])
        if not torch.isfinite(loss):raise ValueError('nonfinite training loss')
        loss.backward();optimizer.step()
        if (step+1)%50==0 or step==steps-1:
            validation=float(loss_function(predict(model,dev[0]),dev[1]))
            trace.append(dict(step=step+1,training_loss=float(loss.detach()),development_loss=validation))
            if validation<best:
                best=validation;best_step=step+1
                best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(best_state)
    destination=Path(output)/(name+'.pt')
    torch.save(best_state,destination)
    before=predict(model,dev[0][:4])
    model.load_state_dict(torch.load(destination,weights_only=True))
    if not torch.equal(before,predict(model,dev[0][:4])):raise ValueError('checkpoint round-trip changed predictions')
    Path(output,name+'-training.json').write_text(json.dumps(dict(seed=seed,steps=steps,batch_size=32,selected_step=best_step,trace=trace),indent=2)+'\n')
    return best_step


def classification(logits, labels, binary=False):
    if binary:
        probabilities=logits.sigmoid()
        return dict(accuracy=float(((probabilities>=.5)==labels).float().mean()),
                    brier=float((probabilities-labels).square().mean()),
                    loss=float(F.binary_cross_entropy_with_logits(logits,labels)))
    return dict(accuracy=float((logits.argmax(-1)==labels).float().mean()),loss=float(F.cross_entropy(logits,labels)))
