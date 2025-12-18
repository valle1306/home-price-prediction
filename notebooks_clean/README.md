# Notebooks Pipeline - Home Price Prediction

## Current Best Results

| Metric | Value |
|--------|-------|
| **Best Model** | XGBoost + LightGBM Blend (10/90) |
| **Test R²** | 85.61% |
| **RMSE** | $321,335 |
| **Target** | 88.4% (Steph's baseline) |
| **Gap** | 2.79 percentage points |
| **Training Samples** | 150,311 |
| **Test Samples** | 22,759 |
| **Features** | 1,022 |

## Notebooks Workflow

### 1. Data Loading (`01_data_loading.ipynb`)
- **Input:** `filled_data/CRMLSSold*_filled.csv` (8 monthly files)
- **Output:** `data/train_raw.csv`, `data/test_raw.csv`
- **Split:** Months 1-7 (Jan-Jul 2025) for training, Month 8 (Aug 2025) for testing
- **Samples:** 151,830 train, 22,759 test

### 2. Preprocessing (`02_preprocessing.ipynb`)
- **Input:** Raw train/test data
- **Output:** `data/X_train.csv`, `data/X_test.csv`, `data/y_train.csv`, `data/y_test.csv`
- **Features:** 1,022 (from 80 raw columns)
- **Key Steps:**
  - Leakage removal (dates, agent names, IDs)
  - Target encoding for high-cardinality features (threshold: 600)
  - One-hot encoding for categoricals
  - Feature engineering: BuildingAge, TotalRooms, HasGarage
  - Missing value imputation, outlier removal

### 3. Baseline Models (`03_baseline_linear_models.ipynb`)
- **Models:** LinearRegression, Ridge, Lasso, ElasticNet
- **Purpose:** Establish baseline performance
- **Expected R²:** 60-70%

### 4. Advanced Tuning (`04_advanced_models_tuning.ipynb`)
- **Models:** Random Forest, XGBoost, LightGBM
- **Tuning:** RandomizedSearchCV (20-25 iterations, 3-fold CV)
- **XGBoost Result:** 85.06% R²
- **LightGBM Result:** 85.60% R²

### 5. Model Analysis (`05_model_analysis.ipynb`)
- **Analysis:** Feature importance, SHAP values
- **Outputs:** Visualization plots, importance rankings

### 6. Ensemble Models (`06_ensemble_models.ipynb`)
- **Methods:** Voting, Stacking, Weighted Blending
- **Best Result:** 85.61% R² (XGBoost + LightGBM blend)

## HPC Scripts (Amarel)

For GPU-accelerated training, use the scripts in `/scripts/`:

```bash
# Advanced XGBoost tuning (targeting 86%+)
sbatch scripts/run_xgb_advanced.sbatch

# Time series feature engineering
sbatch scripts/run_xgb_timeseries.sbatch
```

## Execution

### On Local Machine
```powershell
# Execute notebooks in order
jupyter nbconvert --to notebook --execute notebooks_clean/01_data_loading.ipynb --inplace
jupyter nbconvert --to notebook --execute notebooks_clean/02_preprocessing.ipynb --inplace
jupyter nbconvert --to notebook --execute notebooks_clean/04_advanced_models_tuning.ipynb --inplace
```

### On Amarel HPC
```bash
# Submit GPU jobs
cd /home/hpl14/home-price-prediction
sbatch scripts/run_xgb_advanced.sbatch
sbatch scripts/run_xgb_timeseries.sbatch
```

## Key Files

| File | Description |
|------|-------------|
| `models/ensemble_summary.json` | Best model performance summary |
| `models/lightgbm_ensemble_best.joblib` | Best LightGBM model |
| `models/xgboost_ensemble_best.joblib` | Best XGBoost model |
| `models/feature_importance.csv` | Feature importance rankings |

## Performance Comparison

| Model | Test R² | RMSE |
|-------|---------|------|
| Weighted Blend (10% XGB + 90% LGB) | 85.61% | $321,335 |
| LightGBM Tuned | 85.60% | $321,465 |
| XGBoost GPU-Tuned | 85.06% | $327,396 |
| Stacking (XGB+LGB+Ridge) | 83.95% | $339,609 |
| Voting (XGB+LGB) | 83.25% | $347,083 |

## Next Steps

1. Run advanced XGBoost tuning job (`scripts/run_xgb_advanced.sbatch`)
2. Run time series feature engineering (`scripts/run_xgb_timeseries.sbatch`)
3. Experiment with CatBoost
4. Try neural network approaches
5. Add external data (economic indicators, interest rates)
