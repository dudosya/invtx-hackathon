# invtx-hackathon

## Environment Setup

Follow these steps to set up the project environment. This project requires Python 3.8 or higher.

### 1. Install Python Dependencies

First, install the required Python libraries using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 2. Install Poppler

This project uses the `pdf2image` library, which depends on Poppler, a PDF rendering utility. It must be installed and accessible on your system.

**For Windows:**

1.  **Download Poppler:** Download the latest pre-compiled binaries from [this link](https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.11.0-0). Choose the `.zip` file (e.g., `Release-25.11.0-0.zip`).

2.  **Extract Files:** Extract the downloaded zip file to a permanent location, for example, `C:\poppler`.

3.  **Add to System PATH:** You must add the `bin` directory from the extracted folder to your system's PATH variable to make Poppler accessible from the command line.
    *   Search for "Edit the system environment variables" in the Start Menu and open it.
    *   Click on "Environment Variables...".
    *   In the "System variables" section, find `Path`, select it, and click "Edit...".
    *   Click "New" and add the full path to the `bin` folder. For example: `C:\poppler\poppler-23.11.0\Library\bin`
    *   Click "OK" to save and close all windows.

### 3. Verify Installation (Optional)

Open a **new** terminal or command prompt and run `pdfinfo --version`. If it shows the Poppler version information, the setup is complete and correct.