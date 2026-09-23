"""Regenerate the corrected notebook from the preserved input and revision builder.
Execution clears outputs; run execute_notebook.py afterward.
"""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).parent / 'revision_work' / 'revise_notebook.py'), run_name='__main__')
