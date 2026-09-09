'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const events = new Map();
const sent = [];
const window = {
  location: { hostname: 'tegridydev.com', origin: 'https://tegridydev.com',
    href: 'https://tegridydev.com/blog/?utm_source=bluesky&utm_medium=social&utm_campaign=launch&email=private@example.com#section' },
  umami: { track: (name, data) => sent.push({ name, data }) },
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../site/static/assets/analytics.js'), 'utf8'), {
  window, URL, document: { addEventListener: (name, callback, options) => {
    assert.equal(options.passive, true); events.set(name, callback);
  } },
});
function click(href, attributes = {}, type = 'click', button = 0) {
  const target = { hasAttribute: key => key in attributes, getAttribute: () => href };
  events.get(type)({ type, button, target: { closest: () => target }, preventDefault: () => assert.fail('Navigation must not be blocked') });
}
click('https://github.com/tegridydev?secret=private');
assert.equal(sent.pop().data.domain, 'github.com');
click('/research/paper.pdf');
click('https://example.com/resource.zip');
assert.equal(sent.length,0);
click('/blog/agents/minecraft-time-with-astra/wildblock.html');assert.equal(sent.pop().name,'project-demo');
click('mailto:private@example.com');assert.equal(JSON.stringify(sent.pop()),JSON.stringify({name:'contact-click',data:{method:'email'}}));
click(null, {'data-copy-contact':''});assert.equal(sent.pop().data.method,'copy');
for (const href of ['/blog/', '#heading', 'javascript:alert(1)', 'data:text/plain,hello']) click(href);
click('https://github.com', {'data-umami-event':'manual'});
click('https://github.com', {}, 'auxclick', 2);
assert.equal(sent.length,0);
click('https://github.com', {}, 'auxclick', 1);assert.equal(sent.length,1);sent.length=0;
events.get('submit')({target:{matches:()=>true,hidden:false}});assert.equal(sent.length,0);
events.get('submit')({target:{matches:()=>true,hidden:true}});assert.equal(sent.pop().data.method,'reveal');
const payload = {url:'https://tegridydev.com/blog/',referrer:'https://example.com/path?private=1#part',id:'private-id'};
const clean = window.tegridyAnalyticsFilter('event',payload);
assert.equal(clean.url,'https://tegridydev.com/blog/?utm_source=bluesky&utm_medium=social&utm_campaign=launch');
assert.equal(clean.referrer,'https://example.com/path');assert.equal(clean.id,undefined);assert.equal(payload.id,'private-id');
assert.equal(window.tegridyAnalyticsFilter('identify',payload),false);
window.location.href='https://tegridydev.com/blog/?utm_source=private%40example.com&utm_campaign='+ 'x'.repeat(81);
assert.equal(window.tegridyAnalyticsFilter('performance',payload).url,'https://tegridydev.com/blog/');
window.location.hostname='localhost';click('https://github.com');assert.equal(sent.length,0);
assert.equal(window.tegridyAnalyticsFilter('event',payload),false);
window.location.hostname='tegridydev.com';window.umami=undefined;click('https://github.com');
window.umami={track:()=>{throw new Error('Unavailable')}};click('https://github.com');
console.log('Analytics checks passed: event classification, navigation, campaign filtering, contact scope and unavailable tracker.');
