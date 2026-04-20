# CodeMerger

**CodeMerger is a low-level, clipboard-based bridge designed to give developers absolute custody over their AI context.**

While modern AI-powered IDEs act as a "black box", silently scanning your workspace and sending hidden sequences of prompts to proprietary APIs, CodeMerger operates with total transparency. It is a zero-magic utility, that puts the raw power of context management literally in your hands.

By using the clipboard as your bridge, you decouple your workflow from specific editors and expensive API credits, allowing you to leverage the world’s most powerful LLMs for free via their native web interfaces.

![Main application window](./dev/screenshot_01b.jpg "Main Application Window")

*Tip: We recommend using CodeMerger with models like [Gemini Flash Latest](https://aistudio.google.com/prompts/new_chat?model=gemini-flash-latest), which has a generous free tier and a massive context window capable of handling large code bundles.*

## Download

Download the latest portable executable for Windows from the [Releases page](https://github.com/DrSiemer/codemerger/releases).

*(Note: If you encounter a Windows Defender SmartScreen block, click "More info" > "Run anyway". CodeMerger is a safe, local-only utility.)*

## Key Features

- **Prompt Custody**: Nothing is hidden. You hand-pick the files, dictate their order, and wrap them in your own instructions. The final prompt is a transparent text string that you own and control.
- **Unabridged Context**: No "chunking," no "vector embeddings," and no RAG hallucinations. You provide full source files to the LLM, ensuring it sees your code exactly as it exists on disk.
- **Decoupled Workflow**: Specifically designed for a manual copy-paste loop. This allows you to use the most powerful models for **FREE** through their standard web interfaces (like [Google AI Studio](https://aistudio.google.com/)) rather than paying for API credits or specialized IDE subscriptions.
- **Closed-Loop Transparency**: Once the AI responds, paste it back into CodeMerger. The app automatically parses the output into navigable segments, allowing you to review line-by-line diffs and approve changes before any code is written to disk.
- **Guided Project Starter**: A structured workflow for building new applications. It guides you and your LLM through generating a cohesive concept, tech stack, and step-by-step TODO plan before scaffolding the boilerplate.
- **Compact Widget**: Minimize the main window to activate an always-on-top panel. It handles the "Copy Context / Paste Changes" loop so you never have to leave your editor.

![File management](./dev/screenshot_03b.jpg "Merge List")

## Core Workflow

1. **Select a Project**: Browse for a folder. CodeMerger will automatically create a `.codemerger` configuration folder to save your settings.
2. **Edit Merge List**: Click "Edit Merge List" to open the file manager.
   - Select the specific files you want to share with the AI.
   - Drag and drop the selected files to dictate the order in which the AI reads them. Use the "Order Request" to let an LLM determine the optimal order.
3. **Add Instructions**: Click "Define Instructions" to prepend goals or append code style rules to your project bundle.
4. **Copy Code**:
   - Click **"Copy with Instructions"** (`Ctrl+C`) to bundle the code and wrap it with your custom prompts. Ideal for starting a new chat.
   - Click **"Copy Code Only"** (`Ctrl+Shift+C`) to quickly bundle the code with a simple update header. Ideal for asking questions or updating an existing conversation with the latest context if you made changes outside the conversation.
5. **Paste Changes**: Once the AI gives you updated code, click **"Paste Changes"** (`Ctrl+V`) to import it. CodeMerger parses the AI's Markdown response and opens the **AI Response Review** window, allowing you to diff and approve file modifications line-by-line.

## Compact Mode

When you minimize the main window, CodeMerger transforms into a compact, always-on-top widget.

![Compact mode](./dev/screenshot_02b.jpg "Compact Mode")

- Access your standard "Copy" and "Paste" actions without leaving your IDE.
- Color-coded to match your active project.
- Double-click the title bar or click the expand icon to restore the full dashboard.

## Project Starter

CodeMerger includes a built-in tool to help you kick off new projects. It provides a structured workflow, that guides you and your LLM through generating a solid project foundation.

![Project Starter](./dev/screenshot_04b.jpg "Project Starter")

- **Concept Generation**: Define your goal and let the AI generate a structured problem statement, feature list, and user flows.
- **Stack Selection**: Get intelligent technology recommendations based on your experience and the generated concept.
- **TODO Plan**: Generate a detailed, phase-by-phase implementation plan.
- **Interactive Refinement**: Lock approved segments, request targeted rewrites, and ask contextual questions before scaffolding the final codebase directly to disk.

### Command Line Arguments (Advanced)

- `--console`: Spawns a native command prompt alongside the app for real-time logs.
- `--inspect`: Enables "Inspect Element" and Developer Tools (Ctrl+Shift+I) for debugging.

## Development

- Requires [Python 3.10+](https://www.python.org/downloads/) and [Node.js](https://nodejs.org/) installed.
- Run `go i` before starting.

### Commands
The project uses a `go.bat` script to orchestrate all development and build tasks.

**Running the App**

- `go`: Starts the app (builds production frontend if missing).
- `go dev`: Starts Vite HMR and the Python backend concurrently.
- `go debug`: Starts the app in production mode with DevTools enabled.
- `go api`: Starts only the Python backend in development mode (expects Vite at port 5173).
- `go fe`: Starts only the Vite development server.

**Building & Distribution**

- `go b`: **Full Build**. Compiles frontend, bundles executable, and creates the installer.
- `go ba`: Build App Only (frontend + executable).
- `go bi`: Build Installer Only (requires existing `dist\CodeMerger` folder).
- `go br`: Rebuilds the production frontend and then starts the app.

**Environment & Utilities**

- `go i`: Installs node modules for the frontend.
- `go cmd`: Opens a new command prompt with the Python virtual environment pre-activated.
- `go f`: Freezes current Python dependencies into `requirements.txt`.
- `go r "Comment"`: Handles the release process (verifies branch, creates Git tag, and pushes).

*Configuration is stored in `%APPDATA%\CodeMerger`.*

## License

CodeMerger is free to use for personal and commercial development. However, the distribution of modified versions, resale, or rebranding is strictly prohibited. If you wish to contribute to the project, please reach out via GitHub. See the [LICENSE](LICENSE) file for the full legal text.