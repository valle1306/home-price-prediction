# Running Notebooks on Amarel Cluster

This guide will help you run your Jupyter notebooks on Rutgers' Amarel HPC cluster for faster execution.

## Prerequisites

- SSH access to Amarel: `ssh hpl14@amarel.rutgers.edu`
- Your local repo at: `c:\Users\lpnhu\Downloads\home-price-prediction`

## Step 1: Upload Your Project to Amarel

### Option A: Using rsync (Recommended - excludes unnecessary files)

From your local PowerShell or Git Bash:

```bash
# Upload project files (excludes .git, .venv, data folders)
rsync -avz --exclude='.git' --exclude='.venv' --exclude='data/' --exclude='filled_data/' \
  /c/Users/lpnhu/Downloads/home-price-prediction/ \
  hpl14@amarel.rutgers.edu:~/home-price-prediction/
```

### Option B: Using SCP

```bash
# From PowerShell/Git Bash (may be slower)
scp -r c:\Users\lpnhu\Downloads\home-price-prediction hpl14@amarel.rutgers.edu:~/
```

### Upload Your Data Separately

The data should be uploaded to Amarel's scratch storage for better performance:

```bash
# Upload filled_data (the source data with lat/lon)
rsync -avz --progress /c/Users/lpnhu/Downloads/home-price-prediction/filled_data/ \
  hpl14@amarel.rutgers.edu:/scratch/hpl14/home-price-data/filled_data/

# Upload data folder if needed
rsync -avz --progress /c/Users/lpnhu/Downloads/home-price-prediction/data/ \
  hpl14@amarel.rutgers.edu:/scratch/hpl14/home-price-data/data/
```

## Step 2: Set Up Environment on Amarel

SSH into Amarel:

```bash
ssh hpl14@amarel.rutgers.edu
```

Navigate to your project and set up the environment:

```bash
cd ~/home-price-prediction

# Create logs directory
mkdir -p logs

# Run environment setup (this takes ~10-15 minutes)
bash env_setup.sh
```

## Step 3: Update Notebook Paths for Amarel

You'll need to update the paths in your notebooks to point to the scratch storage. Edit `notebooks_clean/02_preprocessing.ipynb` (and others) to use:

```python
# Change from:
ROOT = Path(r"c:\Users\lpnhu\Downloads\home-price-prediction")

# To:
ROOT = Path("/scratch/hpl14/home-price-data")
# or keep home directory for outputs:
ROOT = Path.home() / "home-price-prediction"
```

Or create a symlink to avoid editing notebooks:

```bash
cd ~/home-price-prediction
ln -s /scratch/hpl14/home-price-data/filled_data filled_data
ln -s /scratch/hpl14/home-price-data/data data
```

## Step 4: Run Notebooks

### Option A: Run All Notebooks in Parallel (Fastest - ~30-60 min total)

```bash
cd ~/home-price-prediction
sbatch run_notebooks_array.sbatch
```

This submits 6 jobs simultaneously, one for each notebook. Check status:

```bash
# Check job status
squeue -u hpl14

# Watch output in real-time (replace JOBID)
tail -f logs/notebook_array_JOBID_0.out
```

### Option B: Run One Notebook at a Time

```bash
# Run a specific notebook
sbatch run_notebook.sbatch notebooks_clean/02_preprocessing.ipynb

# Run multiple notebooks sequentially
sbatch run_notebook.sbatch notebooks_clean/02_preprocessing.ipynb
sbatch run_notebook.sbatch notebooks_clean/03_baseline_linear_models.ipynb
sbatch run_notebook.sbatch notebooks_clean/04_advanced_models_tuning.ipynb
```

## Step 5: Monitor Jobs

```bash
# Check all your jobs
squeue -u hpl14

# Check job details
scontrol show job JOBID

# View output logs (replace JOBID with actual number)
cat logs/notebook_JOBID.out
cat logs/notebook_JOBID.err

# Watch live output
tail -f logs/notebook_JOBID.out
```

## Step 6: Download Results

After jobs complete, download the executed notebooks and models:

```bash
# From your local machine (PowerShell/Git Bash)

# Download executed notebooks
rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/executed_notebooks/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/executed_notebooks/

# Download models
rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/models/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/models/

# Download processed data
rsync -avz hpl14@amarel.rutgers.edu:/scratch/hpl14/home-price-data/data/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/data/
```

## Troubleshooting

### If a job fails:

1. Check error log:
   ```bash
   cat logs/notebook_JOBID.err
   ```

2. Check if data paths are correct:
   ```bash
   ls -lh /scratch/hpl14/home-price-data/filled_data/
   ```

3. Test notebook manually:
   ```bash
   source activate home-price-env
   jupyter nbconvert --to notebook --execute notebooks_clean/02_preprocessing.ipynb
   ```

### Adjust resources if needed:

Edit `run_notebook.sbatch` or `run_notebooks_array.sbatch`:

```bash
#SBATCH --mem=64G        # Increase memory
#SBATCH --time=08:00:00  # Increase time limit
#SBATCH --cpus-per-task=16  # More CPUs
```

### Check available partitions:

```bash
sinfo
```

## Tips for Faster Execution

1. **Use scratch storage**: Always store large data in `/scratch/hpl14/` for better I/O
2. **Run in parallel**: Use the array job script to run all notebooks simultaneously
3. **Monitor resources**: Check `sacct -j JOBID --format=JobID,MaxRSS,Elapsed` to optimize memory/time
4. **Clean up**: Remove old log files with `rm logs/*.out logs/*.err`

## Expected Runtime on Amarel

- **01_data_loading.ipynb**: ~5-10 min
- **02_preprocessing.ipynb**: ~15-30 min
- **03_baseline_linear_models.ipynb**: ~10-20 min
- **04_advanced_models_tuning.ipynb**: ~30-60 min (longest)
- **05_model_analysis.ipynb**: ~5-10 min
- **06_ensemble_models.ipynb**: ~20-40 min

**Total (parallel)**: ~30-60 min vs. several hours locally!
