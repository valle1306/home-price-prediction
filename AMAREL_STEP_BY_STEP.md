# Amarel Execution: Complete Step-by-Step Guide

After `ssh hpl14@amarel.rutgers.edu`, follow these steps in order.

---

## Step 1: Check Your Home Directory

```bash
cd ~
pwd
# Should output: /home/hpl14
```

---

## Step 2: Upload Project from Local Machine

**STOP: Go back to your LOCAL machine (PowerShell) and run:**

```powershell
# On YOUR LOCAL MACHINE (PowerShell)
cd C:\Users\lpnhu\Downloads\home-price-prediction

# Upload entire project (scp will skip .git, .venv if on remote)
# This uploads the whole folder to Amarel
scp -r . hpl14@amarel.rutgers.edu:~/home-price-prediction/

Write-Output "✓ Project uploaded"
```

**Wait for this to complete** (should take 2-5 minutes). This uploads everything including notebooks and scripts.

---

## Step 3: Upload Data (from Local Machine)

**Still on YOUR LOCAL MACHINE (PowerShell), run:**

```powershell
# On YOUR LOCAL MACHINE (PowerShell)
cd C:\Users\lpnhu\Downloads\home-price-prediction

# Create scratch directory on Amarel
ssh hpl14@amarel.rutgers.edu "mkdir -p /scratch/hpl14/home-price-data"

# Upload filled_data folder (the main data you need)
scp -r filled_data hpl14@amarel.rutgers.edu:/scratch/hpl14/home-price-data/

Write-Output "✓ Data uploaded"
```

**Wait for this to complete** (may take 5-15 minutes depending on your data size). You'll see transfer progress on screen.

---

## Step 4: Verify Files Are on Amarel (SSH Terminal)

**Now back to your SSH terminal (already connected to Amarel):**

```bash
# Check project files
ls -lh ~/home-price-prediction/
# Should show: app.py, notebooks_clean/, pages/, requirements.txt, etc.

# Check data files
ls -lh /scratch/hpl14/home-price-data/filled_data/ | head -5
# Should show CSV files like: train_raw.csv, test_raw.csv, etc.
```

---

## Step 5: Navigate to Project Directory

```bash
cd ~/home-price-prediction

# Verify you're in the right place
pwd
# Should output: /home/hpl14/home-price-prediction

# List contents
ls -lh
```

---

## Step 6: Create Logs Directory

```bash
mkdir -p logs
mkdir -p executed_notebooks
```

---

## Step 7: Set Up Conda Environment

```bash
# Load conda module
module purge
module load conda

# Run setup script (takes ~10-15 minutes)
bash env_setup.sh

# Wait for it to complete... (lots of output is normal)
```

**When it finishes, you should see:**
```
✓ Core packages OK
✓ Papermill OK
Environment setup complete!
```

---

## Step 8: Verify Installation

```bash
# Activate environment
source activate home-price-env

# Test imports
python -c "import papermill, pandas, xgboost; print('✓ All packages OK')"
```

---

## Step 9: Create Symlinks to Data

```bash
# Still in ~/home-price-prediction
cd ~/home-price-prediction

# Create symlinks so notebooks find the data
ln -s /scratch/hpl14/home-price-data/filled_data filled_data
ln -s /scratch/hpl14/home-price-data/data data

# Verify
ls -lh filled_data data
# Should show: filled_data -> /scratch/hpl14/home-price-data/filled_data
```

---

## Step 10: Test One Notebook (Optional but Recommended)

```bash
# Test that everything works by running notebook 01 manually
papermill notebooks_clean/01_data_loading.ipynb executed_notebooks/01_data_loading_test.ipynb \
  --log-output

# Wait for it to finish (should take 5-10 minutes)
# Check for errors in the output
```

If this works, you're ready to proceed!

---

## Step 11: Submit All Notebooks (Option C - Sequential)

