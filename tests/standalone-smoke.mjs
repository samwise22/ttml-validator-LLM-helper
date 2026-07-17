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
vm.runInContext(script + ';globalThis.__validate = validate; globalThis.__group = groupFindings; globalThis.__render = render;', context);
const bytes = new Uint8Array(fs.readFileSync(sourcePath));
const text = new TextDecoder().decode(bytes);
const findings = context.__validate(text, bytes, 'vertical');
const rendered = context.__render({ name: sourcePath.split('/').pop() }, 'vertical', findings);
if (!rendered.includes('<details open><summary>Example source context</summary>')) {
  throw new Error('Source context should be expanded by default.');
}
if (rendered.includes('<details open><summary>Every affected location')) {
  throw new Error('Occurrence locations should be collapsed by default.');
}
if (!rendered.includes('target="_blank" rel="noopener noreferrer"')) {
  throw new Error('BBC guidance links should open safely in a new tab.');
}
const codes = new Set(findings.map(item => item.code));
for (const expected of ['imsc_parameter_activeArea', 'ttml_metadata_copyright',
                        'bbc_timing_gaps']) {
  if (!codes.has(expected)) throw new Error(`Expected ${expected}; got ${[...codes]}`);
}
if (sourcePath.includes('Jupiter')) {
  for (const expected of ['ttml_element_style', 'bbc_text_span_constraint', 'ttml_element_br']) {
    if (!codes.has(expected)) throw new Error(`Expected ${expected}; got ${[...codes]}`);
  }
}
if (sourcePath.includes('zztest_demo')) {
  for (const expected of ['xml_xsd', 'bbc_text_backgroundColor_constraint']) {
    if (!codes.has(expected)) throw new Error(`Expected ${expected}; got ${[...codes]}`);
  }
  const groups = context.__group(findings);
  const gaps = groups.find(item => item.code === 'bbc_timing_gaps');
  const backgrounds = groups.find(item => item.code === 'bbc_text_backgroundColor_constraint');
  const xsd = groups.find(item => item.code === 'xml_xsd');
  if (gaps?.occurrences.length !== 10) throw new Error('Expected one gap issue type with 10 occurrences.');
  if (backgrounds?.occurrences.length !== 16) throw new Error('Expected one background issue type with 16 occurrences.');
  if (xsd?.occurrences.length !== 1 || !xsd.message.includes("at position 2. Tag 'tt:styling' expected.")) {
    throw new Error('Expected the exact head-order XSD signature.');
  }
}
if (!findings.some(item => item.status === 3)) throw new Error('Expected blocking errors.');
console.log(`Standalone smoke test passed: ${findings.length} findings across ${codes.size} codes.`);
console.log(context.__group(findings).map(item => `${item.code}=${item.occurrences.length}`).join(', '));
