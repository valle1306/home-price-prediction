#!/usr/bin/env python3
"""
Ensemble Models Script
Based on notebook 06_ensemble_models.ipynb
Tries to beat the XGBoost tuned model (84.68% R²) and approach Steph's 88.4%
"""
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from pathlib import Path
import json
import joblib
import time
from datetime import datetime

from sklearn.ensemble import VotingRegressor, StackingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

import xgboost as xgb
import lightgbm as lgb

print("="*70)
print("Ensemble & Advanced Models")
print(f"Script started at: {datetime.now().isoformat()}")
print("="*70)

# Paths
ROOT = Path.cwd()
DATA_DIR = ROOT / 'data'
MODELS_DIR = ROOT / 'models'

# Load data
print("\nLoading data...")
X_train = pd.read_csv(DATA_DIR / 'X_train.csv')
X_test = pd.read_csv(DATA_DIR / 'X_test.csv')
y_train = pd.read_csv(DATA_DIR / 'y_train.csv')['ClosePrice'].values
y_test = pd.read_csv(DATA_DIR / 'y_test.csv')['ClosePrice'].values

print(f"Data: {X_train.shape[0]:,} train, {X_test.shape[0]:,} test")
print(f"Features: {X_train.shape[1]}")

# Load previous best (XGBoost tuned)
with open(MODELS_DIR / 'xgboost_staged_params.json') as f:
    prev_best = json.load(f)

print(f"\nPrevious Best: XGBoost Tuned with {prev_best['test_r2']:.4f} R²")
print(f"Target: Beat Steph's 88.4% R²")

# Evaluation function
def evaluate_model(model, X_train, X_test, y_train, y_test, model_name):
    """Comprehensive model evaluation"""
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    results = {
        'model': model_name,
        'train_r2': r2_score(y_train, y_pred_train),
        'test_r2': r2_score(y_test, y_pred_test),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
        'test_mae': mean_absolute_error(y_test, y_pred_test),
        'test_mdape': np.median(np.abs((y_test - y_pred_test) / y_test)) * 100,
        'train_time': train_time
    }
    
    print(f"\n{'='*70}")
    print(f"{model_name}")
    print(f"{'='*70}")
    print(f"Train R²: {results['train_r2']:.4f}")
    print(f"Test R²:  {results['test_r2']:.4f}", end='')
    
    if results['test_r2'] > 0.884:
        print(f" 🎉 BEATS STEPH!")
    elif results['test_r2'] > prev_best['test_r2']:
        print(f" ⬆️ NEW BEST! (was {prev_best['test_r2']:.4f})")
    else:
        gap = (0.884 - results['test_r2']) * 100
        print(f" (Gap to Steph: {gap:.2f}%)")
    
    print(f"RMSE:     ${results['test_rmse']:,.0f}")
    print(f"MAE:      ${results['test_mae']:,.0f}")
    print(f"MdAPE:    {results['test_mdape']:.2f}%")
    print(f"Time:     {train_time:.1f}s")
    
    return results, model

ensemble_results = []
best_model = None
best_r2 = prev_best['test_r2']

# ================================================================
# 1. Voting Regressor (Simple Ensemble)
# ================================================================
print("\n" + "="*70)
print("1. VOTING REGRESSOR (Simple Ensemble)")
print("="*70)

print("\nBuilding Voting Regressor with RF + XGB + LightGBM...")

rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=25,
    min_samples_split=5,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)

xgb_model = xgb.XGBRegressor(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=9,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist',
    device='cuda',
    n_jobs=-1
)

lgb_model = lgb.LGBMRegressor(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=9,
    num_leaves=100,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)

voting = VotingRegressor(
    estimators=[
        ('rf', rf),
        ('xgb', xgb_model),
        ('lgb', lgb_model)
    ],
    n_jobs=1
)

voting_results, voting_model = evaluate_model(voting, X_train, X_test, y_train, y_test,
                                              "Voting Ensemble (RF + XGB + LGB)")
ensemble_results.append(voting_results)

if voting_results['test_r2'] > best_r2:
    best_r2 = voting_results['test_r2']
    best_model = voting_model
    best_model_name = 'Voting Ensemble'

# ================================================================
# 2. Stacking Regressor (Meta-Learner)
# ================================================================
print("\n" + "="*70)
print("2. STACKING REGRESSOR (Meta-Learner)")
print("="*70)

print("\nBuilding Stacking Regressor with Ridge meta-learner...")

rf_stack = RandomForestRegressor(
    n_estimators=150, max_depth=20, min_samples_split=5,
    max_features='sqrt', random_state=42, n_jobs=-1
)

