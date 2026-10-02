# Prototyping Hub desktop shortcuts

Both files open https://donnalealn.github.io/workflows/ in your default browser.

## macOS
- `macos/Prototyping Hub.webloc` — drag to the Desktop, double-click to open.
- `macos/Prototyping Hub.command` — same, via a shell script. After downloading, run
  `chmod +x "Prototyping Hub.command"` once (downloads drop the executable bit).

To change the target, edit the URL inside either file.

The page only resolves once GitHub Pages is enabled for this repo and the prototype is
published as `index.html`.
