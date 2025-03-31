import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.analytics import get_user_statistics
from datetime import datetime

st.title("Analytics Dashboard")

# Get statistics
stats = get_user_statistics()

# Create tabs to organize information
tab1, tab2, tab3 = st.tabs(["Overview", "Users", "Technical"])

with tab1:
    # Overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Images", stats["total_images"])
    with col2:
        st.metric("Today", stats.get("today_count", 0))
    with col3:
        st.metric("This Week", stats.get("week_count", 0))
    
    # Activity chart (if you have time-series data)
    st.subheader("Recent Activity")
    st.info("Activity chart to be implemented with time-series data")

with tab2:
    # User statistics
    st.subheader("Most Active Users")
    user_df = pd.DataFrame({
        "User": list(stats["users"].keys()),
        "Images Generated": list(stats["users"].values())
    }).sort_values("Images Generated", ascending=False)
    
    # Limit to top 10 users for readability
    top_users = user_df.head(10)
    
    # Create horizontal bar chart for better readability
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="Images Generated", y="User", data=top_users, ax=ax)
    ax.set_title("Top 10 Most Active Users")
    st.pyplot(fig)
    
    # Complete user table
    st.subheader("All Users")
    st.dataframe(user_df)

with tab3:
    # Technical statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Styles Used")
        style_df = pd.DataFrame({
            "Style": list(stats["styles"].keys()),
            "Count": list(stats["styles"].values())
        })
        
        # Create bar chart instead of pie chart
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x="Style", y="Count", data=style_df, ax=ax)
        ax.set_title("Style Distribution")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Image Formats")
        if "sizes" in stats:
            size_df = pd.DataFrame({
                "Format": list(stats["sizes"].keys()),
                "Count": list(stats["sizes"].values())
            })
            
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(x="Format", y="Count", data=size_df, ax=ax)
            ax.set_title("Format Distribution")
            st.pyplot(fig) 