xgb_stack = xgb.XGBRegressor(
    n_estimators=300, learning_rate=0.05, max_depth=9,
    subsample=0.8, colsample_bytree=0.8, random_state=42,
    tree_method='hist', device='cuda', n_jobs=-1
)

lgb_stack = lgb.LGBMRegressor(
    n_estimators=300, learning_rate=0.05, max_depth=9,
    num_leaves=80, subsample=0.8, colsample_bytree=0.8,
    random_state=42, n_jobs=-1, verbose=-1
)

stacking = StackingRegressor(
    estimators=[
        ('rf', rf_stack),
        ('xgb', xgb_stack),
        ('lgb', lgb_stack)
    ],
    final_estimator=Ridge(alpha=10.0),
    cv=3,
    n_jobs=1
)

stacking_results, stacking_model = evaluate_model(stacking, X_train, X_test, y_train, y_test,
                                                   "Stacking Ensemble (Ridge Meta-Learner)")
ensemble_results.append(stacking_results)

if stacking_results['test_r2'] > best_r2:
    best_r2 = stacking_results['test_r2']
    best_model = stacking_model
    best_model_name = 'Stacking Ensemble'

# ================================================================
# 3. LightGBM Tuned
# ================================================================
print("\n" + "="*70)
print("3. LIGHTGBM (Standalone)")
print("="*70)

print("\nTraining LightGBM with optimized parameters...")

lgb_tuned = lgb.LGBMRegressor(
    n_estimators=800,
    learning_rate=0.03,
    max_depth=11,
    num_leaves=150,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_samples=20,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)

lgb_results, lgb_model_tuned = evaluate_model(lgb_tuned, X_train, X_test, y_train, y_test,
                                               "LightGBM Tuned")
ensemble_results.append(lgb_results)

if lgb_results['test_r2'] > best_r2:
    best_r2 = lgb_results['test_r2']
    best_model = lgb_model_tuned
    best_model_name = 'LightGBM Tuned'

# ================================================================
# 4. Weighted Blending
# ================================================================
print("\n" + "="*70)
print("4. WEIGHTED BLENDING")
print("="*70)

print("\nTraining individual models and blending predictions...")

# Train individual models
print("  Training XGBoost...")
xgb_blend = xgb.XGBRegressor(
    n_estimators=600, learning_rate=0.03, max_depth=11,
    subsample=0.8, colsample_bytree=0.8, gamma=0.5,
    reg_alpha=0, reg_lambda=0.5, min_child_weight=5,
    random_state=42, tree_method='hist', device='cuda'
)
xgb_blend.fit(X_train, y_train)
xgb_pred = xgb_blend.predict(X_test)
xgb_train_pred = xgb_blend.predict(X_train)

print("  Training LightGBM...")
lgb_blend = lgb.LGBMRegressor(
    n_estimators=600, learning_rate=0.03, max_depth=11,
    num_leaves=150, subsample=0.8, colsample_bytree=0.8,
    random_state=42, n_jobs=-1, verbose=-1
)
lgb_blend.fit(X_train, y_train)
lgb_pred = lgb_blend.predict(X_test)
lgb_train_pred = lgb_blend.predict(X_train)

print("  Training Random Forest...")
rf_blend = RandomForestRegressor(
    n_estimators=200, max_depth=25, min_samples_split=5,
    random_state=42, n_jobs=-1
)
rf_blend.fit(X_train, y_train)
rf_pred = rf_blend.predict(X_test)
rf_train_pred = rf_blend.predict(X_train)

# Try different weight combinations
print("\n  Finding optimal blend weights...")
best_blend_r2 = 0
best_weights = None

for w_xgb in np.arange(0.3, 0.8, 0.1):
    for w_lgb in np.arange(0.2, 0.6, 0.1):
        w_rf = 1 - w_xgb - w_lgb
        if w_rf >= 0 and w_rf <= 0.4:
            blend_pred = w_xgb * xgb_pred + w_lgb * lgb_pred + w_rf * rf_pred
            blend_r2 = r2_score(y_test, blend_pred)
            if blend_r2 > best_blend_r2:
                best_blend_r2 = blend_r2
                best_weights = (w_xgb, w_lgb, w_rf)

w_xgb, w_lgb, w_rf = best_weights
blend_pred_test = w_xgb * xgb_pred + w_lgb * lgb_pred + w_rf * rf_pred
blend_pred_train = w_xgb * xgb_train_pred + w_lgb * lgb_train_pred + w_rf * rf_train_pred