```bash
# Copy and paste this entire block:

cd ~/home-price-prediction

JOB1=$(sbatch --parsable run_notebook.sbatch notebooks_clean/01_data_loading.ipynb)
JOB2=$(sbatch --parsable --dependency=afterok:$JOB1 run_notebook.sbatch notebooks_clean/02_preprocessing.ipynb)
JOB3=$(sbatch --parsable --dependency=afterok:$JOB2 run_notebook.sbatch notebooks_clean/03_baseline_linear_models.ipynb)
JOB4=$(sbatch --parsable --dependency=afterok:$JOB3 run_notebook.sbatch notebooks_clean/04_advanced_models_tuning.ipynb)
JOB5=$(sbatch --parsable --dependency=afterok:$JOB4 run_notebook.sbatch notebooks_clean/05_model_analysis.ipynb)
JOB6=$(sbatch --parsable --dependency=afterok:$JOB5 run_notebook.sbatch notebooks_clean/06_ensemble_models.ipynb)

echo "Jobs submitted!"
echo "JOB1: $JOB1"
echo "JOB2: $JOB2 (waits for JOB1)"
echo "JOB3: $JOB3 (waits for JOB2)"
echo "JOB4: $JOB4 (waits for JOB3)"
echo "JOB5: $JOB5 (waits for JOB4)"
echo "JOB6: $JOB6 (waits for JOB5)"

# Check status
squeue -u hpl14
```

You should see output like:
```
Jobs submitted!
JOB1: 12345
JOB2: 12346 (waits for JOB1)
JOB3: 12347 (waits for JOB2)
...

JOBID PARTITION  NAME  USER ST  TIME  NODES NODELIST(REASON)
12345      main  job1 hpl14  R  0:05      1 node001
```

---

## Step 12: Monitor Progress

```bash
# Check status every few minutes
squeue -u hpl14

# Watch live output of current job
tail -f logs/notebook_*.out

# To stop watching (press Ctrl+C)
```

---

## Step 13: When Jobs Are Done

Check completion:
```bash
# See all your jobs (completed and running)
sacct -u hpl14 --format=JobID,JobName,State,ExitCode

# Look for State=COMPLETED for all jobs
```

---

## Step 14: Download Results (from Local Machine)

**Back on YOUR LOCAL MACHINE (PowerShell), run:**

```powershell
# From PowerShell on your laptop
cd C:\Users\lpnhu\Downloads\home-price-prediction

# Download executed notebooks
scp -r hpl14@amarel.rutgers.edu:~/home-price-prediction/executed_notebooks ./

# Download models and outputs
scp -r hpl14@amarel.rutgers.edu:~/home-price-prediction/models ./

Write-Output "✓ Results downloaded"
```

Open the executed notebooks in Jupyter to see results!

---

## Summary (TL;DR)

1. ✅ SSH to Amarel
2. ✅ Upload project from local machine
3. ✅ Upload data from local machine
4. ✅ Verify files exist on Amarel
5. ✅ Run `bash env_setup.sh` (on Amarel)
6. ✅ Create symlinks (on Amarel)
7. ✅ Test one notebook (optional)
8. ✅ Submit all 6 jobs (on Amarel)
9. ✅ Monitor with `squeue -u hpl14`
10. ✅ Download results when done (from local machine)

---

## Troubleshooting

**Q: "scp: command not found"**
- Make sure OpenSSH is installed (Windows 10+ has it built-in)
- Or install via PowerShell: `winget install OpenSSH.Client`

**Q: "No such file or directory: filled_data"**
- Make sure you're in the right directory: `pwd` should show `C:\Users\lpnhu\Downloads\home-price-prediction`
- Make sure you uploaded data in Step 3 before running setup

**Q: "Permission denied"**
- Check your SSH key setup: `ssh hpl14@amarel.rutgers.edu` should work
- Or use password authentication when prompted

**Q: "module load conda" doesn't work**
- Try: `module load miniconda3` or `module avail | grep conda`

**Q: Job failed immediately**
- Check error log: `cat logs/notebook_JOBID.err`
- Make sure symlinks are correct: `ls -lh ~/home-price-prediction/filled_data`

**Q: "Python not found"**
- Make sure environment is activated: `source activate home-price-env`

---

**Questions? Ask anytime!**
