# CodeMerger

A simple app for developers that prefer to stay in control and want to avoid working in AI powered IDE's. It allows you to define which files should be merged into a single string, so you can easily paste all relevant code into an LLM. Settings for a folder are stored in a .allcode file that can be committed with your project.

I recommend using this with [Gemini 2.5 Pro](https://aistudio.google.com/prompts/new_chat), because at this time it offers a large context length for free.

## Download

Download the latest (portable) release [here](https://github.com/DrSiemer/codemerger/releases).

Ignore the Windows Defender SmartScreen block if you get it (click "More info" > "Run anyway"); all this app does is bundle text with a convenient UI.

## Usage

- Select a working directory
- Add the files you want to manage
    - You can open an added file by double clicking
- Click "Copy merged" to merge all the selected files into a single string in your clipboard
- Click "Compact Mode" to switch to a small, always-on-top copy button. This is useful for keeping the copy functionality handy while you work.
    - Double-click the move bar or use the close button to return to the full view

### Settings

- Select your preferred editor in the settings (none means default will be used)
- To manage indexed filetypes, click "Manage Filetypes" from the main window

## Development

- Make sure you have Python installed (and added to your PATH)
- Run `go` to start (`./go.sh` on a Mac)
- Run `go b` to build executable (`./go.sh b` on a Mac)

### Mac

- Untested!
- Make `go.sh` executable with `chmod +x go.sh`

### Planned features

- Installer
- Actual design