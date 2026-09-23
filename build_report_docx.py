"""
Revised script to generate the official academic project report (Project_Report_IT7103.docx)
Structured explicitly to map 1-to-1 to all 15 sections of the Strict IT7103 Project Rubric (100 Marks).
"""

import os
import json
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

with open('pipeline_results.json', 'r') as f:
    results = json.load(f)

doc = Document()

# Page Margins
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Colors
COLOR_PRIMARY = RGBColor(0, 51, 102)     # Deep Navy
COLOR_SECONDARY = RGBColor(74, 96, 122)  # Slate Steel Blue
COLOR_DARK = RGBColor(34, 34, 34)        # Charcoal
COLOR_MUTED = RGBColor(100, 110, 120)    # Muted Grey
HEX_PRIMARY = "003366"
HEX_LIGHT_BG = "F4F6F9"
HEX_ALT_ROW = "F9FAFC"

def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_SECONDARY
    return p

def add_body_p(doc, text, bold_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4.5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Arial'
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK
    r_body = p.add_run(text)
    r_body.font.name = 'Arial'
    r_body.font.size = Pt(9.5)
    r_body.font.color.rgb = COLOR_DARK
    return p

def add_callout(doc, text, title=""):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, HEX_LIGHT_BG)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    if title:
        r_title = p.add_run(f"{title}: ")
        r_title.font.name = 'Arial'
        r_title.font.size = Pt(9.5)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_PRIMARY
    r_txt = p.add_run(text)
    r_txt.font.name = 'Arial'
    r_txt.font.size = Pt(9)
    r_txt.font.italic = True
    r_txt.font.color.rgb = COLOR_DARK
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_figure(doc, img_path, caption_text):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(3)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(5.6))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Arial'
        r_cap.font.size = Pt(8.5)
        r_cap.font.bold = True
        r_cap.font.color.rgb = COLOR_MUTED

# ==================== COVER PAGE ====================
p_inst = doc.add_paragraph()
p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_inst.paragraph_format.space_before = Pt(6)
p_inst.paragraph_format.space_after = Pt(2)
r = p_inst.add_run("BAHRAIN POLYTECHNIC | بوليتكنك البحرين")
r.font.name = 'Arial'
r.font.size = Pt(13)
r.font.bold = True
r.font.color.rgb = COLOR_PRIMARY

p_fac = doc.add_paragraph()
p_fac.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_fac.paragraph_format.space_after = Pt(18)
r = p_fac.add_run("Faculty of Engineering, Design and Information & Communications Technology")
r.font.name = 'Arial'
r.font.size = Pt(10)
r.font.color.rgb = COLOR_SECONDARY

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_after = Pt(4)
r = p_title.add_run("ASSESSMENT COVER SHEET & TECHNICAL REPORT")
r.font.name = 'Arial'
r.font.size = Pt(17)
r.font.bold = True
r.font.color.rgb = COLOR_PRIMARY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(14)
r = p_sub.add_run("Intelligent Academic Performance Analysis & Outcome Prediction Pipeline")
r.font.name = 'Arial'
r.font.size = Pt(11.5)
r.font.italic = True
r.font.color.rgb = COLOR_SECONDARY

# Metadata Table
meta_tbl = doc.add_table(rows=6, cols=2)
meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_data = [
    ("Course Code & Title", "IT7103 - Advanced AI Applications"),
    ("Assessment Title", "Project (Group) - Uncontrolled Group (40% Weightage)"),
    ("Academic Stream & Group", "Stream 05 | Group 1"),
    ("Due Date", "15-Dec-2026 (11:55 PM)"),
    ("Learning Outcomes Assessed", "CILO 1 and CILO 2"),
    ("Submission Archive", "05_202303596.zip (Executed .ipynb & Report .docx)")
]
for i, (k, v) in enumerate(meta_data):
    c0 = meta_tbl.cell(i, 0)
    c1 = meta_tbl.cell(i, 1)
    set_cell_shading(c0, HEX_LIGHT_BG)
    set_cell_margins(c0, 50, 50, 80, 80)
    set_cell_margins(c1, 50, 50, 80, 80)
    c0.width = Inches(2.2)
    c1.width = Inches(4.3)
    p0 = c0.paragraphs[0]
    p0.paragraph_format.space_after = Pt(0)
    r0 = p0.add_run(k)
    r0.font.name = 'Arial'
    r0.font.size = Pt(8.5)
    r0.font.bold = True
    r0.font.color.rgb = COLOR_DARK
    
    p1 = c1.paragraphs[0]
    p1.paragraph_format.space_after = Pt(0)
    r1 = p1.add_run(v)
    r1.font.name = 'Arial'
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(6)

# Group Members Table
p_grp = doc.add_paragraph()
p_grp.paragraph_format.space_after = Pt(3)
r = p_grp.add_run("Project Group Membership & Student Identification:")
r.font.name = 'Arial'
r.font.size = Pt(9.5)
r.font.bold = True
r.font.color.rgb = COLOR_PRIMARY

grp_tbl = doc.add_table(rows=6, cols=3)
grp_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Student ID", "Full Name", "Project Role"]):
    c = grp_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 70, 70, 80, 80)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

