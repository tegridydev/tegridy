"""Real pinned-model occurrence capture and a discovery-only shared projection."""
import json
from pathlib import Path
import torch
from model_assets import causal
from capture import capture,fit_projection,project,straightness


def run(seed,data_seed,profile,output):
    model,tokenizer,entry=causal();output=Path(output)
    prompts=['The red bird flew over the quiet river.','The blue bird flew over the quiet river.','Two plus three equals five.','Seven plus four equals eleven.','The old document was replaced by a correction.','The original citation still points to its saved source.']
    matrices=[];records=[]
    for index,prompt in enumerate(prompts[:2] if profile=='smoke' else prompts):
        tokens=tokenizer(prompt,return_tensors='pt')['input_ids']
        result=capture(model,tokens,['transformer.h.0'],entry['revision'],entry['revision'],max_values=100000)
        result['manifest']['model_id']=entry['repo'];result['manifest']['prompt']=prompt
        Path(output,f'capture-{index}.json').write_text(json.dumps(result,indent=2)+'\n')
        matrix=torch.tensor([r['value'] for r in result['records']]).reshape(tokens.shape[1],-1)
        matrices.append(matrix);records.append(dict(prompt=prompt,tokens=tokens.tolist(),values=len(result['records'])))
    projection=fit_projection(matrices[0],2)
    projected=[project(matrix,projection) for matrix in matrices]
    torch.save(dict(mean=projection[0],basis=projection[1],projected=projected),output/'projection.pt')
    Path(output,'model.json').write_text(json.dumps(entry,indent=2)+'\n')
    return dict(scope='Real GPT-Neo first-block activations for explicitly listed short prompts; shared PCA fitted only on the first prompt. Occurrence identity is retained; this does not establish semantic selectivity or causal circuits.',metrics=dict(prompts=len(matrices),recorded_values=sum(r['values'] for r in records),projected_dimensions=2),seed=seed,data_seed=data_seed,prompts=records)