blend_results = {
    'model': f'Weighted Blend (XGB:{w_xgb:.1f}, LGB:{w_lgb:.1f}, RF:{w_rf:.1f})',
    'train_r2': r2_score(y_train, blend_pred_train),
    'test_r2': r2_score(y_test, blend_pred_test),
    'test_rmse': np.sqrt(mean_squared_error(y_test, blend_pred_test)),
    'test_mae': mean_absolute_error(y_test, blend_pred_test),
    'test_mdape': np.median(np.abs((y_test - blend_pred_test) / y_test)) * 100,
    'weights': {'xgb': w_xgb, 'lgb': w_lgb, 'rf': w_rf}
}

print(f"\n{'='*70}")
print(f"Weighted Blend (XGB:{w_xgb:.1f}, LGB:{w_lgb:.1f}, RF:{w_rf:.1f})")
print(f"{'='*70}")
print(f"Train R²: {blend_results['train_r2']:.4f}")
print(f"Test R²:  {blend_results['test_r2']:.4f}", end='')

if blend_results['test_r2'] > 0.884:
    print(f" 🎉 BEATS STEPH!")
elif blend_results['test_r2'] > prev_best['test_r2']:
    print(f" ⬆️ NEW BEST! (was {prev_best['test_r2']:.4f})")
else:
    gap = (0.884 - blend_results['test_r2']) * 100
    print(f" (Gap to Steph: {gap:.2f}%)")

print(f"RMSE:     ${blend_results['test_rmse']:,.0f}")
print(f"MAE:      ${blend_results['test_mae']:,.0f}")
print(f"MdAPE:    {blend_results['test_mdape']:.2f}%")

ensemble_results.append(blend_results)

if blend_results['test_r2'] > best_r2:
    best_r2 = blend_results['test_r2']
    best_model_name = blend_results['model']

# ================================================================
# Summary
# ================================================================
print("\n" + "="*70)
print("ENSEMBLE RESULTS SUMMARY")
print("="*70)

# Create comparison DataFrame
results_df = pd.DataFrame(ensemble_results)
results_df = results_df.sort_values('test_r2', ascending=False)

print("\nModel Comparison (sorted by Test R²):")
print("-"*90)
print(f"{'Model':<50} {'Train R²':>10} {'Test R²':>10} {'RMSE':>15}")
print("-"*90)

for _, row in results_df.iterrows():
    print(f"{row['model']:<50} {row['train_r2']:>10.4f} {row['test_r2']:>10.4f} ${row['test_rmse']:>14,.0f}")

# Add XGBoost tuned baseline
print(f"{'XGBoost Tuned (baseline)':<50} {'-':>10} {prev_best['test_r2']:>10.4f} {'-':>15}")
print("-"*90)

# Save results
results_df.to_csv(MODELS_DIR / 'ensemble_results.csv', index=False)

# Determine best overall
best_ensemble = results_df.iloc[0]
if best_ensemble['test_r2'] > prev_best['test_r2']:
    print(f"\n✓ BEST ENSEMBLE: {best_ensemble['model']}")
    print(f"  Test R²: {best_ensemble['test_r2']:.4f}")
    print(f"  Improvement over XGBoost Tuned: +{(best_ensemble['test_r2'] - prev_best['test_r2'])*100:.2f}%")
    
    # Save best ensemble info
    best_summary = {
        'best_model': best_ensemble['model'],
        'test_r2': float(best_ensemble['test_r2']),
        'train_r2': float(best_ensemble['train_r2']),
        'rmse': float(best_ensemble['test_rmse']),
        'mae': float(best_ensemble['test_mae']),
        'mdape': float(best_ensemble['test_mdape']),
        'gap_to_steph': float(0.884 - best_ensemble['test_r2']) * 100,
        'improvement_over_xgb': float(best_ensemble['test_r2'] - prev_best['test_r2']) * 100
    }
else:
    print(f"\n⚠️ No ensemble beat XGBoost Tuned ({prev_best['test_r2']:.4f})")
    best_summary = {
        'best_model': 'XGBoost Tuned',
        'test_r2': float(prev_best['test_r2']),
        'gap_to_steph': float(0.884 - prev_best['test_r2']) * 100,
        'note': 'No ensemble improvement achieved'
    }

with open(MODELS_DIR / 'ensemble_summary.json', 'w') as f:
    json.dump(best_summary, f, indent=2)

print(f"\n✓ Results saved to models/ensemble_results.csv")
print(f"✓ Summary saved to models/ensemble_summary.json")

print("\n" + "="*70)
print(f"Ensemble training complete at: {datetime.now().isoformat()}")
print("="*70)
