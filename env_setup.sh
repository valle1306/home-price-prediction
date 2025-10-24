#!/bin/bash

# Environment setup script for Amarel cluster
# Run this once after cloning/uploading your project to set up the conda environment
# Usage: bash env_setup.sh
# Must be run on a computing node: salloc -N 1 -n 8 --mem=32GB -t 4:00:00

set -e  # Exit on error

# Initialize conda if not already initialized
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
    echo "ERROR: Conda not found. Please install miniconda first."
    exit 1
fi

ENV_NAME=${ENV_NAME:-home-price-env}
PYTHON_VERSION=${PYTHON_VERSION:-3.9}

echo "=========================================="
echo "Setting up home-price-prediction environment on Amarel"
echo "=========================================="
echo "Environment name: '$ENV_NAME'"
echo "Python version: $PYTHON_VERSION"

# Remove environment if it exists
conda remove -n "$ENV_NAME" --all -y 2>/dev/null || true

# Try to use mamba if available for speed, otherwise conda
if command -v mamba >/dev/null 2>&1; then
    echo "Using mamba to create environment..."
    mamba create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
else
    echo "Using conda to create environment..."
    conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
fi

# Activate environment
echo "Activating environment..."
conda activate "$ENV_NAME"

# Install packages using default conda channels (no internet required)
echo "Installing core packages..."
conda install numpy pandas scikit-learn -y

# Install ML packages
echo "Installing ML packages..."
conda install xgboost lightgbm -y

# Install stats packages
echo "Installing statistical packages..."
conda install scipy statsmodels -y

# Install plotting libraries
echo "Installing plotting libraries..."
conda install matplotlib seaborn plotly -y

# Install Jupyter and tools
echo "Installing Jupyter and papermill..."
conda install jupyter jupyterlab -y

# Upgrade pip and install papermill via pip (smaller, faster)
echo "Upgrading pip..."
pip install --upgrade pip --no-index 2>/dev/null || pip install --upgrade pip

echo "Installing papermill..."
pip install papermill nbconvert nbformat 2>&1 | grep -v "already satisfied" || true

# Install additional requirements from requirements.txt if present
if [ -f requirements.txt ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt 2>&1 | grep -v "already satisfied" || true
fi

# Verify installation
echo ""
echo "=========================================="
echo "Verifying installation..."
echo "=========================================="
python -c "import numpy, pandas, sklearn, xgboost; print('✓ Core packages OK')"
python -c "import papermill; print('✓ Papermill OK')"
echo ""
echo "Environment setup complete!"
echo "To activate: conda activate $ENV_NAME"
echo "=========================================="
