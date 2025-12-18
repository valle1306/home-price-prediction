#!/usr/bin/env python3
"""
Model Analysis Script
Based on notebook 05_model_analysis.ipynb
Analyzes the tuned XGBoost model
"""
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from pathlib import Path
import json
import joblib
import matplotlib
matplotlib.use('Agg')  # For headless server
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from datetime import datetime

print("="*70)
print("Model Analysis & Visualization")
print(f"Script started at: {datetime.now().isoformat()}")
print("="*70)

# Paths
ROOT = Path.cwd()
DATA_DIR = ROOT / 'data'
MODELS_DIR = ROOT / 'models'
PLOTS_DIR = ROOT / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)

# Plotting settings
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
sns.set_style('whitegrid')

# Load data
print("\nLoading data...")
X_train = pd.read_csv(DATA_DIR / 'X_train.csv')
X_test = pd.read_csv(DATA_DIR / 'X_test.csv')
y_train = pd.read_csv(DATA_DIR / 'y_train.csv')['ClosePrice'].values
y_test = pd.read_csv(DATA_DIR / 'y_test.csv')['ClosePrice'].values

print(f"Features: {X_train.shape[1]}")
print(f"Samples: {X_train.shape[0]:,} train, {X_test.shape[0]:,} test")

# Load the tuned XGBoost model
print("\nLoading tuned XGBoost model...")
model = joblib.load(MODELS_DIR / 'xgboost_tuned.joblib')

# Load parameters
with open(MODELS_DIR / 'xgboost_staged_params.json') as f:
    params = json.load(f)

print(f"Model Test R²: {params['test_r2']:.4f}")
print(f"Trees: {params.get('actual_n_estimators', 'N/A')}")

# ================================================================
# 1. Feature Importance Analysis
# ================================================================
print("\n" + "="*70)
print("1. FEATURE IMPORTANCE ANALYSIS")
print("="*70)

if hasattr(model, 'feature_importances_'):
    importance_df = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Top 30 features
    top_30 = importance_df.head(30)
    
    plt.figure(figsize=(12, 10))
    plt.barh(range(len(top_30)), top_30['importance'], color='steelblue')
    plt.yticks(range(len(top_30)), top_30['feature'])
    plt.xlabel('Feature Importance')
    plt.title('Top 30 Most Important Features - XGBoost Tuned')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'feature_importance_top30.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\nTop 20 Most Important Features:")
    print("-"*50)
    for i, row in importance_df.head(20).iterrows():
        print(f"{row['feature']:50s} {row['importance']:.6f}")
    
    # Save full importance
    importance_df.to_csv(MODELS_DIR / 'feature_importance_analysis.csv', index=False)
    print(f"\n✓ Feature importance saved to models/feature_importance_analysis.csv")
else:
    print("Model doesn't support feature_importances_")

# ================================================================
# 2. Predictions vs Actual Analysis
# ================================================================
print("\n" + "="*70)
print("2. PREDICTION vs ACTUAL ANALYSIS")
print("="*70)

y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)

print(f"\nTrain R²: {train_r2:.4f}")
print(f"Test R²:  {test_r2:.4f}")
print(f"Gap:      {(train_r2 - test_r2)*100:.2f}%")

# Scatter plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Actual vs Predicted
axes[0].scatter(y_test, y_pred_test, alpha=0.3, s=10)
axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
             'r--', lw=2, label='Perfect Prediction')
axes[0].set_xlabel('Actual Price ($)')
axes[0].set_ylabel('Predicted Price ($)')
axes[0].set_title(f'Actual vs Predicted (R² = {test_r2:.4f})')
axes[0].legend()

# Residuals
residuals = y_test - y_pred_test
axes[1].scatter(y_pred_test, residuals, alpha=0.3, s=10)
axes[1].axhline(0, color='r', linestyle='--', lw=2)
axes[1].set_xlabel('Predicted Price ($)')
axes[1].set_ylabel('Residuals ($)')
axes[1].set_title('Residual Plot')

