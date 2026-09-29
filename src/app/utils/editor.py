from pathlib import Path
import tempfile
from builder.utils.logger import error
import subprocess

def open_editor(editor: str, extension: str, name: str, text: str) -> str:
    """Open an editor to edit a text.

    The method invokes the selected editor on a temporary file with
    the specified file extension and returns the edited content.
    
    Args:
        editor (str): The binary of the editor.
        extension (str): File extension of the file to edit.
        name (str): Prefix of the tmpfile's name.
        text (str): Text to edit.
    
    Returns:
        (str): The edited content.
    """
    with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=f".{extension}",
            prefix=f"{name}-",
            delete=True,
            encoding="utf-8"
        ) as file:
            path = Path(file.name)
            path.write_text(text)

            try:
                import shlex
                subprocess.run(
                    shlex.split(editor) + [ str(path) ],
                    check=True
                )
            
            except subprocess.CalledProcessError as e:
                error(f"Editor exited with status {e.returncode}")
                return text
            
            except FileNotFoundError as e:
                error(f"Editor '{editor}' was not found.")
                return text
            
            text = path.read_text(encoding="utf-8")

    return text
