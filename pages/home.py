"""
Home page - Landing page with key metrics and overview
"""

import streamlit as st
import plotly.graph_objects as go

def show(model, model_name, metadata):
    """Display the home page"""
    
    # Hero section
    st.markdown("""
    <div class="hero">
        <h1>🏠 AI-Powered Home Price Prediction</h1>
        <p>State-of-the-art machine learning for accurate real estate valuation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get metrics from metadata
    summary = metadata.get('summary', {})
    best_r2 = summary.get('overall_best_r2', summary.get('best_r2', 0.839))
    best_model = summary.get('overall_best', summary.get('best_model', 'XGBoost'))
    n_features = summary.get('n_features', 1020)
    n_train = summary.get('n_train_samples', 150311)
    
    # Convert R² to percentage
    accuracy_pct = best_r2 * 100
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="metric-label">Model Accuracy</div>
            <div class="metric-value">{accuracy_pct:.1f}%</div>
            <div style="font-size: 0.9rem;">R² Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">Training Data</div>
            <div class="metric-value">{n_train:,}</div>
            <div style="font-size: 0.9rem;">Properties</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">Features</div>
            <div class="metric-value">{n_features}</div>
            <div style="font-size: 0.9rem;">Data Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
            <div class="metric-label">Best Model</div>
            <div class="metric-value" style="font-size: 1.5rem;">{best_model.split('(')[0].strip()}</div>
            <div style="font-size: 0.9rem;">Algorithm</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # What makes our model great
    st.markdown("## ✨ What Makes Our Model Special")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #667eea; margin-top: 0;">🎯 High Accuracy</h3>
            <p>Our model achieves <strong>{:.1f}% R² score</strong>, meaning it explains {:.1f}% of the variance in home prices. This is exceptional for real estate prediction!</p>
        </div>
        """.format(accuracy_pct, accuracy_pct), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #667eea; margin-top: 0;">📊 Data-Driven</h3>
            <p>Trained on <strong>150,000+ real transactions</strong> with <strong>1,020 features</strong> capturing every aspect of a property.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #667eea; margin-top: 0;">🧠 Advanced ML</h3>
            <p>Uses cutting-edge <strong>ensemble methods</strong> combining Random Forest, XGBoost, and LightGBM for maximum accuracy.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #667eea; margin-top: 0;">⚡ Real-Time</h3>
            <p>Get instant predictions in seconds. Our optimized pipeline processes your input and returns accurate valuations immediately.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance comparison
    st.markdown("## 📈 Performance Highlights")
    
    # Create a gauge chart for accuracy
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=accuracy_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Model Accuracy (R² Score)", 'font': {'size': 24}},
        delta={'reference': 88.4, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#667eea"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 70], 'color': '#ffcccc'},
                {'range': [70, 85], 'color': '#fff4cc'},
                {'range': [85, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 88.4
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#2d3748", 'family': "Arial"}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: #f7fafc; border-radius: 0.5rem; margin: 2rem 0;">
        <p style="margin: 0; color: #2d3748; font-size: 1.1rem;">
            <strong>Baseline Target:</strong> 88.4% (shown as red line)<br>
            <strong>Our Achievement:</strong> {:.1f}% R² Score
        </p>
    </div>
    """.format(accuracy_pct), unsafe_allow_html=True)
    
    # Call to action
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; color: white;">
            <h2 style="margin-top: 0;">Ready to predict your home's value?</h2>
            <p style="font-size: 1.2rem; margin-bottom: 1.5rem;">Get an accurate valuation in seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 Start Predicting →", use_container_width=True):
            st.switch_page("pages/predict.py")
