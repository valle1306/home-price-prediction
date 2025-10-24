"""
Home Price Prediction - Streamlit App

A beautiful, intuitive web app showcasing our high-accuracy home price prediction model.

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

# Page config
st.set_page_config(
    page_title="Home Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sleek design
st.markdown("""
<style>
    /* Main color scheme */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #4facfe;
        --text-color: #2d3748;
    }
    
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    .hero h1 {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero p {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-bottom: 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load model and data
@st.cache_resource
def load_model():
    """Load the trained model"""
    ROOT = Path(__file__).parent
    MODELS_DIR = ROOT / 'models'
    
    try:
        # Try to load best ensemble model first
        model_path = MODELS_DIR / 'best_ensemble_model.joblib'
        if not model_path.exists():
            # Fallback to best advanced model
            model_path = MODELS_DIR / 'best_advanced_model.joblib'
        if not model_path.exists():
            # Final fallback to best model
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
    
    # Try to load final ensemble summary
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
    
    # Load feature importance
    fi_path = MODELS_DIR / 'feature_importance.csv'
    if fi_path.exists():
        metadata['feature_importance'] = pd.read_csv(fi_path)
    
    # Load feature schema
    schema_path = MODELS_DIR / 'feature_schema.json'
    if schema_path.exists():
        with open(schema_path) as f:
            metadata['feature_schema'] = json.load(f)
    
    # Load expected features
    expected_path = MODELS_DIR / 'expected_feature_columns.json'
    if expected_path.exists():
        with open(expected_path) as f:
            metadata['expected_features'] = json.load(f)
    
    return metadata

# Sidebar navigation
st.sidebar.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='color: white; font-size: 2rem;'>🏠</h1>
    <h2 style='color: white; margin: 0;'>Home Price</h2>
    <h2 style='color: white; margin: 0;'>Predictor</h2>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigate",
    ["🏡 Home", "🎯 Predict", "📊 Analysis", "ℹ️ About"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='color: white; padding: 1rem; text-align: center;'>
    <p style='margin: 0; font-size: 0.9rem;'>Built with ❤️ using</p>
    <p style='margin: 0; font-weight: bold;'>Streamlit & Python</p>
</div>
""", unsafe_allow_html=True)

# Load model and metadata
model, model_name = load_model()
metadata = load_metadata()

# Page routing
if page == "🏡 Home":
    from pages import home
    home.show(model, model_name, metadata)
elif page == "🎯 Predict":
    from pages import predict
    predict.show(model, model_name, metadata)
elif page == "📊 Analysis":
    from pages import analysis
    analysis.show(model, model_name, metadata)
else:
    from pages import about
    about.show(metadata)
