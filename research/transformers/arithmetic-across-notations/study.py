"""Predeclared two-notation competence gate on an explicitly pinned checkpoint."""
import json
from pathlib import Path
import torch
from model_assets import causal
from protocol_reference import pairs,exact_answer


def run(seed,data_seed,profile,output):
    model,tokenizer,entry=causal();rows=[]
    tokenizer.padding_side='left';tokenizer.pad_token=tokenizer.eos_token
    selected=[row for row in pairs(data_seed) if row['split']=='development']
    if profile=='smoke':selected=selected[:2]
    tasks=[dict(a=row['a'],b=row['b'],prompt=prompt,target=row['target'],notation='digits' if index%2==0 else 'words') for row in selected for index,prompt in enumerate(row['prompts'])]
    for start in range(0,len(tasks),16):
        batch=tasks[start:start+16];encoded=tokenizer([r['prompt'] for r in batch],return_tensors='pt',padding=True)
        with torch.no_grad():generated=model.generate(**encoded,max_new_tokens=8,do_sample=False,pad_token_id=tokenizer.eos_token_id,eos_token_id=[tokenizer.eos_token_id]+tokenizer.encode('\n',add_special_tokens=False))
        texts=tokenizer.batch_decode(generated[:,encoded['input_ids'].shape[1]:],skip_special_tokens=True)
        rows.extend(dict(row,response=text,correct=exact_answer(text,int(row['target']))) for row,text in zip(batch,texts))
    metrics={notation+'.development_exact_match':sum(r['correct'] for r in rows if r['notation']==notation)/sum(r['notation']==notation for r in rows) for notation in ['digits','words']}
    passed=all(value>=.8 for value in metrics.values());metrics['feasibility_passed']=int(passed)
    Path(output,'development-predictions.json').write_text(json.dumps(rows,indent=2)+'\n');Path(output,'model.json').write_text(json.dumps(entry,indent=2)+'\n')
    return dict(scope='Development-only 80% per-notation gate; greedy full-response exact scoring on grouped operand pairs. Discovery and final sets remain untouched. This gate alone is not a circuit-transfer experiment.',metrics=metrics,seed=seed,data_seed=data_seed,
                next_stage='Gate passed: a separately reviewed intervention run is required before circuit claims.' if passed else 'Checkpoint failed the competence gate; no component discovery or final transfer evaluation is justified.')
