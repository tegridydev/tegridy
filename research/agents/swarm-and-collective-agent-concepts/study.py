"""Enumerated grammar transfer and topology comparison at equal token budgets."""
from collections import Counter
import itertools
import json
import math
import random
import time
from pathlib import Path


def generate(seed, width, depth, coupling, topology, tokens):
    rng = random.Random(seed)
    histories = [None]*4
    sequences = []
    for turn in range(tokens//depth):
        agent = turn%4
        neighbours = [] if topology == 'none' else [(agent-1)%4] if topology=='ring' else [i for i in range(4) if i!=agent]
        sequence = []
        for position in range(depth):
            weights = [1 + coupling*sum(histories[i] is not None and histories[i][position]==token for i in neighbours)/max(1,len(neighbours)) for token in range(width)]
            sequence.append(rng.choices(range(width), weights=weights)[0])
        histories[agent] = tuple(sequence)
        sequences.append(tuple(sequence))
    return sequences


def run(seed, data_seed, profile, output):
    rows, metrics = [], {}
    budget = 200 if profile=='smoke' else 2000
    for name,width,depth in [('development',2,4),('changed',3,4),('deeper',2,5)]:
        legal = list(itertools.product(range(width),repeat=depth))
        for condition, coupling, topology in [('markov',0,'none'),('independent',0,'ring'),('ring',2,'ring'),('complete',2,'complete')]:
            start=time.perf_counter()
            sequences=generate(seed,width,depth,coupling,topology,budget)
            elapsed=time.perf_counter()-start
            counts=Counter(sequences)
            # Exact uniform grammar evaluation with fixed Dirichlet smoothing.
            logs=[]
            transition=Counter((pos,seq[pos-1] if pos else -1,token) for seq in sequences for pos,token in enumerate(seq))
            for seq in legal:
                for pos,token in enumerate(seq):
                    previous=seq[pos-1] if pos else -1
                    total=sum(transition[pos,previous,t] for t in range(width))
                    logs.append(math.log((transition[pos,previous,token]+1)/(total+width)))
            values=dict(coverage=len(counts)/len(legal),repetition=1-len(counts)/len(sequences),
                        uniform_grammar_logprob=sum(logs)/len(logs),elapsed_seconds=elapsed)
            metrics.update({name+'.'+condition+'.'+k:v for k,v in values.items()})
            rows.append(dict(grammar=name,width=width,depth=depth,condition=condition,coupling=coupling,
                             topology=topology,tokens=sum(map(len,sequences)),metrics=values,sequences=sequences))
    Path(output,'sequences.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='SW-01 finite layered grammars; exact uniform legal-set evaluation; fixed coupling, four agents, equal token budgets; no downstream training claim.',metrics=metrics,seed=seed,data_seed=data_seed)
