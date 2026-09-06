const assert=require('node:assert/strict');
const {validateRun,compatible,colour}=require('./viewer.js');
const fixture=require('./fixture.json');
assert.equal(validateRun(fixture),fixture);
assert.notEqual(colour(0,1),colour(null,1));
assert.equal(compatible(fixture,{manifest:{...fixture.manifest,model_revision:'other'}}),false);
for(const value of [NaN,Infinity,'0']) assert.throws(()=>validateRun({...fixture,records:[{...fixture.records[0],value}]}));
assert.throws(()=>validateRun({...fixture,records:[fixture.records[0],fixture.records[0]]}));
console.log('Viewer contract checks passed');
