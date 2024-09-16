**Clarity Notes**

Clarity Notes is a distraction-free text editor designed for writers and coders. It allows users to write in a simple and focused environment, providing both a rich text editing mode and a code editing mode.

The present is an alpha release (version 0.1) and the release file is clarity.py.

**Features**

    Distraction-Free Writing: Offers a simple, clean interface with minimal distractions.
    Dual Modes: Switch between Normal Mode (rich text) and Code Mode (plain text/code).
    Basic Formatting: Supports bold, italics, underline, bullet points, numbered lists, and tables.
    Speech Recognition: Basic audio-to-text functionality.
    Dark Mode: Toggle between light and dark themes for a comfortable writing experience.
    File Support: Open and save files in various formats, including .txt, .odt, .odf, .pdf, .py, .js, and .html.
    Line and Paragraph Spacing: Customize line and paragraph spacing for a tailored writing experience.
    Cross-Platform: Works on macOS, Windows, and Linux (requires Python and PyQt5).

**Prerequisites**

    Python 3.x: Ensure that Python 3.x is installed on your system. You can download it from python.org.
    Virtual Environment (recommended): It is recommended to use a virtual environment to manage dependencies.

**Installation**

    Clone the Repository: Download or clone the project files from the repository:
            git clone https://github.com/mnani87/clarity.git
            cd clarity

    Set Up Virtual Environment: Create and activate a virtual environment:
            python3 -m venv clarity_notes_env
            source clarity_notes_env/bin/activate  # On macOS/Linux
            clarity_notes_env\Scripts\activate     # On Windows

    Install Dependencies: Install the required packages using requirements.txt:
            pip install -r requirements.txt

    Run Clarity Notes: Run the application:
            python clarity.py

**Usage**

    Normal Mode: Use this mode for rich text editing, including formatting options like bold, italics, underline, bullet points, and numbered lists.
    Code Mode: Switch to this mode for writing plain text or code (e.g., Python, JavaScript, HTML).
    Dark Mode: Toggle dark mode for a more comfortable viewing experience in low-light environments.
    File Operations: Open and save files in various formats.
        Open: Supports .txt, .odt, .odf, .py, .js, .html.
        Save: Save your work in .txt, .odt, .odf, or .pdf. Code Mode saves in .py, .js or .html.

**Keyboard Shortcuts**

    Bold: Ctrl+B
    Italic: Ctrl+I
    Underline: Ctrl+U
    Toggle Code Mode: Ctrl+M
    Save: Ctrl+S
    Open: Ctrl+O
    New Document: Ctrl+N

**Important Notes**

    Switching to Code Mode: Switching to Code Mode will strip away all rich text formatting.
    Saving Changes: If you open a file and make changes, use "Save" to save changes to the same file. Use "Save As" to save to a new file.

**Dependencies**

    PyQt5
    odfpy
    PyInstaller (for creating standalone executables)

    All dependencies are listed in the requirements.txt file.

**Troubleshooting**

    Error: ModuleNotFoundError: Ensure all dependencies are installed using pip install -r requirements.txt.
    Switching to Code Mode: Ensure you save your work before switching modes, as Code Mode will remove all rich text formatting.
    Speech Recognition: Works best with audio files up to 60 seconds long. This is basic functionality only - no punctuations etc. 

**License**

    This project is licensed under the GPL-3 License.

**Contributing**

    Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