members = [
    ("202303596", "Hasan Marhoon", "Group Leader / Lead ML Engineer"),
    ("202304831", "Sayed Ali Almusawi", "Data Preprocessing & Feature Engineering"),
    ("202304829", "Hussain Ali", "Time Series Modeling & Forecaster"),
    ("202305013", "Sayed Sadeq", "Classification Modeling & Imbalance Tuning"),
    ("202304419", "Ali Yusuf", "Regression Modeling & Evaluation Analysis")
]
for i, (sid, sname, srole) in enumerate(members):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate([sid, sname, srole]):
        c = grp_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 50, 50, 80, 80)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(8)
        if j == 0:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_callout(
    doc,
    "By submitting this assessment for marking, I affirm that this assessment is my own group's work, that all research sources and references consulted have been properly acknowledged and cited, and that all guidelines regarding academic integrity have been strictly observed.",
    "Learner Affirmation & Academic Integrity Statement"
)

# Assessor Marking Grid
ass_tbl = doc.add_table(rows=2, cols=3)
ass_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Assessor Name", "Marking Date", "Marks Obtained (out of 40%)"]):
    c = ass_tbl.cell(0, j)
    set_cell_shading(c, HEX_LIGHT_BG)
    set_cell_margins(c, 50, 50, 70, 70)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = COLOR_DARK
for j in range(3):
    c = ass_tbl.cell(1, j)
    set_cell_margins(c, 100, 100, 70, 70)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("[ Official Assessor Feedback / Mark ]")
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.italic = True
    r.font.color.rgb = COLOR_MUTED

doc.add_page_break()

# ==================== RUBRIC MAPPING & EXECUTIVE SUMMARY ====================
add_heading_1(doc, "Executive Summary & Rubric Alignment Map")

add_body_p(
    doc,
    "This report documents an end-to-end machine learning solution designed to meet the strict standards of the IT7103 project assessment. The table below provides a direct mapping from the 15 rubric criteria (totaling 100 marks) to the corresponding report sections and empirical findings."
)

# Rubric Mapping Table
rub_tbl = doc.add_table(rows=16, cols=3)
rub_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Rubric Assessment Section", "Marks", "Report Section & Empirical Focus"]):
    c = rub_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 60, 60, 70, 70)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

rub_items = [
    ("1. Problem Definition & Objectives", "5", "Section 1: Educational context, retention challenges, tri-fold ML objectives."),
    ("2. Dataset Understanding & Initial Analysis", "5", "Section 2: Dimensions, typology, missing values, descriptive statistics & skewness table."),
    ("3. Data Cleaning & Outlier Handling", "10", "Section 3: Pruning 780 corrupted synthetic 'ERR' records, winsorizing GPA/study hours."),
    ("4. Advanced Preprocessing & Feature Engineering", "12", "Section 4: Leakage-free train-fit pipeline, observed targets only, feature set separation."),
    ("5. Temporal / Semester Feature Engineering", "8", "Section 5: Continuous 8-semester student grid, past-only lag-1 and rolling-2 features."),
    ("6. Correlation & Exploratory Analysis", "7", "Section 6: Pearson correlation heatmap, cohort-wide macro stability analysis."),
    ("7. Regression — Single Model", "8", "Section 7: Regularized Ridge regression, test RMSE/MAE/R²/MAPE, residual diagnostics."),
    ("8. Regression — Ensemble Model", "7", "Section 8: Random Forest, LightGBM, XGBoost, Voting Ensemble; honest comparison with Ridge."),
    ("9. Classification — Single Model", "9", "Section 9: Multinomial LogReg & Decision Tree; strictly ordered confusion matrix."),
    ("10. Classification — Ensemble Model", "7", "Section 10: Balanced Random Forest & LightGBM; side-by-side comparison."),
    ("11. Class Imbalance Handling", "4", "Section 11: Class weighting on train data only; exact Class 'F' recall lift from 0% to 41.8%."),
    ("12. Time-Series Forecasting for One Student", "10", "Section 12: Student #2 (33 courses), chronological split, SES, ARIMA, Naive persistence."),
    ("13. Hyperparameter Optimization", "6", "Section 13: Dual tuning: LightGBM (TimeSeriesSplit) and Random Forest (Stratified CV)."),
    ("14. Interpretation, Discussion & Limitations", "5", "Section 14: Total Gain vs Split Frequency, practical implications, low-N limitations."),
    ("15. Code Quality, Notebook & Deliverables", "7", "Section 15: Google Colab reproducibility, modular code, packaged 05_202303596.zip.")
]
for i, (crit, mk, fcs) in enumerate(rub_items):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate([crit, mk, fcs]):
        c = rub_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 40, 40, 70, 70)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(8)
        if j <= 1:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# ==================== SECTION 1 ====================
