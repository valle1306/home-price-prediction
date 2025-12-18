#!/bin/bash
#SBATCH --job-name=analysis-ensemble
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64GB
#SBATCH --time=02:00:00
#SBATCH --output=slurm-analysis-ensemble-%j.out

echo "=========================================="
echo "Analysis & Ensemble Models Pipeline"
echo "Script started at: $(date)"
echo "=========================================="

# Load modules
module purge
module load cuda/11.8

# Activate conda
source ~/.bashrc
conda activate home-price-env

# Set paths
cd /cache/home/hpl14/home-price-prediction

# Check GPU
echo ""
echo "GPU Information:"
nvidia-smi --query-gpu=name,memory.total --format=csv

# Environment info
echo ""
echo "Python: $(which python)"
echo "XGBoost version: $(python -c 'import xgboost; print(xgboost.__version__)')"
echo "LightGBM version: $(python -c 'import lightgbm; print(lightgbm.__version__)')"

# Check that XGBoost model exists
if [ ! -f "models/xgboost_tuned.joblib" ]; then
    echo "ERROR: xgboost_tuned.joblib not found!"
    exit 1
fi

echo ""
echo "=========================================="
echo "STAGE 1: Model Analysis"
echo "=========================================="
python -u executed/model_analysis.py

echo ""
echo "=========================================="
echo "STAGE 2: Ensemble Models"
echo "=========================================="
python -u executed/ensemble_models.py

echo ""
echo "=========================================="
echo "Pipeline complete at: $(date)"
echo "=========================================="
