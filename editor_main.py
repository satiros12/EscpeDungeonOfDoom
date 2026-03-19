import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from editor import Editor

if __name__ == "__main__":
    editor = Editor()
    editor.run()