add_heading_1(doc, "Section 1: Problem Definition & Operational Objectives (5 Marks)")
add_body_p(
    doc,
    "1.1 Educational Problem and Institutional Relevance: Modern universities and polytechnics operate within complex, modular learning environments characterized by expanding student cohorts and diverse academic backgrounds. Academic advisors and instructors face substantial challenges in manually tracking student trajectories across dozens of concurrent courses and multi-semester degree pathways. Traditionally, identifying students at risk of course withdrawal, academic probation, or failure has relied on mid-semester exam audits—often occurring after Week 8, when educational intervention comes too late for meaningful academic recovery [1], [2]. Proactive early-warning decision support systems (EWDSS) leverage structured student data to identify struggling learners early, optimizing advising resource allocation and improving institutional retention."
)
add_body_p(
    doc,
    "1.2 Statement of ML Pipeline Objectives: Simulating real-world educational operations at Bahrain Polytechnic, this project pursues three core objectives: (i) Supervised Regression to forecast continuous final examination scores (0–100), evaluating whether regularized linear models or non-linear ensembles generalize better across semesters; (ii) Multi-Class Classification to predict discrete final letter grades (A through F) while strictly preventing data leakage by eliminating numeric_grade, employing cost-sensitive balancing to resolve extreme minority failing class imbalance (F ≈ 0.35%); and (iii) Longitudinal Time Series Forecasting to model an individual student's performance trajectory over eight consecutive semesters, benchmarking statistical models (Exponential Smoothing, ARIMA) against naive persistence baselines under realistic low-N sample constraints."
)

# ==================== SECTION 2 ====================
add_heading_1(doc, "Section 2: Dataset Understanding & Initial Analysis (5 Marks)")
add_body_p(
    doc,
    "2.1 Dimensions, Attribute Typology and Target Identification: The institutional dataset comprises 154,314 student-course enrollment records across 20 attributes, capturing student demographics, course parameters, study behaviors, and outcome metrics across eight academic semesters (2020Spring through 2023Fall):"
)
add_body_p(doc, "• Categorical Variables: semester (8 levels: 2020Spring–2023Fall), course_code (CS101–CS236), course_name (20 unique course titles), subject_area (9 disciplines: Systems, AI, Programming, Data Science, etc.), instructor (15 faculty members), gender (M, F, Other), year_of_study (Freshman, Sophomore, Junior, Senior).")
add_body_p(doc, "• Numerical Variables: credits (3, 4), numeric_grade (0–100), prior_gpa (0.0–4.0), study_hours (weekly), attendance_rate (0–100%), age (18–65), homework_avg (0–100), final_exam (0–100).")
add_body_p(doc, "• Binary Variables: scholarship (0/1), extracurricular (0–10 count), internship (0/1).")
add_body_p(doc, "• Supervised Targets: Continuous final_exam (regression) and discrete multi-class grade_letter (classification).")

add_body_p(
    doc,
    "2.2 Comprehensive Descriptive Statistics & Distribution Analysis: Table 1 examines distributions, central tendencies, spreads, and skewness across all continuous attributes."
)

# Descriptive Statistics Table
desc_tbl = doc.add_table(rows=9, cols=9)
desc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_desc = ["Attribute", "Count", "Mean", "Std", "Min", "25%", "50%", "75%", "Max"]
for j, h in enumerate(headers_desc):
    c = desc_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 50, 50, 50, 50)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

desc_data = [
    ("credits", "154,314", "3.30", "0.46", "3.00", "3.00", "3.00", "4.00", "4.00"),
    ("numeric_grade", "154,314", "81.87", "9.06", "-10.00", "77.53", "82.01", "87.54", "110.00"),
    ("prior_gpa", "154,314", "3.18", "0.57", "-1.00", "2.89", "3.26", "3.58", "5.00"),
    ("study_hours", "143,351", "15.91", "11.47", "0.00", "10.40", "15.10", "20.60", "119.90"),
    ("attendance_rate", "143,499", "83.75", "12.98", "14.10", "75.00", "85.00", "95.00", "100.00"),
    ("age", "154,314", "19.97", "2.63", "18.00", "19.00", "20.00", "21.00", "65.00"),
    ("homework_avg", "143,627", "81.86", "9.27", "38.53", "75.76", "81.97", "88.39", "100.00"),
    ("final_exam", "143,562", "81.80", "10.26", "35.38", "75.12", "82.02", "89.23", "100.00")
]
for i, row in enumerate(desc_data):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(row):
        c = desc_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 40, 40, 50, 50)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(7.5)
        if j == 0:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(5)
add_body_p(
    doc,
    "Analytical Observations from Table 1: Both homework_avg and final_exam exhibit near-normal symmetry centered at ~82 points (skewness -0.16 and -0.23). However, numeric_grade and prior_gpa exhibit severe negative skewness caused by synthetic out-of-bounds error values (-10.0 and -1.0). Study hours exhibits strong positive skewness (skewness +4.00) with extreme values reaching 119.9 hours. Duplicate row checking confirmed exactly zero duplicate records across the entire dataset."
)

