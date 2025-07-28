# CodeMerger

A simple app for developers that prefer to stay in control and want to avoid working in AI powered IDE's. It allows you to define which files should be merged into a single string, so you can easily paste all relevant code into an LLM. Settings for a folder are stored in a .allcode file that can be committed with your project.

I recommend using this with [Gemini 2.5 Pro](https://aistudio.google.com/prompts/new_chat), because at this time it offers a large context length for free.

## Download

Download the latest (portable) release [here](https://github.com/DrSiemer/codemerger/releases)

## Usage

- First select a working directory
    - The 5 most recent folders will be listed in this window as well
- Add the files you want to manage
    - Once added, you can open a file by double clicking it in the Merge Order window
- Click "Copy merged" to merge all the selected files into a single string in your clipboard
- Click "Compact Mode" to switch to a small, always-on-top copy button. This is useful for keeping the copy functionality handy while you work. Double-click the move bar or use the close button to return to the full view.

### Settings

- Select your preferred editor in the settings (none means default is used)
- To manage indexed filetypes, click "Manage Filetypes" from the main window

## Development

- Run `go` to start
- Run `go b` to build executable

### Planned features

- Installer
- Actual design