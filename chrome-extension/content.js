const mediaSelectorPattern = /\/mediaselector\/.*?\/(?:vpid|cvid)\/([a-z0-9]{8})(?:\/|$)/i;
let currentPageUrl = location.href;
let pageStartedAt = 0;

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

function pidFromSubtitleUrl(url) {
  try {
    const filename = new URL(url).pathname.split('/').pop() || '';
    return filename.match(/^([a-z0-9]{8})(?:-|\.xml$)/i)?.[1]?.toLowerCase() || '';
  } catch {
    return '';
  }
}

function scan() {
  if (location.href !== currentPageUrl) {
    currentPageUrl = location.href;
    pageStartedAt = performance.now();
  }
  const resources = performance.getEntriesByType('resource')
    .filter(entry => entry.startTime >= pageStartedAt)
    .map(entry => entry.name)
    .reverse();
  const selectorUrl = resources.find(url => mediaSelectorPattern.test(url));
  const detectedSubtitleUrl = resources.find(subtitleUrl);
  const details = {};
  const requestPid = selectorUrl?.match(mediaSelectorPattern)?.[1];
  if (requestPid) details.pid = requestPid.toLowerCase();
  if (detectedSubtitleUrl) {
    details.subtitleUrl = detectedSubtitleUrl;
    details.pid ||= pidFromSubtitleUrl(detectedSubtitleUrl);
  }

  if (!details.pid) {
    const scripts = [...document.scripts].map(script => script.textContent || '').join('\n');
    const embedded = scripts.match(/\\"id\\":\\"([a-z0-9]{8})\\",\\"idType\\":\\"versionID\\"/i) ||
      scripts.match(/"id":"([a-z0-9]{8})","idType":"versionID"/i);
    if (embedded) details.pid = embedded[1].toLowerCase();
  }

  if (details.pid || details.subtitleUrl) {
    chrome.runtime.sendMessage({type: 'FOUND_DETAILS', pageUrl: location.href, details});
  }
}

scan();
const observer = new PerformanceObserver(scan);
observer.observe({type: 'resource', buffered: true});
chrome.runtime.onMessage.addListener(message => {
  if (message?.type === 'SCAN_NOW') scan();
});
