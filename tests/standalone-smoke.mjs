import fs from 'node:fs';
import vm from 'node:vm';
import { createRequire } from 'node:module';

const moduleRoot = process.env.TEST_NODE_MODULES;
if (!moduleRoot) throw new Error('Set TEST_NODE_MODULES to a temporary npm prefix.');
const require = createRequire(`${moduleRoot}/package.json`);
const { DOMParser, parseHTML } = require('linkedom');

const appPath = new URL('../standalone/ttml-guide.html', import.meta.url);
const sourcePath = process.argv[2];
if (!sourcePath) throw new Error('Pass a TTML fixture path.');

const html = fs.readFileSync(appPath, 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];
const { document, window } = parseHTML(html);
const context = vm.createContext({
  ...window,
  document,
  DOMParser,
  TextDecoder,
  Uint8Array,
  Blob,
  URL,
  console,
  alert() {},
  location: { reload() {} },
  setTimeout,
});
vm.runInContext(script + ';globalThis.__validate = validate;', context);
const bytes = new Uint8Array(fs.readFileSync(sourcePath));
const text = new TextDecoder().decode(bytes);
const findings = context.__validate(text, bytes, 'vertical');
const codes = new Set(findings.map(item => item.code));
for (const expected of ['imsc_parameter_activeArea', 'ttml_metadata_copyright',
                        'ttml_element_style', 'bbc_text_span_constraint',
                        'ttml_element_br', 'bbc_timing_gaps']) {
  if (!codes.has(expected)) throw new Error(`Expected ${expected}; got ${[...codes]}`);
}
if (!findings.some(item => item.status === 3)) throw new Error('Expected blocking errors.');
console.log(`Standalone smoke test passed: ${findings.length} findings across ${codes.size} codes.`);
