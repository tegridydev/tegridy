"""Batch image conversion with per-file receipts and no source overwrites."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from convert import convert


def batch(inputs, destination, **options):
    destination=Path(destination)
    if destination.exists():raise FileExistsError(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.image-batch-',dir=destination.parent))
    receipts=[]
    try:
        for index,source in enumerate(inputs):
            source=Path(source)
            name=f'{index:06d}.'+options.get('format','PNG').lower().replace('jpeg','jpg')
            try:
                raw=source.read_bytes()
                encoded,receipt=convert(raw,**options)
                (stage/name).write_bytes(encoded)
                receipts.append(dict(input=str(source),output=name,status='converted',**receipt))
            except (OSError,ValueError) as error:
                receipts.append(dict(input=str(source),status='failed',error=str(error)))
        result=dict(schema=1,files=receipts,converted=sum(r['status']=='converted' for r in receipts),failed=sum(r['status']=='failed' for r in receipts))
        (stage/'receipts.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        stage.rename(destination)
        return result
    finally:
        if stage.exists():shutil.rmtree(stage)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('inputs',type=Path,nargs='+')
    p.add_argument('--format',choices=['PNG','JPEG','WEBP'],default='WEBP');p.add_argument('--bounds',type=int,nargs=2);p.add_argument('--byte-limit',type=int);p.add_argument('--first-frame',action='store_true')
    a=p.parse_args();result=batch(a.inputs,a.output,format=a.format,bounds=a.bounds,byte_limit=a.byte_limit,first_frame=a.first_frame)
    print(json.dumps(result,indent=2));raise SystemExit(bool(result['failed']))
