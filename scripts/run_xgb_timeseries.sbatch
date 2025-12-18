#!/bin/bash
#SBATCH --job-name=xgb_timeseries
#SBATCH --output=logs/xgb_timeseries_%j.out
#SBATCH --error=logs/xgb_timeseries_%j.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00

# Time Series Features XGBoost job

echo "========================================="
echo "TIME SERIES XGBOOST JOB"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start: $(date)"
echo "========================================="

# Load modules
module purge
module load cuda/12.0

# Activate conda environment
source /home/hpl14/miniconda3/etc/profile.d/conda.sh
conda activate home-price-env

# Change to project directory
cd /home/hpl14/home-price-prediction

# Create logs directory
mkdir -p logs

# Run the time series script
echo ""
echo "Running time series feature engineering + XGBoost..."
python scripts/xgboost_timeseries.py

echo ""
echo "========================================="
echo "Job completed: $(date)"
echo "========================================="
