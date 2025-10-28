#!/bin/bash#!/bin/bash#!/bin/bash

#SBATCH --job-name=hp_notebook

#SBATCH --output=logs/notebook_%j.out#SBATCH --job-name=notebook_run# Single-notebook sbatch runner for Amarel (adjust resources as needed)

#SBATCH --error=logs/notebook_%j.err

#SBATCH --time=04:00:00#SBATCH --output=logs/notebook_%j.out# Usage: sbatch run_notebook.sbatch -- NOTEBOOK=notebooks_clean/02_preprocessing.ipynb

#SBATCH --mem=32G

#SBATCH --cpus-per-task=8#SBATCH --error=logs/notebook_%j.err

#SBATCH --partition=main

#!/bin/bash

# Single-notebook sbatch runner for Amarel (clean, robust)
# Usage: sbatch run_notebook.sbatch <notebook_path>

#SBATCH --job-name=hp_notebook
#SBATCH --output=logs/notebook_%j.out
#SBATCH --error=logs/notebook_%j.err
#SBATCH --time=06:00:00
#SBATCH --partition=main
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --ntasks=1

set -euo pipefail

# NOTEBOOK can be passed as first positional arg or via environment variable NOTEBOOK
NOTEBOOK=${1:-${NOTEBOOK:-}}

if [ -z "$NOTEBOOK" ]; then
    echo "Error: No notebook specified"
    echo "Usage: sbatch run_notebook.sbatch <notebook_path>"
    exit 1
fi

echo "=========================================="
echo "Running notebook: $NOTEBOOK"
echo "Job ID: ${SLURM_JOB_ID:-LOCAL}"
echo "Node: ${SLURM_NODELIST:-LOCAL}"
echo "Start time: $(date)"
echo "=========================================="

# Ensure output dirs exist (use working dir of the job)
mkdir -p logs executed_notebooks

# Initialize conda - try standard locations used on Amarel
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "/home/${USER}/miniconda3/etc/profile.d/conda.sh" ]; then
    source "/home/${USER}/miniconda3/etc/profile.d/conda.sh"
else
    # fallback to .bashrc (may already initialize conda)
    source "$HOME/.bashrc" >/dev/null 2>&1 || true
fi

# Activate the environment (best-effort)
if command -v conda >/dev/null 2>&1; then
    conda activate home-price-env || true
fi

OUTPUT_NOTEBOOK="executed_notebooks/$(basename "$NOTEBOOK")"

echo "Executing $NOTEBOOK -> $OUTPUT_NOTEBOOK"

# Run notebook using papermill (preferred)
if command -v papermill >/dev/null 2>&1; then
    papermill "$NOTEBOOK" "$OUTPUT_NOTEBOOK" --log-output --progress-bar
    EXIT_CODE=$?
else
    # Fallback to nbconvert execute
    jupyter nbconvert --to notebook --execute "$NOTEBOOK" --output "$OUTPUT_NOTEBOOK" --ExecutePreprocessor.timeout=0
    EXIT_CODE=$?
fi

echo "=========================================="
echo "Notebook execution completed"
echo "Exit code: $EXIT_CODE"
echo "End time: $(date)"
echo "=========================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: Notebook executed successfully"
    echo "Output saved to: $OUTPUT_NOTEBOOK"
    exit 0
else
    echo "ERROR: Notebook execution failed with code $EXIT_CODE"
    exit $EXIT_CODE
fi
    --progress-bar
