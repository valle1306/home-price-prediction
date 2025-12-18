"""
Home Price Prediction - Streamlit App

A professional web app showcasing our high-accuracy home price prediction model.

Features:
- Landing page with key metrics
- Interactive prediction tool
- Analysis & insights dashboard
- Model performance visualization
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page config - minimal, professional
st.set_page_config(
    page_title="Home Price Predictor",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sleek, professional design with smaller fonts
st.markdown("""
<style>
    /* Main color scheme - professional blues */
    :root {
        --primary-color: #4a5568;
        --secondary-color: #2d3748;
        --accent-color: #3182ce;
        --success-color: #38a169;
        --text-color: #2d3748;
    }
    
    /* Reduce base font size globally */
    html, body, [class*="css"] {
        font-size: 14px;
    }
    
    /* Hero section - professional gradient */
    .hero {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        padding: 2rem 1.5rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .hero h1 {
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .hero p {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    /* Metric cards - professional style */
    .metric-card {
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.25rem;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0.25rem 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Buttons - professional */
    .stButton>button {
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 0.375rem;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Cards - clean professional look */
    .info-card {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        margin: 0.75rem 0;
        border-left: 3px solid #3182ce;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    
    section[data-testid="stSidebar"] .stRadio label {
        color: white !important;
        font-size: 0.9rem !important;
    }
    
    section[data-testid="stSidebar"] .stRadio label span {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: white !important;
    }
    
    /* Headers - smaller */
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Reduce padding in main content */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load model and data
@st.cache_resource
def load_model():
    """Load the trained model"""
    ROOT = Path(__file__).parent
    MODELS_DIR = ROOT / 'models'
    
    try:
        # Priority 1: Ensemble models (best performance - 85.6% R²)
        model_path = MODELS_DIR / 'lightgbm_ensemble_best.joblib'
        if not model_path.exists():
            # Priority 2: XGBoost ensemble
            model_path = MODELS_DIR / 'xgboost_ensemble_best.joblib'
        if not model_path.exists():
            # Priority 3: chronological models
            model_path = MODELS_DIR / 'best_chronological_model.joblib'
        if not model_path.exists():
            # Fallback to XGBoost chronological
            model_path = MODELS_DIR / 'xgboost_chronological.joblib'
        if not model_path.exists():
            # Fallback to best advanced model
            model_path = MODELS_DIR / 'best_advanced_model.joblib'
        if not model_path.exists():
            # Final fallback
            model_path = MODELS_DIR / 'best_model_final.joblib'
        
        model = joblib.load(model_path)
        return model, str(model_path.name)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None

@st.cache_data
def load_metadata():
    """Load model metadata and results"""
    ROOT = Path(__file__).parent
    MODELS_DIR = ROOT / 'models'
    
    metadata = {}
    
    # Priority 1: Ensemble results (latest and best - 85.6% R²)
    summary_path = MODELS_DIR / 'ensemble_summary.json'
    if summary_path.exists():
        with open(summary_path) as f:
            metadata['summary'] = json.load(f)
    else:
        # Priority 2: chronological results
        summary_path = MODELS_DIR / 'chronological_results_summary.json'
        if summary_path.exists():
            with open(summary_path) as f:
                metadata['summary'] = json.load(f)
        else:
            # Fallback to final ensemble summary
            summary_path = MODELS_DIR / 'final_ensemble_summary.json'
            if summary_path.exists():
                with open(summary_path) as f:
                    metadata['summary'] = json.load(f)
            else:
                # Fallback to advanced models summary
                summary_path = MODELS_DIR / 'advanced_models_summary.json'
                if summary_path.exists():
                    with open(summary_path) as f:
                        metadata['summary'] = json.load(f)
    
    # Load ensemble results CSV if available
    results_path = MODELS_DIR / 'ensemble_results.csv'
    if results_path.exists():
        metadata['ensemble_results'] = pd.read_csv(results_path)
    
    # Load feature importance (chronological first)
    fi_path = MODELS_DIR / 'feature_importance_chronological.csv'
    if not fi_path.exists():
        fi_path = MODELS_DIR / 'feature_importance.csv'
    if fi_path.exists():
        metadata['feature_importance'] = pd.read_csv(fi_path)
    
    # Load feature schema
    schema_path = MODELS_DIR / 'feature_schema.json'
    if schema_path.exists():
        with open(schema_path) as f:
            metadata['feature_schema'] = json.load(f)
    
    # Load expected features (prefer sanitized version for model compatibility)
    expected_path = MODELS_DIR / 'expected_feature_columns_sanitized.json'
    if not expected_path.exists():
        expected_path = MODELS_DIR / 'expected_feature_columns.json'
    if expected_path.exists():
        with open(expected_path) as f:
            metadata['expected_features'] = json.load(f)
    
    return metadata

# Sidebar navigation - clean, professional
st.sidebar.markdown("""
<div style='text-align: center; padding: 1.5rem 0;'>
    <h2 style='color: white; margin: 0; font-size: 1.25rem;'>Home Price</h2>
    <h2 style='color: white; margin: 0; font-size: 1.25rem;'>Predictor</h2>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Predict", "Analysis"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='color: #a0aec0; padding: 0.75rem; text-align: center; font-size: 0.8rem;'>
    <p style='margin: 0;'>Powered by</p>
    <p style='margin: 0; color: white;'>XGBoost & LightGBM</p>
</div>
""", unsafe_allow_html=True)

# Load model and metadata
model, model_name = load_model()
metadata = load_metadata()

# Page routing - no emojis
if page == "Home":
    from views import home
    home.show(model, model_name, metadata)
elif page == "Predict":
    from views import predict
    predict.show(model, model_name, metadata)
elif page == "Analysis":
    from views import analysis
    analysis.show(model, model_name, metadata)
