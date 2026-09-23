"""
Script to execute the notebook and save all generated outputs directly into the .ipynb file
"""
import nbformat
from nbclient import NotebookClient

nb_path = 'student_academic_performance_pipeline.ipynb'
print(f"Reading {nb_path}...")
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

print("Executing notebook cells with NotebookClient...")
client = NotebookClient(nb, timeout=900, kernel_name='python3')
client.execute()

print(f"Saving executed notebook back to {nb_path}...")
with open(nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print("Notebook execution finished successfully! All outputs, plots, and metrics embedded.")
