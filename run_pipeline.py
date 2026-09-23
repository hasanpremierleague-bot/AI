"""
Academic Performance Analytics Pipeline (IT7103 Advanced AI Applications)
Comprehensive pipeline covering all 8 objectives:
1. Data Cleaning & Outlier Handling
2. Advanced Pre-processing & Feature Engineering
3. Correlation & Time Series Analysis
4. Regression Modeling for Final Exam Prediction
5. Classification Modeling for Grade Prediction
6. Time Series Forecasting for One Student
7. Ensemble Modeling for Classification & Regression
8. Hyperparameter Optimization & Interpretability
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error,
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
)
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, StackingRegressor, VotingRegressor
import xgboost as xgb
import lightgbm as lgb
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300

FIGURES_DIR = os.path.join(os.getcwd(), 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

print("--- [Step 1] Loading and Inspecting Raw Dataset ---")
df_raw = pd.read_csv('Project1-EducationDataset.csv')
print(f"Raw shape: {df_raw.shape}")

# Define semester chronological order
SEMESTER_ORDER = [
    '2020Spring', '2020Fall',
    '2021Spring', '2021Fall',
    '2022Spring', '2022Fall',
    '2023Spring', '2023Fall'
]
sem_to_int = {sem: i+1 for i, sem in enumerate(SEMESTER_ORDER)}

# Outlier & Anomaly Detection
# 1. Identify corrupt ERR records
err_mask = (df_raw['grade_letter'] == 'ERR') | (df_raw['numeric_grade'] < 0) | (df_raw['numeric_grade'] > 100)
err_count = err_mask.sum()
print(f"Corrupted ERR records detected: {err_count}")

# 2. Prior GPA invalid entries
bad_gpa_mask = (df_raw['prior_gpa'] < 0) | (df_raw['prior_gpa'] > 4.0)
bad_gpa_count = bad_gpa_mask.sum()
print(f"Invalid prior_gpa (<0 or >4.0): {bad_gpa_count}")

# 3. Extreme study hours
extreme_study_mask = df_raw['study_hours'] > 60
extreme_study_count = extreme_study_mask.sum()
print(f"Extreme study_hours (>60h): {extreme_study_count}")

# Basic Data Cleaning
df_clean = df_raw[~err_mask].copy()
print(f"Shape after dropping ERR records: {df_clean.shape}")

# Clip / clean physical boundary outliers
df_clean['prior_gpa_cleaned'] = df_clean['prior_gpa'].clip(lower=0.0, upper=4.0)
df_clean['study_hours_cleaned'] = df_clean['study_hours'].clip(lower=0.0, upper=60.0)

# Missing value handling:
# Impute missing values in attendance_rate, homework_avg, study_hours, final_exam using median by course_code
num_impute_cols = ['study_hours_cleaned', 'attendance_rate', 'homework_avg', 'final_exam']
for col in num_impute_cols:
    course_medians = df_clean.groupby('course_code')[col].transform('median')
    df_clean[col] = df_clean[col].fillna(course_medians).fillna(df_clean[col].median())

print(f"Missing values remaining in clean df: {df_clean[num_impute_cols].isna().sum().to_dict()}")

# --- Visualization 1: Data Cleaning & Distributions ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
# Grade distribution
grade_counts = df_clean['grade_letter'].value_counts()
grade_order = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']
grade_counts = grade_counts.reindex(grade_order).fillna(0)
sns.barplot(x=grade_counts.index, y=grade_counts.values, ax=axes[0], palette='Blues_d')
axes[0].set_title('Letter Grade Distribution (Post-Cleaning)', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Grade Letter', fontsize=12)
axes[0].set_ylabel('Number of Records', fontsize=12)
for i, v in enumerate(grade_counts.values):
    axes[0].text(i, v + 200, f"{int(v)}", ha='center', fontsize=9)

# Prior GPA vs Study Hours
sns.scatterplot(
    data=df_clean.sample(5000, random_state=42),
    x='study_hours_cleaned', y='numeric_grade', hue='gender', alpha=0.4, ax=axes[1], palette='tab10'
)
axes[1].set_title('Study Hours vs. Numeric Grade (Sampled n=5000)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Study Hours (Weekly)', fontsize=12)
axes[1].set_ylabel('Numeric Grade', fontsize=12)
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'fig1_data_cleaning.png'), dpi=300)
plt.close()
print("Saved fig1_data_cleaning.png")

# --- [Step 2] Advanced Preprocessing & Temporal Feature Engineering ---
print("\n--- [Step 2] Preprocessing & Temporal Feature Engineering ---")
df_clean['sem_num'] = df_clean['semester'].map(sem_to_int)
df_clean = df_clean.sort_values(by=['student_id', 'sem_num', 'course_code']).reset_index(drop=True)

# Student-level chronological aggregation & lag features
# Compute student's average final exam, homework, attendance per semester
student_sem_agg = df_clean.groupby(['student_id', 'sem_num']).agg(
    sem_final_exam_mean=('final_exam', 'mean'),
    sem_homework_mean=('homework_avg', 'mean'),
    sem_attendance_mean=('attendance_rate', 'mean')
).reset_index()

student_sem_agg['sem_num_next'] = student_sem_agg['sem_num'] + 1
student_sem_agg = student_sem_agg.rename(columns={
    'sem_final_exam_mean': 'final_exam_prev_semester',
    'sem_homework_mean': 'homework_avg_prev_semester',
    'sem_attendance_mean': 'attendance_prev_semester'
})

# Merge lag features back to course-level records
df_featured = pd.merge(
    df_clean,
    student_sem_agg[['student_id', 'sem_num_next', 'final_exam_prev_semester', 'homework_avg_prev_semester', 'attendance_prev_semester']],
    left_on=['student_id', 'sem_num'],
    right_on=['student_id', 'sem_num_next'],
    how='left'
).drop(columns=['sem_num_next'])

# Impute initial semester lag values with overall student median or global median
for col in ['final_exam_prev_semester', 'homework_avg_prev_semester', 'attendance_prev_semester']:
    df_featured[col] = df_featured[col].fillna(df_featured[col].median())

# Derived domain features
df_featured['study_hours_per_credit'] = df_featured['study_hours_cleaned'] / df_featured['credits']
df_featured['hw_study_interaction'] = df_featured['homework_avg'] * (df_featured['study_hours_cleaned'] / 10.0)
df_featured['attendance_hw_composite'] = (df_featured['attendance_rate'] * 0.4) + (df_featured['homework_avg'] * 0.6)

print(f"Features created successfully. Featured dataset shape: {df_featured.shape}")

# --- [Step 3] Correlation & Time Series Analysis ---
print("\n--- [Step 3] Correlation & Cohort Time Series Analysis ---")
corr_cols = [
    'final_exam', 'numeric_grade', 'prior_gpa_cleaned', 'study_hours_cleaned',
    'attendance_rate', 'homework_avg', 'final_exam_prev_semester',
    'homework_avg_prev_semester', 'attendance_prev_semester',
    'study_hours_per_credit', 'attendance_hw_composite'
]
corr_matrix = df_featured[corr_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='Blues', vmin=-0.2, vmax=1.0, cbar=True)
plt.title('Correlation Matrix of Academic Performance Drivers', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig2_correlation_matrix.png'), dpi=300)
plt.close()
print("Saved fig2_correlation_matrix.png")

# Macro cohort temporal trend
cohort_trend = df_featured.groupby('semester')[['final_exam', 'homework_avg', 'attendance_rate']].mean().reindex(SEMESTER_ORDER)
fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()
ax1.plot(cohort_trend.index, cohort_trend['final_exam'], 'o-', color='#1f77b4', lw=2.5, label='Mean Final Exam')
ax1.plot(cohort_trend.index, cohort_trend['homework_avg'], 's--', color='#2ca02c', lw=2.0, label='Mean Homework Avg')
ax2.plot(cohort_trend.index, cohort_trend['attendance_rate'], '^-.', color='#d62728', lw=2.0, label='Mean Attendance Rate')
ax1.set_title('Cohort Academic Trends Across Semesters (2020-2023)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Semester', fontsize=12)
ax1.set_ylabel('Score / Average (0-100)', fontsize=12)
ax2.set_ylabel('Attendance (%)', fontsize=12)
ax1.set_ylim(60, 95)
ax2.set_ylim(60, 95)
ax1.tick_params(axis='x', rotation=30)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'fig3_cohort_trend.png'), dpi=300)
plt.close()
print("Saved fig3_cohort_trend.png")

# --- Prepare Datasets for Machine Learning ---
# Feature lists
cat_cols = ['subject_area', 'gender', 'year_of_study', 'scholarship', 'extracurricular', 'internship']
num_cols = [
    'credits', 'prior_gpa_cleaned', 'study_hours_cleaned', 'attendance_rate',
    'homework_avg', 'final_exam_prev_semester', 'homework_avg_prev_semester',
    'attendance_prev_semester', 'study_hours_per_credit', 'attendance_hw_composite'
]

X_raw = df_featured[cat_cols + num_cols]
y_reg = df_featured['final_exam']
y_clf = df_featured['grade_letter']

# One-hot encode categorical features and scale numerical features
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_cols),
    ('num', StandardScaler(), num_cols)
])

X_transformed = preprocessor.fit_transform(X_raw)
feature_names = (
    preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols).tolist() +
    num_cols
)
X_df = pd.DataFrame(X_transformed, columns=feature_names)

# Split Train/Test (80/20) with stratified split for classification
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X_df, y_reg, test_size=0.2, random_state=42
)

# Label encoding for classification target
le = LabelEncoder()
le.fit(grade_order)
y_clf_encoded = le.transform(y_clf)

X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
    X_df, y_clf_encoded, test_size=0.2, random_state=42, stratify=y_clf_encoded
)

print(f"Training set: {X_train_reg.shape}, Test set: {X_test_reg.shape}")

# --- [Step 4 & 7] Regression Modeling for Final Exam Prediction ---
print("\n--- [Step 4 & 7] Training Regression Models ---")
reg_models = {
    'Ridge Regression': Ridge(alpha=1.0),
    'Decision Tree': DecisionTreeRegressor(max_depth=8, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
    'LightGBM': lgb.LGBMRegressor(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42, verbose=-1),
    'XGBoost': xgb.XGBRegressor(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42, n_jobs=-1)
}

reg_results = {}
reg_preds = {}

for name, model in reg_models.items():
    print(f"Training {name}...")
    model.fit(X_train_reg, y_train_reg)
    preds = model.predict(X_test_reg)
    reg_preds[name] = preds
    rmse = np.sqrt(mean_squared_error(y_test_reg, preds))
    mae = mean_absolute_error(y_test_reg, preds)
    r2 = r2_score(y_test_reg, preds)
    mape = mean_absolute_percentage_error(y_test_reg, preds) * 100
    reg_results[name] = {
        'RMSE': round(float(rmse), 4),
        'MAE': round(float(mae), 4),
        'R2': round(float(r2), 4),
        'MAPE': round(float(mape), 4)
    }
    print(f"-> {name}: RMSE={rmse:.4f}, MAE={mae:.4f}, R2={r2:.4f}, MAPE={mape:.2f}%")

# Ensemble: Stacking / Voting Regressor
print("Training Voting Regressor Ensemble...")
voting_reg = VotingRegressor(
    estimators=[('rf', reg_models['Random Forest']), ('lgb', reg_models['LightGBM']), ('xgb', reg_models['XGBoost'])],
    weights=[1, 2, 2]
)
voting_reg.fit(X_train_reg, y_train_reg)
v_preds = voting_reg.predict(X_test_reg)
reg_preds['Voting Ensemble'] = v_preds
reg_results['Voting Ensemble'] = {
    'RMSE': round(float(np.sqrt(mean_squared_error(y_test_reg, v_preds))), 4),
    'MAE': round(float(mean_absolute_error(y_test_reg, v_preds)), 4),
    'R2': round(float(r2_score(y_test_reg, v_preds)), 4),
    'MAPE': round(float(mean_absolute_percentage_error(y_test_reg, v_preds) * 100), 4)
}
print(f"-> Voting Ensemble: {reg_results['Voting Ensemble']}")

# Plot Regression Comparisons
reg_df = pd.DataFrame(reg_results).T
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
reg_df[['RMSE', 'MAE']].plot(kind='bar', ax=axes[0], colormap='Blues_r')
axes[0].set_title('Regression Error Comparison (RMSE & MAE)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Error Score', fontsize=11)
axes[0].tick_params(axis='x', rotation=30)
for p in axes[0].patches:
    axes[0].annotate(f"{p.get_height():.2f}", (p.get_x() * 1.005, p.get_height() * 1.01), fontsize=8)

reg_df['R2'].plot(kind='bar', ax=axes[1], color='#2b5c8f')
axes[1].set_title('Goodness of Fit ($R^2$ Score)', fontsize=13, fontweight='bold')
axes[1].set_ylabel('$R^2$', fontsize=11)
axes[1].tick_params(axis='x', rotation=30)
axes[1].set_ylim(0, 1.0)
for p in axes[1].patches:
    axes[1].annotate(f"{p.get_height():.3f}", (p.get_x() * 1.01, p.get_height() * 1.01), fontsize=9)
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'fig4_regression_comparison.png'), dpi=300)
plt.close()
print("Saved fig4_regression_comparison.png")

# Residual Diagnostic Plot for Best Model (LightGBM/Ensemble)
best_reg_name = 'LightGBM'
best_preds = reg_preds[best_reg_name]
residuals = y_test_reg - best_preds

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].scatter(best_preds[:3000], residuals[:3000], alpha=0.3, color='#1f77b4', s=15)
axes[0].axhline(0, color='red', linestyle='--', lw=2)
axes[0].set_title(f'Residuals vs. Predicted Values ({best_reg_name})', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Predicted Final Exam Score', fontsize=11)
axes[0].set_ylabel('Residual (Actual - Predicted)', fontsize=11)

sns.histplot(residuals, kde=True, ax=axes[1], color='#2ca02c', bins=40)
axes[1].set_title('Residual Error Distribution (Normality Check)', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Residual Error', fontsize=11)
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'fig5_residuals_diagnostic.png'), dpi=300)
plt.close()
print("Saved fig5_residuals_diagnostic.png")

# --- [Step 5 & 7] Classification Modeling for Grade Prediction ---
print("\n--- [Step 5 & 7] Training Multi-Class Classification Models ---")
# Strict check: numeric_grade is NOT in X_df!
assert 'numeric_grade' not in X_df.columns, "DATA LEAKAGE DETECTED: numeric_grade present in classification features!"

clf_models = {
    'Multinomial LogReg': LogisticRegression(max_iter=500, class_weight='balanced', random_state=42),
    'Decision Tree': DecisionTreeClassifier(max_depth=8, class_weight='balanced', random_state=42),
    'Random Forest (Balanced)': RandomForestClassifier(n_estimators=100, max_depth=12, class_weight='balanced', random_state=42, n_jobs=-1),
    'LightGBM Classifier': lgb.LGBMClassifier(n_estimators=150, learning_rate=0.08, max_depth=6, class_weight='balanced', random_state=42, verbose=-1),
    'XGBoost Classifier': xgb.XGBClassifier(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42, n_jobs=-1)
}

clf_results = {}
clf_preds = {}

for name, model in clf_models.items():
    print(f"Training {name}...")
    model.fit(X_train_clf, y_train_clf)
    preds = model.predict(X_test_clf)
    clf_preds[name] = preds
    acc = accuracy_score(y_test_clf, preds)
    prec_macro = precision_score(y_test_clf, preds, average='macro', zero_division=0)
    rec_macro = recall_score(y_test_clf, preds, average='macro', zero_division=0)
    f1_macro = f1_score(y_test_clf, preds, average='macro', zero_division=0)
    f1_weighted = f1_score(y_test_clf, preds, average='weighted', zero_division=0)
    clf_results[name] = {
        'Accuracy': round(float(acc), 4),
        'Precision_Macro': round(float(prec_macro), 4),
        'Recall_Macro': round(float(rec_macro), 4),
        'F1_Macro': round(float(f1_macro), 4),
        'F1_Weighted': round(float(f1_weighted), 4)
    }
    print(f"-> {name}: Acc={acc:.4f}, F1-Macro={f1_macro:.4f}, F1-Weighted={f1_weighted:.4f}")

# Plot Classification Comparison
clf_df = pd.DataFrame(clf_results).T
fig, ax = plt.subplots(figsize=(10, 5))
clf_df[['Accuracy', 'F1_Macro', 'F1_Weighted']].plot(kind='bar', ax=ax, colormap='viridis')
ax.set_title('Classification Performance across Architectures (Avoiding Data Leakage)', fontsize=13, fontweight='bold')
ax.set_ylabel('Score (0.0 - 1.0)', fontsize=11)
ax.tick_params(axis='x', rotation=30)
ax.set_ylim(0, 1.0)
for p in ax.patches:
    ax.annotate(f"{p.get_height():.2f}", (p.get_x() * 1.005, p.get_height() * 1.01), fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'fig6_classification_comparison.png'), dpi=300)
plt.close()
print("Saved fig6_classification_comparison.png")

# Confusion Matrix for Best Classification Model
best_clf_name = 'Random Forest (Balanced)'
best_clf_preds = clf_preds[best_clf_name]
cm = confusion_matrix(y_test_clf, best_clf_preds, normalize='true')

plt.figure(figsize=(9, 7))
sns.heatmap(cm, annot=True, fmt='.2f', cmap='Blues',
            xticklabels=grade_order, yticklabels=grade_order)
plt.title(f'Normalized Confusion Matrix ({best_clf_name})', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Predicted Letter Grade', fontsize=12)
plt.ylabel('True Letter Grade', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig7_confusion_matrix.png'), dpi=300)
plt.close()
print("Saved fig7_confusion_matrix.png")

# --- [Step 6] Time Series Forecasting for One Student ---
print("\n--- [Step 6] Time Series Forecasting for Student #2 ---")
student_id_target = 2
df_student = df_featured[df_featured['student_id'] == student_id_target].copy()
df_student = df_student.sort_values(by='sem_num')

# Aggregate by semester to get clean temporal trajectory
student_ts = df_student.groupby(['sem_num', 'semester'])['final_exam'].mean().reset_index()
student_ts = student_ts.sort_values(by='sem_num').reset_index(drop=True)
print("Student #2 Semester Scores:")
print(student_ts)

# Train/Test Split (first 6 semesters train, last 2 semesters test)
train_ts = student_ts.iloc[:6].copy()
test_ts = student_ts.iloc[6:].copy()

y_train_series = train_ts['final_exam'].values
y_test_series = test_ts['final_exam'].values

# Model 1: Holt-Winters Exponential Smoothing
hw_model = SimpleExpSmoothing(y_train_series, initialization_method="estimated").fit()
hw_forecast = hw_model.forecast(len(test_ts))

# Model 2: ARIMA(1, 0, 0)
arima_model = ARIMA(y_train_series, order=(1, 0, 0)).fit()
arima_forecast = arima_model.forecast(len(test_ts))

# Model 3: Persistence Baseline (last known value)
naive_forecast = np.repeat(y_train_series[-1], len(test_ts))

ts_metrics = {}
for m_name, f_vals in [('Exponential Smoothing', hw_forecast), ('ARIMA(1,0,0)', arima_forecast), ('Naive Lag-1', naive_forecast)]:
    rmse_ts = np.sqrt(mean_squared_error(y_test_series, f_vals))
    mae_ts = mean_absolute_error(y_test_series, f_vals)
    mape_ts = mean_absolute_percentage_error(y_test_series, f_vals) * 100
    ts_metrics[m_name] = {
        'RMSE': round(float(rmse_ts), 4),
        'MAE': round(float(mae_ts), 4),
        'MAPE': round(float(mape_ts), 4)
    }
    print(f"Time Series Forecast {m_name}: RMSE={rmse_ts:.4f}, MAE={mae_ts:.4f}, MAPE={mape_ts:.2f}%")

# Plot Student #2 Time Series
fig, ax = plt.subplots(figsize=(10, 5))
x_all = student_ts['semester'].values
ax.plot(x_all[:6], y_train_series, 'o-', color='#1f77b4', lw=2.5, label='Historical Actuals (Train)')
ax.plot(x_all[5:], [y_train_series[-1]] + list(y_test_series), 'o-', color='#2ca02c', lw=2.5, label='Observed Ground Truth (Test)')
ax.plot(x_all[6:], hw_forecast, 's--', color='#ff7f0e', lw=2, label=f'Exp Smoothing (RMSE: {ts_metrics["Exponential Smoothing"]["RMSE"]:.2f})')
ax.plot(x_all[6:], arima_forecast, '^:', color='#d62728', lw=2, label=f'ARIMA(1,0,0) (RMSE: {ts_metrics["ARIMA(1,0,0)"]["RMSE"]:.2f})')

ax.set_title(f'Student #2 Time Series Trajectory & Multi-Step Forecasting', fontsize=14, fontweight='bold')
ax.set_xlabel('Academic Semester (Chronological)', fontsize=12)
ax.set_ylabel('Mean Final Exam Score', fontsize=12)
ax.legend(loc='lower left', frameon=True)
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'fig8_student_forecasting.png'), dpi=300)
plt.close()
print("Saved fig8_student_forecasting.png")

# --- [Step 8] Hyperparameter Optimization & Feature Importance ---
print("\n--- [Step 8] Hyperparameter Optimization ---")
param_grid_lgb = {
    'n_estimators': [100, 200],
    'learning_rate': [0.03, 0.08, 0.15],
    'max_depth': [4, 6, 8],
    'subsample': [0.8, 1.0]
}
grid_search = GridSearchCV(
    estimator=lgb.LGBMRegressor(random_state=42, verbose=-1),
    param_grid=param_grid_lgb,
    cv=3,
    scoring='neg_root_mean_squared_error',
    n_jobs=-1
)
grid_search.fit(X_train_reg, y_train_reg)
best_lgb = grid_search.best_estimator_
tuned_preds = best_lgb.predict(X_test_reg)
tuned_rmse = np.sqrt(mean_squared_error(y_test_reg, tuned_preds))
tuned_mae = mean_absolute_error(y_test_reg, tuned_preds)
tuned_r2 = r2_score(y_test_reg, tuned_preds)

tuning_comparison = {
    'Default LightGBM': reg_results['LightGBM'],
    'Tuned LightGBM': {
        'RMSE': round(float(tuned_rmse), 4),
        'MAE': round(float(tuned_mae), 4),
        'R2': round(float(tuned_r2), 4),
        'MAPE': round(float(mean_absolute_percentage_error(y_test_reg, tuned_preds) * 100), 4)
    },
    'Best Parameters': grid_search.best_params_
}
print(f"Tuned LightGBM: {tuning_comparison['Tuned LightGBM']}")
print(f"Best Params: {grid_search.best_params_}")

# Feature Importance Plot
feature_imp = pd.Series(best_lgb.feature_importances_, index=feature_names).sort_values(ascending=False).head(12)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=feature_imp.values, y=feature_imp.index, ax=ax, palette='Blues_r')
ax.set_title('Top 12 Most Influential Features (Tuned LightGBM Regressor)', fontsize=14, fontweight='bold')
ax.set_xlabel('Gain / Split Importance', fontsize=12)
ax.set_ylabel('Engineered Feature', fontsize=12)
plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, 'fig9_feature_importance.png'), dpi=300)
plt.close()
print("Saved fig9_feature_importance.png")

# Save summary metrics to JSON for the report generator
summary_output = {
    'dataset_stats': {
        'raw_rows': int(len(df_raw)),
        'clean_rows': int(len(df_clean)),
        'dropped_err_count': int(err_count),
        'cleaned_gpa_count': int(bad_gpa_count),
        'extreme_study_count': int(extreme_study_count)
    },
    'regression_results': reg_results,
    'classification_results': clf_results,
    'time_series_metrics': ts_metrics,
    'tuning_comparison': tuning_comparison,
    'student_2_history': student_ts.to_dict(orient='records')
}

with open('pipeline_results.json', 'w') as f:
    json.dump(summary_output, f, indent=2)

print("\nPipeline completed successfully! All figures and metrics saved.")
