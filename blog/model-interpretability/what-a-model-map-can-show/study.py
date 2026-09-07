"""Export a real occurrence capture accepted by the existing viewer format."""
import importlib.util
import json
from pathlib import Path
from model_assets import causal


def run(seed,data_seed,profile,output):
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('occurrence_capture',root/'research/transformers/neuron-mapping-and-token-trajectories/capture.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    model,tokenizer,entry=causal();prompt='The original document and its corrected version share a citation.'
    ids=tokenizer(prompt,return_tensors='pt')['input_ids']
    result=module.capture(model,ids,['transformer.h.0'],entry['revision'],entry['revision'])
    result['manifest'].update(model_id=entry['repo'],prompt=prompt)
    Path(output,'viewer-capture.json').write_text(json.dumps(result,indent=2)+'\n');Path(output,'model.json').write_text(json.dumps(entry,indent=2)+'\n')
    return dict(scope='Real pinned-model activation file for manual loading in the existing viewer. No browser was opened; no circuit interpretation follows from visualising this capture.',metrics=dict(recorded_values=len(result['records']),tokens=ids.numel()),seed=seed,data_seed=data_seed)
