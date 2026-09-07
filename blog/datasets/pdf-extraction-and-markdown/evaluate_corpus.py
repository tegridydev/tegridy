"""Evaluate an explicitly labelled PDF corpus; does not invent reference text."""
import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
from extract import extract


def evaluate(manifest_path,output,ocr=None,required_families=18):
    manifest_path=Path(manifest_path);output=Path(output);data=json.loads(manifest_path.read_text())
    documents=data['documents']
    if len({d['family'] for d in documents})<required_families:raise ValueError('labelled corpus does not cover the required layout families')
    if output.exists():raise FileExistsError(output)
    rows=[]
    for index,document in enumerate(documents):
        source=(manifest_path.parent/document['path']).resolve()
        if not source.is_relative_to(manifest_path.parent.resolve()):raise ValueError('PDF must be within corpus directory')
        if hashlib.sha256(source.read_bytes()).hexdigest()!=document['sha256']:raise ValueError('source hash mismatch')
        result=extract(source,output/str(index),ocr=ocr,review=True)
        if len(document['pages'])!=result['page_count']:raise ValueError('reference page count mismatch')
        for reference,page in zip(document['pages'],result['pages']):
            expected=reference['text'];actual='\n'.join(b['text'] for b in page['blocks'])
            a,b=Counter(actual.split()),Counter(expected.split());overlap=sum((a&b).values())
            rows.append(dict(document=document['path'],family=document['family'],page=page['page'],status=page['status'],expected=expected,actual=actual,word_precision=overlap/sum(a.values()) if a else int(not b),word_recall=overlap/sum(b.values()) if b else int(not a),character_sequence_ratio=SequenceMatcher(None,expected,actual,autojunk=False).ratio(),reference_ocr_required=reference['ocr_required']))
    result=dict(scope='Labelled page-text comparison; sequence similarity is not character error rate and does not certify table/equation semantics.',pages=rows,families=len({d['family'] for d in documents}))
    (output/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);p.add_argument('output',type=Path);p.add_argument('--ocr',action='store_true');a=p.parse_args()
    from ocr import tesseract
    result=evaluate(a.manifest,a.output,tesseract() if a.ocr else None);print(json.dumps(dict(pages=len(result['pages']),families=result['families'])))
