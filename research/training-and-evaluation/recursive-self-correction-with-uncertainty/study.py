"""Actual pinned-model arithmetic answers and one revision, with objective labels."""
import importlib.util
import json
import math
from pathlib import Path
import torch
from model_assets import causal
from evaluate import evaluate


def run(seed,data_seed,profile,output):
    root=Path(__file__).resolve().parents[3];output=Path(output)
    spec=importlib.util.spec_from_file_location('arithmetic_protocol',root/'research/transformers/arithmetic-across-notations/protocol_reference.py');protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
    model,tokenizer,entry=causal();tokenizer.padding_side='left';tokenizer.pad_token=tokenizer.eos_token;torch.manual_seed(seed)
    stop=[tokenizer.eos_token_id]+tokenizer.encode('\n',add_special_tokens=False)
    def generate(prompts,sample=False):
        rows=[]
        for start in range(0,len(prompts),16):
            batch=tokenizer(prompts[start:start+16],padding=True,return_tensors='pt')
            with torch.no_grad():result=model.generate(**batch,max_new_tokens=8,do_sample=sample,pad_token_id=tokenizer.eos_token_id,eos_token_id=stop,return_dict_in_generate=True,output_scores=True)
            tokens=result.sequences[:,batch['input_ids'].shape[1]:]
            for index,row in enumerate(tokens):
                selected=[];logs=[]
                for step,token in enumerate(row.tolist()):
                    selected.append(token);logs.append(float(result.scores[step][index].log_softmax(-1)[token]))
                    if token in stop:break
                rows.append(dict(text=tokenizer.decode(selected,skip_special_tokens=True),tokens=selected,confidence=math.exp(sum(logs)/len(logs)),input_tokens=int(batch['attention_mask'][index].sum())))
        return rows
    groups=protocol.pairs(data_seed);partitions={}
    for split,count in [('development',4 if profile=='smoke' else 64),('final',4 if profile=='smoke' else 128)]:
        chosen=[r for r in groups if r['split']==split][:count]
        prompts=[r['prompts'][0] for r in chosen];initial=generate(prompts)
        revised=generate([p+' '+a['text'].strip()+'\nCheck the calculation and give the corrected answer with digits only:' for p,a in zip(prompts,initial)])
        independent=generate(prompts,sample=True)
        rows=[]
        for index,(task,before,after,control) in enumerate(zip(chosen,initial,revised,independent)):
            rows.append(dict(id=split+'-'+str(index),group=str((task['a'],task['b'])),rounds=1,cost=len(before['tokens'])+len(after['tokens']),action='critique',before=protocol.exact_answer(before['text'],int(task['target'])),after=protocol.exact_answer(after['text'],int(task['target'])),confidence=after['confidence'],prompt=task['prompts'][0],target=task['target'],initial=before,revised=after,independent=control,independent_correct=protocol.exact_answer(control['text'],int(task['target']))))
        partitions[split]=rows
    result=evaluate(partitions['development'],partitions['final'])
    final=partitions['final'];metrics=dict(initial_accuracy=sum(r['before'] for r in final)/len(final),revision_accuracy=sum(r['after'] for r in final)/len(final),independent_accuracy=sum(r['independent_correct'] for r in final)/len(final),repair_count=sum(not r['before'] and r['after'] for r in final),damage_count=sum(r['before'] and not r['after'] for r in final),brier=sum((r['confidence']-r['after'])**2 for r in final)/len(final),generated_revision_tokens=sum(r['cost'] for r in final))
    Path(output,'predictions.json').write_text(json.dumps(partitions,indent=2)+'\n');Path(output,'evaluation.json').write_text(json.dumps(result,indent=2)+'\n');Path(output,'model.json').write_text(json.dumps(entry,indent=2)+'\n')
    return dict(scope='Pinned GPT-Neo digit arithmetic with exact response labels, one prompted revision and independent sampling at the same maximum output length. Actual token counts vary and are retained. Token likelihood is evaluated as a confidence proxy, not assumed calibrated.',metrics=metrics,seed=seed,data_seed=data_seed)
