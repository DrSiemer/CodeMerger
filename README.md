# CodeMerger

A simple app for developers that prefer to stay in control and want to avoid working in AI powered IDE's. It allows you to define which files should be merged into a single string, so you can easily paste all relevant code into an LLM. Settings for a folder are stored in a .allcode file that can be committed with your project.


![Main application window](./dev/screenshot_01c.png "The main application window")


I recommend using this with [Gemini 2.5 Pro](https://aistudio.google.com/prompts/new_chat), because there you currently get a very large context length with high rate limits for free.


## Download

Download the latest release [here](https://github.com/DrSiemer/codemerger/releases).

The download is a portable executable for Windows. Ignore the Windows Defender SmartScreen block if you get it (click "More info" > "Run anyway"). The app is safe; all it does is bundle text with a convenient UI.


![Compact mode](./dev/screenshot_02b.png "Always-in-front compact mode")


## Features

- **Project-Based Settings**: Saves all your file selections, merge order, and window state in a local `.allcode` file for each project
- **`.gitignore` Aware**: The file browser automatically hides files and folders listed in your `.gitignore` file
- **New File Detection**: Automatically scans your project for new files that match your filetype settings and alerts you with a visual indicator. New files are highlighted in the file manager for easy review
- **Token Counting**: Calculates the total token count of your selected files to help you stay within an LLM's context limit
- **Customizable Prompts**: Configure a default prompt that is automatically prepended to your code when using the "Copy Code Only" button. You can also set application-wide default intro and outro texts for the instructions feature
- **Customizable Instructions**: Add project-specific text (like prompts or instructions) before and after the merged code block. You can easily load your predefined default prompts
- **Drag & Drop Reordering**: Easily reorder the files in your merge list to control the final output structure
- **Compact Mode**: A small, always-on-top, draggable window for quick access to core functions that appears when the main window is minimized. It includes an adaptive copy button (Copy with Instructions / Copy Code Only) and a paste button.
- **Recent Projects**: Quickly switch between your recent project folders
- **Project Colors**: Assign a unique color to each project for easy identification in compact mode


![File management](./dev/screenshot_03d.png "File management")


## Usage

- **Select a project**
    - Click "Select project" to browse for a folder or choose one from your recent projects list
- **Manage Files**
    - A warning icon will appear in the top bar if new files are detected in your project. Click this or the "Manage Files" button to open the file manager
        - **Ctrl-clicking** the new files icon will immediately add all new files to the current merge list without opening the file manager.
    - In the "Manage Files" window, a tree of available files is shown on the left
        - Newly detected files are highlighted in green for easy identification
        - Files listed in `.gitignore` are automatically hidden
        - Double-click a file or select it and click the button to add/remove it from the merge list
    - The "Merge Order" list on the right shows the files that will be copied
        - Drag and drop files or use the buttons to reorder them
        - The window title displays the number of selected files and the total token count
    - Double-click a file in either list to open it in your default or configured editor
    - Click "Save and Close" to save your selection to `.allcode`
- **Add Instructions**
    - Click "Define Instructions" to add a project-specific introduction or conclusion that will be wrapped around the merged code block
    - You can click the "Load Defaults" icon in this window to populate the fields with your predefined default prompts from the Settings
- **Copy Code**
    - Click "Copy Code Only" to merge the selected files and prepend your custom prompt (configured in Settings). This is useful for providing ongoing context to an LLM. The keyboard shortcut for this action is **`Ctrl+Shift+C`**.
    - If you added instructions, a "Copy with Instructions" button will appear to include your project-specific intro/outro text. This is ideal for starting a new conversation. The keyboard shortcut for this action is **`Ctrl+C`**.
- **Paste Changes**
    - To apply changes from a language model, you can use the paste functionality.
    - Pressing **`Ctrl+V`** will open the "Paste Changes" window, allowing you to review and apply the code from your clipboard.
    - Pressing **`Ctrl+Shift+V`** will apply the changes from your clipboard immediately, without opening the review window (unless new files need to be created).
- **Compact Mode**
    - Minimize the main window to activate the compact mode panel. All keyboard shortcuts (`Ctrl+C`, `Ctrl+Shift+C`, `Ctrl+V`, and `Ctrl+Shift+V`) are also active in this mode.
    - The panel contains two primary buttons:
        - **Copy (Instructions/Code Only)**: A single adaptive button for copying code.
            - It appears as "Copy with Instructions" if you have defined instructions for the project, and "Copy Code Only" if you have not.
            - A normal click performs the action shown on the button.
            - Holding **Ctrl** while clicking will always perform the "Copy Code Only" action.
        - **Paste**: Opens the "Paste Changes" window. If you hold **Ctrl** while clicking, it will immediately apply the changes from your clipboard without opening the window (unless new files need to be created).
    - The panel is colored with your project's assigned color.
    - A warning icon will appear in the move bar if new files are found.
        - **Click** the icon to restore the main window and open the file manager.
        - **Ctrl-click** the icon to immediately add all new files to the merge list.
    - Double-click the move bar or click the close button to exit compact mode and restore the main window. **Ctrl-clicking** the close button will exit the application immediately.


![Settings](./dev/screenshot_04.png "Settings")


### Settings

- **Application Updates**: Enable or disable the automatic daily check for new versions
- **Window Behavior**: Disable the automatic compact mode when the main window is minimized
- **File System Monitoring**: Configure the automatic check for new files (enable/disable and set the check interval)
- **Secret Scanning**: Enable a check for potential secrets (API keys, etc) that runs before copying code to the clipboard
- **Prompts**:
    - **"Copy Code Only" Prompt**: Set the default text that is automatically prepended when you click "Copy Code Only"
    - **Default Intro/Outro Prompts**: Define reusable, application-wide default texts for the instructions feature. These can be quickly loaded into any project's specific instructions
- **Default Editor**: Select your preferred editor for opening files from the file manager (leaving it blank uses the system default)
- To manage indexed filetypes, click "Manage Filetypes" from the main window


## Development

- Make sure you have [Python](https://www.python.org/downloads/) installed (and added to your PATH)
- Make sure you have [Inno Setup](https://jrsoftware.org/isdl.php) installed
- Run `go` to start
- Run `go b` to build executable and installer
- Run `go ba` to build the executable only
- Run `go bi` to build the installer only (requires a prior successful build)
- Run `go r` to push or update a release on Github using Actions
    - Update `/version.txt` if you want to create a new release
    - You can add a comment to the release like this: `go r "Comment"`
    - The release will be a draft, you'll need to finalize it on github.com
- Run the Inno Setup with a log like this: `CodeMerger_Setup.exe /LOG="setup.log"`
- When the app is installed, config can be found in `%APPDATA%\CodeMerger`