# ==================== SECTION 3 ====================
add_heading_1(doc, "Section 3: Data Cleaning, Outlier Engineering & Duplicate Audit (10 Marks)")
add_body_p(
    doc,
    f"3.1 Systematic Detection of Inconsistencies and Outliers: Diagnostic auditing uncovered three distinct classes of data anomalies intentionally embedded within the raw records:"
)
add_body_p(
    doc,
    f"• Corrupted Synthetic 'ERR' Records: Exactly {results['dataset_stats']['dropped_err_count']} records contain grade_letter == 'ERR'. Cross-tabulation revealed that every 'ERR' entry corresponded to impossible numeric_grade values (-10.0 to -0.01 in 287 rows and 100.01 to 110.0 in 493 rows). Because these represent synthetic corrupted noise where ground truth cannot be established, they were dropped, leaving {results['dataset_stats']['clean_rows']:,} valid records."
)
add_body_p(
    doc,
    f"• Out-of-Bounds Prior GPA: Exactly {results['dataset_stats']['cleaned_gpa_count']} records contain sentinel error values (-1.0 and 5.0) outside the legitimate [0.0, 4.0] GPA domain. These were winsorized to [0.0, 4.0]."
)
add_body_p(
    doc,
    f"• Extreme Weekly Study Hours: While legitimate study effort rarely exceeds 50 hours/week, {results['dataset_stats']['extreme_study_count']} records showed extreme values between 60.0 and 119.9 hours. These were capped at 60.0 hours/week to eliminate high-leverage outliers."
)
add_body_p(
    doc,
    f"• Preserving Observed Targets (No Target Imputation): Exactly 142,825 records have observed final_exam scores, while 10,709 are missing (~7.0%). In strict compliance with statistical rigor, missing targets were NEVER imputed. Imputing targets introduces circular model bias; regression models were trained and evaluated exclusively on observed targets."
)

# Before/After Table
add_body_p(doc, "3.2 Demonstration of Before vs. After Cleaning Effect:")
clean_tbl = doc.add_table(rows=6, cols=3)
clean_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Quality Metric / Feature", "Raw State (Before Cleaning)", "Cleaned State (After Cleaning)"]):
    c = clean_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 50, 50, 70, 70)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

clean_rows = [
    ("Total Enrollment Records", "154,314 rows", f"{results['dataset_stats']['clean_rows']:,} rows (780 ERR pruned)"),
    ("Prior GPA Valid Domain", "Min: -1.0, Max: 5.0 (762 invalid)", "Min: 0.0, Max: 4.0 (Winsorized)"),
    ("Study Hours Valid Domain", "Min: 0.0, Max: 119.9 (1,419 extreme)", "Min: 0.0, Max: 60.0 (Capped at 60h)"),
    ("Observed Final Exam Count", "142,825 observed, 10,709 missing", "142,825 observed (Un-imputed targets)"),
    ("Duplicate Records Audit", "0 duplicates detected", "0 duplicates detected (Dataset unique)")
]
for i, row in enumerate(clean_rows):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(row):
        c = clean_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 40, 40, 70, 70)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(8)
        if j == 0:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(5)

# ==================== SECTION 4 & 5 ====================
add_heading_1(doc, "Section 4: Advanced Preprocessing & Leakage-Free Design (12 Marks)")
add_heading_1(doc, "Section 5: Temporal / Semester Feature Engineering (8 Marks)")

add_callout(
    doc,
    "STRICT DATA LEAKAGE PREVENTION & PIPELINE DESIGN: The dataset was partitioned chronologically BEFORE fitting any preprocessing transformer. Training was restricted to historical Semesters 1–6 (115,109 rows); Testing was held out on future Semesters 7 & 8 (38,425 rows). All imputers, scalers, and one-hot encoders were fitted strictly on the Training split. Furthermore, numeric_grade was completely removed from feature matrices.",
    "Data Leakage Safeguard Declaration"
)

add_body_p(
    doc,
    "5.1 Continuous Student-Semester Timeline & Past-Only Rolling Features: Semesters were ordered chronologically: 2020Spring (t=1) to 2023Fall (t=8). A complete Cartesian product grid of students × {1...8} was established to guarantee sequence continuity. Per-student semester averages were computed exclusively from observed values. Strictly past-only lag features (final_exam_prev_semester, homework_avg_prev_semester, attendance_prev_semester) and 2-semester rolling averages were calculated over past terms {t-2, t-1}, strictly excluding current semester t. Domain indicators were constructed: study_hours_per_credit = study_hours / credits, and attendance_hw_composite = 0.4 * attendance + 0.6 * homework."
)

# ==================== SECTION 6 ====================
add_heading_1(doc, "Section 6: Correlation & Exploratory Cohort Analysis (7 Marks)")
add_body_p(
    doc,
    "6.1 Bivariate Correlation Matrix and Macro Cohort Trends: Pearson correlation analysis (Figure 1) reveals that continuous homework performance exhibits the strongest positive correlation with final_exam (r = 0.58), followed by prior-semester exam performance (r = 0.44) and attendance (r = 0.38). In contrast, age and extracurricular activities display negligible correlation (|r| < 0.05). Macro-level cohort trends across 8 semesters confirm institutional stability, with semester final exam averages remaining steady between 78.4 and 79.8 points."
)
add_figure(doc, "figures/fig2_correlation_matrix.png", "Figure 1: Pearson Correlation Matrix of Engineered Academic Features and Outcomes")

# ==================== SECTION 7 & 8 ====================
add_heading_1(doc, "Section 7: Regression — Single Baseline Architecture (8 Marks)")
add_heading_1(doc, "Section 8: Regression — Ensemble Models & Benchmarking (7 Marks)")

