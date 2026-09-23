from pathlib import Path
import nbformat as nbf
import re

root = Path(__file__).resolve().parent.parent
nb = nbf.read(root/'revision_work/source_notebook.ipynb', as_version=4)
cells = nb.cells
cells[0].source = cells[0].source.split('---')[0] + '''
## Scope and assessment coverage
This notebook covers cleaning, preprocessing, semester features, correlation analysis,
single and ensemble regression and classification, individual forecasting, and tuning.
The supplied brief does not specify individual section marks.
Predictions use current-semester aggregate predictors and previously observed semesters.
This is a retrospective semester-level evaluation, not a validated early-week alert system.
'''
cells[1].source = '''## Environment and reproducibility
Run every cell in order in a fresh Colab session. Upload the supplied CSV when prompted.
The setup installs the tested modeling-library versions if necessary. The full model suite
and both searches can take several minutes. Random seeds and bounded parallelism are explicit.
'''
cells[2].source = '''import importlib.metadata as metadata
import subprocess
import sys
required = {'scikit-learn': '1.9.1', 'lightgbm': '4.7.0', 'xgboost': '3.2.0'}
for package, version in required.items():
    try:
        installed = metadata.version(package)
    except metadata.PackageNotFoundError:
        installed = None
    if installed != version:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', f'{package}=={version}'])
''' + cells[2].source.replace("warnings.filterwarnings('ignore')", "# Keep warnings visible for diagnostic review.").replace("from sklearn.model_selection import TimeSeriesSplit, StratifiedKFold, GridSearchCV", "from sklearn.model_selection import GridSearchCV\nfrom sklearn.base import clone\nfrom sklearn.dummy import DummyRegressor, DummyClassifier")
cells[2].source += "\nprint({p: metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'lightgbm', 'xgboost', 'statsmodels']})\n"
cells[4].source = '''## Dataset understanding
The CSV contains 154,314 course-enrollment rows and 20 columns for 6,000 students over
eight semesters. final_exam is the regression target and grade_letter is the classification target.
The following tables audit numeric distributions, missingness and duplicates directly.
Scholarship and internship are binary indicators; extracurricular is a count, not binary.
The brief provides the dataset; no claim is made that these are actual institutional records.
'''
cells[6].source = '''## Cleaning and target preservation
Remove ERR grades and out-of-range numeric grades as invalid records. Clip GPA to the stated
0-4 domain and study hours to 0-60. Clipping is a transparent modeling assumption: invalid GPA
values could alternatively be set missing, and the study-hours cap warrants sensitivity analysis.
Missing final_exam targets remain missing. Regression uses observed targets only; classification
retains valid letter-grade records. Missing predictor values are imputed within training data.
The cause of the anomalies is unknown; the CSV alone does not establish intentional corruption.
'''
cells[8].source = '''## Prediction protocol and preprocessing
Train on semesters 1-6 and evaluate on semesters 7-8. The evaluation is sequential: semester-8
features may use observed semester-7 outcomes, as those results are available by the next term.
This is not a two-semester forecast issued at the end of semester 6. Individual time-series
forecasting below separately uses a fixed six-semester history to forecast two future terms.
Current-semester homework and attendance summaries have no within-term timestamps, so their
availability at Week 6 cannot be established. The task concerns recurring students; it does not
estimate cold-start performance on an entirely unseen student population.
Imputation, scaling and encoding are fitted on training data only. Hyperparameter searches
fit an entire preprocessing/model pipeline separately inside each expanding semester fold.
'''
cells[11].source = '''## Correlation and cohort trends
Compute descriptive associations from observed values. Correlations are not causal effects.
The full-period EDA below is retrospective and is not used to choose tuning parameters.
'''
cells[12].source += '''
print('Observed correlations with final_exam:')
display(corr_matrix['final_exam'].round(4))
print('Cohort exam mean range:', cohort_trend.final_exam.min(), cohort_trend.final_exam.max())
'''
cells[13].source = cells[13].source.replace("strategy='median'", "strategy='median', keep_empty_features=True")
cells[15].source = cells[15].source.replace("'Ridge Regression': Ridge(alpha=1.0),", "'Mean baseline': DummyRegressor(strategy='mean'),\n    'Ridge Regression': Ridge(alpha=1.0),")
cells[15].source = cells[15].source.replace('Impact of Temporal', 'Impact of Added').replace('Empirical Lift of Temporal Features', 'Effect of temporal and interaction features')
cells[17].source = '''## Classification and class imbalance
Compare unweighted and balanced versions with identical baseline hyperparameters.
Use accuracy, macro precision, macro recall and macro F1, plus F-specific precision and recall.
The majority-class baseline establishes a minimal reference. High recall can produce many false
alerts; operational usefulness requires considering precision and available advising capacity.
'''
cells[18].source = cells[18].source.replace("clf_suite = {", "clf_suite = {\n    'Majority baseline': DummyClassifier(strategy='most_frequent'),")
cells[20].source = '''## Individual forecasting
Student 2 has eight semesters. Semester means use observed exams; the number of enrolled courses
can exceed the number of observed exams. Train on six semester means and forecast the last two
without updating from the first test outcome. Compare SES and ARIMA(1,0,0) with persistence.
Two test observations cannot establish forecast stability, statistical superiority or deployment readiness.
'''
cells[21].source = cells[21].source.replace("course_count=('course_code', 'count'),", "course_count=('course_code', 'count'),\n    observed_exam_count=('final_exam', 'count'),")
cells[22].source = '''## Hyperparameter optimization
Both searches use expanding whole-semester folds: train 1-3 / validate 4, train 1-4 / validate 5,
and train 1-5 / validate 6. Each fold fits preprocessing only on its training rows. The held-out
semesters 7-8 never enter parameter selection. Regression optimizes RMSE; classification optimizes
macro F1. The bounded grids below trade search coverage for reproducible runtime.
LightGBM subsampling is omitted rather than searching an inactive parameter.
'''
cells[23].source = '''def semester_folds(frame):
    folds = []
    for valid_sem in (4, 5, 6):
        train_idx = np.flatnonzero(frame.sem_num.to_numpy() < valid_sem)
        valid_idx = np.flatnonzero(frame.sem_num.to_numpy() == valid_sem)
        assert len(train_idx) and len(valid_idx)
        assert frame.iloc[train_idx].sem_num.max() < frame.iloc[valid_idx].sem_num.min()
        folds.append((train_idx, valid_idx))
    return folds

reg_frame = df_train_full.loc[train_reg_mask].reset_index(drop=True)
clf_frame = df_train_full.reset_index(drop=True)
fold_audit = []
for task, frame in [('Regression', reg_frame), ('Classification', clf_frame)]:
    for train_idx, valid_idx in semester_folds(frame):
        fold_audit.append({'Task': task, 'Train semesters': str(sorted(frame.iloc[train_idx].sem_num.unique().tolist())),
                           'Validation semester': int(frame.iloc[valid_idx].sem_num.min()),
                           'Train rows': len(train_idx), 'Validation rows': len(valid_idx)})
display(pd.DataFrame(fold_audit))

features = all_num_features + cat_features
reg_pipeline = Pipeline([('preprocess', clone(preprocessor)),
                         ('model', lgb.LGBMRegressor(random_state=42, verbose=-1, n_jobs=4))])
param_grid_reg = {'model__n_estimators': [100, 200], 'model__learning_rate': [0.03, 0.08],
                  'model__max_depth': [4, 6]}
grid_reg = GridSearchCV(reg_pipeline, param_grid_reg, cv=semester_folds(reg_frame),
                       scoring='neg_root_mean_squared_error', n_jobs=1, error_score='raise')
grid_reg.fit(reg_frame[features], reg_frame.final_exam)
best_lgb_pipeline = grid_reg.best_estimator_
best_lgb = best_lgb_pipeline.named_steps['model']
tuned_reg_preds = best_lgb_pipeline.predict(df_test_full.loc[test_reg_mask, features])
df_tuning_reg = pd.DataFrame({
    'Baseline LightGBM': df_reg_metrics.loc['LightGBM'],
    'Tuned LightGBM': [np.sqrt(mean_squared_error(y_test_reg, tuned_reg_preds)),
        mean_absolute_error(y_test_reg, tuned_reg_preds), r2_score(y_test_reg, tuned_reg_preds),
        mean_absolute_percentage_error(y_test_reg, tuned_reg_preds)*100]
}, index=['RMSE', 'MAE', 'R2', 'MAPE (%)'])
print('Regression search:', param_grid_reg)
print('Best parameters:', grid_reg.best_params_, 'Mean validation RMSE:', -grid_reg.best_score_)
display(df_tuning_reg.round(4))

clf_pipeline = Pipeline([('preprocess', clone(preprocessor)),
                        ('model', RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=4))])
param_grid_clf = {'model__n_estimators': [100], 'model__max_depth': [10, 14],
                  'model__min_samples_leaf': [1, 5]}
grid_clf = GridSearchCV(clf_pipeline, param_grid_clf, cv=semester_folds(clf_frame),
                       scoring='f1_macro', n_jobs=1, error_score='raise')
grid_clf.fit(clf_frame[features], clf_frame.grade_encoded)
tuned_clf_preds = grid_clf.predict(df_test_full[features])
tuned_clf_metrics = {
    'Overall Acc': accuracy_score(y_test_clf, tuned_clf_preds),
    'Macro Precision': precision_score(y_test_clf, tuned_clf_preds, average='macro', zero_division=0),
    'Macro Recall': recall_score(y_test_clf, tuned_clf_preds, average='macro', zero_division=0),
    'Macro F1': f1_score(y_test_clf, tuned_clf_preds, average='macro', zero_division=0),
    'Class F Recall': recall_score(y_test_clf==f_idx, tuned_clf_preds==f_idx, zero_division=0),
    'Class F Precision': precision_score(y_test_clf==f_idx, tuned_clf_preds==f_idx, zero_division=0)}
df_tuning_clf = pd.DataFrame({'Baseline balanced RF': df_clf_comp.loc['Random Forest (Balanced)'],
                             'Tuned balanced RF': pd.Series(tuned_clf_metrics)})
print('Classification search:', param_grid_clf)
print('Best parameters:', grid_clf.best_params_, 'Mean validation macro F1:', grid_clf.best_score_)
display(df_tuning_clf.round(4))
'''
cells[24].source = '''## Model interpretation and limitations
Gain importance measures contribution to fitted tree loss reduction; split importance counts splits.
Neither establishes causality. Correlated predictors can share or substitute importance.
The ablation comparison includes both temporal and interaction features; it does not isolate the
effect of lags alone. Very small test differences should not be described as meaningful gains.
The same historical holdout has been inspected during project revision, so it is no longer a
pristine external validation set. Future claims require a new cohort or later unseen semesters.
'''
cells[25].source = cells[25].source.replace("df_imp = pd.DataFrame({", "all_feature_names = best_lgb_pipeline.named_steps['preprocess'].get_feature_names_out()\ndf_imp = pd.DataFrame({")
cells[25].source += "\ndf_imp['Gain_share'] = df_imp.Gain_Importance / df_imp.Gain_Importance.sum()\ndisplay(df_imp.sort_values('Gain_share', ascending=False).head(12))\n"
cells[26].source = '''## Findings and practical limits
Use the computed tables above to compare models. Report both benefits and costs of class weighting.
Failure prediction is a screening aid requiring human review; model performance alone does not
demonstrate improved student outcomes. Future work should validate predictor availability, evaluate
subgroup performance and calibration, assess clipping sensitivity, and test on an untouched cohort.
References: the supplied IT7103 project brief and supplied CSV define the task and data. Algorithm
background: Breiman (2001), Random Forests; Chen and Guestrin (2016), XGBoost; Ke et al. (2017),
LightGBM; Hyndman and Athanasopoulos (2021), Forecasting: Principles and Practice, third edition.
'''
for c in cells:
    c.source = re.sub(r' \(\d+ Marks\)', '', c.source)
    c.source = c.source.replace('n_jobs=-1', 'n_jobs=4')
    if c.cell_type == 'code':
        c.outputs = []; c.execution_count = None
