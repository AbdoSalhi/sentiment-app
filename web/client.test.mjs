import {test} from 'node:test';
import assert from 'node:assert/strict';
import {predire} from './client.mjs';
for (const label of ['POSITIVE','NEGATIVE','INDETERMINE']) {
  test(label, async()=>assert.equal((await predire('http://api/','key','avis',async(url,opts)=>{
    assert.equal(url,'http://api/v1/predict'); assert.equal(opts.headers['X-API-Key'],'key');
    assert.equal(JSON.parse(opts.body).text,'avis'); return {ok:true,json:async()=>({label,score:0.7})};
  })).label,label));
}
for(const status of [401,403,422,500,503]) test(`erreur ${status}`,async()=>{
  await assert.rejects(predire('http://api','key','avis',async()=>({ok:false,json:async()=>({erreur:{message:'Refus'}})})),/Refus/);
});
for(const payload of [{label:'autre',score:0.7},{label:'POSITIVE',score:2},{label:'POSITIVE',score:'0.7'}])
  test(`contrat ${JSON.stringify(payload)}`, async()=>assert.rejects(predire('http://api','key','avis',async()=>({ok:true,json:async()=>payload})),/invalide/));
test('panne réseau',async()=>assert.rejects(predire('http://api','key','avis',async()=>{throw new TypeError('offline');}),/offline/));