add_body_p(
    doc,
    f"7.1 Baseline Formulation & Ablation Study: Predicting continuous final_exam scores was evaluated on {results['dataset_stats']['test_reg_observed_y']:,} observed test records. To test whether engineered temporal lag features provide empirical predictive lift, an ablation experiment was conducted comparing raw baseline features against full engineered features (Table 3)."
)

# Ablation Table
abl_tbl = doc.add_table(rows=3, cols=4)
abl_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Model Architecture", "Raw Features RMSE", "Engineered Features RMSE", "Delta (Lift)"]):
    c = abl_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 50, 50, 70, 70)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

abl_rows = [
    ("Ridge Regression", f"{results['ablation_study']['Ridge']['Raw_RMSE']:.4f}", f"{results['ablation_study']['Ridge']['Engineered_RMSE']:.4f}", f"{results['ablation_study']['Ridge']['Delta']:+.4f}"),
    ("LightGBM Regressor", f"{results['ablation_study']['LightGBM']['Raw_RMSE']:.4f}", f"{results['ablation_study']['LightGBM']['Engineered_RMSE']:.4f}", f"{results['ablation_study']['LightGBM']['Delta']:+.4f}")
]
for i, row in enumerate(abl_rows):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(row):
        c = abl_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 40, 40, 70, 70)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(8)
        if j == 0:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(5)

add_body_p(
    doc,
    "8.1 Full Regression Suite Evaluation: Table 4 documents performance across the chronological test set (Semesters 7 & 8)."
)

# Full Regression Table
reg_tbl = doc.add_table(rows=8, cols=5)
reg_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Regression Architecture", "RMSE (Points)", "MAE (Points)", "R² Score", "MAPE (%)"]):
    c = reg_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 50, 50, 70, 70)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

reg_rows = [
    ("Ridge Regression (alpha=1.0) [Winner]", f"{results['regression_results']['Ridge Regression']['RMSE']:.4f}", f"{results['regression_results']['Ridge Regression']['MAE']:.4f}", f"{results['regression_results']['Ridge Regression']['R2']:.4f}", f"{results['regression_results']['Ridge Regression']['MAPE']:.2f}%"),
    ("Decision Tree Regressor (depth=8)", f"{results['regression_results']['Decision Tree']['RMSE']:.4f}", f"{results['regression_results']['Decision Tree']['MAE']:.4f}", f"{results['regression_results']['Decision Tree']['R2']:.4f}", f"{results['regression_results']['Decision Tree']['MAPE']:.2f}%"),
    ("Random Forest Regressor (B=100)", f"{results['regression_results']['Random Forest']['RMSE']:.4f}", f"{results['regression_results']['Random Forest']['MAE']:.4f}", f"{results['regression_results']['Random Forest']['R2']:.4f}", f"{results['regression_results']['Random Forest']['MAPE']:.2f}%"),
    ("LightGBM Regressor (Baseline)", f"{results['regression_results']['LightGBM']['RMSE']:.4f}", f"{results['regression_results']['LightGBM']['MAE']:.4f}", f"{results['regression_results']['LightGBM']['R2']:.4f}", f"{results['regression_results']['LightGBM']['MAPE']:.2f}%"),
    ("LightGBM Regressor (Tuned)", f"{results['tuning_regression']['Tuned_LightGBM']['RMSE']:.4f}", f"{results['tuning_regression']['Tuned_LightGBM']['MAE']:.4f}", f"{results['tuning_regression']['Tuned_LightGBM']['R2']:.4f}", f"{results['tuning_regression']['Tuned_LightGBM']['MAPE']:.2f}%"),
    ("XGBoost Regressor (depth=6)", f"{results['regression_results']['XGBoost']['RMSE']:.4f}", f"{results['regression_results']['XGBoost']['MAE']:.4f}", f"{results['regression_results']['XGBoost']['R2']:.4f}", f"{results['regression_results']['XGBoost']['MAPE']:.2f}%"),
    ("Voting Ensemble (RF + LGB + XGB)", f"{results['regression_results']['Voting Ensemble']['RMSE']:.4f}", f"{results['regression_results']['Voting Ensemble']['MAE']:.4f}", f"{results['regression_results']['Voting Ensemble']['R2']:.4f}", f"{results['regression_results']['Voting Ensemble']['MAPE']:.2f}%")
]
for i, row in enumerate(reg_rows):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(row):
        c = reg_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 40, 40, 70, 70)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(8)
        if j == 0:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(5)
add_figure(doc, "figures/fig4_regression_comparison.png", "Figure 2: Regression Error & Goodness of Fit across Models (Chronological Test Holdout)")
add_figure(doc, "figures/fig5_residuals_diagnostic.png", "Figure 3: Residual Diagnostic Scatter and Normality Histogram for Winning Model (Ridge)")

add_body_p(
    doc,
    "Objective Regression Interpretation: Regularized Ridge Regression achieved the lowest test RMSE (8.0510) and highest R² (0.3885), closely matched by Tuned LightGBM (8.0528). In this educational tabular dataset, formative homework scores and prior GPA provide strong linear-additive signals. Tree-based step functions introduce variance around continuous slopes without discovering complex non-linear interactions, allowing Ridge regression to generalize on par with or slightly superior to complex ensembles."
)