plt.tight_layout()
plt.savefig(PLOTS_DIR / 'prediction_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"\n✓ Prediction plots saved")

# Residual statistics
print("\nResidual Statistics:")
print(f"  Mean Residual: ${residuals.mean():,.0f}")
print(f"  Std Residual:  ${residuals.std():,.0f}")
print(f"  MAE:           ${mean_absolute_error(y_test, y_pred_test):,.0f}")
print(f"  RMSE:          ${np.sqrt(mean_squared_error(y_test, y_pred_test)):,.0f}")
print(f"  Median Residual: ${np.median(residuals):,.0f}")

# ================================================================
# 3. Error Distribution Analysis
# ================================================================
print("\n" + "="*70)
print("3. ERROR DISTRIBUTION ANALYSIS")
print("="*70)

pct_errors = (residuals / y_test) * 100

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Absolute residuals histogram
axes[0].hist(residuals / 1000, bins=50, edgecolor='black', alpha=0.7)
axes[0].set_xlabel('Residual ($1000s)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of Residuals')
axes[0].axvline(0, color='r', linestyle='--', lw=2)

# Percentage errors
axes[1].hist(pct_errors, bins=50, edgecolor='black', alpha=0.7, range=(-50, 50))
axes[1].set_xlabel('Percentage Error (%)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Distribution of Percentage Errors')
axes[1].axvline(0, color='r', linestyle='--', lw=2)

plt.tight_layout()
plt.savefig(PLOTS_DIR / 'error_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nPercentage Error Statistics:")
print(f"  Mean:       {pct_errors.mean():.2f}%")
print(f"  Median:     {np.median(pct_errors):.2f}%")
print(f"  Std:        {pct_errors.std():.2f}%")
print(f"  Within ±10%: {(np.abs(pct_errors) <= 10).sum() / len(pct_errors) * 100:.1f}%")
print(f"  Within ±20%: {(np.abs(pct_errors) <= 20).sum() / len(pct_errors) * 100:.1f}%")
print(f"  Within ±30%: {(np.abs(pct_errors) <= 30).sum() / len(pct_errors) * 100:.1f}%")

# ================================================================
# 4. Price Range Performance
# ================================================================
print("\n" + "="*70)
print("4. PERFORMANCE BY PRICE RANGE")
print("="*70)

price_bins = [0, 300000, 500000, 750000, 1000000, 1500000, 2000000, np.inf]
labels = ['<300K', '300-500K', '500-750K', '750K-1M', '1M-1.5M', '1.5M-2M', '>2M']

df_analysis = pd.DataFrame({
    'actual': y_test,
    'predicted': y_pred_test,
    'residual': residuals,
    'pct_error': pct_errors,
    'abs_pct_error': np.abs(pct_errors),
    'price_range': pd.cut(y_test, bins=price_bins, labels=labels)
})

print("\nPerformance by Price Range:")
print("-"*80)
print(f"{'Price Range':<15} {'Count':>8} {'Mean % Err':>12} {'Std % Err':>12} {'R²':>10}")
print("-"*80)

for price_range in labels:
    subset = df_analysis[df_analysis['price_range'] == price_range]
    if len(subset) > 10:
        r2 = r2_score(subset['actual'], subset['predicted'])
        print(f"{price_range:<15} {len(subset):>8,} {subset['pct_error'].mean():>12.2f} {subset['pct_error'].std():>12.2f} {r2:>10.4f}")
    else:
        print(f"{price_range:<15} {len(subset):>8,} {'N/A':>12} {'N/A':>12} {'N/A':>10}")

# Visualize by price range
fig, ax = plt.subplots(figsize=(10, 6))
range_mae = df_analysis.groupby('price_range')['abs_pct_error'].mean()
range_mae.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
ax.set_ylabel('Mean Absolute Percentage Error (%)')
ax.set_xlabel('Price Range')
ax.set_title('Prediction Error by Price Range')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'error_by_price_range.png', dpi=300, bbox_inches='tight')
plt.close()

# ================================================================
# 5. Summary Statistics
# ================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Calculate additional metrics
mape = np.mean(np.abs(pct_errors))
mdape = np.median(np.abs(pct_errors))

summary = {
    'model': 'XGBoost Tuned (3-Stage)',
    'train_r2': float(train_r2),
    'test_r2': float(test_r2),
    'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
    'mae': float(mean_absolute_error(y_test, y_pred_test)),
    'mape': float(mape),
    'mdape': float(mdape),
    'within_10pct': float((np.abs(pct_errors) <= 10).mean() * 100),
    'within_20pct': float((np.abs(pct_errors) <= 20).mean() * 100),
    'gap_to_steph': float(0.884 - test_r2) * 100
}

print(f"\nModel: {summary['model']}")
print(f"Train R²: {summary['train_r2']:.4f}")
print(f"Test R²:  {summary['test_r2']:.4f} (Gap to Steph: {summary['gap_to_steph']:.2f}%)")
print(f"RMSE:     ${summary['rmse']:,.0f}")
print(f"MAE:      ${summary['mae']:,.0f}")
print(f"MAPE:     {summary['mape']:.2f}%")
print(f"MdAPE:    {summary['mdape']:.2f}%")

# Save summary
with open(MODELS_DIR / 'model_analysis_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n✓ Analysis summary saved to models/model_analysis_summary.json")
print(f"✓ Plots saved to plots/ directory")

print("\n" + "="*70)
print(f"Analysis complete at: {datetime.now().isoformat()}")
print("="*70)
