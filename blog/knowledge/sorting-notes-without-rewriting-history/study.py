"""Archive inventory with known duplicate and conflicting-name ground truth."""
import json
from pathlib import Path
from inventory import inventory


def run(seed,data_seed,profile,output):
    root=Path(output)/'archive';root.mkdir();count=10 if profile=='smoke' else 500
    for index in range(count):
        folder=root/str(index);folder.mkdir();(folder/'note.md').write_text(f'Original record {index}\n')
        (folder/'copy.md').write_text(f'Original record {index}\n')
    result=inventory(root)
    if len(result['files'])!=2*count or len(result['exact_duplicates'])!=count:raise ValueError('duplicate inventory mismatch')
    Path(output,'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    return dict(scope='Known byte-duplicate archive fixture; originals are never modified or moved. Name collisions do not imply semantic duplicates.',metrics=dict(files=len(result['files']),duplicate_groups=len(result['exact_duplicates']),name_conflicts=len(result['name_conflicts'])),seed=seed,data_seed=data_seed)
