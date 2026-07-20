const pid = document.querySelector('#pid');
const subtitleUrl = document.querySelector('#subtitleUrl');
const status = document.querySelector('#status');

async function load() {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  if (!tab?.id || !/^https:\/\/(?:www\.)?bbc\.(?:co\.uk|com)\//i.test(tab.url || '')) {
    status.textContent = 'Open a BBC page containing a video.';
    disableEmptyCopyButtons();
    return;
  }
  try {
    await chrome.tabs.sendMessage(tab.id, {type: 'SCAN_NOW'});
  } catch {}
  await new Promise(resolve => setTimeout(resolve, 120));
  const details = await chrome.runtime.sendMessage({type: 'GET_DETAILS', tabId: tab.id, pageUrl: tab.url});
  pid.value = details.pid || '';
  subtitleUrl.value = details.subtitleUrl || '';
  if (details.pid && details.subtitleUrl) {
    status.textContent = 'PID and subtitle request found.';
    status.className = 'ready';
  } else if (details.pid || details.subtitleUrl) {
    status.textContent = 'One detail found. Start playback with subtitles enabled to capture the other.';
    status.className = 'partial';
  } else {
    status.textContent = 'Nothing detected yet. Start playback with subtitles enabled.';
  }
  disableEmptyCopyButtons();
}

function disableEmptyCopyButtons() {
  document.querySelectorAll('[data-copy]').forEach(button => {
    button.disabled = !document.querySelector(`#${button.dataset.copy}`).value;
  });
}

document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const field = document.querySelector(`#${button.dataset.copy}`);
    await navigator.clipboard.writeText(field.value);
    const original = button.textContent;
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = original; }, 1000);
  });
});

load();
