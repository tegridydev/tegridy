"""Pinned neural encoder versus lexical/fused retrieval on declared fixtures."""
import json
from pathlib import Path
from model_assets import encoder
from search import rank


PAIRS=[('PDF extraction','Recover selectable text from portable document files.','How can I read words stored inside a PDF?'),
       ('OCR','Recognise printed characters from scanned page images.','My scan contains a picture of text. How do I transcribe it?'),
       ('Dataset splits','Keep related records together across training and evaluation partitions.','How do I prevent similar examples leaking into my test set?'),
       ('Image conversion','Resize pictures and remove metadata while targeting a byte limit.','Make a photo smaller and strip its location information.'),
       ('Versioned evidence','Retain old source passages when a document is corrected.','How can an old citation still be inspected after an edit?'),
       ('Memory history','Retrieve facts valid at a requested time for the correct owner.','What preference did this person have before their correction?'),
       ('Compression','Replace a matrix with low-rank factors and measure held-out functional error.','Does a smaller weight file still produce the same outputs?'),
       ('Temporal attention','Use elapsed time to weight past observations when predicting a changing state.','How should a predictor handle old observations arriving at irregular intervals?'),
       ('Repair','Recover corrupted repeated records while avoiding changes to clean symbols.','Can damaged data be fixed without altering valid positions?'),
       ('Index freshness','Replay durable database updates into a versioned search index after a crash.','How do I stop a search service returning stale document versions?')]


def run(seed,data_seed,profile,output):
    encode,manifest,entry=encoder()
    documents=[dict(id=str(i),text=title+'. '+text) for i,(title,text,_) in enumerate(PAIRS)]
    vectors=encode([d['text'] for d in documents]);index=dict(manifest=manifest,documents=[dict(d,vector=v) for d,v in zip(documents,vectors)])
    queries=[p[2] for p in PAIRS];query_vectors=encode(queries);rows=[];metrics={}
    for i,(query,vector) in enumerate(zip(queries,query_vectors)):
        ranking=rank(query,index,vector,manifest)
        rows.append(dict(query=query,relevant=str(i),rankings=ranking))
    for mode in ['lexical','vector','hybrid']:
        ranks=[next((position for position,(identity,_) in enumerate(row['rankings'][mode],1) if identity==row['relevant']),None) for row in rows]
        metrics[mode+'.mrr']=sum(1/r if r else 0 for r in ranks)/len(ranks)
        metrics[mode+'.recall_at_3']=sum(r is not None and r<=3 for r in ranks)/len(ranks)
    try:rank(queries[0],index,query_vectors[0],dict(manifest,pooling='incompatible'))
    except ValueError:metrics['mismatch_rejected']=1
    else:raise ValueError('incompatible manifest accepted')
    Path(output,'index.json').write_text(json.dumps(index,indent=2)+'\n');Path(output,'rankings.json').write_text(json.dumps(rows,indent=2)+'\n');Path(output,'model.json').write_text(json.dumps(entry,indent=2)+'\n')
    return dict(scope='Ten explicitly authored topic/paraphrase relevance fixtures using a real pinned pretrained encoder; labels are engineering fixtures, not an independently annotated retrieval benchmark. Deterministic seed repeats do not add evidence.',metrics=metrics,seed=seed,data_seed=data_seed)
