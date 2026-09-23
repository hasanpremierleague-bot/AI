"""
Script to create the required submission zip archive: 05_202303596.zip
Containing:
- student_academic_performance_pipeline.ipynb
- Project_Report_IT7103.docx
"""

import os
import zipfile

zip_filename = '05_202303596.zip'
files_to_pack = [
    'student_academic_performance_pipeline.ipynb',
    'Project_Report_IT7103.docx'
]

print(f"Creating submission zip: {zip_filename}...")
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in files_to_pack:
        if os.path.exists(file):
            print(f" - Adding {file} ({os.path.getsize(file):,} bytes)")
            zipf.write(file, arcname=os.path.basename(file))
        else:
            raise FileNotFoundError(f"Missing required deliverable: {file}")

# Also create 5_202303596.zip just in case Moodle prefers unpadded stream number
alt_zip_filename = '5_202303596.zip'
with zipfile.ZipFile(alt_zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in files_to_pack:
        zipf.write(file, arcname=os.path.basename(file))

print(f"Verifying {zip_filename} contents:")
with zipfile.ZipFile(zip_filename, 'r') as zipf:
    for info in zipf.infolist():
        print(f"   * {info.filename} ({info.file_size:,} bytes uncompressed)")

print("\nSubmission packaging complete! Both 05_202303596.zip and 5_202303596.zip created successfully.")
