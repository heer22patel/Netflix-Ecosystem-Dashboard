import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec
import time
from io import BytesIO

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Netflix Dynamic Dashboard", page_icon="🎬", layout="wide")

# --- 2. CUSTOM CSS FOR LOGO AND PADDING ---
st.markdown("""
    <style>
    /* Global padding adjustment */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }

    /* Logo styling */
    .logo-img {
        width: 100px !important;
        height: 100px !important;
        display: inline-block;
        vertical-align: middle;
        margin-right: 20px;
    }

    /* Title styling */
    .header-title {
        display: inline-block;
        vertical-align: middle;
        font-size: 42px;
        font-weight: 800;
        color: #E50914;
        margin: 0;
    }

    /* Summary Box Styling */
    .summary-container {
        border: 2px solid #E50914;
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER SECTION ---
# Using columns to place the logo right next to the text
header_col1, header_col2 = st.columns([0.1, 0.9])

with header_col1:
    # Replace the URL with your local "logo.png" file path
    st.image("netflix logo.png")

with header_col2:
    st.markdown('<h1 class="header-title">Netflix Content Ecosystem Dashboard</h1>', unsafe_allow_html=True)

st.markdown("Upload the `netflix_titles.csv` file below to generate the interactive statistical overview.")
st.divider()

# --- 4. FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Netflix CSV", type="csv")

if uploaded_file is not None:
    # --- 5. DATA LOADING & CLEANING ---
    df = pd.read_csv(uploaded_file).dropna(subset=['date_added'])
    df['year_added'] = pd.to_datetime(df['date_added'].str.strip()).dt.year

    # --- 6. SIDEBAR FILTERS ---
    st.sidebar.header("Dashboard Controls")
    st.sidebar.info("Adjust the sliders to update the charts in real-time.")
    
    min_year = int(df['year_added'].min())
    max_year = int(df['year_added'].max())
    
    selected_range = st.sidebar.slider(
        "Select Year Added Range",
        min_year, max_year, (2010, 2021)
    )

    # Filtering data based on selection
    filtered_df = df[(df['year_added'] >= selected_range[0]) & (df['year_added'] <= selected_range[1])]

    # --- 7. VISUALIZATION LOGIC ---
    plt.rcParams['figure.facecolor'] = 'white'
    sns.set_style("white")

    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(3, 2, figure=fig, height_ratios=[0.05, 1, 1], hspace=0.4, wspace=0.3)

    # Main Title (on Figure)
    fig.suptitle(f'Netflix Statistical Overview ({selected_range[0]} - {selected_range[1]})', 
                 fontsize=26, fontweight='bold', color='#221F1F', y=0.98)

    # --- SUBPLOT 1: DONUT CHART ---
    ax1 = fig.add_subplot(gs[1, 0])
    counts = filtered_df['type'].value_counts()
    if not counts.empty:
        ax1.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, 
                colors=['#E50914', '#444444'], pctdistance=0.8, 
                textprops={'weight':'bold', 'color':'white', 'fontsize':11})
        ax1.add_artist(plt.Circle((0,0), 0.70, fc='white'))
        ax1.set_title('Movies vs TV Shows Distribution', fontsize=14, fontweight='bold', pad=15)
    else:
        ax1.text(0.5, 0.5, 'No Data for this range', ha='center')

    # --- SUBPLOT 2: TOP COUNTRIES ---
    ax2 = fig.add_subplot(gs[1, 1])
    top_10 = filtered_df['country'].value_counts().head(10)
    if not top_10.empty:
        sns.barplot(x=top_10.values, y=top_10.index, hue=top_10.index, palette="Reds_r", ax=ax2, legend=False)
        ax2.bar_label(ax2.containers[0], padding=5, fontweight='bold', fontsize=10)
        ax2.set_title('Top 10 Content Producing Hubs', fontsize=14, fontweight='bold', pad=15)
        sns.despine(ax=ax2, left=True, bottom=True)
        ax2.set_xticks([])

    # --- SUBPLOT 3: AREA TREND ---
    ax3 = fig.add_subplot(gs[2, 0])
    growth = filtered_df.groupby('year_added').size()
    if not growth.empty:
        ax3.plot(growth.index, growth.values, color='#E50914', lw=3, marker='o', markersize=6)
        ax3.fill_between(growth.index, growth.values, color='#E50914', alpha=0.1)
        ax3.set_title('Content Addition Growth Trend', fontsize=14, fontweight='bold', pad=15)
        sns.despine(ax=ax3)

    # --- SUBPLOT 4: SUMMARY BOX ---
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.axis('off')
    summary_text = (
        "EXECUTIVE SUMMARY\n"
        "----------------------------\n"
        f"• Titles Found: {len(filtered_df):,}\n"
        f"• Timeframe: {selected_range[0]} - {selected_range[1]}\n"
        f"• Peak Activity Year: {growth.idxmax() if not growth.empty else 'N/A'}\n"
        "• Top Genre: Dynamic Analysis\n"
        "• Status: Live Data Stream"
    )
    ax4.text(0.1, 0.2, summary_text, fontsize=14, fontweight='medium', linespacing=1.8,
             bbox=dict(boxstyle='round,pad=1.2', fc='#F5F5F1', ec='#E50914', lw=1.5, alpha=0.9))

    # --- 8. RENDER PLOT ---
    st.pyplot(fig)

    if st.checkbox("Show Raw Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("👋 Welcome! Please upload the Netflix dataset to get started.")
