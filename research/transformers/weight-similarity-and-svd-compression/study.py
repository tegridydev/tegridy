"""Real-model layer SVD with calibration and held-out functional measurements."""
import json
from pathlib import Path
import time
import numpy as np
import torch
from model_assets import causal
from compress import factorize,report


def run(seed,data_seed,profile,output):
    model,tokenizer,entry=causal();output=Path(output)
    module=model.transformer.h[0].mlp.c_fc;captured=[]
    def receive(layer,inputs,result):captured.append(inputs[0].detach().cpu().reshape(-1,inputs[0].shape[-1]).numpy())
    handle=module.register_forward_hook(receive)
    prompts=['A document keeps its original citation when a revision is published.','Training examples must remain separate from held out evaluation examples.','A changing observation arrives after an irregular interval.','The red bird crossed the river before sunset.']
    try:
        with torch.no_grad():
            for text in prompts:model(**tokenizer(text,return_tensors='pt'))
    finally:handle.remove()
    weight=module.weight.detach().cpu().numpy();calibration=np.concatenate(captured[:2]);evaluation=np.concatenate(captured[2:]);rows=[];metrics={}
    np.savez_compressed(output/'inputs.npz',weight=weight,calibration=calibration,evaluation=evaluation)
    for rank in ([8] if profile=='smoke' else [8,32,64,128]):
        start=time.perf_counter();left,right=factorize(weight,rank);factor_seconds=time.perf_counter()-start
        record=report(weight,calibration,evaluation,rank)
        np.savez(output/f'factors-{rank}.npz',left=left,right=right)
        record['factor_seconds']=factor_seconds;rows.append(record)
        metrics[f'rank{rank}.held_out_mse']=record['held_out']['mse'];metrics[f'rank{rank}.factor_file_bytes']=record['factor_file_bytes'];metrics[f'rank{rank}.dense_file_bytes']=record['dense_file_bytes']
    Path(output,'comparisons.json').write_text(json.dumps(rows,indent=2)+'\n');Path(output,'model.json').write_text(json.dumps(entry,indent=2)+'\n')
    return dict(scope='First GPT-Neo MLP projection, four declared short texts split into calibration/evaluation; measured factor bytes and layer-output error. No end-to-end language-model loss or speed claim.',metrics=metrics,seed=seed,data_seed=data_seed)
