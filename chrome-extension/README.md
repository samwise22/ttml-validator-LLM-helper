# BBC Subtitle Details Chrome extension

This unpacked Manifest V3 extension observes BBC player requests and presents the
playable media PID and signed subtitle XML URL in copyable fields. It does not
download or modify the subtitle file.

## Install for testing

1. Open `chrome://extensions` in Chrome.
2. Turn on **Developer mode**.
3. Select **Load unpacked** and choose this `chrome-extension` directory.
4. Open a BBC page containing a video.
5. Start playback and enable subtitles.
6. Open **BBC Subtitle Details** from the extensions menu.

Signed subtitle URLs expire. Copy and use the URL while it is current. If either
field is missing, reload the BBC page after installing the extension, start the
video with subtitles enabled, and open the extension again.
