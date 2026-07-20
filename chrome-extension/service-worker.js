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

async function mergeTabDetails(tabId, details) {
  if (tabId < 0) return;
  const key = `tab:${tabId}`;
  const existing = (await chrome.storage.session.get(key))[key] || {};
  await chrome.storage.session.set({
    [key]: {...existing, ...details, updatedAt: Date.now()},
  });
}

chrome.webRequest.onBeforeRequest.addListener(
  details => {
    const pid = details.url.match(mediaSelectorPattern)?.[1]?.toLowerCase();
    if (pid) mergeTabDetails(details.tabId, {pid});
    if (isSubtitleUrl(details.url)) mergeTabDetails(details.tabId, {subtitleUrl: details.url});
  },
  {urls: ['https://*/*']},
);

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'FOUND_DETAILS' && sender.tab?.id != null) {
    mergeTabDetails(sender.tab.id, message.details).then(() => sendResponse({ok: true}));
    return true;
  }
  if (message?.type === 'GET_DETAILS') {
    const key = `tab:${message.tabId}`;
    chrome.storage.session.get(key).then(result => sendResponse(result[key] || {}));
    return true;
  }
});

chrome.tabs.onRemoved.addListener(tabId => chrome.storage.session.remove(`tab:${tabId}`));
