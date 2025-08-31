# CodeMerger

A simple app for developers that prefer to stay in control and want to avoid working in AI powered IDE's. It allows you to define which files should be merged into a single string, so you can easily paste all relevant code into an LLM. Settings for a folder are stored in a .allcode file that can be committed with your project.

I recommend using this with [Gemini 2.5 Pro](https://aistudio.google.com/prompts/new_chat), because at this time it offers a large context length for free.


## Features

- **Project-Based Settings**: Saves all your file selections, merge order, and window state in a local `.allcode` file for each project
- **`.gitignore` Aware**: The file browser automatically hides files and folders listed in your `.gitignore` file.
- **Token Counting**: Calculates the total token count of your selected files to help you stay within an LLM's context limit
- **Customizable Wrapper Text**: Add custom text (like prompts or instructions) before and after the merged code block
- **Drag & Drop Reordering**: Easily reorder the files in your merge list to control the final output structure
- **Compact Mode**: A small, always-on-top, draggable window for quick copy-pasting while you work
- **Recent Projects**: Quickly switch between your recent project folders
- **Project Colors**: Assign a unique color to each project for easy identification in compact mode


## Download

Download the latest release [here](https://github.com/DrSiemer/codemerger/releases).

The download is a portable executable for Windows. Ignore the Windows Defender SmartScreen block if you get it (click "More info" > "Run anyway"). The app is safe; all it does is bundle text with a convenient UI.


## Usage

- **Select a project**
    - Click "Select project" to browse for a folder or choose one from your recent projects list
- **Manage Files**
    - In the "Manage Files" window, a tree of available files is shown on the left
        - Files listed in `.gitignore` are automatically hidden
        - Double-click a file or select it and click the button to add/remove it from the merge list
    - The "Merge Order" list on the right shows the files that will be copied
        - Drag and drop files or use the buttons to reorder them
        - The window title displays the number of selected files and the total token count
    - Double-click a file in either list to open it in your default or configured editor
    - Click "Save and Close" to save your selection to `.allcode`
- **Add Wrapper Text**
    - Click "Wrapper Text" to add an introduction or conclusion that will be wrapped around the merged code block
- **Copy Code**
    - Click "Copy Merged" to merge only the selected files into a single string in your clipboard
    - If you added wrapper text, a "Copy Wrapped" button will appear to include your intro/outro text
- **Compact Mode**
    - Click "Compact Mode" to switch to a small, always-on-top copy button
    - The button is colored with your project's assigned color and shows the project name on hover
    - A small "W" button is available for copying the wrapped version
    - Double-click the move bar or use the close button to return to the full view


### Settings

- Select your preferred editor in the settings (none means default will be used)
- To manage indexed filetypes, click "Manage Filetypes" from the main window


## Development

- Make sure you have [Python](https://www.python.org/downloads/) installed (and added to your PATH)
- Make sure you have [Inno Setup](https://jrsoftware.org/isdl.php) installed
- Run `go` to start
- Run `go b` to build executable
- Run `go r` to push or update a release on Github using Actions
    - Update `/version.txt` if you want to create a new release
    - You can add a comment to the release like this: `go r "Comment"`
    - The release will be a draft, you'll need to finalize it on github.com
- Config once installed can be found in `%APPDATA%\CodeMerger`

### Planned features

- Design