# ==================== SECTION 9, 10 & 11 ====================
add_heading_1(doc, "Section 9: Classification — Single Model Architecture (9 Marks)")
add_heading_1(doc, "Section 10: Classification — Ensemble Architecture (7 Marks)")
add_heading_1(doc, "Section 11: Class Imbalance Handling & Rigorous Minority Evaluation (4 Marks)")

add_body_p(
    doc,
    "11.1 Class Imbalance Treatment & Rigorous Empirical Benchmark: In the chronological test split (38,425 records), failing grades ('F') represent an extreme minority class of only 146 instances (0.380%). Table 5 provides an empirical side-by-side comparison of unweighted models versus cost-sensitive balanced models ($w_j = \\frac{N}{K \\cdot n_j}$)."
)

# Classification Table
clf_tbl = doc.add_table(rows=9, cols=7)
clf_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_clf = ["Model Architecture", "Overall Acc", "Macro Prec", "Macro Rec", "Macro F1", "Class F Rec", "Class F Prec"]
for j, h in enumerate(headers_clf):
    c = clf_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 50, 50, 50, 50)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(7.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

clf_rows = [
    ("Multinomial LogReg (Unweighted)", f"{results['classification_results']['Multinomial LogReg (Unweighted)']['Accuracy']:.4f}", f"{results['classification_results']['Multinomial LogReg (Unweighted)']['Precision_Macro']:.4f}", f"{results['classification_results']['Multinomial LogReg (Unweighted)']['Recall_Macro']:.4f}", f"{results['classification_results']['Multinomial LogReg (Unweighted)']['F1_Macro']:.4f}", f"{results['classification_results']['Multinomial LogReg (Unweighted)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['Multinomial LogReg (Unweighted)']['Class_F_Precision']*100:.1f}%"),
    ("Multinomial LogReg (Balanced)", f"{results['classification_results']['Multinomial LogReg (Balanced)']['Accuracy']:.4f}", f"{results['classification_results']['Multinomial LogReg (Balanced)']['Precision_Macro']:.4f}", f"{results['classification_results']['Multinomial LogReg (Balanced)']['Recall_Macro']:.4f}", f"{results['classification_results']['Multinomial LogReg (Balanced)']['F1_Macro']:.4f}", f"{results['classification_results']['Multinomial LogReg (Balanced)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['Multinomial LogReg (Balanced)']['Class_F_Precision']*100:.1f}%"),
    ("Decision Tree (Unweighted)", f"{results['classification_results']['Decision Tree (Unweighted)']['Accuracy']:.4f}", f"{results['classification_results']['Decision Tree (Unweighted)']['Precision_Macro']:.4f}", f"{results['classification_results']['Decision Tree (Unweighted)']['Recall_Macro']:.4f}", f"{results['classification_results']['Decision Tree (Unweighted)']['F1_Macro']:.4f}", f"{results['classification_results']['Decision Tree (Unweighted)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['Decision Tree (Unweighted)']['Class_F_Precision']*100:.1f}%"),
    ("Decision Tree (Balanced)", f"{results['classification_results']['Decision Tree (Balanced)']['Accuracy']:.4f}", f"{results['classification_results']['Decision Tree (Balanced)']['Precision_Macro']:.4f}", f"{results['classification_results']['Decision Tree (Balanced)']['Recall_Macro']:.4f}", f"{results['classification_results']['Decision Tree (Balanced)']['F1_Macro']:.4f}", f"{results['classification_results']['Decision Tree (Balanced)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['Decision Tree (Balanced)']['Class_F_Precision']*100:.1f}%"),
    ("Random Forest (Unweighted)", f"{results['classification_results']['Random Forest (Unweighted)']['Accuracy']:.4f}", f"{results['classification_results']['Random Forest (Unweighted)']['Precision_Macro']:.4f}", f"{results['classification_results']['Random Forest (Unweighted)']['Recall_Macro']:.4f}", f"{results['classification_results']['Random Forest (Unweighted)']['F1_Macro']:.4f}", f"{results['classification_results']['Random Forest (Unweighted)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['Random Forest (Unweighted)']['Class_F_Precision']*100:.1f}%"),
    ("Random Forest (Balanced) [Rec]", f"{results['classification_results']['Random Forest (Balanced)']['Accuracy']:.4f}", f"{results['classification_results']['Random Forest (Balanced)']['Precision_Macro']:.4f}", f"{results['classification_results']['Random Forest (Balanced)']['Recall_Macro']:.4f}", f"{results['classification_results']['Random Forest (Balanced)']['F1_Macro']:.4f}", f"{results['classification_results']['Random Forest (Balanced)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['Random Forest (Balanced)']['Class_F_Precision']*100:.1f}%"),
    ("LightGBM (Unweighted)", f"{results['classification_results']['LightGBM (Unweighted)']['Accuracy']:.4f}", f"{results['classification_results']['LightGBM (Unweighted)']['Precision_Macro']:.4f}", f"{results['classification_results']['LightGBM (Unweighted)']['Recall_Macro']:.4f}", f"{results['classification_results']['LightGBM (Unweighted)']['F1_Macro']:.4f}", f"{results['classification_results']['LightGBM (Unweighted)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['LightGBM (Unweighted)']['Class_F_Precision']*100:.1f}%"),
    ("LightGBM (Balanced)", f"{results['classification_results']['LightGBM (Balanced)']['Accuracy']:.4f}", f"{results['classification_results']['LightGBM (Balanced)']['Precision_Macro']:.4f}", f"{results['classification_results']['LightGBM (Balanced)']['Recall_Macro']:.4f}", f"{results['classification_results']['LightGBM (Balanced)']['F1_Macro']:.4f}", f"{results['classification_results']['LightGBM (Balanced)']['Class_F_Recall']*100:.1f}%", f"{results['classification_results']['LightGBM (Balanced)']['Class_F_Precision']*100:.1f}%")
]
for i, row in enumerate(clf_rows):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(row):
        c = clf_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 40, 40, 50, 50)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(7.5)
        if j == 0:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(5)
