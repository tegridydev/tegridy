"""Generated image fixtures covering bytes, alpha, metadata and failed targets."""
import io
import json
from pathlib import Path
import numpy as np
from PIL import Image,PngImagePlugin
from convert import convert


def run(seed,data_seed,profile,output):
    rng=np.random.default_rng(seed+data_seed);rows=[];metrics={}
    for family in ['flat','noise','gradient','alpha']:
        size=64 if profile=='smoke' else 512
        pixels=rng.integers(0,256,(size,size,4),dtype=np.uint8)
        if family=='flat':pixels[:]=[30,60,90,255]
        elif family=='gradient':pixels[:,:,:3]=np.arange(size,dtype=np.uint16)[None,:,None]%256;pixels[:,:,3]=255
        elif family=='noise':pixels[:,:,3]=255
        image=Image.fromarray(pixels);buffer=io.BytesIO();meta=PngImagePlugin.PngInfo();meta.add_text('private-note','fixture metadata')
        image.save(buffer,format='PNG',pnginfo=meta);raw=buffer.getvalue();Path(output,f'{family}-source.png').write_bytes(raw)
        for format in ['PNG','JPEG','WEBP']:
            for limit in [1,100000]:
                encoded,receipt=convert(raw,format,bounds=(256,256),byte_limit=limit)
                if receipt['bytes']!=len(encoded) or receipt['target_met']!=(len(encoded)<=limit):raise ValueError('incorrect target receipt')
                with Image.open(io.BytesIO(encoded)) as decoded:
                    if 'private-note' in decoded.info:raise ValueError('metadata leaked')
                filename=f'{family}-{format}-{limit}.'+format.lower();Path(output,filename).write_bytes(encoded)
                rows.append(dict(family=family,limit=limit,output=filename,**receipt))
    Path(output,'receipts.json').write_text(json.dumps(rows,indent=2)+'\n')
    for format in ['PNG','JPEG','WEBP']:
        selected=[r for r in rows if r['format']==format]
        metrics[format+'.mean_bytes']=sum(r['bytes'] for r in selected)/len(selected)
        metrics[format+'.targets_met']=sum(r['target_met'] for r in selected)
    return dict(scope='Generated image fixtures; actual encoded bytes and metadata checks, not a photographic perceptual-quality or browser study.',metrics=metrics,seed=seed,data_seed=data_seed)
