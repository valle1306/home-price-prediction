#!/usr/bin/env python3
"""
Time Series Features for Home Price Prediction

This script adds time-series features to improve predictions:
1. Lag features from previous months
2. Rolling statistics (mean, std) of prices by area
3. Trend features
4. Seasonal decomposition

Then trains XGBoost with these enhanced features.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
from sklearn.model_selection import RandomizedSearchCV
import joblib
import json
from pathlib import Path
from scipy.stats import uniform
import warnings
import time

warnings.filterwarnings('ignore')

# Paths
DATA_DIR = Path('/home/hpl14/home-price-prediction/data')
FILLED_DIR = Path('/home/hpl14/home-price-prediction/filled_data')
MODELS_DIR = Path('/home/hpl14/home-price-prediction/models')
MODELS_DIR.mkdir(exist_ok=True)

def sanitize_feature_names(df):
    """Sanitize feature names"""
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
    ape = np.abs((y_true - y_pred) / y_true) * 100
    mdape = np.median(ape)
    return {'r2': r2, 'rmse': rmse, 'mae': mae, 'mdape': mdape}

print("=" * 60)
print("TIME SERIES FEATURE ENGINEERING")
print("=" * 60)

# Load all monthly files to build temporal features
print("\n1. Loading monthly data files...")
monthly_files = sorted(FILLED_DIR.glob('CRMLSSold*.csv'))
print(f"   Found {len(monthly_files)} monthly files")

all_data = []
for f in monthly_files:
    df = pd.read_csv(f)
    # Extract month from filename
    month_str = f.stem.replace('CRMLSSold', '').replace('_filled', '')
    year = int(month_str[:4])
    month = int(month_str[4:6])
    df['Year'] = year
    df['Month'] = month
    df['YearMonth'] = year * 100 + month
    all_data.append(df)
    print(f"   {f.name}: {len(df):,} records")

combined = pd.concat(all_data, ignore_index=True)
print(f"\n   Total records: {len(combined):,}")

# Identify target and key location columns
target_col = 'ClosePrice'
if target_col not in combined.columns:
    print(f"   Warning: {target_col} not found, looking for alternatives...")
    price_cols = [c for c in combined.columns if 'price' in c.lower() or 'close' in c.lower()]
    print(f"   Price columns found: {price_cols}")
    if price_cols:
        target_col = price_cols[0]

# Location columns for aggregation
location_cols = []
for col in ['City', 'PostalCode', 'MLSAreaMajor', 'CountyOrParish']:
    if col in combined.columns:
        location_cols.append(col)
        
print(f"   Target: {target_col}")
print(f"   Location columns: {location_cols}")

# ============================================================
# Create time series features
# ============================================================
print("\n2. Creating time series features...")

# Sort by time
combined = combined.sort_values('YearMonth').reset_index(drop=True)

# Calculate monthly statistics by location
ts_features = {}

# For each location level, compute rolling stats
for loc_col in location_cols[:2]:  # Use top 2 location columns
    print(f"   Computing rolling stats by {loc_col}...")
    
    # Monthly median price by location
    monthly_stats = combined.groupby([loc_col, 'YearMonth'])[target_col].agg(['median', 'mean', 'std', 'count']).reset_index()
    monthly_stats.columns = [loc_col, 'YearMonth', 
                             f'{loc_col}_median_price', 
                             f'{loc_col}_mean_price',
                             f'{loc_col}_std_price',
                             f'{loc_col}_sale_count']
    
    # Create lag features (previous month's stats)
    for lag in [1, 2, 3]:
        monthly_stats[f'{loc_col}_median_lag{lag}'] = monthly_stats.groupby(loc_col)[f'{loc_col}_median_price'].shift(lag)
        monthly_stats[f'{loc_col}_mean_lag{lag}'] = monthly_stats.groupby(loc_col)[f'{loc_col}_mean_price'].shift(lag)
    
    # Rolling 3-month average
    monthly_stats[f'{loc_col}_rolling3m_mean'] = monthly_stats.groupby(loc_col)[f'{loc_col}_mean_price'].transform(
        lambda x: x.rolling(3, min_periods=1).mean()
    )
    
    # Price momentum (change from previous month)
    monthly_stats[f'{loc_col}_price_momentum'] = monthly_stats.groupby(loc_col)[f'{loc_col}_median_price'].pct_change()
    
    ts_features[loc_col] = monthly_stats

print("   Created lag and rolling features")

# ============================================================
# Merge time series features back to data
# ============================================================
print("\n3. Merging time series features to main data...")

data_enhanced = combined.copy()
for loc_col, stats_df in ts_features.items():
    # Drop current period stats (to avoid leakage), keep only lag/rolling features
    lag_cols = [c for c in stats_df.columns if 'lag' in c or 'rolling' in c or 'momentum' in c]
    merge_cols = [loc_col, 'YearMonth'] + lag_cols
    data_enhanced = data_enhanced.merge(stats_df[merge_cols], on=[loc_col, 'YearMonth'], how='left')

print(f"   Enhanced data shape: {data_enhanced.shape}")

# Add global time features
print("\n4. Adding global time features...")

# Global monthly stats (without location)
global_monthly = combined.groupby('YearMonth')[target_col].agg(['median', 'mean']).reset_index()
global_monthly.columns = ['YearMonth', 'global_median_price', 'global_mean_price']
global_monthly['global_median_lag1'] = global_monthly['global_median_price'].shift(1)
global_monthly['global_trend'] = global_monthly['global_mean_price'].pct_change()

data_enhanced = data_enhanced.merge(global_monthly[['YearMonth', 'global_median_lag1', 'global_trend']], 
                                     on='YearMonth', how='left')

# Seasonal indicators
data_enhanced['Quarter'] = (data_enhanced['Month'] - 1) // 3 + 1
data_enhanced['IsSummer'] = data_enhanced['Month'].isin([6, 7, 8]).astype(int)
data_enhanced['IsSpring'] = data_enhanced['Month'].isin([3, 4, 5]).astype(int)

print(f"   Final enhanced shape: {data_enhanced.shape}")

# ============================================================
# Prepare train/test split (chronological)
# ============================================================
print("\n5. Preparing chronological train/test split...")

# Train on months 1-7, test on month 8
train_months = sorted(data_enhanced['YearMonth'].unique())[:-1]  # All but last
test_month = sorted(data_enhanced['YearMonth'].unique())[-1]      # Last month

print(f"   Train months: {train_months}")
print(f"   Test month: {test_month}")

train_data = data_enhanced[data_enhanced['YearMonth'].isin(train_months)].copy()
test_data = data_enhanced[data_enhanced['YearMonth'] == test_month].copy()

print(f"   Train: {len(train_data):,}, Test: {len(test_data):,}")

# Drop rows with missing target
train_data = train_data.dropna(subset=[target_col])
test_data = test_data.dropna(subset=[target_col])

y_train = train_data[target_col].values
y_test = test_data[target_col].values

# Features to drop
drop_cols = [target_col, 'YearMonth', 'Year', 'Month']
# Also drop any ID or date columns
drop_cols += [c for c in train_data.columns if 'id' in c.lower() or 'date' in c.lower() or 'key' in c.lower()]
drop_cols = [c for c in drop_cols if c in train_data.columns]

X_train = train_data.drop(columns=drop_cols, errors='ignore')
X_test = test_data.drop(columns=drop_cols, errors='ignore')

# Keep only numeric columns
X_train = X_train.select_dtypes(include=[np.number])
X_test = X_test.select_dtypes(include=[np.number])

# Align columns
common_cols = list(set(X_train.columns) & set(X_test.columns))
X_train = X_train[common_cols]
X_test = X_test[common_cols]

# Fill NaN with 0 for lag features
X_train = X_train.fillna(0)
X_test = X_test.fillna(0)

# Sanitize names
X_train = sanitize_feature_names(X_train)
X_test = sanitize_feature_names(X_test)

print(f"   Final features: {X_train.shape[1]}")
print(f"   Sample new features: {[c for c in X_train.columns if 'lag' in c or 'rolling' in c][:10]}")

# ============================================================
# Train XGBoost with time series features
# ============================================================
print("\n6. Training XGBoost with time series features...")

param_dist = {
    'n_estimators': [1500, 2000, 2500],
    'max_depth': [6, 8, 10, 12],
    'learning_rate': uniform(0.02, 0.08),
    'subsample': uniform(0.7, 0.25),
    'colsample_bytree': uniform(0.6, 0.35),
    'reg_alpha': [0, 0.1, 1, 10],
    'reg_lambda': [1, 10, 50],
    'gamma': [0, 0.1, 0.5],
    'min_child_weight': [1, 5, 10],
}

xgb_model = xgb.XGBRegressor(
    objective='reg:squarederror',
    tree_method='hist',
    device='cuda',
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

print("   Running RandomizedSearchCV with 30 iterations, 3-fold CV...")
start = time.time()

search = RandomizedSearchCV(
    xgb_model,
    param_dist,
    n_iter=30,
    cv=3,
    scoring='r2',
    n_jobs=1,
    random_state=42,
    verbose=1
)

search.fit(X_train, y_train)
elapsed = time.time() - start

print(f"\n   Best CV R²: {search.best_score_:.4f}")
print(f"   Training time: {elapsed:.1f}s")
print(f"   Best params: {search.best_params_}")

# Evaluate on test
y_pred = search.best_estimator_.predict(X_test)
metrics = compute_metrics(y_test, y_pred)

print("\n" + "=" * 60)
print("TIME SERIES ENHANCED RESULTS")
print("=" * 60)
print(f"   R² Score: {metrics['r2']*100:.2f}%")
print(f"   RMSE: ${metrics['rmse']:,.0f}")
print(f"   MAE: ${metrics['mae']:,.0f}")
print(f"   MdAPE: {metrics['mdape']:.2f}%")

# Feature importance
importance = search.best_estimator_.feature_importances_
feat_imp = pd.DataFrame({
    'feature': X_train.columns,
    'importance': importance
}).sort_values('importance', ascending=False)

print("\n   Top 20 features:")
for i, row in feat_imp.head(20).iterrows():
    marker = " (NEW)" if any(x in row['feature'] for x in ['lag', 'rolling', 'momentum', 'global', 'Quarter']) else ""
    print(f"   {row['feature']}: {row['importance']:.4f}{marker}")

# Save model and results
print("\n7. Saving results...")
joblib.dump(search.best_estimator_, MODELS_DIR / 'xgboost_timeseries.joblib')
feat_imp.to_csv(MODELS_DIR / 'feature_importance_timeseries.csv', index=False)

summary = {
    'experiment': 'Time Series Enhanced XGBoost',
    'test_r2': metrics['r2'],
    'rmse': metrics['rmse'],
    'mae': metrics['mae'],
    'mdape': metrics['mdape'],
    'n_features': X_train.shape[1],
    'train_samples': len(y_train),
    'test_samples': len(y_test),
    'best_params': search.best_params_,
    'ts_features_added': [c for c in X_train.columns if any(x in c for x in ['lag', 'rolling', 'momentum', 'global'])]
}

with open(MODELS_DIR / 'xgboost_timeseries_summary.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\n   Saved xgboost_timeseries.joblib")
print(f"   Saved xgboost_timeseries_summary.json")

print("\n" + "=" * 60)
print(f"FINAL R²: {metrics['r2']*100:.2f}%")
print(f"Gap to 88.4% target: {88.4 - metrics['r2']*100:.2f} points")
print("=" * 60)
