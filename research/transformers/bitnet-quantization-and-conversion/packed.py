"""Portable two-bit matrix storage and scalar CPU execution; no speed claim."""
import json
import math
import struct
from pathlib import Path
from ternary_reference import pack,unpack

MAGIC=b'TEGTERN1'


def save(path,symbols,shape,scale):
    if len(shape)!=2 or any(type(v) is not int or v<1 for v in shape) or len(symbols)!=math.prod(shape):raise ValueError('positive matrix shape must match symbols')
    if type(scale) not in (float,int) or not math.isfinite(scale) or scale<0:raise ValueError('finite nonnegative scale required')
    header=json.dumps(dict(shape=list(shape),scale=scale),sort_keys=True,allow_nan=False).encode()
    payload=pack(symbols)
    with Path(path).open('xb') as stream:stream.write(MAGIC+struct.pack('<I',len(header))+header+payload)


def load(path):
    with Path(path).open('rb') as stream:
        if stream.read(8)!=MAGIC:raise ValueError('unknown packed format')
        encoded=stream.read(4)
        if len(encoded)!=4:raise ValueError('truncated header')
        length=struct.unpack('<I',encoded)[0]
        if length>4096:raise ValueError('header too large')
        header=json.loads(stream.read(length))
        shape=header['shape'];scale=header['scale']
        if len(shape)!=2 or any(type(v) is not int or v<1 for v in shape):raise ValueError('invalid shape')
        if type(scale) not in (float,int) or not math.isfinite(scale) or scale<0:raise ValueError('invalid scale')
        payload=stream.read()
    unpack(payload,math.prod(shape))
    return header,payload


def matvec(header,payload,vector):
    rows,columns=header['shape']
    if len(vector)!=columns or any(type(x) not in (int,float) or not math.isfinite(x) for x in vector):raise ValueError('finite input of matching width required')
    if len(payload)!=(rows*columns+3)//4:raise ValueError('payload length mismatch')
    result=[]
    for row in range(rows):
        terms=[]
        for column in range(columns):
            index=row*columns+column;code=(payload[index//4]>>(2*(index%4)))&3
            if code==3:raise ValueError('reserved symbol')
            terms.append(vector[column]*(0 if code==0 else -1 if code==1 else 1))
        result.append(math.fsum(terms)*header['scale'])
    return result
