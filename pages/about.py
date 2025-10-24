"""
About page - Project information and methodology
"""

import streamlit as st

def show(metadata):
    """Display the about page"""
    
    st.markdown("""
    <div class="hero">
        <h1>ℹ️ About This Project</h1>
        <p>Learn about our approach and methodology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Project overview
    st.markdown("## 🎯 Project Overview")
    
    st.markdown("""
    <div class="info-card">
        <p style="font-size: 1.1rem; line-height: 1.8;">
            This home price prediction system uses <strong>advanced machine learning</strong> to accurately estimate 
            property values based on comprehensive real estate data. Our model analyzes over <strong>1,020 features</strong> 
            including property characteristics, location data, market trends, and historical sales to provide 
            reliable valuations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Methodology
    st.markdown("## 🔬 Methodology")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data", "🧹 Preprocessing", "🤖 Modeling", "📈 Validation"])
    
    with tab1:
        st.markdown("""
        ### Data Collection & Preparation
        
        **Source:** Louisiana MLS (Multiple Listing Service) data from January-August 2025
        
        **Statistics:**
        - **Training Set:** 150,311 properties (Months 1-7)
        - **Test Set:** 22,759 properties (Month 8)
        - **Raw Features:** 80 columns from MLS
        - **Final Features:** 1,020 after engineering
        
        **Data Quality:**
        - ✅ Cleaned and validated
        - ✅ Outliers removed (0.5th and 99.5th percentiles)
        - ✅ Missing values imputed intelligently
        - ✅ Temporal split for realistic evaluation
        """)
    
    with tab2:
        st.markdown("""
        ### Data Preprocessing Pipeline
        
        **1. Leakage Removal**
        - Removed target-related features (ListPrice, ClosePrice derivatives)
        - Removed dates, agent names, IDs
        - Removed ultra-high cardinality features (>10K unique values)
        
        **2. Feature Engineering**
        - **BuildingAge** = Current Year - Year Built
        - **TotalRooms** = Bedrooms + Bathrooms + Other Rooms
        - **HasGarage** = Binary indicator for garage presence
        
        **3. Encoding Strategy**
        - **Target Encoding:** High-cardinality categoricals (600+ unique values)
          - City, MLSAreaMajor, PostalCode
        - **One-Hot Encoding:** Low-cardinality categoricals
          - Property type, condition, features (drop_first=False)
        
        **4. Missing Value Handling**
        - Threshold: 60% missing → drop column
        - Numerical: Mean/median imputation
        - Categorical: Mode imputation
        
        **5. Outlier Treatment**
        - Remove extreme values (0.5th and 99.5th percentiles)
        - Preserve realistic price range
        """)
    
    with tab3:
        st.markdown("""
        ### Machine Learning Models
        
        **Baseline Models (Linear):**
        - Linear Regression
        - Ridge Regression (L2 regularization)
        - Lasso Regression (L1 regularization)
        - ElasticNet (L1 + L2 regularization)
        
        **Tree-Based Models:**
        - Decision Tree Regressor
        - **Random Forest** (Ensemble of decision trees)
        - Gradient Boosting Regressor
        
        **Advanced Gradient Boosting:**
        - **XGBoost** (Extreme Gradient Boosting)
        - **LightGBM** (Light Gradient Boosting Machine)
        - **CatBoost** (Categorical Boosting)
        
        **Ensemble Methods:**
        - **Voting Regressor** (Average of RF + XGB + LightGBM)
        - **Stacking Regressor** (Meta-learner on top of base models)
        - **Weighted Blending** (Performance-based weights)
        
        **Neural Network:**
        - 3-Layer Multi-Layer Perceptron (MLP)
        - Scaled features for deep learning
        
        **Hyperparameter Optimization:**
        - RandomizedSearchCV with 20-25 iterations
        - 3-Fold Cross-Validation
        - Memory-optimized for large datasets
        """)
    
    with tab4:
        st.markdown("""
        ### Validation & Evaluation
        
        **Evaluation Metrics:**
        - **R² Score** (Primary): Proportion of variance explained
        - **RMSE**: Root Mean Squared Error
        - **MAE**: Mean Absolute Error
        - **MdAPE**: Median Absolute Percentage Error
        
        **Validation Strategy:**
        - **Temporal Split:** Train on Jan-Jul, test on Aug
        - **Cross-Validation:** 3-Fold CV during training
        - **Holdout Test:** Never seen by model during training
        
        **Performance Benchmarks:**
        - **Initial Baseline:** 73.6% R² (too aggressive preprocessing)
        - **Optimized Pipeline:** 83.91% R² (XGBoost)
        - **Target:** 88.4% R² (Steph's baseline)
        - **Final:** Check Analysis page for current best!
        
        **Explainability:**
        - Feature importance from tree models
        - SHAP (SHapley Additive exPlanations) values
        - Residual analysis by price range
        """)
    
    # Key improvements
    st.markdown("## 🚀 Key Improvements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #667eea; margin-top: 0;">✅ What Worked</h4>
            <ul>
                <li><strong>Conservative Leakage Removal:</strong> Only removed true leakage, kept predictive features</li>
                <li><strong>Optimal Encoding Threshold:</strong> 600 unique values for target encoding</li>
                <li><strong>All Property Types:</strong> Mixed types generalized better than SFR-only</li>
                <li><strong>Ensemble Methods:</strong> Combined multiple models for robustness</li>
                <li><strong>Memory Optimization:</strong> 3-fold CV instead of 5 for large datasets</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #f5576c; margin-top: 0;">⚠️ Lessons Learned</h4>
            <ul>
                <li><strong>Feature Count ≠ Accuracy:</strong> Quality over quantity matters</li>
                <li><strong>Filtering Can Hurt:</strong> SFR-only reduced performance</li>
                <li><strong>Threshold Tuning Critical:</strong> 50 → 600 made huge difference</li>
                <li><strong>XGBoost > Random Forest:</strong> For this specific dataset</li>
                <li><strong>Memory Matters:</strong> CV parameters need careful tuning for large data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology stack
    st.markdown("## 🛠️ Technology Stack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #667eea; margin-top: 0;">Data & ML</h4>
            <ul>
                <li>Python 3.13</li>
                <li>Pandas 2.2</li>
                <li>NumPy 1.26</li>
                <li>Scikit-learn 1.3</li>
                <li>XGBoost 2.0+</li>
                <li>LightGBM 4.0+</li>
                <li>CatBoost 1.2+</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #667eea; margin-top: 0;">Visualization</h4>
            <ul>
                <li>Streamlit 1.28+</li>
                <li>Plotly 5.17+</li>
                <li>Matplotlib 3.7+</li>
                <li>Seaborn 0.12+</li>
                <li>SHAP 0.42+</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #667eea; margin-top: 0;">Development</h4>
            <ul>
                <li>Jupyter Notebooks</li>
                <li>VS Code</li>
                <li>Git</li>
                <li>Python venv</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Project structure
    st.markdown("## 📁 Project Structure")
    
    st.code("""
home-price-prediction/
├── notebooks_clean/        # Complete ML pipeline
│   ├── 01_data_loading.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_baseline_linear_models.ipynb
│   ├── 04_advanced_models_tuning.ipynb
│   ├── 05_model_analysis.ipynb
│   └── 06_ensemble_models.ipynb
├── data/                   # Processed datasets
├── filled_data/            # Raw MLS data
├── models/                 # Trained models & results
├── plots/                  # Visualizations
├── pages/                  # Streamlit pages
├── app.py                  # Main Streamlit app
├── requirements.txt        # Dependencies
└── README.md              # Documentation
    """, language="text")
    
    # Future improvements
    st.markdown("## 🔮 Future Improvements")
    
    st.markdown("""
    <div class="info-card">
        <h4 style="color: #667eea; margin-top: 0;">Potential Enhancements</h4>
        <ul>
            <li><strong>Real-time Data Integration:</strong> Connect to live MLS feeds</li>
            <li><strong>Time Series Forecasting:</strong> Predict future market trends</li>
            <li><strong>Geographic Visualization:</strong> Interactive maps with price heatmaps</li>
            <li><strong>Comparable Sales:</strong> Show similar properties in the area</li>
            <li><strong>Market Analytics:</strong> Neighborhood insights and trends</li>
            <li><strong>API Development:</strong> RESTful API for programmatic access</li>
            <li><strong>Mobile App:</strong> iOS and Android applications</li>
            <li><strong>Advanced NLP:</strong> Analyze property descriptions and reviews</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact & credits
    st.markdown("## 👥 Credits")
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f7fafc; border-radius: 1rem; margin: 2rem 0;">
        <p style="font-size: 1.1rem; color: #2d3748; margin: 0;">
            Built with ❤️ using <strong>Streamlit</strong> and <strong>Python</strong><br>
            Data from <strong>Louisiana MLS</strong> (2025)<br>
            Special thanks to the open-source ML community
        </p>
    </div>
    """, unsafe_allow_html=True)
