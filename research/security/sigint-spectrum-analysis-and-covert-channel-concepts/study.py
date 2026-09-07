"""Longer seeded synthetic detector comparison with raw probabilities."""
import json
from pathlib import Path
import torch
from signal_experiment import run as experiment


def run(seed,data_seed,profile,output):
    torch.set_num_threads(2)
    result=experiment(seed,2 if profile=='smoke' else 1000,output=output);metrics={}
    for condition,values in result['conditions'].items():
        for split in ['final','shifted']:
            for metric in ['auroc','detection','false_alarm','brier']:metrics[condition+'.'+split+'.'+metric]=values[split][metric]
    Path(output,'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    return dict(scope='Seeded synthetic session-held-out detector comparison with frozen development threshold and offset shift. Raw probabilities retained; no real RF performance claim. Deliberately label-correlated-SNR audit remains separate.',metrics=metrics,seed=seed,data_seed=data_seed)
