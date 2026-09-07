"""Headless fake-provider task completion and restart accounting."""
from pathlib import Path
import json
from app import Simulation,fake


def run(seed,data_seed,profile,output):
    path=Path(output)/'simulation.sqlite';simulation=Simulation(path,max_messages=1000,max_depth=2)
    events=[simulation.post('workshop',f'Fixture question {index}') for index in range(2 if profile=='smoke' else 20)]
    calls=0;restarts=0
    try:
        while simulation.step(fake):
            calls+=1
            if calls%13==0:
                simulation.close();simulation=Simulation(path,max_messages=1000,max_depth=2);simulation.recover();restarts+=1
        tasks=[dict(r) for r in simulation.db.execute('SELECT * FROM tasks ORDER BY event,persona')]
        messages=[dict(r) for r in simulation.db.execute('SELECT * FROM messages ORDER BY ordinal')]
        if any(t['status']!='completed' for t in tasks):raise ValueError('fake task failed')
        if len(messages)!=len(events)+len(tasks):raise ValueError('missing or duplicate message commit')
        Path(output,'trace.json').write_text(json.dumps(dict(tasks=tasks,messages=messages),indent=2)+'\n')
        return dict(scope='Headless deterministic fake-provider workflow with repeated process-level storage reopen; no live Ollama or social-simulation validity claim.',metrics=dict(tasks=len(tasks),messages=len(messages),restarts=restarts),seed=seed,data_seed=data_seed)
    finally:simulation.close()
