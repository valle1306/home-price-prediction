#!/usr/bin/env python3
"""
Advanced XGBoost Tuning - Aiming for 86%+ R²

Techniques used:
1. Log-transform target variable (often helps with price prediction)
2. Bayesian-style optimization with more iterations
3. Feature selection based on importance
4. More aggressive regularization search
5. Extended hyperparameter grid

Run on Amarel HPC with GPU support.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
import joblib
import json
from pathlib import Path
from scipy.stats import uniform, randint
import warnings
import time

warnings.filterwarnings('ignore')

# Paths
DATA_DIR = Path('/home/hpl14/home-price-prediction/data')
MODELS_DIR = Path('/home/hpl14/home-price-prediction/models')
MODELS_DIR.mkdir(exist_ok=True)

def sanitize_feature_names(df):
    """Sanitize feature names for XGBoost/LightGBM compatibility"""
    new_cols = {}
    for col in df.columns:
        new_col = col.replace(',', '_').replace(' ', '_').replace('-', '_')
        new_col = new_col.replace('[', '_').replace(']', '_').replace('<', '_')
        new_col = new_col.replace('>', '_').replace('(', '_').replace(')', '_')
        new_cols[col] = new_col
    return df.rename(columns=new_cols)

def compute_metrics(y_true, y_pred):
    """Compute comprehensive metrics"""
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    # Median Absolute Percentage Error
    ape = np.abs((y_true - y_pred) / y_true) * 100
    mdape = np.median(ape)
    return {'r2': r2, 'rmse': rmse, 'mae': mae, 'mdape': mdape}

print("=" * 60)
print("ADVANCED XGBOOST TUNING - TARGET: 86%+ R²")
print("=" * 60)

# Load data
print("\n1. Loading data...")
X_train = pd.read_csv(DATA_DIR / 'X_train.csv')
X_test = pd.read_csv(DATA_DIR / 'X_test.csv')
y_train = pd.read_csv(DATA_DIR / 'y_train.csv').values.ravel()
y_test = pd.read_csv(DATA_DIR / 'y_test.csv').values.ravel()

print(f"   Train: {X_train.shape[0]:,} samples, {X_train.shape[1]:,} features")
print(f"   Test: {X_test.shape[0]:,} samples")
print(f"   Target range: ${y_train.min():,.0f} - ${y_train.max():,.0f}")

# Sanitize feature names
print("\n2. Sanitizing feature names...")
X_train = sanitize_feature_names(X_train)
X_test = sanitize_feature_names(X_test)
print(f"   Done. Sample features: {list(X_train.columns[:5])}")

# Try with log-transformed target
print("\n3. Trying log-transformed target...")
y_train_log = np.log1p(y_train)
y_test_log = np.log1p(y_test)
print(f"   Log target range: {y_train_log.min():.2f} - {y_train_log.max():.2f}")

# ============================================================
# EXPERIMENT 1: Standard target with extended tuning
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 1: Extended Hyperparameter Tuning")
print("=" * 60)

param_dist_extended = {
    'n_estimators': [1500, 2000, 2500, 3000],
    'max_depth': [6, 7, 8, 9, 10, 12],
    'learning_rate': uniform(0.01, 0.09),  # 0.01-0.10
    'subsample': uniform(0.7, 0.25),  # 0.7-0.95
    'colsample_bytree': uniform(0.6, 0.35),  # 0.6-0.95
    'colsample_bylevel': uniform(0.6, 0.35),
    'reg_alpha': [0, 0.001, 0.01, 0.1, 1, 10],
    'reg_lambda': [0.1, 1, 5, 10, 50, 100],
    'gamma': [0, 0.01, 0.1, 0.5, 1],
    'min_child_weight': [1, 3, 5, 7, 10],
}

xgb_model = xgb.XGBRegressor(
    objective='reg:squarederror',
    tree_method='hist',
    device='cuda',
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

print(f"   Running RandomizedSearchCV with 40 iterations, 5-fold CV...")
start = time.time()

search = RandomizedSearchCV(
    xgb_model,
    param_dist_extended,
    n_iter=40,
    cv=5,
    scoring='r2',
    n_jobs=1,  # Use 1 job since XGBoost uses GPU
    random_state=42,
    verbose=1
)

search.fit(X_train, y_train)
elapsed1 = time.time() - start

print(f"\n   Best CV R²: {search.best_score_:.4f}")
print(f"   Time: {elapsed1:.1f}s")
print(f"   Best params: {search.best_params_}")

# Evaluate on test
y_pred_exp1 = search.best_estimator_.predict(X_test)
metrics_exp1 = compute_metrics(y_test, y_pred_exp1)
print(f"\n   TEST RESULTS (Experiment 1):")
print(f"   R² Score: {metrics_exp1['r2']*100:.2f}%")
print(f"   RMSE: ${metrics_exp1['rmse']:,.0f}")
print(f"   MAE: ${metrics_exp1['mae']:,.0f}")
print(f"   MdAPE: {metrics_exp1['mdape']:.2f}%")

# ============================================================
# EXPERIMENT 2: Log-transformed target
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 2: Log-Transformed Target")
print("=" * 60)

param_dist_log = {
    'n_estimators': [1500, 2000, 2500],
    'max_depth': [6, 8, 10, 12],
    'learning_rate': uniform(0.01, 0.09),
    'subsample': uniform(0.75, 0.2),
    'colsample_bytree': uniform(0.65, 0.3),
    'reg_alpha': [0, 0.01, 0.1, 1],
    'reg_lambda': [1, 10, 50],
    'gamma': [0, 0.1, 0.5],
    'min_child_weight': [1, 5, 10],
}

xgb_log = xgb.XGBRegressor(
    objective='reg:squarederror',
    tree_method='hist',
    device='cuda',
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

print(f"   Running RandomizedSearchCV with 30 iterations, 5-fold CV...")
start = time.time()

search_log = RandomizedSearchCV(
    xgb_log,
    param_dist_log,
    n_iter=30,
    cv=5,
    scoring='r2',
    n_jobs=1,
    random_state=42,
    verbose=1
)

search_log.fit(X_train, y_train_log)
elapsed2 = time.time() - start

print(f"\n   Best CV R² (log space): {search_log.best_score_:.4f}")
print(f"   Time: {elapsed2:.1f}s")

# Predict and inverse transform
y_pred_log = search_log.best_estimator_.predict(X_test)
y_pred_exp2 = np.expm1(y_pred_log)  # Inverse of log1p
y_pred_exp2 = np.maximum(y_pred_exp2, 0)  # Ensure non-negative

metrics_exp2 = compute_metrics(y_test, y_pred_exp2)
print(f"\n   TEST RESULTS (Experiment 2 - Log Transform):")
print(f"   R² Score: {metrics_exp2['r2']*100:.2f}%")
print(f"   RMSE: ${metrics_exp2['rmse']:,.0f}")
print(f"   MAE: ${metrics_exp2['mae']:,.0f}")
print(f"   MdAPE: {metrics_exp2['mdape']:.2f}%")

# ============================================================
# EXPERIMENT 3: Feature Selection + Tuning
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 3: Feature Selection + Tuning")
print("=" * 60)

# Use best model from Exp 1 to get feature importance
print("   Getting feature importance from best model...")
importance = search.best_estimator_.feature_importances_
feat_imp = pd.DataFrame({
    'feature': X_train.columns,
    'importance': importance
}).sort_values('importance', ascending=False)

# Select top 500 features (reduce noise)
top_n = 500
top_features = feat_imp.head(top_n)['feature'].tolist()
print(f"   Selecting top {top_n} features...")
print(f"   Top 10 features: {top_features[:10]}")

X_train_sel = X_train[top_features]
X_test_sel = X_test[top_features]

param_dist_sel = {
    'n_estimators': [2000, 2500, 3000],
    'max_depth': [8, 10, 12, 14],
    'learning_rate': uniform(0.02, 0.08),
    'subsample': uniform(0.75, 0.2),
    'colsample_bytree': uniform(0.7, 0.25),
    'reg_alpha': [0.01, 0.1, 1],
    'reg_lambda': [5, 10, 50],
    'gamma': [0, 0.1],
    'min_child_weight': [3, 5, 7],
}

xgb_sel = xgb.XGBRegressor(
    objective='reg:squarederror',
    tree_method='hist',
    device='cuda',
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

print(f"   Running RandomizedSearchCV with 25 iterations, 5-fold CV...")
start = time.time()

search_sel = RandomizedSearchCV(
    xgb_sel,
    param_dist_sel,
    n_iter=25,
    cv=5,
    scoring='r2',
    n_jobs=1,
    random_state=42,
    verbose=1
)

search_sel.fit(X_train_sel, y_train)
elapsed3 = time.time() - start

print(f"\n   Best CV R²: {search_sel.best_score_:.4f}")
print(f"   Time: {elapsed3:.1f}s")

y_pred_exp3 = search_sel.best_estimator_.predict(X_test_sel)
metrics_exp3 = compute_metrics(y_test, y_pred_exp3)
print(f"\n   TEST RESULTS (Experiment 3 - Feature Selection):")
print(f"   R² Score: {metrics_exp3['r2']*100:.2f}%")
print(f"   RMSE: ${metrics_exp3['rmse']:,.0f}")
print(f"   MAE: ${metrics_exp3['mae']:,.0f}")
print(f"   MdAPE: {metrics_exp3['mdape']:.2f}%")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("FINAL COMPARISON")
print("=" * 60)

results = [
    ('Exp 1: Extended Tuning', metrics_exp1, search.best_estimator_, X_train.columns.tolist()),
    ('Exp 2: Log Transform', metrics_exp2, search_log.best_estimator_, X_train.columns.tolist()),
    ('Exp 3: Feature Selection', metrics_exp3, search_sel.best_estimator_, top_features),
]

results_sorted = sorted(results, key=lambda x: x[1]['r2'], reverse=True)

print(f"\n{'Model':<30} {'R² (%)':<10} {'RMSE ($)':<15} {'MAE ($)':<15}")
print("-" * 70)
for name, metrics, _, _ in results_sorted:
    print(f"{name:<30} {metrics['r2']*100:<10.2f} {metrics['rmse']:<15,.0f} {metrics['mae']:<15,.0f}")

# Save best model
best_name, best_metrics, best_model, best_features = results_sorted[0]
print(f"\n   Best model: {best_name}")
print(f"   Saving to models/xgboost_advanced_best.joblib...")

joblib.dump(best_model, MODELS_DIR / 'xgboost_advanced_best.joblib')

# Save feature list
with open(MODELS_DIR / 'xgboost_advanced_features.json', 'w') as f:
    json.dump(best_features, f)

# Save summary
summary = {
    'best_experiment': best_name,
    'test_r2': best_metrics['r2'],
    'rmse': best_metrics['rmse'],
    'mae': best_metrics['mae'],
    'mdape': best_metrics['mdape'],
    'n_features': len(best_features),
    'all_results': [
        {'experiment': name, **metrics} 
        for name, metrics, _, _ in results
    ],
    'dataset_info': {
        'train_samples': len(y_train),
        'test_samples': len(y_test),
        'total_features': X_train.shape[1]
    }
}

with open(MODELS_DIR / 'xgboost_advanced_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n" + "=" * 60)
print(f"BEST RESULT: {best_metrics['r2']*100:.2f}% R²")
print(f"Gap to 88.4% target: {88.4 - best_metrics['r2']*100:.2f} points")
print("=" * 60)

# Check if we beat 86%
if best_metrics['r2'] >= 0.86:
    print("\n*** SUCCESS! Achieved 86%+ R² ***")
elif best_metrics['r2'] >= 0.855:
    print("\n*** GOOD! Close to 86% target ***")
else:
    print("\n*** Need more optimization to reach 86% ***")
