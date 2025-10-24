#!/bin/bash#!/bin/bash

#SBATCH --job-name=notebooks_array# Array sbatch to run multiple notebooks in parallel on Amarel

#SBATCH --output=logs/notebook_array_%A_%a.out# Edit NOTEBOOKS array below to select which notebooks to run

#SBATCH --error=logs/notebook_array_%A_%a.err

#SBATCH --array=0-5#SBATCH --job-name=hp_nb_array

#SBATCH --time=04:00:00#SBATCH --output=slurm-%A_%a.out

#SBATCH --mem=32G#SBATCH --error=slurm-%A_%a.err

#SBATCH --cpus-per-task=8#SBATCH --time=08:00:00

#SBATCH --partition=main#SBATCH --partition=compute

#SBATCH --ntasks=1

# Array job to run multiple notebooks in parallel on Amarel#SBATCH --cpus-per-task=6

# This runs all 6 notebooks from notebooks_clean/ simultaneously#SBATCH --mem=24G

# Usage: sbatch run_notebooks_array.sbatch#SBATCH --array=1-5

#SBATCH --mail-type=END,FAIL

# Define array of notebooks to run#SBATCH --mail-user=you@example.com

NOTEBOOKS=(

    "notebooks_clean/01_data_loading.ipynb"set -euo pipefail

    "notebooks_clean/02_preprocessing.ipynb"

    "notebooks_clean/03_baseline_linear_models.ipynb"echo "Array job starting on $(hostname)"

    "notebooks_clean/04_advanced_models_tuning.ipynb"

    "notebooks_clean/05_model_analysis.ipynb"SCRATCH_DIR=${SCRATCH:-/scratch/$USER}/home-price-prediction

    "notebooks_clean/06_ensemble_models.ipynb"mkdir -p "$SCRATCH_DIR"

)cd "$SCRATCH_DIR"



# Get the notebook for this array taskmodule load anaconda || true

NOTEBOOK=${NOTEBOOKS[$SLURM_ARRAY_TASK_ID]}source "$HOME/.bashrc" >/dev/null 2>&1 || true

conda activate hp || echo "Activate failed - ensure env 'hp' exists"

echo "=========================================="

echo "Array Job ID: $SLURM_ARRAY_JOB_ID"# NOTE: Edit this list to control which notebooks the array runs (order matters)

echo "Task ID: $SLURM_ARRAY_TASK_ID"NOTEBOOKS=(

echo "Running notebook: $NOTEBOOK"  "notebooks_clean/02_preprocessing.ipynb"

echo "Node: $SLURM_NODELIST"  "notebooks_clean/03_baseline_linear_models.ipynb"

echo "Start time: $(date)"  "notebooks_clean/04_advanced_models_tuning.ipynb"

echo "=========================================="  "notebooks_clean/05_model_analysis.ipynb"

  "notebooks_clean/06_ensemble_models.ipynb"

# Load conda module)

module purge

module load condaIDX=$((SLURM_ARRAY_TASK_ID - 1))

NOTEBOOK=${NOTEBOOKS[$IDX]}

# Activate your conda environment

source activate home-price-envecho "Running task ${SLURM_ARRAY_TASK_ID}: $NOTEBOOK"



# Create output directorymkdir -p executed

mkdir -p executed_notebooksOUT=executed/$(basename "${NOTEBOOK%.*}")_job${SLURM_ARRAY_JOB_ID}_task${SLURM_ARRAY_TASK_ID}.ipynb



# Get notebook name without pathif command -v papermill >/dev/null 2>&1; then

NOTEBOOK_NAME=$(basename "$NOTEBOOK")  papermill "$NOTEBOOK" "$OUT" -k python3 --log-output

OUTPUT_NOTEBOOK="executed_notebooks/${NOTEBOOK_NAME}"else

  jupyter nbconvert --to notebook --execute "$NOTEBOOK" --output "$OUT" --ExecutePreprocessor.timeout=0

# Run notebook using papermillfi

echo "Executing notebook with papermill..."

papermill "$NOTEBOOK" "$OUTPUT_NOTEBOOK" \echo "Finished $NOTEBOOK -> $OUT"

    --log-output \
    --progress-bar

EXIT_CODE=$?

echo "=========================================="
echo "Notebook execution completed"
echo "Exit code: $EXIT_CODE"
echo "End time: $(date)"
echo "=========================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: Notebook $NOTEBOOK executed successfully"
    echo "Output saved to: $OUTPUT_NOTEBOOK"
else
    echo "ERROR: Notebook $NOTEBOOK execution failed"
    exit $EXIT_CODE
fi
