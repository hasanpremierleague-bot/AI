"""Execute the canonical notebook, including both temporal pipeline searches.
This replaces the separate modeling implementation to prevent divergent results.
"""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).parent / 'execute_notebook.py'), run_name='__main__')