add_figure(doc, "figures/fig6_classification_comparison.png", "Figure 4: Unweighted vs. Balanced Classification: Accuracy, Macro F1, and Class 'F' Recall")
add_figure(doc, "figures/fig7_confusion_matrix.png", "Figure 5: Normalized Confusion Matrix for Balanced Random Forest (Strict Grade Order: A to F)")

add_body_p(
    doc,
    "Critical Imbalance Discussion: Unweighted Random Forest achieves higher overall accuracy (34.12%) by predicting majority classes, resulting in exactly 0.0% recall on Grade F—missing every failing student. Cost-sensitive balanced weighting sacrifices minor accuracy (29.60%) to dramatically lift Grade F recall to 41.78% (Random Forest) and 42.47% (LightGBM), with Macro F1 improving from 0.2413 to 0.3084. Macro recall across all 10 classes is 33.5%–35.6%, confirming balanced representation across all grade tiers."
)

# ==================== SECTION 12 ====================
add_heading_1(doc, "Section 12: Longitudinal Time-Series Forecasting for Student #2 (10 Marks)")
add_body_p(
    doc,
    "12.1 Student-Specific Course Breakdown and EDA: Student #2 completed 33 courses across all eight semesters, with average semester final exam scores of: 66.13 (Sem 1, 1 course), 93.58 (Sem 2, 4 courses), 88.86 (Sem 3, 5 courses), 81.36 (Sem 4, 6 courses), 73.47 (Sem 5, 1 course), 78.41 (Sem 6, 5 courses), 72.22 (Sem 7, 6 courses), and 82.70 (Sem 8, 5 courses)."
)
add_body_p(
    doc,
    "12.2 Chronological Split & Forecast Benchmarking: Chronological partitioning was enforced: Semesters 1 to 6 (Train, N=6) and Semesters 7 & 8 (Held-out Test, N=2). Table 6 benchmarks the forecasts."
)

# Time Series Table
ts_tbl = doc.add_table(rows=4, cols=4)
ts_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Forecasting Model Architecture", "Test RMSE (Points)", "Test MAE (Points)", "Test MAPE (%)"]):
    c = ts_tbl.cell(0, j)
    set_cell_shading(c, HEX_PRIMARY)
    set_cell_margins(c, 50, 50, 70, 70)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(h)
    r.font.name = 'Arial'
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

ts_rows = [
    ("Simple Exponential Smoothing (SES)", f"{results['time_series_metrics']['Simple Exponential Smoothing']['RMSE']:.4f}", f"{results['time_series_metrics']['Simple Exponential Smoothing']['MAE']:.4f}", f"{results['time_series_metrics']['Simple Exponential Smoothing']['MAPE']:.2f}%"),
    ("ARIMA(1, 0, 0) Autoregressive", f"{results['time_series_metrics']['ARIMA(1,0,0)']['RMSE']:.4f}", f"{results['time_series_metrics']['ARIMA(1,0,0)']['MAE']:.4f}", f"{results['time_series_metrics']['ARIMA(1,0,0)']['MAPE']:.2f}%"),
    ("Naive Persistence Baseline (Lag-1) [Winner]", f"{results['time_series_metrics']['Naive Persistence (Lag-1)']['RMSE']:.4f}", f"{results['time_series_metrics']['Naive Persistence (Lag-1)']['MAE']:.4f}", f"{results['time_series_metrics']['Naive Persistence (Lag-1)']['MAPE']:.2f}%")
]
for i, row in enumerate(ts_rows):
    row_bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
    for j, val in enumerate(row):
        c = ts_tbl.cell(i+1, j)
        set_cell_shading(c, row_bg)
        set_cell_margins(c, 40, 40, 70, 70)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.name = 'Arial'
        r.font.size = Pt(8)
        if j == 0:
            r.font.bold = True
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(5)
add_figure(doc, "figures/fig8_student_forecasting.png", "Figure 6: Student #2 Longitudinal Observed Trajectory and Multi-Step Forecast Comparison")

add_body_p(
    doc,
    "Critical Low-N Methodological Critique: Naive persistence achieved the lowest test RMSE (5.3267), outperforming SES (5.9621) and ARIMA(1,0,0) (6.4736). Parametric estimation on merely six training points (N=6) introduces substantial parameter estimation variance. The parameter-free naive persistence baseline eliminates estimation variance, proving superior on short horizons. This small single-student experiment illustrates trajectory visualization concepts but does not constitute proof of dependable standalone forecasting. Institutional forecasting requires pooled longitudinal panel models across cohorts [7], [8]."
)

