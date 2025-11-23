"""
Streamlit dashboard for lead analytics (optional).

To run:
    streamlit run dashboard/app.py

Requires: pip install streamlit pandas
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import streamlit as st
    import pandas as pd
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("[DASHBOARD] Streamlit not installed. Install with: pip install streamlit pandas")


if STREAMLIT_AVAILABLE:
    st.set_page_config(
        page_title="Lead Intelligence Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Lead Intelligence Dashboard")
    st.markdown("**Visualize and analyze scraped leads with advanced filtering and insights**")
    
    # File upload or path input
    st.sidebar.header("📁 Data Source")
    csv_path = st.sidebar.text_input(
        "CSV File Path",
        value=os.path.expanduser("~/Documents/social_leads/all_platforms.csv"),
        help="Path to the consolidated CSV file"
    )
    
    # File upload option
    uploaded_file = st.sidebar.file_uploader(
        "Or upload CSV file",
        type=["csv"],
        help="Upload a CSV file directly"
    )
    
    # Use uploaded file if available
    if uploaded_file is not None:
        csv_path = None  # Will use uploaded file instead
    
    # Load data
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error loading uploaded file: {e}")
    elif csv_path and os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
    
    if df is not None and not df.empty:
        st.sidebar.header("🔍 Filters")
        
        # Platform filter
        if "Platform" in df.columns:
            platforms = sorted(df["Platform"].unique().tolist())
            selected_platforms = st.sidebar.multiselect("Platforms", platforms, default=platforms)
            if selected_platforms:
                df = df[df["Platform"].isin(selected_platforms)]
        
        # Business type filter
        if "business_type" in df.columns:
            business_types = sorted([bt for bt in df["business_type"].dropna().unique() if bt != "N/A"])
            if business_types:
                selected_types = st.sidebar.multiselect("Business Types", business_types, default=[])
                if selected_types:
                    df = df[df["business_type"].isin(selected_types)]
        
        # Location filters
        if "city" in df.columns:
            cities = sorted([c for c in df["city"].dropna().unique() if c != "N/A"])
            if cities:
                selected_cities = st.sidebar.multiselect("Cities", cities, default=[])
                if selected_cities:
                    df = df[df["city"].isin(selected_cities)]
        
        if "region" in df.columns:
            regions = sorted([r for r in df["region"].dropna().unique() if r != "N/A"])
            if regions:
                selected_regions = st.sidebar.multiselect("Regions", regions, default=[])
                if selected_regions:
                    df = df[df["region"].isin(selected_regions)]
        
        # Job level filter
        if "seniority_level" in df.columns:
            job_levels = sorted([jl for jl in df["seniority_level"].dropna().unique() if jl != "N/A"])
            if job_levels:
                selected_levels = st.sidebar.multiselect("Job Levels", job_levels, default=[])
                if selected_levels:
                    df = df[df["seniority_level"].isin(selected_levels)]
        
        # Education filter
        if "education_level" in df.columns:
            education_levels = sorted([el for el in df["education_level"].dropna().unique() if el != "N/A"])
            if education_levels:
                selected_education = st.sidebar.multiselect("Education Levels", education_levels, default=[])
                if selected_education:
                    df = df[df["education_level"].isin(selected_education)]
        
        # Lead score filter
        if "lead_score" in df.columns:
            st.sidebar.markdown("---")
            scores = pd.to_numeric(df["lead_score"], errors="coerce").dropna()
            if not scores.empty:
                min_score = st.sidebar.slider(
                    "Minimum Lead Score",
                    float(scores.min()),
                    float(scores.max()),
                    float(scores.min()),
                    step=1.0
                )
                df = df[pd.to_numeric(df["lead_score"], errors="coerce") >= min_score]
        
        # Boosted posts filter
        if "is_boosted" in df.columns:
            boosted_only = st.sidebar.checkbox("Boosted Posts Only", value=False)
            if boosted_only:
                df = df[df["is_boosted"].str.lower() == "true"]
        
        # Active within days filter
        if "last_post_date" in df.columns:
            active_days = st.sidebar.number_input("Active Within (days)", min_value=0, value=0, step=7)
            if active_days > 0:
                # Simple filter - could be enhanced with date parsing
                df = df[df["last_post_date"] != "N/A"]
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Filtered Results:** {len(df)} leads")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Leads", len(df))
        
        with col2:
            if "lead_score" in df.columns:
                avg_score = pd.to_numeric(df["lead_score"], errors="coerce").mean()
                st.metric("Avg Lead Score", f"{avg_score:.1f}" if not pd.isna(avg_score) else "N/A")
            else:
                st.metric("Avg Lead Score", "N/A")
        
        with col3:
            if "Platform" in df.columns:
                unique_platforms = df["Platform"].nunique()
                st.metric("Platforms", unique_platforms)
            else:
                st.metric("Platforms", "N/A")
        
        with col4:
            if "business_type" in df.columns:
                unique_types = df["business_type"].nunique()
                st.metric("Business Types", unique_types)
            else:
                st.metric("Business Types", "N/A")
        
        # Charts section
        st.markdown("---")
        st.header("📈 Analytics")
        
        # Top row charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Leads by Platform")
            if "Platform" in df.columns:
                platform_counts = df["Platform"].value_counts()
                st.bar_chart(platform_counts)
            else:
                st.info("No platform data available")
        
        with col2:
            st.subheader("Leads by Business Type")
            if "business_type" in df.columns:
                type_counts = df["business_type"].value_counts().head(10)
                if not type_counts.empty:
                    st.bar_chart(type_counts)
                else:
                    st.info("No business type data available")
            else:
                st.info("No business type data available")
        
        # Second row charts
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Leads by City (Top 10)")
            if "city" in df.columns:
                city_counts = df["city"].value_counts().head(10)
                if not city_counts.empty:
                    st.bar_chart(city_counts)
                else:
                    st.info("No city data available")
            else:
                st.info("No city data available")
        
        with col4:
            st.subheader("Leads by Job Level")
            if "seniority_level" in df.columns:
                job_counts = df["seniority_level"].value_counts()
                if not job_counts.empty:
                    st.bar_chart(job_counts)
                else:
                    st.info("No job level data available")
            else:
                st.info("No job level data available")
        
        # Lead score distribution
        if "lead_score" in df.columns:
            st.subheader("Lead Score Distribution")
            scores = pd.to_numeric(df["lead_score"], errors="coerce").dropna()
            if not scores.empty:
                st.histogram_chart(scores)
            else:
                st.info("No lead score data available")
        
        # Engagement metrics
        if "post_engagement" in df.columns or "Followers" in df.columns:
            st.subheader("Engagement Metrics")
            eng_col1, eng_col2 = st.columns(2)
            
            with eng_col1:
                if "is_boosted" in df.columns:
                    boosted_count = (df["is_boosted"].str.lower() == "true").sum()
                    st.metric("Boosted Posts", boosted_count)
            
            with eng_col2:
                if "Followers" in df.columns:
                    # Try to parse follower counts
                    followers = df["Followers"].dropna()
                    if not followers.empty:
                        st.metric("Profiles with Followers", len(followers[followers != "N/A"]))
        
        # Data table section
        st.markdown("---")
        st.header("📋 Lead Data")
        
        # Search/filter in table
        search_term = st.text_input("🔍 Search in table", placeholder="Search by name, URL, or any field...")
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            df_display = df[mask]
        else:
            df_display = df
        
        # Sort options
        if "lead_score" in df_display.columns:
            sort_by = st.selectbox("Sort by", ["Lead Score (High to Low)", "Lead Score (Low to High)", "Display Name", "Platform"])
            if "Lead Score (High to Low)" in sort_by:
                df_display = df_display.sort_values(by="lead_score", ascending=False, key=lambda x: pd.to_numeric(x, errors="coerce"))
            elif "Lead Score (Low to High)" in sort_by:
                df_display = df_display.sort_values(by="lead_score", ascending=True, key=lambda x: pd.to_numeric(x, errors="coerce"))
            elif "Display Name" in sort_by:
                df_display = df_display.sort_values(by="Display Name", ascending=True)
            elif "Platform" in sort_by:
                df_display = df_display.sort_values(by="Platform", ascending=True)
        
        # Display table
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )
        
        # Export section
        st.markdown("---")
        st.header("💾 Export")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv_export = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered CSV",
                data=csv_export,
                file_name="filtered_leads.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            # Summary stats
            st.markdown("**Export Summary:**")
            st.markdown(f"- Total leads: {len(df_display)}")
            if "lead_score" in df_display.columns:
                scores = pd.to_numeric(df_display["lead_score"], errors="coerce").dropna()
                if not scores.empty:
                    st.markdown(f"- Score range: {scores.min():.1f} - {scores.max():.1f}")
                    st.markdown(f"- Average score: {scores.mean():.1f:.1f}")
            
    elif csv_path and not os.path.exists(csv_path):
        st.warning(f"📁 CSV file not found: {csv_path}")
        st.info("💡 Update the path in the sidebar or upload a CSV file directly.")
        st.markdown("""
        **Quick Start:**
        1. Run the scraper to generate a CSV file
        2. Update the path above, or
        3. Use the file uploader in the sidebar
        """)
    else:
        st.info("👆 Please provide a CSV file path or upload a file to get started.")

else:
    print("[DASHBOARD] Streamlit dashboard requires: pip install streamlit pandas")
    print("[DASHBOARD] Run with: streamlit run dashboard/app.py")

