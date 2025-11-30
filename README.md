# Tarqim

**Tarqim** is an ultra-lightweight, high-performance Markdown viewer for Linux.

## Features

*   **Zero Bloat:** Built with Python and Tkinter. No Electron.
*   **Native Performance:** Starts instantly (< 1s) and uses minimal RAM (< 50MB).
*   **Clean UI:** Focused reading experience with a modern flat theme.

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python3 main.py
    ```

## Usage
*   **Open Folder:** Click the 📂 icon in the sidebar or press `Ctrl+O`.
*   **Pin File:** Click the ➕ icon in the sidebar to pin a file.
*   **Edit File:** Click the 📝 icon in the preview header to toggle edit mode. Changes are auto-saved.
*   **Copy Content:** Click the 📋 icon to copy the file content to clipboard.
*   **Toggle Sidebar:** Click the ◀☰ button in the bottom left.
*   **Scroll:** Use the ▲/▼ buttons in the bottom right to scroll the preview.
*   **Quit:** `Ctrl+Q`.

## Structure

*   `main.py`: Entry point.
*   `app/`: Application source code.
    *   `core/`: Core logic (Renderer, Config).
    *   `ui/`: User Interface components.

## License

MIT
