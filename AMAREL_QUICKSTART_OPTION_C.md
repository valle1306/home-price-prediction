# Amarel Quick Start: Option C - Sequential Notebook Execution

Run notebooks one-by-one with automatic dependencies (each waits for the previous to finish).

## Prerequisites
✅ Project uploaded to `~/home-price-prediction`  
✅ Data uploaded to `/scratch/hpl14/home-price-data/`  
✅ Environment created with `bash env_setup.sh`  
✅ Symlinks created: `ln -s /scratch/hpl14/home-price-data/filled_data filled_data`

## One-Command Submit (Copy & Paste)

```bash
cd ~/home-price-prediction
JOB1=$(sbatch --parsable run_notebook.sbatch notebooks_clean/01_data_loading.ipynb)
JOB2=$(sbatch --parsable --dependency=afterok:$JOB1 run_notebook.sbatch notebooks_clean/02_preprocessing.ipynb)
JOB3=$(sbatch --parsable --dependency=afterok:$JOB2 run_notebook.sbatch notebooks_clean/03_baseline_linear_models.ipynb)
JOB4=$(sbatch --parsable --dependency=afterok:$JOB3 run_notebook.sbatch notebooks_clean/04_advanced_models_tuning.ipynb)
JOB5=$(sbatch --parsable --dependency=afterok:$JOB4 run_notebook.sbatch notebooks_clean/05_model_analysis.ipynb)
JOB6=$(sbatch --parsable --dependency=afterok:$JOB5 run_notebook.sbatch notebooks_clean/06_ensemble_models.ipynb)

echo "Submitted 6 sequential jobs:"
squeue -u hpl14
```

## What This Does

- **JOB1**: Starts immediately (01_data_loading.ipynb)
- **JOB2**: Waits for JOB1 to succeed, then runs (02_preprocessing.ipynb)
- **JOB3**: Waits for JOB2 to succeed, then runs (03_baseline_linear_models.ipynb)
- **JOB4**: Waits for JOB3 to succeed, then runs (04_advanced_models_tuning.ipynb)
- **JOB5**: Waits for JOB4 to succeed, then runs (05_model_analysis.ipynb)
- **JOB6**: Waits for JOB5 to succeed, then runs (06_ensemble_models.ipynb)

If any job fails, remaining jobs are cancelled automatically.

## Monitor Progress

```bash
# Check status (run multiple times)
squeue -u hpl14

# Watch specific job output
tail -f logs/notebook_JOBID.out

# Check if a job finished (look for COMPLETED or FAILED)
sacct -u hpl14 --format=JobID,JobName,State,ExitCode
```

## Download Results When Done

```bash
# From your local machine (PowerShell or Git Bash)
rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/executed_notebooks/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/executed_notebooks/

rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/models/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/models/
```

## Why Option C?

✅ **Automatic flow**: Each notebook runs only after the previous succeeds  
✅ **Error handling**: Stops if any notebook fails  
✅ **Efficient**: No manual monitoring needed  
✅ **Suitable for**: When you need guaranteed sequential execution (e.g., 02 depends on 01's output)

---

**Total Runtime**: ~2-3 hours (vs 8+ hours locally)

**Alternative Options**:
- **Option A**: Run all 6 simultaneously (30-60 min) - use if notebooks are independent
- **Option B**: Run one notebook manually - use for testing/debugging
