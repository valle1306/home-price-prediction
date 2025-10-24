# Clean Notebooks Pipeline - Home Price Prediction

**Target:** Beat Steph's 88.4% R² baseline

## Current Status

| Metric | Value |
|--------|-------|
| **Baseline (Initial)** | 73.6% R² (65 features) |
| **After Optimization** | 83.91% R² (XGBoost, 1,020 features) |
| **Gap to Steph** | 4.51 percentage points |
| **Training Samples** | 150,311 (vs Steph's 58,088) |
| **Features** | 1,020 (vs Steph's 451) |

## Notebooks Workflow

### 1. `01_data_loading.ipynb` - Data Loading & Temporal Split
- **Input:** `filled_data/CRMLSSold*_filled.csv` (8 monthly files)
- **Output:** `data/train_raw.csv`, `data/test_raw.csv`
- **Split:** Months 1-7 (Jan-Jul 2025) for training, Month 8 (Aug 2025) for testing
- **Data:** 151,830 train samples, 22,759 test samples, 80 raw columns
- **Status:** ✅ Working

### 2. `02_preprocessing.ipynb` - Feature Engineering & Preprocessing
- **Input:** `data/train_raw.csv`, `data/test_raw.csv`
- **Output:** `data/X_train.csv`, `data/X_test.csv`, `data/y_train.csv`, `data/y_test.csv`
- **Features:** 1,020 features (from 80 raw columns)
- **Key Steps:**
  - Remove leakage (dates, agent names, IDs, >10K cardinality columns)
  - Target encoding for high-cardinality features (threshold: 600 unique values)
  - One-hot encoding for remaining categoricals (drop_first=False)
  - Feature engineering: BuildingAge, TotalRooms, HasGarage
  - Missing value imputation (threshold: 60%)
  - Outlier removal (0.5th and 99.5th percentiles)
- **Final:** 150,311 train samples, 22,759 test samples
- **Status:** ✅ Working (produces 1,020 features)

### 3. `03_baseline_linear_models.ipynb` - Linear Models
- **Input:** Preprocessed data from notebook 02
- **Output:** `models/baseline_linear_results.csv`
- **Models:** LinearRegression, Ridge, Lasso, ElasticNet
- **Memory Fix:** Reduced CV folds (5→3), limited n_jobs (4), reduced iterations
- **Expected R²:** ~0.60-0.70 (linear models, baseline)
- **Status:** 🔧 Memory optimized, ready to execute

### 4. `04_advanced_models_tuning.ipynb` - Tree Models with Hyperparameter Tuning
- **Input:** Preprocessed data from notebook 02
- **Output:** `models/best_advanced_model.joblib`, `models/advanced_models_results.csv`
- **Models:**
  - Random Forest (Steph's best model type)
  - Gradient Boosting
  - XGBoost (current best: 83.91% R²)
  - LightGBM
- **Tuning:** RandomizedSearchCV with 20-25 iterations, 3-fold CV
- **Target:** Beat Steph's 88.4% R²
- **Status:** 🆕 Ready for execution

### 5. `05_model_analysis.ipynb` - Visualization & Feature Importance
- **Input:** Best model from notebook 04
- **Output:** 
  - `plots/feature_importance_top30.png`
  - `plots/prediction_analysis.png`
  - `plots/error_distribution.png`
  - `plots/performance_by_price_range.png`
  - `plots/shap_summary.png`
  - `models/feature_importance.csv`
  - `models/shap_importance.csv`
- **Analysis:**
  - Feature importance from tree models
  - SHAP values for explainability
  - Prediction error analysis
  - Performance by price range
  - Feature correlations
- **Purpose:** Understand what drives predictions and identify improvement opportunities
- **Status:** 🆕 Ready for execution

### 6. `06_ensemble_models.ipynb` - Ensemble & Advanced Techniques
- **Input:** Preprocessed data from notebook 02
- **Output:** `models/best_ensemble_model.joblib`, `models/final_ensemble_summary.json`
- **Models:**
  - Voting Regressor (RF + XGB + LightGBM)
  - Stacking Regressor (Ridge meta-learner)
  - CatBoost
  - Weighted Blending
  - Neural Network (3-layer MLP)
- **Target:** Push beyond single model performance to exceed Steph's 88.4% R²
- **Status:** 🆕 Ready for execution

## Execution Order

### Quick Run (Recommended)
```powershell
# Run notebooks 4, 5, 6 (notebooks 1-2 already executed, 3 optional)
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/04_advanced_models_tuning.ipynb --inplace
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/05_model_analysis.ipynb --inplace
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/06_ensemble_models.ipynb --inplace
```

### Full Pipeline (From Scratch)
```powershell
# Execute all notebooks in sequence
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/01_data_loading.ipynb --inplace
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/02_preprocessing.ipynb --inplace
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/03_baseline_linear_models.ipynb --inplace
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/04_advanced_models_tuning.ipynb --inplace
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/05_model_analysis.ipynb --inplace
.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute notebooks_clean/06_ensemble_models.ipynb --inplace
```

## Key Differences from Steph's Pipeline

| Aspect | Steph | Our Pipeline |
|--------|-------|--------------|
| Data Source | `data/cleaned_enhanced.csv` (pre-processed) | `filled_data/` (raw monthly files) |
| Samples | 58,088 train | 150,311 train (2.6x more) |
| Features | 451 | 1,020 (2.3x more) |
| Target Encoding | Only 3 columns (City, MLSAreaMajor, CountyOrParish) | Threshold-based (600 unique values) |
| One-Hot Encoding | HighSchoolDistrict creates 406 features | All remaining categoricals |
| Property Types | Single Family Residential only (?) | All types (SFR filtering hurt performance) |
| Best Model | Random Forest 88.42% R² | XGBoost 83.91% R² (pre-tuning) |
| Data Split | Unknown | Temporal: months 1-7 train, 8 test |

## Improvement Journey

1. **Initial Problem:** 73.6% R² with only 65 features
   - Root cause: Too aggressive preprocessing (target encoding threshold = 50)
   
2. **Investigation Phase:**
   - Compared to Steph's 451 features
   - Tested data sources: `data/` vs `filled_data/` (same performance)
   - Tested SFR filtering (hurt performance: 77.82% → 74.65%)
   
3. **Optimization Phase:**
   - Increased target encoding threshold to 600
   - Removed SFR filter (all property types better)
   - Conservative leakage removal (only true leakage + >10K cardinality)
   - Result: 1,020 features, 83.91% R² with XGBoost
   
4. **Current Phase:** Hyperparameter tuning and ensemble methods to close 4.51% gap

## Memory Considerations

**Issue:** 150K samples × 1,020 features × 5-fold CV = ~7.5GB memory requirement

**Solution:**
- Reduced CV folds from 5 to 3 (saves 40% memory)
- Limited parallel jobs to 4 (prevents memory spikes)
- Reduced iterations (10-15 vs 20-30)
- Use tree_method='hist' for XGBoost (memory efficient)

**If still memory issues:**
- Reduce cv=3 to cv=2
- Reduce n_iter further (e.g., 20→10)
- Close other applications

## Dependencies

Install additional packages for new notebooks:
```powershell
.venv\Scripts\pip install shap>=0.42.0 catboost>=1.2.0
```

Or install from requirements.txt:
```powershell
.venv\Scripts\pip install -r requirements.txt
```

## Troubleshooting

### MemoryError in notebook 3
- Already fixed with reduced CV parameters
- If still occurs, reduce cv=3 to cv=2 or reduce n_iter further

### Slow execution in notebook 4/6
- Expected - hyperparameter tuning takes time
- Notebook 4: ~30-60 minutes (4 models × 20-25 iterations)
- Notebook 6: ~20-40 minutes (5 models, some pre-trained)
- Reduce n_iter in RandomizedSearchCV if needed (e.g., 20→10)

### SHAP calculation fails in notebook 5
- Normal for some model types
- Notebook will skip SHAP and continue with other analyses

### CatBoost not installed
- Install with: `.venv\Scripts\pip install catboost>=1.2.0`
- Or notebook will skip CatBoost and continue

## Expected Results

After executing all notebooks:

**Files Generated:**
- `data/X_train.csv`, `data/X_test.csv`, `data/y_train.csv`, `data/y_test.csv`
- `models/baseline_linear_results.csv`
- `models/advanced_models_results.csv`
- `models/ensemble_models_results.csv`
- `models/best_advanced_model.joblib`
- `models/best_ensemble_model.joblib`
- `models/feature_importance.csv`
- `models/shap_importance.csv`
- `models/final_ensemble_summary.json`
- `plots/*.png` (5+ visualization files)

**Performance Targets:**
- ✅ Beat initial 73.6% baseline (already done: 83.91%)
- 🎯 Match Steph's 88.4% R² (needs notebook 4 tuning)
- 🏆 Exceed 90% R² (stretch goal with ensemble methods)

## Next Steps

1. **Execute notebook 4** to find optimal hyperparameters
2. **Execute notebook 5** to understand feature importance
3. **Execute notebook 6** to test ensemble methods
4. **If still behind Steph:**
   - Analyze SHAP values for insights
   - Engineer domain-specific features
   - Try deeper neural networks
   - Investigate data quality issues
