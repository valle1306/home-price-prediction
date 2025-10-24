# Running Notebooks on Amarel Cluster

This guide will help you run your Jupyter notebooks on Rutgers' Amarel HPC cluster for faster execution.

## Prerequisites

- SSH access to Amarel: `ssh hpl14@amarel.rutgers.edu`
- Your local repo at: `c:\Users\lpnhu\Downloads\home-price-prediction`

## Step 1: Upload Your Project to Amarel

### Option A: Using rsync from Git Bash (Recommended)

Open **Git Bash** (not PowerShell - rsync works better there):

```bash
cd /c/Users/lpnhu/Downloads/home-price-prediction

# Upload project files (excludes .git, .venv, data folders)
rsync -avz --exclude='.git' --exclude='.venv' --exclude='data/' --exclude='filled_data/' \
  ./ hpl14@amarel.rutgers.edu:~/home-price-prediction/
```

### Option B: Using SCP from PowerShell

From PowerShell:

```powershell
# Upload entire project (slower, includes everything)
scp -r "c:\Users\lpnhu\Downloads\home-price-prediction" hpl14@amarel.rutgers.edu:~/
```

### Step 1b: Upload Your Data to Scratch Storage

Use **Git Bash** (data transfers work better with rsync):

```bash
cd /c/Users/lpnhu/Downloads/home-price-prediction

# Create scratch directory on Amarel and upload filled_data
rsync -avz --progress filled_data/ hpl14@amarel.rutgers.edu:/scratch/hpl14/home-price-data/filled_data/

# Optional: Also upload data folder if you have processed outputs
rsync -avz --progress data/ hpl14@amarel.rutgers.edu:/scratch/hpl14/home-price-data/data/
```

## Step 2: Set Up Environment on Amarel

SSH into Amarel (from PowerShell or Git Bash):

```bash
ssh hpl14@amarel.rutgers.edu
```

Once connected, navigate to your project and set up the environment:

```bash
# Go to your project directory
cd ~/home-price-prediction

# Create logs directory for job outputs
mkdir -p logs

# Run environment setup (takes ~10-15 minutes first time)
bash env_setup.sh

# Verify installation worked
python -c "import papermill; print('✓ Ready to run notebooks')"
```

## Step 3: Create Symlinks to Data (Optional but Recommended)

This way you don't need to edit notebook paths:

```bash
# Still on Amarel, in ~/home-price-prediction
cd ~/home-price-prediction

# Create symlinks to scratch storage
ln -s /scratch/hpl14/home-price-data/filled_data filled_data
ln -s /scratch/hpl14/home-price-data/data data

# Verify symlinks work
ls -lh filled_data/ data/
```

If you prefer to keep notebooks as-is without symlinks, edit the notebook paths:
- Change `ROOT = Path(r"c:\Users\...")` to `ROOT = Path.home() / "home-price-prediction"`
- Or change `RAW_DATA_DIR = ROOT / 'filled_data'` to `RAW_DATA_DIR = Path("/scratch/hpl14/home-price-data/filled_data")`

## Step 4: Run Notebooks

All commands below run on Amarel (while SSH'd in).

### Option A: Run All Notebooks in Parallel (FASTEST - 30-60 min total)

```bash
cd ~/home-price-prediction

# Submit all 6 notebooks as parallel array job
sbatch run_notebooks_array.sbatch

# Check job status
squeue -u hpl14

# Watch output in real-time (job ID shown by squeue)
tail -f logs/notebook_array_JOBID_0.out
```

### Option B: Run One Notebook

```bash
cd ~/home-price-prediction

# Run a specific notebook (waits for completion)
sbatch run_notebook.sbatch notebooks_clean/02_preprocessing.ipynb

# Check status
squeue -u hpl14
```

### Option C: Run Notebooks Sequentially

```bash
cd ~/home-price-prediction

# Submit jobs that depend on each other (runs one after another)
JOB1=$(sbatch --parsable run_notebook.sbatch notebooks_clean/01_data_loading.ipynb)
JOB2=$(sbatch --parsable --dependency=afterok:$JOB1 run_notebook.sbatch notebooks_clean/02_preprocessing.ipynb)
JOB3=$(sbatch --parsable --dependency=afterok:$JOB2 run_notebook.sbatch notebooks_clean/03_baseline_linear_models.ipynb)

squeue -u hpl14
```

## Step 5: Monitor & Troubleshoot Jobs

Monitor progress while running:

```bash
# Check all your running/completed jobs
squeue -u hpl14

# Get detailed job info
scontrol show job JOBID

# View real-time output
tail -f logs/notebook_array_JOBID_0.out

# View error log if something failed
cat logs/notebook_array_JOBID_0.err

# Get resource usage stats (after job completes)
sacct -j JOBID --format=JobID,MaxRSS,Elapsed,ExitCode
```

## Step 6: Download Results Back to Your Laptop

From **PowerShell** or **Git Bash** on your local machine:

```bash
# Option 1: Download executed notebooks only
rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/executed_notebooks/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/executed_notebooks/

# Option 2: Download models and outputs
rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/models/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/models/

# Option 3: Download processed data from scratch
rsync -avz hpl14@amarel.rutgers.edu:/scratch/hpl14/home-price-data/data/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/data/

# Option 4: Download everything at once
rsync -avz --exclude='.git' --exclude='filled_data' \
  hpl14@amarel.rutgers.edu:~/home-price-prediction/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/
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
