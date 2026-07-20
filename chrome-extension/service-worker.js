const mediaSelectorPattern = /\/mediaselector\/.*?\/(?:vpid|cvid)\/([a-z0-9]{8})(?:\/|$)/i;

function isSubtitleUrl(url) {
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

function normalisePageUrl(value) {
  try {
    const url = new URL(value);
    if (!/^www\.bbc\.(?:co\.uk|com)$/i.test(url.hostname)) return '';
    url.hash = '';
    return url.href;
  } catch {
    return '';
  }
}

async function mergeTabDetails(tabId, details, rawPageUrl = '') {
  if (tabId < 0) return;
  const key = `tab:${tabId}`;
  const pageUrl = normalisePageUrl(rawPageUrl);
  const stored = (await chrome.storage.session.get(key))[key] || {};
  const existing = pageUrl && stored.pageUrl !== pageUrl ? {} : stored;
  await chrome.storage.session.set({
    [key]: {...existing, ...details, ...(pageUrl ? {pageUrl} : {}), updatedAt: Date.now()},
  });
}

chrome.webRequest.onBeforeRequest.addListener(
  details => {
    const pid = details.url.match(mediaSelectorPattern)?.[1]?.toLowerCase();
    const found = {};
    if (pid) found.pid = pid;
    if (isSubtitleUrl(details.url)) found.subtitleUrl = details.url;
    if (found.pid || found.subtitleUrl) {
      mergeTabDetails(details.tabId, found, details.documentUrl || details.initiator);
    }
  },
  {urls: ['https://*/*']},
);

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'FOUND_DETAILS' && sender.tab?.id != null) {
    mergeTabDetails(sender.tab.id, message.details, message.pageUrl || sender.tab.url)
      .then(() => sendResponse({ok: true}));
    return true;
  }
  if (message?.type === 'GET_DETAILS') {
    const key = `tab:${message.tabId}`;
    const pageUrl = normalisePageUrl(message.pageUrl);
    chrome.storage.session.get(key).then(result => {
      const details = result[key] || {};
      sendResponse(!pageUrl || details.pageUrl === pageUrl ? details : {});
    });
    return true;
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  const pageUrl = normalisePageUrl(changeInfo.url);
  if (pageUrl) chrome.storage.session.set({[`tab:${tabId}`]: {pageUrl, updatedAt: Date.now()}});
});
chrome.tabs.onRemoved.addListener(tabId => chrome.storage.session.remove(`tab:${tabId}`));
