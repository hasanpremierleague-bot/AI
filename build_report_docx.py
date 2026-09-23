"""Build the report from the executed notebook and its exported results.
Use the Codex bundled document Python runtime for this builder.
"""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).parent / 'revision_work' / 'build_verified_report.py'), run_name='__main__')
