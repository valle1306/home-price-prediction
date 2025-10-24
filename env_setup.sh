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
PYTHON_VERSION=${PYTHON_VERSION:-3.10}

echo "=========================================="
echo "Setting up home-price-prediction environment on Amarel"
echo "=========================================="
echo "Environment name: '$ENV_NAME'"
echo "Python version: $PYTHON_VERSION"

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

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install core packages
echo "Installing core packages..."
pip install numpy pandas scikit-learn

# Install ML packages
echo "Installing ML packages..."
pip install xgboost lightgbm catboost
pip install scipy statsmodels

# Install plotting libraries
echo "Installing plotting libraries..."
pip install matplotlib seaborn plotly

# Install Jupyter and notebook execution tools
echo "Installing Jupyter and papermill..."
pip install jupyter jupyterlab
pip install papermill nbconvert nbformat

# Install additional requirements from requirements.txt if present
if [ -f requirements.txt ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
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