cells.append(nbf.v4.new_code_cell('''# Export computed results for the companion report; no metrics are manually entered.
import json
from pathlib import Path
summary = {
    'dataset': {'raw_rows': len(df_raw), 'clean_rows': len(df_clean), 'students': df_clean.student_id.nunique(),
                'raw_observed_exams': int(df_raw.final_exam.notna().sum()),
                'clean_observed_exams': int(df_clean.final_exam.notna().sum()),
                'missing_exams_clean': int(df_clean.final_exam.isna().sum()),
                'bad_gpa_clean': int(bad_gpa_count), 'study_hours_capped': int(extreme_study_count),
                'train_rows': len(df_train_full), 'test_rows': len(df_test_full),
                'reg_train_rows': len(y_train_reg), 'reg_test_rows': len(y_test_reg)},
    'correlations': corr_matrix.final_exam.to_dict(), 'cohort': cohort_trend.to_dict(),
    'regression': df_reg_metrics.to_dict(orient='index'), 'classification': df_clf_comp.to_dict(orient='index'),
    'ablation': df_ablation.to_dict(orient='index'), 'forecast': df_ts.to_dict(orient='index'),
    'student_history': s2_sem.to_dict(orient='records'), 'folds': fold_audit,
    'tuning_regression': df_tuning_reg.to_dict(), 'tuning_classification': df_tuning_clf.to_dict(),
    'reg_best_params': grid_reg.best_params_, 'clf_best_params': grid_clf.best_params_,
    'reg_search': param_grid_reg, 'clf_search': param_grid_clf,
    'reg_cv_rmse': -grid_reg.best_score_, 'clf_cv_f1': grid_clf.best_score_,
    'importance': df_imp.sort_values('Gain_share', ascending=False).to_dict(orient='records'),
    'versions': {p: metadata.version(p) for p in ['numpy','pandas','scikit-learn','lightgbm','xgboost','statsmodels']}}
Path('pipeline_results.json').write_text(json.dumps(summary, indent=2, allow_nan=False), encoding='utf-8')
print('Saved computed report results to pipeline_results.json')
'''))
nb.cells = cells
nbf.write(nb, root/'student_academic_performance_pipeline.ipynb')
print('Revised notebook written')
