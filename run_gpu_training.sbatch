#!/bin/bash
#SBATCH --job-name=hp_gpu_tune
#SBATCH --output=logs/gpu_tuning_%j.out
#SBATCH --error=logs/gpu_tuning_%j.err
#SBATCH --time=04:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G

set -euo pipefail

echo "=========================================="
echo "Home Price Prediction - GPU XGBoost Tuning"
echo "=========================================="
echo "Job ID: ${SLURM_JOB_ID:-LOCAL}"
echo "Node: ${SLURM_NODELIST:-LOCAL}"
echo "Start time: $(date)"
echo "=========================================="

# Check GPU
echo ""
echo "GPU Information:"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv || echo "nvidia-smi not available"
echo ""

# Create output directories
mkdir -p logs executed_notebooks models

# Change to project directory
cd ~/home-price-prediction

# Initialize conda
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
    source "/opt/conda/etc/profile.d/conda.sh"
else
    source "$HOME/.bashrc" >/dev/null 2>&1 || true
fi

# Activate environment
conda activate home-price-env || {
    echo "Failed to activate home-price-env, trying hp..."
    conda activate hp || echo "Warning: Could not activate conda environment"
}

echo ""
echo "Python environment:"
python --version
python -c "import xgboost; print(f'XGBoost: {xgboost.__version__}')" || echo "XGBoost not installed"

# Run notebooks in sequence
echo ""
echo "=========================================="
echo "Running Notebooks"
echo "=========================================="

NOTEBOOKS=(
    "notebooks_clean/01_data_loading.ipynb"
    "notebooks_clean/02_preprocessing.ipynb"
    "notebooks_clean/03_baseline_linear_models.ipynb"
    "notebooks_clean/04_xgboost_gpu_tuning.ipynb"
    "notebooks_clean/05_model_analysis.ipynb"
    "notebooks_clean/06_ensemble_models.ipynb"
)

for nb in "${NOTEBOOKS[@]}"; do
    if [ -f "$nb" ]; then
        echo ""
        echo "Running: $nb"
        echo "Time: $(date)"
        
        OUTPUT="executed_notebooks/$(basename "$nb")"
        
        if command -v papermill >/dev/null 2>&1; then
            papermill "$nb" "$OUTPUT" -k python3 --log-output || {
                echo "Warning: $nb failed, continuing..."
            }
        else
            jupyter nbconvert --to notebook --execute "$nb" \
                --output-dir=executed_notebooks \
                --ExecutePreprocessor.timeout=7200 || {
                echo "Warning: $nb failed, continuing..."
            }
        fi
    else
        echo "Skipping (not found): $nb"
    fi
done

echo ""
echo "=========================================="
echo "Job Complete"
echo "=========================================="
echo "End time: $(date)"
echo ""
echo "Results saved to:"
echo "  - models/"
echo "  - executed_notebooks/"
echo ""

# Show model results if available
if [ -f "models/xgboost_gpu_tuned_params.json" ]; then
    echo "XGBoost Results:"
    cat models/xgboost_gpu_tuned_params.json
fi
