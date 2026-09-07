"""Load only explicitly acquired, hash-checked, pinned local model assets."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def asset(name):
    manifest=ROOT/'tools/studies/assets.json'
    if not manifest.exists():raise ValueError('Acquire the public model first using tools/studies/assets.py; experiments never download implicitly.')
    entry=json.loads(manifest.read_text())['models'][name]
    directory=(ROOT/entry['directory']).resolve()
    if not directory.is_relative_to(ROOT/'tools/_models'):raise ValueError('model path outside local cache')
    for relative,expected in entry['files'].items():
        path=directory/relative
        if path.is_symlink() or not path.resolve().is_relative_to(directory) or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('model asset integrity failure: '+relative)
    return directory,entry


def causal():
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(2)
    path,entry=asset('causal')
    tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,trust_remote_code=False,use_safetensors=True)
    model.eval()
    return model,tokenizer,entry


def encoder():
    import torch
    from transformers import AutoModel,AutoTokenizer
    torch.set_num_threads(2)
    path,entry=asset('encoder')
    tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True,trust_remote_code=False)
    model=AutoModel.from_pretrained(path,local_files_only=True,trust_remote_code=False,use_safetensors=True)
    model.eval()
    manifest=dict(model_revision=entry['repo']+'@'+entry['revision'],tokenizer_revision=entry['revision'],pooling='attention-mask mean, L2 normalized',dimension=model.config.hidden_size,max_length=256,truncation=True)
    def encode(texts):
        vectors=[]
        with torch.no_grad():
            for start in range(0,len(texts),16):
                batch=tokenizer(texts[start:start+16],padding=True,truncation=True,max_length=256,return_tensors='pt')
                hidden=model(**batch).last_hidden_state;mask=batch['attention_mask'].unsqueeze(-1)
                mean=(hidden*mask).sum(1)/mask.sum(1).clamp_min(1)
                vectors.extend(torch.nn.functional.normalize(mean,p=2,dim=1).tolist())
        return vectors
    return encode,manifest,entry
