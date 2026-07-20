import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../chrome-extension/content.js', import.meta.url), 'utf8');
const subtitleUrl = 'https://vod-sub-uk-live.akamaized.net/iplayer/subtitles/ng/galileo/p0/nz/8v/p0nz8v4q-19a859a3-80c5-4501-9ac8-e2e6ebb7e346.xml?__gda__=example';
let captured;
const context = vm.createContext({
  URL,
  location: {href: 'https://www.bbc.co.uk/'},
  document: {scripts: []},
  performance: {
    now: () => 20,
    getEntriesByType: () => [{name: subtitleUrl, startTime: 10}],
  },
  chrome: {runtime: {
    sendMessage: message => { captured = message; },
    onMessage: {addListener() {}},
  }},
  PerformanceObserver: class {
    observe() {}
  },
});

vm.runInContext(source, context);
if (captured?.details?.pid !== 'p0nz8v4q') {
  throw new Error(`Expected PID from subtitle filename, got ${captured?.details?.pid}`);
}
if (captured?.details?.subtitleUrl !== subtitleUrl) {
  throw new Error('Expected the current subtitle request URL.');
}
console.log('Chrome extension smoke test passed: subtitle URL resolves PID p0nz8v4q.');