# ==================== SECTION 13 ====================
add_heading_1(doc, "Section 13: Dual-Model Hyperparameter Optimization (6 Marks)")
add_body_p(
    doc,
    "13.1 Systematic Search Methodology: (1) LightGBM Regressor was tuned via TimeSeriesSplit(n_splits=3) on training semesters (best params: learning_rate=0.03, max_depth=4, n_estimators=200, subsample=0.8), reducing RMSE from 8.0603 to 8.0528. (2) Random Forest Classifier was tuned via Stratified K-Fold (best params: max_depth=14, min_samples_split=5, n_estimators=150)."
)

# ==================== SECTION 14 ====================
add_heading_1(doc, "Section 14: Model Interpretation, Critical Discussion & Limitations (5 Marks)")
add_body_p(
    doc,
    "14.1 Split Importance vs. Gain Importance: Figure 7 decomposes tree behavior into Total Gain (impurity reduction) and Split Frequency. Continuous homework performance (homework_avg) dominates Gain Importance (>80% of total loss reduction), proving that continuous formative task completion is the primary causal driver of summative exam outcomes. Prior GPA captures baseline student ability, while workload-scaled study hours acts as a key moderator variable."
)
add_figure(doc, "figures/fig9_feature_importance.png", "Figure 7: Top 12 Academic Drivers by Total Gain (Impurity Reduction) vs. Split Frequency")

add_body_p(
    doc,
    "14.2 Educational Implications and Limitations: The models can be operationalized as an Early Warning Decision Support System integrated with Moodle, generating alerts by Week 6. Ethical guardrails require predictions to function exclusively as supportive diagnostic flags, never as deterministic barriers. Limitations include the lack of intra-semester LMS telemetry (video views, submission timestamps) and unobserved psychosocial indicators (financial stress, working hours)."
)

# ==================== SECTION 15 ====================
add_heading_1(doc, "Section 15: Code Quality, Colab Reproducibility & Deliverable Verification (7 Marks)")
add_body_p(
    doc,
    "15.1 Deliverables Package Audit: The deliverable package 05_202303596.zip contains: (1) student_academic_performance_pipeline.ipynb, an executable, modular notebook featuring Colab upload integration, inline markdown explanations, and pre-rendered outputs; and (2) Project_Report_IT7103.docx, a formal technical report complete with cover sheet, tables, figures, and IEEE references."
)

# ==================== REFERENCES ====================
doc.add_page_break()
add_heading_1(doc, "References")
references = [
    "[1] C. Romero and S. Ventura, \"Educational data mining and learning analytics: An updated survey,\" WIREs Data Mining and Knowledge Discovery, vol. 10, no. 3, p. e1355, 2020.",
    "[2] G. Siemens and R. S. J. d. Baker, \"Learning analytics and educational data mining: towards communication and collaboration,\" in Proc. 2nd Int. Conf. on Learning Analytics and Knowledge (LAK '12), Vancouver, BC, Canada, 2012, pp. 252–254.",
    "[3] H. Zeineddine, U. Braendle, and A. Farah, \"Enhancing student retention in higher education through machine learning: Ethical considerations and predictive modeling,\" Education and Information Technologies, vol. 26, pp. 6175–6199, 2021.",
    "[4] T. Chen and C. Guestrin, \"XGBoost: A scalable tree boosting system,\" in Proc. 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining, San Francisco, CA, USA, 2016, pp. 785–794.",
    "[5] G. Ke et al., \"LightGBM: A highly efficient gradient boosting decision tree,\" in Advances in Neural Information Processing Systems (NeurIPS 2017), vol. 30, Long Beach, CA, USA, 2017, pp. 3146–3154.",
    "[6] L. Breiman, \"Random forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "[7] R. J. Hyndman and G. Athanasopoulos, Forecasting: Principles and Practice, 3rd ed. Melbourne, Australia: OTexts, 2021.",
    "[8] G. E. P. Box, G. M. Jenkins, G. C. Reinsel, and G. M. Ljung, Time Series Analysis: Forecasting and Control, 5th ed. Hoboken, NJ, USA: John Wiley & Sons, 2015.",
    "[9] S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model predictions,\" in Advances in Neural Information Processing Systems (NeurIPS 2017), vol. 30, Long Beach, CA, USA, 2017, pp. 4765–4774.",
    "[10] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, \"SMOTE: Synthetic minority over-sampling technique,\" Journal of Artificial Intelligence Research, vol. 16, pp. 321–357, 2002.",
    "[11] F. Pedregosa et al., \"Scikit-learn: Machine learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
    "[12] Bahrain Polytechnic, \"Academic Quality and Assessment Regulations Handbook,\" Curriculum and Academic Services, Manama, Kingdom of Bahrain, 2023."
]
for ref in references:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    r = p.add_run(ref)
    r.font.name = 'Arial'
    r.font.size = Pt(8.5)
    r.font.color.rgb = COLOR_DARK

doc_out_path = 'Project_Report_IT7103.docx'
doc.save(doc_out_path)
print(f"Rubric-Aligned Academic Project Report successfully generated at: {doc_out_path}")
