from crewai.tools import tool
from pathlib import Path
import subprocess

# Define the sandbox directory and ensure it exists.
SANDBOX_DIR = Path(__file__).parents[3] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

@tool("List Sandbox Files")
def list_sandbox_files() -> str:
    # Get a sorted list of all filenames in the sandbox directory.
    """
    List the filenames currently in the sandbox directory.

    Returns:
        A newline-separated list of filenames, or a message if the
        sandbox is empty.
    """
    # List all filenames in the sandbox directory.
    names = sorted(p.name for p in SANDBOX_DIR.iterdir())
    # Return the list of filenames, or a message if the sandbox is empty.
    return "\n".join(names) if names else "The sandbox is empty."


@tool("Read Sandbox File")
# Read the contents of a file in the sandbox directory.
def read_sandbox_file(filename: str) -> str:
    """
    Read and return the text contents of a file in the sandbox directory.

    Args:
        filename: The name of the file to read (e.g. "solution.py").
    Returns:
        The file's contents, or a message if the file does not exist.
    """
    # Construct the full path to the file in the sandbox directory.
    path = SANDBOX_DIR / filename
    # Check if the file exists before attempting to read it.
    if not path.is_file():
        # Return a message indicating the file does not exist.
        return f"No such file in the sandbox: {filename}"
    # Read and return the file's contents.
    return path.read_text()


@tool("Write Sandbox File")
# Write text to a file in the sandbox directory, replacing any existing file with the same name.
def write_sandbox_file(filename: str, content: str) -> str:
    """
    Write text to a file in the sandbox directory, replacing any existing
    file with the same name.

    Args:
        filename: The name of the file to write (e.g. "solution.py").
        content: The text content to write.
    Returns:
        A confirmation message.
    """
    # Construct the full path to the file in the sandbox directory.
    path = SANDBOX_DIR / filename
    # Write the content to the file, replacing any existing file with the same name.
    path.write_text(content)
    return f"Wrote {len(content)} characters to {filename}."


@tool("Run Sandbox Python File")
# Run a Python file from the sandbox directory inside an ephemeral Docker container.
def run_sandbox_python(filename: str) -> str:
    """
    Execute a Python file from the sandbox directory inside an ephemeral
    Docker container, with the sandbox mounted as the working directory,
    and return whatever the script printed to stdout.

    Args:
        filename: The name of the Python file to run (e.g. "solution.py").
    Returns:
        The text printed to stdout by the executed script.
    """
    # Construct the full path to the Python file in the sandbox directory.
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{SANDBOX_DIR}:/workspace",
            "-w", "/workspace",
            "python:3.13-slim",
            "python", filename,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.stdout

sandbox_tools = [list_sandbox_files, read_sandbox_file, write_sandbox_file, run_sandbox_python]


def _never_cache(*_args, **_kwargs) -> bool:
    return False


# Sandbox state changes between calls (files appear/change/run), so caching tool
# results would feed agents stale data. Opt out of CrewAI's default tool caching.
for _t in sandbox_tools:
    _t.cache_function = _never_cache
