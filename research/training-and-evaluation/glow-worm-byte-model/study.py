"""Bounded byte-language-model training on pinned document-grouped WikiText-2."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from experiment import ByteModel,windows
from byte_baseline import fit


def run(seed,data_seed,profile,output):
    torch.set_num_threads(2);output=Path(output);root=Path(__file__).resolve().parents[3]
    metadata=json.loads((root/'tools/studies/corpus.json').read_text())
    for name,digest in metadata['files'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('corpus integrity failure')
    docs=json.loads((root/metadata['documents_path']).read_text())
    split={name:[d for d in docs if d['split']==name] for name in ['train','validation','test']}
    hashes=[{d['sha256'] for d in split[name]} for name in split]
    if any(hashes[i]&hashes[j] for i in range(3) for j in range(i)):raise ValueError('duplicate documents cross splits')
    train_docs=[];used=0
    for doc in split['train']:
        train_docs.append(doc);used+=len(doc['text'].encode())
        if used>=10000000:break
    if profile=='smoke':train_docs=train_docs[:2];split['validation']=split['validation'][:1];split['test']=split['test'][:1]
    train=windows([d['text'].encode() for d in train_docs],256)
    dev=windows([d['text'].encode() for d in split['validation']],256)
    final=windows([d['text'].encode() for d in split['test']],256)
    torch.manual_seed(seed);model=ByteModel();optimizer=torch.optim.Adam(model.parameters(),lr=.001);generator=torch.Generator().manual_seed(seed+data_seed)
    steps=2 if profile=='smoke' else 512;trace=[];best=float('inf');state=None
    def evaluation(data):
        model.eval();losses=[]
        with torch.no_grad():
            for x,y in zip(data[0].split(16),data[1].split(16)):
                loss=F.cross_entropy(model(x).transpose(1,2),y,reduction='none')
                losses.extend(loss[y<256].tolist())
        values=np.asarray(losses);return float(values.mean()/math.log(2)),values
    for step in range(steps):
        model.train();idx=torch.randint(len(train[0]),(16,),generator=generator);optimizer.zero_grad()
        loss=F.cross_entropy(model(train[0][idx]).transpose(1,2),train[1][idx]);loss.backward();optimizer.step()
        if (step+1)%128==0 or step==steps-1:
            score,_=evaluation(dev);trace.append(dict(step=step+1,development_bits_per_byte=score))
            if score<best:best=score;state={k:v.detach().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(state);torch.save(state,output/'checkpoint.pt');score,losses=evaluation(final)
    probabilities=np.asarray(fit([d['text'].encode() for d in train_docs]));targets=final[1].numpy();targets=targets[targets<256]
    unigram=float(-np.log2(probabilities[targets]).mean())
    np.savez_compressed(output/'evaluation.npz',target_bytes=targets,negative_log_likelihood=losses,unigram_probabilities=probabilities)
    Path(output,'corpus.json').write_text(json.dumps(dict(metadata=metadata,training_documents=[{k:v for k,v in d.items() if k!='text'} for d in train_docs],trace=trace),indent=2)+'\n')
    return dict(scope='Pinned WikiText-2 article-grouped byte study with up to roughly ten million available training bytes; fixed 512-step CPU budget, 256-byte windows, development checkpoint selection. Unigram sees the full selected corpus; Transformer training exposure is separately recorded. No chatbot-quality claim.',metrics=dict(bits_per_byte=score,unigram_bits_per_byte=unigram,evaluated_bytes=len(losses),training_available_bytes=sum(len(d['text'].encode()) for d in train_docs),training_token_exposures=steps*16*256,checkpoint_bytes=(output/'checkpoint.pt').stat().st_size),seed=seed,data_seed=data_seed)
