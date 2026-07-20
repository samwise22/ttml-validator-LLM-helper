# BBC Subtitle Details Chrome extension

This unpacked Manifest V3 extension observes BBC player requests and presents the
playable media PID and signed subtitle XML URL in copyable fields. It does not
download or modify the subtitle file.

**Copy both for validator** writes a three-line import block containing both
values. Paste that block into the standalone validator's **Import via Chrome
extension** field to populate its PID and subtitle URL inputs together.

For homepage overlays and other experiences without a video-specific page URL,
the extension derives the PID from BBC subtitle filenames such as
`p0nz8v4q-….xml`. A new subtitle request replaces the previous capture even when
the browser remains on the same root URL.

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

After updating an unpacked copy, select **Reload** on its `chrome://extensions`
card before testing the new version.
