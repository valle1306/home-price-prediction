"""
Predict page - Interactive prediction tool
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def show(model, model_name, metadata):
    """Display the prediction page"""
    
    st.markdown("""
    <div class="hero">
        <h1>🎯 Predict Home Price</h1>
        <p>Enter property details to get an instant valuation</p>
    </div>
    """, unsafe_allow_html=True)
    
    if model is None:
        st.error("⚠️ Model not loaded. Please check the models directory.")
        return
    
    # Get expected features
    expected_features = metadata.get('expected_features', [])
    feature_schema = metadata.get('feature_schema', {})
    
    if not expected_features:
        st.warning("Feature schema not found. Using simplified prediction form.")
        expected_features = ['LivingArea', 'BedroomsTotal', 'BathroomsTotalInteger', 
                           'YearBuilt', 'GarageSpaces']
    
    st.markdown("## Property Details")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📝 Simple Form", "🔧 Advanced"])
    
    with tab1:
        st.markdown("### Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            living_area = st.number_input("Living Area (sq ft)", min_value=500, max_value=10000, value=2000, step=100)
            bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=3, step=1)
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=2, step=1)
        
        with col2:
            year_built = st.number_input("Year Built", min_value=1900, max_value=datetime.now().year, value=2000, step=1)
            garage = st.number_input("Garage Spaces", min_value=0, max_value=5, value=2, step=1)
            stories = st.number_input("Stories", min_value=1, max_value=4, value=1, step=1)
        
        st.markdown("### Location & Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            city = st.text_input("City", value="Baton Rouge")
            postal_code = st.text_input("Postal Code", value="70808")
        
        with col2:
            property_type = st.selectbox("Property Type", 
                ["Single Family Residential", "Condo/Townhouse", "Multi-Family", "Other"])
            condition = st.selectbox("Condition", ["Excellent", "Good", "Average", "Fair", "Poor"])
        
        # Predict button
        if st.button("🔮 Predict Price", use_container_width=True, type="primary"):
            with st.spinner("Analyzing property..."):
                # Create a feature vector (simplified for demo)
                # In production, this would use the full feature set
                features = {
                    'LivingArea': living_area,
                    'BedroomsTotal': bedrooms,
                    'BathroomsTotalInteger': bathrooms,
                    'YearBuilt': year_built,
                    'GarageSpaces': garage,
                    'StoriesTotal': stories,
                }
                
                # For demo, create a dummy dataframe with all expected features
                # Set most to 0 and only fill in what we have
                X = pd.DataFrame(0, index=[0], columns=expected_features if expected_features else features.keys())
                
                # Fill in the features we have
                for key, value in features.items():
                    if key in X.columns:
                        X[key] = value
                
                try:
                    # Make prediction
                    prediction = model.predict(X)[0]
                    
                    # Display result
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; color: white; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
                        <h2 style="margin: 0; font-size: 1.5rem; opacity: 0.9;">Estimated Home Value</h2>
                        <h1 style="margin: 1rem 0; font-size: 4rem; font-weight: 800;">${:,.0f}</h1>
                        <p style="margin: 0; font-size: 1.2rem; opacity: 0.9;">Based on {} analysis</p>
                    </div>
                    """.format(prediction, model_name.replace('_', ' ').replace('.joblib', '')), unsafe_allow_html=True)
                    
                    # Confidence range (±10%)
                    lower = prediction * 0.9
                    upper = prediction * 1.1
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="info-card" style="text-align: center;">
                            <h4 style="color: #667eea; margin: 0;">Conservative</h4>
                            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">${lower:,.0f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="info-card" style="text-align: center; border-left: 4px solid #f5576c;">
                            <h4 style="color: #f5576c; margin: 0;">Most Likely</h4>
                            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">${prediction:,.0f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="info-card" style="text-align: center;">
                            <h4 style="color: #667eea; margin: 0;">Optimistic</h4>
                            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">${upper:,.0f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Property summary
                    st.markdown("### 📋 Property Summary")
                    
                    summary_col1, summary_col2 = st.columns(2)
                    
                    with summary_col1:
                        st.markdown(f"""
                        - **Living Area:** {living_area:,} sq ft
                        - **Bedrooms:** {bedrooms}
                        - **Bathrooms:** {bathrooms}
                        - **Year Built:** {year_built}
                        """)
                    
                    with summary_col2:
                        st.markdown(f"""
                        - **Garage:** {garage} spaces
                        - **Stories:** {stories}
                        - **Property Type:** {property_type}
                        - **Condition:** {condition}
                        """)
                    
                    st.info("💡 **Tip:** This prediction is based on historical data and market trends. Actual sale prices may vary based on current market conditions, negotiation, and other factors.")
                    
                except Exception as e:
                    st.error(f"❌ Prediction failed: {e}")
                    st.info("This might be due to missing features in the simplified form. Try using the Advanced tab or check the model requirements.")
    
    with tab2:
        st.markdown("### Advanced Feature Input")
        st.warning("⚠️ For demonstration purposes. In production, this would include all 1,020 features with proper encoding.")
        
        if expected_features:
            st.markdown(f"**Model expects {len(expected_features)} features**")
            
            # Show first 20 features as example
            st.markdown("**Sample features (first 20):**")
            for i, feature in enumerate(expected_features[:20]):
                st.text(f"{i+1}. {feature}")
            
            if len(expected_features) > 20:
                st.markdown(f"... and {len(expected_features) - 20} more features")
        
        st.info("💡 **Note:** The advanced feature input is designed for API integration or batch predictions. Use the Simple Form for manual predictions.")
