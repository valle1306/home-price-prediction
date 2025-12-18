#!/bin/bash
#SBATCH --job-name=xgb_advanced
#SBATCH --output=logs/xgb_advanced_%j.out
#SBATCH --error=logs/xgb_advanced_%j.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00

# Advanced XGBoost tuning job - targeting 86%+ R²

echo "========================================="
echo "ADVANCED XGBOOST TUNING JOB"
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

# Run the advanced tuning script
echo ""
echo "Running advanced XGBoost tuning..."
python scripts/xgboost_advanced_tuning.py

echo ""
echo "========================================="
echo "Job completed: $(date)"
echo "========================================="
