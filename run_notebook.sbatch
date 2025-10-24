#!/bin/bash#!/bin/bash

#SBATCH --job-name=notebook_run# Single-notebook sbatch runner for Amarel (adjust resources as needed)

#SBATCH --output=logs/notebook_%j.out# Usage: sbatch run_notebook.sbatch -- NOTEBOOK=notebooks_clean/02_preprocessing.ipynb

#SBATCH --error=logs/notebook_%j.err

#SBATCH --time=04:00:00#SBATCH --job-name=hp_nb

#SBATCH --mem=32G#SBATCH --output=slurm-%j.out

#SBATCH --cpus-per-task=8#SBATCH --error=slurm-%j.err

#SBATCH --partition=main#SBATCH --time=06:00:00

#SBATCH --partition=compute

# Single notebook execution script for Amarel#SBATCH --ntasks=1

# Usage: sbatch run_notebook.sbatch <notebook_name.ipynb>#SBATCH --cpus-per-task=8

# Example: sbatch run_notebook.sbatch notebooks_clean/02_preprocessing.ipynb#SBATCH --mem=32G

#SBATCH --mail-type=END,FAIL

NOTEBOOK=$1#SBATCH --mail-user=you@example.com



if [ -z "$NOTEBOOK" ]; thenset -euo pipefail

    echo "Error: No notebook specified"

    echo "Usage: sbatch run_notebook.sbatch <notebook_path>"echo "Starting single-notebook job on $(hostname)"

    exit 1

fi# Allow notebook override from sbatch -- NOTEBOOK=...

NOTEBOOK=${NOTEBOOK:-"notebooks_clean/02_preprocessing.ipynb"}

echo "=========================================="

echo "Running notebook: $NOTEBOOK"# Location on cluster

echo "Job ID: $SLURM_JOB_ID"SCRATCH_DIR=${SCRATCH:-/scratch/$USER}/home-price-prediction

echo "Node: $SLURM_NODELIST"mkdir -p "$SCRATCH_DIR"

echo "Start time: $(date)"

echo "=========================================="echo "Working dir: $SCRATCH_DIR"



# Load conda module (adjust based on Amarel's module system)cd "$SCRATCH_DIR"

module purge

module load condaecho "Activating environment..."

# Load conda module if available - adjust to your cluster modules

# Activate your conda environmentmodule load anaconda || true

source activate home-price-envsource "$HOME/.bashrc" >/dev/null 2>&1 || true

conda activate hp || echo "Activate failed - ensure env 'hp' exists"

# Create output directory for executed notebooks

mkdir -p executed_notebooksmkdir -p executed

OUT=executed/$(basename "${NOTEBOOK%.*}")_$(date +%Y%m%d-%H%M%S).ipynb

# Get notebook name without path

NOTEBOOK_NAME=$(basename "$NOTEBOOK")echo "Executing $NOTEBOOK -> $OUT"

OUTPUT_NOTEBOOK="executed_notebooks/${NOTEBOOK_NAME}"# Use papermill if available for better logging; fallback to nbconvert

if command -v papermill >/dev/null 2>&1; then

# Run notebook using papermill (preserves output)  papermill "$NOTEBOOK" "$OUT" -k python3 --log-output

echo "Executing notebook with papermill..."else

papermill "$NOTEBOOK" "$OUTPUT_NOTEBOOK" \  jupyter nbconvert --to notebook --execute "$NOTEBOOK" --output "$OUT" --ExecutePreprocessor.timeout=0

    --log-output \fi

    --progress-bar

echo "Notebook finished. Output saved to $OUT"

EXIT_CODE=$?

echo "=========================================="
echo "Notebook execution completed"
echo "Exit code: $EXIT_CODE"
echo "End time: $(date)"
echo "=========================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: Notebook executed successfully"
    echo "Output saved to: $OUTPUT_NOTEBOOK"
else
    echo "ERROR: Notebook execution failed"
    exit $EXIT_CODE
fi
