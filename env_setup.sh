#!/bin/bash#!/bin/bash

# Environment setup script for Amarel cluster# Environment setup helper for Amarel (create conda env and install requirements)

# Run this once after uploading your project to set up the conda environment# Run as: bash env_setup.sh

# Usage: bash env_setup.sh

set -euo pipefail

set -e  # Exit on error

ENV_NAME=${ENV_NAME:-hp}

echo "=========================================="PYTHON_VERSION=${PYTHON_VERSION:-3.10}

echo "Setting up home-price-prediction environment on Amarel"

echo "=========================================="echo "Creating conda environment '$ENV_NAME' with Python $PYTHON_VERSION"



# Load conda module# Try to use mamba if available for speed, otherwise conda

echo "Loading conda module..."if command -v mamba >/dev/null 2>&1; then

module purge  echo "Using mamba to create environment"

module load conda  mamba create -n "$ENV_NAME" python="$PYTHON_VERSION" -y

else

# Create conda environment with Python 3.10 (more stable for ML packages)  echo "Using conda to create environment"

echo "Creating conda environment: home-price-env"  conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y

conda create -n home-price-env python=3.10 -yfi



# Activate environmentecho "Activating environment and installing dependencies"

echo "Activating environment..."source "$HOME/.bashrc" >/dev/null 2>&1 || true

source activate home-price-envconda activate "$ENV_NAME"



# Upgrade pipif [ -f requirements.txt ]; then

echo "Upgrading pip..."  pip install --upgrade pip

pip install --upgrade pip  pip install -r requirements.txt

fi

# Install core packages

echo "Installing core packages..."# Tools for notebook execution

pip install numpy pandas scikit-learnpip install --upgrade papermill nbconvert jupyter-client



# Install ML/stats packagesecho "Environment '$ENV_NAME' ready. Activate with: conda activate $ENV_NAME"

echo "Installing ML and statistical packages..."
pip install xgboost lightgbm catboost
pip install scipy statsmodels

# Install plotting
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
echo "To activate: source activate home-price-env"
echo "=========================================="
