# Streamlit Tax Calculator App 

This README provides instructions for setting up and running a Streamlit application (`tax_cal.py`) using `uvx` on Windows and macOS.

## Release Note

### Version 0.1.0

## Prerequisites
- Python 3.8 or higher installed.
- Internet connection for installing `uv` and dependencies.
- A terminal (Command Prompt/PowerShell for Windows, Terminal for macOS).

## Setup Instructions

### Install UV
UV is a Python package and environment manager. Install it to use `uvx`.

#### On Windows
1. Open PowerShell or Command Prompt.
2. Install UV using pip:
   ```bash
   pip install uv
   ```
3. Verify installation:
   ```bash
   uv --version
   ```

#### On macOS
1. Open Terminal.
2. Install UV using pip:
   ```bash
   pip3 install uv
   ```
3. Verify installation:
   ```bash
   uv --version
   ```

### Run the Streamlit App with `uvx`
`uvx` allows you to run Streamlit in an isolated environment without manually creating a virtual environment.

#### On Windows
1. Open PowerShell or Command Prompt.
2. Navigate to the directory containing `tax_cal.py`:
   ```bash
   cd path\to\your\project
   ```
3. Run the Streamlit app:
   ```bash
   uvx streamlit run tax_cal.py
   ```
4. Open your browser to `http://localhost:8501` to view the app.

#### On macOS
1. Open Terminal.
2. Navigate to the directory containing `tax_cal.py`:
   ```bash
   cd /path/to/your/project
   ```
3. Run the Streamlit app:
   ```bash
   uvx streamlit run tax_cal.py
   ```
4. Open your browser to `http://localhost:8501` to view the app.

## Troubleshooting
- **Port Conflict**: If `localhost:8501` is in use, Streamlit will suggest an alternative port.
- **Dependency Issues**: If errors occur, try specifying a Streamlit version:
  ```bash
  uvx streamlit==1.38.0 run tax_cal.py
  ```
- **UV Not Found**: Ensure UV is installed (`uv --version`). Reinstall if needed:
  ```bash
  pip install uv --force-reinstall  # Windows
  pip3 install uv --force-reinstall  # macOS
  ```
- **Network Issues**: Ensure an active internet connection for `uvx` to download dependencies.

## Notes
- `uvx` creates a temporary environment for each run, ensuring a clean setup.
- For persistent environments, consider using `uv venv` and `uv pip install streamlit` (see UV documentation).
- Check the Streamlit documentation for advanced configuration: https://docs.streamlit.io/

For further assistance, contact the project maintainer or refer to the UV documentation: https://docs.astral.sh/uv/