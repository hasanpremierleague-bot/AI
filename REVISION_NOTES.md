# Verified project revision

- Preserved previous files in revision_backup.
- Replaced row-order cross-validation with whole-semester expanding folds for both tasks.
- Fitted complete preprocessing/model pipelines within each tuning fold.
- Added executable classification tuning and baseline-versus-tuned comparisons.
- Removed inactive subsampling search and unsupported marks allocations.
- Replaced report statistics and figures with executed notebook results.
- Added mean/majority baselines, observed-exam counts, false-alert discussion and realistic temporal assumptions.
- Rebuilt and visually checked the 11-page report using Word PDF export because bundled LibreOffice was unavailable.
- Executed all 14 code cells in a fresh local kernel. Hosted Colab was not run.
- Verified both ZIPs contain the current notebook and report byte-for-byte.

Run the notebook with the supplied CSV in its working directory, or upload the CSV when prompted in Colab. The ZIP intentionally contains the notebook and DOCX required by the brief. The notebook exports pipeline_results.json when run.

Model fitting and code run successfully; this is not a guarantee of marks or real-world deployment suitability. The historical holdout has been reused during revision. A later unseen cohort is needed for independent validation.
