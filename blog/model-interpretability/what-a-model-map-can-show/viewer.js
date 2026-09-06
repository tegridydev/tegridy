'use strict';
function validateRun(run) {
  if (!run || run.schema !== 1 || !run.manifest || !Array.isArray(run.records)) throw Error('Expected schema 1 activation export');
  for (const key of ['model_revision', 'tokenizer_revision', 'measurement', 'mode']) {
    if (typeof run.manifest[key] !== 'string' || !run.manifest[key]) throw Error('Missing manifest field: ' + key);
  }
  if (!Array.isArray(run.manifest.tokens) || !run.manifest.tokens.length) throw Error('Token sequences missing');
  if (run.records.length > 100000) throw Error('Viewer limit: 100,000 measurements per file');
  const identities = new Set();
  for (const row of run.records) {
    for (const key of ['sample','position','token_id','feature']) if (!Number.isInteger(row[key]) || row[key] < 0) throw Error('Invalid occurrence coordinate');
    if (typeof row.component !== 'string' || !row.component || typeof row.prompt_hash !== 'string') throw Error('Missing component or prompt identity');
    if (row.value !== null && (typeof row.value !== 'number' || !Number.isFinite(row.value))) throw Error('Values must be finite numbers or explicit null');
    if (run.manifest.tokens[row.sample]?.[row.position] !== row.token_id) throw Error('Token occurrence disagrees with manifest');
    const id = JSON.stringify([row.sample,row.position,row.component,row.feature]);
    if (identities.has(id)) throw Error('Duplicate measurement identity');
    identities.add(id);
  }
  return run;
}
function compatible(a,b) {
  return ['model_revision','tokenizer_revision','measurement','mode'].every(key => a.manifest[key] === b.manifest[key]);
}
function colour(value,limit) {
  if (value === null) return '#ddd';
  const intensity = limit ? Math.min(1, Math.abs(value)/limit) : 0;
  return value < 0 ? `rgba(40,100,230,${intensity})` : `rgba(225,65,50,${intensity})`;
}
if (typeof module !== 'undefined') module.exports = {validateRun,compatible,colour};
if (typeof document !== 'undefined') {
  const input=document.querySelector('#files'), output=document.querySelector('#output'), status=document.querySelector('#status');
  input.addEventListener('change',async () => {
    output.replaceChildren();status.textContent='Reading local files…';
    try {
      const files=Array.from(input.files);
      if (files.length>4 || files.some(f=>f.size>20000000)) throw Error('Choose up to four files, at most 20 MB each');
      const runs=await Promise.all(files.map(async f=>validateRun(JSON.parse(await f.text()))));
      if (runs.some(run=>!compatible(runs[0],run))) throw Error('Incompatible model, tokenizer, measurement or mode; compare separately');
      let limit=0;for (const run of runs) for (const row of run.records) if (row.value!==null) limit=Math.max(limit,Math.abs(row.value));
      status.textContent=`Shared signed colour range: ${-limit} to ${limit}. Null means missing; zero is measured zero. Rows are token occurrences, not semantic alignments.`;
      runs.forEach((run,index)=>{
        const section=document.createElement('section'),title=document.createElement('h2'),manifest=document.createElement('pre');
        title.textContent=files[index].name;manifest.textContent=JSON.stringify(run.manifest,null,2);section.append(title,manifest);
        const table=document.createElement('table'),header=document.createElement('tr');
        for (const name of ['Sample','Position','Token ID','Component','Feature','Raw value']) {const cell=document.createElement('th');cell.textContent=name;header.append(cell);}table.append(header);
        for (const row of run.records.slice(0,2000)) {
          const tr=document.createElement('tr');
          for (const key of ['sample','position','token_id','component','feature','value']) {const td=document.createElement('td');td.textContent=row[key]===null?'missing':String(row[key]);if(key==='value') td.style.backgroundColor=colour(row.value,limit);tr.append(td);}table.append(tr);
        }
        section.append(table);if(run.records.length>2000){const note=document.createElement('p');note.textContent='Showing the first 2,000 records; colour limits use every loaded record.';section.append(note);}output.append(section);
      });
    } catch (error) {status.textContent=error.message;}
  });
}
