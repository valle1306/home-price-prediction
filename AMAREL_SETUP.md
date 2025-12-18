# Running on Amarel Cluster

Quick guide to run the GPU-accelerated XGBoost training on Rutgers' Amarel cluster.

## Prerequisites

- SSH access: `ssh hpl14@amarel.rutgers.edu`
- Environment `home-price-env` already created on Amarel

## Quick Start

### 1. Push Changes from Local

```bash
# On your local machine
cd /c/Users/lpnhu/Downloads/home-price-prediction
git add -A
git commit -m "Update GPU XGBoost tuning"
git push
```

### 2. Pull on Amarel

```bash
# SSH to Amarel
ssh hpl14@amarel.rutgers.edu

# Navigate and pull
cd ~/home-price-prediction
git pull

# Create directories
mkdir -p logs executed_notebooks models
```

### 3. Submit GPU Job

```bash
# Submit the GPU training job
sbatch run_gpu_training.sbatch

# Monitor progress
squeue -u $USER
tail -f logs/gpu_tuning_*.out
```

### 4. Download Results

```bash
# From Git Bash on local machine
rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/models/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/models/

rsync -avz hpl14@amarel.rutgers.edu:~/home-price-prediction/executed_notebooks/ \
  /c/Users/lpnhu/Downloads/home-price-prediction/executed_notebooks/
```

## GPU Job Details

The `run_gpu_training.sbatch` script:
- Requests 1 GPU, 48GB RAM, 8 CPUs
- Runs all 6 notebooks in sequence
- Uses `device='cuda'` for XGBoost acceleration
- Expected runtime: 30-60 minutes total

## Troubleshooting

### Check job status
```bash
squeue -u $USER
sacct -j JOBID --format=JobID,State,Elapsed,MaxRSS
```

### View logs
```bash
cat logs/gpu_tuning_JOBID.out
cat logs/gpu_tuning_JOBID.err
```

### Check GPU availability
```bash
nvidia-smi
sinfo -p gpu
```

### Cancel job
```bash
scancel JOBID
```
