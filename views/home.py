"""
Home page - Landing page with key metrics and overview
"""

import streamlit as st
import plotly.graph_objects as go

def show(model, model_name, metadata):
    """Display the home page"""
    
    # Hero section - professional, no emoji
    st.markdown("""
    <div class="hero">
        <h1>AI-Powered Home Price Prediction</h1>
        <p>Machine learning for accurate real estate valuation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get metrics from metadata
    summary = metadata.get('summary', {})
    
    # Handle ensemble results format (new)
    if 'best_model' in summary and 'test_r2' in summary:
        # Ensemble summary format (85.6% R²)
        best_r2 = summary.get('test_r2', 0.8561)
        best_model = summary.get('best_model', 'LightGBM + XGBoost Blend')
        dataset_info = summary.get('dataset_info', {})
        n_features = dataset_info.get('features_count', 1022)
        n_train = dataset_info.get('train_samples', 150311)
    elif 'results' in summary:
        # Chronological pipeline format
        results = summary.get('results', {})
        best_model = summary.get('best_model', 'CatBoost')
        best_r2 = results.get(best_model, {}).get('r2', 0.9993)
        n_features = summary.get('n_features', 63)
        n_train = summary.get('n_train', 115235)
    else:
        # Legacy format
        best_r2 = summary.get('overall_best_r2', summary.get('best_r2', 0.839))
        best_model = summary.get('overall_best', summary.get('best_model', 'XGBoost'))
        n_features = summary.get('n_features', 1020)
        n_train = summary.get('n_train_samples', 150311)
    
    # Convert R² to percentage
    accuracy_pct = best_r2 * 100
    
    # Key metrics - professional colors
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);">
            <div class="metric-label">Model Accuracy</div>
            <div class="metric-value">{accuracy_pct:.1f}%</div>
            <div style="font-size: 0.75rem;">R² Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);">
            <div class="metric-label">Training Data</div>
            <div class="metric-value">{n_train:,}</div>
            <div style="font-size: 0.75rem;">Properties</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #805ad5 0%, #6b46c1 100%);">
            <div class="metric-label">Features</div>
            <div class="metric-value">{n_features}</div>
            <div style="font-size: 0.75rem;">Data Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        model_short = best_model.replace('Blend_XGB0.1_LGB0.9', 'XGB+LGB').replace('_', ' ')[:12]
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #dd6b20 0%, #c05621 100%);">
            <div class="metric-label">Best Model</div>
            <div class="metric-value" style="font-size: 1.1rem;">{model_short}</div>
            <div style="font-size: 0.75rem;">Algorithm</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key features - professional, no emoji
    st.markdown("## Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #3182ce; margin-top: 0;">High Accuracy</h4>
            <p style="font-size: 0.9rem;">Our model achieves <strong>{:.1f}% R²</strong>, explaining {:.1f}% of price variance. Exceptional for real estate prediction.</p>
        </div>
        """.format(accuracy_pct, accuracy_pct), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #3182ce; margin-top: 0;">Data-Driven</h4>
            <p style="font-size: 0.9rem;">Trained on <strong>{:,} transactions</strong> with <strong>{} features</strong> using chronological train/test split.</p>
        </div>
        """.format(n_train, n_features), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #3182ce; margin-top: 0;">Advanced ML</h4>
            <p style="font-size: 0.9rem;">Uses <strong>XGBoost + LightGBM</strong> ensemble with GPU acceleration for maximum accuracy.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #3182ce; margin-top: 0;">Real-Time</h4>
            <p style="font-size: 0.9rem;">Get instant predictions in seconds. Optimized pipeline returns valuations immediately.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance gauge
    st.markdown("## Performance")
    
    # Previous model was 83.91% R²
    previous_r2 = 83.91
    improvement = accuracy_pct - previous_r2
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=accuracy_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Model Accuracy (R² Score)", 'font': {'size': 16}},
        delta={'reference': previous_r2, 'increasing': {'color': "green"}, 'suffix': '%'},
        gauge={
            'axis': {'range': [75, 100], 'tickwidth': 1, 'tickcolor': "#4a5568"},
            'bar': {'color': "#3182ce"},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [75, 80], 'color': '#fed7d7'},
                {'range': [80, 85], 'color': '#fefcbf'},
                {'range': [85, 90], 'color': '#c6f6d5'},
                {'range': [90, 100], 'color': '#9ae6b4'}
            ]
        }
    ))
    
    fig.update_layout(
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#2d3748", 'family': "Arial", 'size': 12}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 0.75rem; background: #f7fafc; border-radius: 0.375rem; margin: 1rem 0; font-size: 0.9rem;">
        <strong>Previous:</strong> {:.2f}% | <strong>Current:</strong> {:.2f}% | <strong>Improvement:</strong> +{:.2f} points
    </div>
    """.format(previous_r2, accuracy_pct, improvement), unsafe_allow_html=True)
