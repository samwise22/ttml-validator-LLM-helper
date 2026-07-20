const mediaSelectorPattern = /\/mediaselector\/.*?\/(?:vpid|cvid)\/([a-z0-9]{8})(?:\/|$)/i;

function subtitleUrl(url) {
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.toLowerCase();
    return parsed.protocol === 'https:' &&
      (host.endsWith('.bbci.co.uk') || host.endsWith('.akamaized.net')) &&
      parsed.pathname.toLowerCase().endsWith('.xml') &&
      parsed.pathname.includes('/subtitles/');
  } catch {
    return false;
  }
}

function scan() {
  const resources = performance.getEntriesByType('resource').map(entry => entry.name);
  const selectorUrl = resources.find(url => mediaSelectorPattern.test(url));
  const detectedSubtitleUrl = resources.find(subtitleUrl);
  const details = {};
  const requestPid = selectorUrl?.match(mediaSelectorPattern)?.[1];
  if (requestPid) details.pid = requestPid.toLowerCase();
  if (detectedSubtitleUrl) details.subtitleUrl = detectedSubtitleUrl;

  if (!details.pid) {
    const scripts = [...document.scripts].map(script => script.textContent || '').join('\n');
    const embedded = scripts.match(/\\"id\\":\\"([a-z0-9]{8})\\",\\"idType\\":\\"versionID\\"/i) ||
      scripts.match(/"id":"([a-z0-9]{8})","idType":"versionID"/i);
    if (embedded) details.pid = embedded[1].toLowerCase();
  }

  if (details.pid || details.subtitleUrl) {
    chrome.runtime.sendMessage({type: 'FOUND_DETAILS', details});
  }
}

scan();
const observer = new PerformanceObserver(scan);
observer.observe({type: 'resource', buffered: true});
chrome.runtime.onMessage.addListener(message => {
  if (message?.type === 'SCAN_NOW') scan();
});
