"""
Ethiopia Financial Inclusion Dashboard
Task 5: Interactive Dashboard for Stakeholder Exploration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="🇪🇹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a5f2a;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a5f2a 0%, #2d8a3e 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.2rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .metric-delta {
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    .delta-positive { color: #90EE90; }
    .delta-negative { color: #FFB6C1; }
    .delta-neutral { color: #FFE4B5; }
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1a5f2a;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #1a5f2a;
    }
    .info-box {
        background-color: #f0f8f0;
        border-left: 4px solid #1a5f2a;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff8e1;
        border-left: 4px solid #f9a825;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f8f0;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a5f2a !important;
        color: white !important;
    }
    .scenario-optimistic { color: #2d8a3e; font-weight: 600; }
    .scenario-base { color: #1976d2; font-weight: 600; }
    .scenario-pessimistic { color: #d32f2f; font-weight: 600; }
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    acc_ownership_hist = pd.DataFrame({
        'year': [2014, 2017, 2021, 2024],
        'value': [22.0, 35.0, 46.0, 49.0],
        'source': ['Findex 2014', 'Findex 2017', 'Findex 2021', 'Findex 2024']
    })
    mm_hist = pd.DataFrame({
        'year': [2021, 2024],
        'value': [4.7, 9.45],
        'source': ['Findex 2021', 'Findex 2024']
    })
    gender_gap_hist = pd.DataFrame({
        'year': [2021, 2024],
        'value': [20.0, 18.0],
        'source': ['Findex 2021', 'Findex 2024']
    })
    digital_pay_hist = pd.DataFrame({
        'year': [2020, 2021, 2022, 2023, 2024],
        'value': [20.0, 24.0, 29.0, 35.0, 42.0],
        'source': ['NFIS-II Baseline', 'NFIS-II Est.', 'NFIS-II Est.', 'NFIS-II Est.', 'Projected']
    })
    p2p_atm = pd.DataFrame({
        'metric': ['P2P Transactions', 'ATM Transactions'],
        'fy2023_24_count_millions': [49.7, 94.7],
        'fy2024_25_count_millions': [128.3, 119.3],
        'fy2024_25_value_billions_etb': [577.7, 156.1],
        'growth_rate': [158.0, 26.0]
    })
    events = pd.DataFrame({
        'event': ['Telebirr Launch', 'NFIS-II Strategy', 'Safaricom Entry', 'M-Pesa Launch',
                  'Fayda ID Rollout', 'FX Liberalization', 'P2P > ATM Milestone',
                  'M-Pesa Interop', 'EthioPay Launch', 'Safaricom Price Hike'],
        'date': pd.to_datetime(['2021-05-17', '2021-09-01', '2022-08-01', '2023-08-01',
                                '2024-01-01', '2024-07-29', '2024-10-01', '2025-10-27',
                                '2025-12-18', '2025-12-15']),
        'category': ['Product Launch', 'Policy', 'Market Entry', 'Product Launch',
                     'Infrastructure', 'Policy', 'Milestone', 'Partnership',
                     'Infrastructure', 'Pricing'],
        'pillar_impact': ['Access/Usage', 'Access', 'Access/Afford.', 'Usage',
                          'Access/Gender', 'Affordability', 'Usage', 'Usage', 'Usage', 'Affordability'],
        'description': [
            'First major mobile money service launched by Ethio Telecom',
            '5-year national financial inclusion strategy (2021-2025)',
            'End of state telecom monopoly; brought competition',
            'Second mobile money entrant; expanded digital payments',
            'National biometric digital ID system rollout began',
            'Birr float introduced; macroeconomic reform',
            'Historic: digital P2P transactions surpassed ATM for first time',
            'Full interoperability for M-Pesa across platforms',
            'National real-time payment system launched',
            'Data and voice prices increased 20-82%'
        ]
    })
    events['year'] = events['date'].dt.year
    forecast_years = [2025, 2026, 2027]
    acc_forecast = pd.DataFrame({
        'year': forecast_years,
        'base': [53.5, 57.0, 60.0],
        'optimistic': [56.0, 62.0, 67.0],
        'pessimistic': [50.0, 52.0, 54.0],
        'ci_lower': [49.5, 52.0, 54.0],
        'ci_upper': [57.5, 62.0, 66.0]
    })
    digital_forecast = pd.DataFrame({
        'year': forecast_years,
        'base': [46.0, 50.0, 54.0],
        'optimistic': [50.0, 56.0, 62.0],
        'pessimistic': [40.0, 43.0, 46.0]
    })
    mm_forecast = pd.DataFrame({
        'year': forecast_years,
        'base': [12.0, 15.0, 18.0],
        'optimistic': [15.0, 20.0, 25.0],
        'pessimistic': [10.0, 12.0, 14.0]
    })
    ggap_forecast = pd.DataFrame({
        'year': forecast_years,
        'base': [16.0, 14.0, 12.0],
        'optimistic': [14.0, 11.0, 8.0],
        'pessimistic': [18.0, 17.0, 16.0]
    })
    impact_summary = pd.DataFrame({
        'event': ['Telebirr Launch', 'Telebirr Launch', 'Telebirr Launch',
                  'Safaricom Entry', 'Safaricom Entry',
                  'M-Pesa Launch', 'M-Pesa Launch',
                  'Fayda ID Rollout', 'Fayda ID Rollout',
                  'FX Liberalization',
                  'M-Pesa Interop', 'M-Pesa Interop',
                  'EthioPay Launch',
                  'Safaricom Price Hike'],
        'indicator': ['Account Ownership', 'Telebirr Users', 'P2P Transactions',
                      '4G Coverage', 'Data Affordability',
                      'M-Pesa Users', 'Mobile Money Account Rate',
                      'Account Ownership', 'Gender Gap',
                      'Data Affordability',
                      'M-Pesa Active Users', 'P2P Transactions',
                      'P2P Transactions',
                      'Data Affordability'],
        'impact_direction': ['Increase', 'Increase', 'Increase',
                             'Increase', 'Decrease',
                             'Increase', 'Increase',
                             'Increase', 'Decrease',
                             'Increase',
                             'Increase', 'Increase',
                             'Increase',
                             'Increase'],
        'impact_magnitude': ['High (+15pp)', 'High', 'High (+25%)',
                             'Medium (+15pp)', 'Medium (-20%)',
                             'High', 'Medium (+5pp)',
                             'Medium (+10pp)', 'Medium (-5pp)',
                             'High (+30%)',
                             'Medium (+15%)', 'Medium (+10%)',
                             'Medium (+15%)',
                             'Low (+10%)'],
        'lag_months': [12, 3, 6, 12, 12, 3, 6, 24, 24, 3, 3, 3, 6, 1],
        'evidence_basis': ['Literature (Kenya)', 'Empirical', 'Empirical',
                           'Empirical', 'Literature (Rwanda)',
                           'Empirical', 'Theoretical',
                           'Literature (India)', 'Literature (India)',
                           'Empirical',
                           'Literature (Tanzania)', 'Literature (Tanzania)',
                           'Literature (India UPI)',
                           'Empirical']
    })
    return {
        'acc_ownership_hist': acc_ownership_hist,
        'mm_hist': mm_hist,
        'gender_gap_hist': gender_gap_hist,
        'digital_pay_hist': digital_pay_hist,
        'p2p_atm': p2p_atm,
        'events': events,
        'acc_forecast': acc_forecast,
        'digital_forecast': digital_forecast,
        'mm_forecast': mm_forecast,
        'ggap_forecast': ggap_forecast,
        'impact_summary': impact_summary
    }

data = load_data()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.image("https://flagcdn.com/w160/et.png", width=80)
st.sidebar.title("Ethiopia FI Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("### Global Scenario Selector")
scenario = st.sidebar.radio(
    "Select scenario for projections:",
    ["Base Case", "Optimistic", "Pessimistic"],
    index=0,
    help="Base Case: Moderate event effects and steady growth. Optimistic: Strong policy implementation. Pessimistic: Weak event effects and economic headwinds."
)
scenario_map = {"Base Case": "base", "Optimistic": "optimistic", "Pessimistic": "pessimistic"}
scen_col = scenario_map[scenario]

st.sidebar.markdown("---")
st.sidebar.markdown("### Dashboard Sections")
page = st.sidebar.radio(
    "Navigate to:",
    ["Overview", "Trends", "Forecasts", "Inclusion Projections", "Key Questions"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Data Coverage")
st.sidebar.markdown("""
- **Findex surveys**: 2014, 2017, 2021, 2024
- **Operator data**: FY2023/24, FY2024/25
- **Forecast horizon**: 2025-2027
- **Last updated**: July 2026
""")

st.sidebar.markdown("---")
with st.sidebar.expander("About"):
    st.markdown("""
    This dashboard presents Ethiopia's financial inclusion landscape
    based on the unified dataset from Tasks 1-4. It integrates
    observations, events, impact models, and forecasts to support
    stakeholder decision-making.

    **Data sources**: Global Findex, EthSwitch, Ethio Telecom,
    Safaricom Ethiopia, NBE, GSMA, ITU, World Bank.
    """)

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="main-header">Ethiopia Financial Inclusion Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Exploring Access, Usage, and Progress Toward Financial Inclusion Targets</div>', unsafe_allow_html=True)

# ============================================================
# OVERVIEW PAGE
# ============================================================
if page == "Overview":
    st.markdown('<div class="section-title">Key Metrics at a Glance</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Account Ownership (2024)</div>
            <div class="metric-value">49.0%</div>
            <div class="metric-delta delta-positive">+3.0pp from 2021</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Mobile Money Accounts (2024)</div>
            <div class="metric-value">9.45%</div>
            <div class="metric-delta delta-positive">+4.75pp from 2021</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">P2P/ATM Crossover Ratio</div>
            <div class="metric-value">1.08</div>
            <div class="metric-delta delta-positive">Digital > Cash (FY2024/25)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Gender Gap (2024)</div>
            <div class="metric-value">18pp</div>
            <div class="metric-delta delta-positive">-2pp from 2021</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Growth Rate Highlights</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="P2P Transaction Growth (YoY)", value="+158%", delta="FY2024/25 vs FY2023/24", delta_color="normal")
    with col2:
        st.metric(label="Telebirr Registered Users", value="54.8M", delta="Dominant mobile money platform", delta_color="off")
    with col3:
        st.metric(label="M-Pesa Registered Users", value="10.8M", delta="+245% growth since launch", delta_color="normal")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Progress Toward NFIS-II Targets</div>', unsafe_allow_html=True)
    targets_df = pd.DataFrame({
        'Indicator': ['Account Ownership', 'Digital Payments', 'Gender Gap', 'Mobile Money Accounts'],
        'Current (2024)': [49.0, 42.0, 18.0, 9.45],
        'NFIS-II Target (2025)': [70.0, 49.0, 10.0, 25.0],
        'Unit': ['%', '%', 'pp', '%']
    })
    targets_df['Progress %'] = (targets_df['Current (2024)'] / targets_df['NFIS-II Target (2025)'] * 100).round(1)
    targets_df['Gap'] = (targets_df['NFIS-II Target (2025)'] - targets_df['Current (2024)']).round(1)

    fig_targets = go.Figure()
    fig_targets.add_trace(go.Bar(
        name='Current (2024)', x=targets_df['Indicator'], y=targets_df['Current (2024)'],
        marker_color='#1a5f2a',
        text=[f"{v}{u}" for v, u in zip(targets_df['Current (2024)'], targets_df['Unit'])],
        textposition='outside'
    ))
    fig_targets.add_trace(go.Bar(
        name='NFIS-II Target (2025)', x=targets_df['Indicator'], y=targets_df['NFIS-II Target (2025)'],
        marker_color='#90EE90', marker_pattern_shape='/',
        text=[f"{v}{u}" for v, u in zip(targets_df['NFIS-II Target (2025)'], targets_df['Unit'])],
        textposition='outside'
    ))
    fig_targets.update_layout(
        barmode='group', title='Current Progress vs. NFIS-II 2025 Targets',
        yaxis_title='Value', height=450, template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig_targets, use_container_width=True)

    gap_df = targets_df[['Indicator', 'Current (2024)', 'NFIS-II Target (2025)', 'Gap', 'Progress %']].copy()
    gap_df.columns = ['Indicator', 'Current', 'Target', 'Gap to Close', 'Progress %']
    st.dataframe(gap_df, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="warning-box">
        <b>Key Insight:</b> Account ownership is tracking significantly below the NFIS-II target of 70% by 2025.
        With only 49% achieved in late 2024 (vs. a 63% interim target), the 70% goal appears out of reach.
        A revised target of ~60% by 2027 is more realistic based on current trajectory and event impacts.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Key Events Timeline</div>', unsafe_allow_html=True)
    events_fig = go.Figure()
    category_colors = {
        'Product Launch': '#2d8a3e', 'Policy': '#1976d2', 'Market Entry': '#f9a825',
        'Infrastructure': '#7b1fa2', 'Milestone': '#e64a19',
        'Partnership': '#00838f', 'Pricing': '#c62828'
    }
    for cat in data['events']['category'].unique():
        cat_events = data['events'][data['events']['category'] == cat]
        events_fig.add_trace(go.Scatter(
            x=cat_events['date'], y=[cat] * len(cat_events),
            mode='markers+text', name=cat,
            marker=dict(size=16, color=category_colors.get(cat, '#888')),
            text=cat_events['event'], textposition='top center', textfont=dict(size=9),
            hovertemplate='<b>%{text}</b><br>%{x|%b %Y}<extra></extra>'
        ))
    events_fig.update_layout(
        title='Financial Inclusion Events in Ethiopia (2021-2025)',
        xaxis_title='Date', yaxis_title='', height=400, template='plotly_white',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(events_fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Download Data</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        csv_acc = data['acc_ownership_hist'].to_csv(index=False)
        st.download_button(label="Account Ownership History", data=csv_acc,
                           file_name="account_ownership_history.csv", mime="text/csv")
    with col2:
        csv_events = data['events'][['event', 'date', 'category', 'pillar_impact', 'description']].to_csv(index=False)
        st.download_button(label="Events Timeline", data=csv_events,
                           file_name="events_timeline.csv", mime="text/csv")
    with col3:
        csv_impact = data['impact_summary'].to_csv(index=False)
        st.download_button(label="Event Impact Summary", data=csv_impact,
                           file_name="event_impacts.csv", mime="text/csv")

# ============================================================
# TRENDS PAGE
# ============================================================
elif page == "Trends":
    st.markdown('<div class="section-title">Interactive Trends Explorer</div>', unsafe_allow_html=True)
    st.markdown("### Date Range Filter")
    col1, col2 = st.columns(2)
    with col1:
        start_year = st.selectbox("From Year", [2014, 2017, 2021, 2024, 2025], index=0)
    with col2:
        end_year = st.selectbox("To Year", [2024, 2025, 2026, 2027], index=3)
    st.markdown("---")

    trend_tab1, trend_tab2, trend_tab3, trend_tab4 = st.tabs([
        "Account Ownership", "Mobile Money", "P2P vs ATM", "Gender Analysis"
    ])

    with trend_tab1:
        st.markdown("#### Account Ownership Trajectory")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=data['acc_ownership_hist']['year'], y=data['acc_ownership_hist']['value'],
            mode='lines+markers+text', name='Observed (Findex)',
            line=dict(color='#1a5f2a', width=3), marker=dict(size=12),
            text=[f"{v}%" for v in data['acc_ownership_hist']['value']], textposition='top center'
        ))
        fig1.add_trace(go.Scatter(
            x=data['acc_forecast']['year'], y=data['acc_forecast'][scen_col],
            mode='lines+markers', name=f'{scenario} Forecast',
            line=dict(color='#f9a825', width=3, dash='dash'), marker=dict(size=10, symbol='diamond')
        ))
        if scenario == "Base Case":
            fig1.add_trace(go.Scatter(
                x=list(data['acc_forecast']['year']) + list(data['acc_forecast']['year'][::-1]),
                y=list(data['acc_forecast']['ci_upper']) + list(data['acc_forecast']['ci_lower'][::-1]),
                fill='toself', fillcolor='rgba(249, 168, 37, 0.2)',
                line=dict(color='rgba(0,0,0,0)'), name='95% Confidence Interval'
            ))
        fig1.add_hline(y=70, line_dash="dot", line_color="red",
                       annotation_text="NFIS-II Target: 70%", annotation_position="right")
        fig1.add_hline(y=60, line_dash="dot", line_color="orange",
                       annotation_text="Revised Target: 60%", annotation_position="right")
        fig1.update_layout(
            title='Account Ownership Rate: Historical & Projected',
            xaxis_title='Year', yaxis_title='Account Ownership (%)',
            yaxis_range=[0, 85], height=500, template='plotly_white', hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("#### Growth Rate Analysis")
        growth_data = []
        hist = data['acc_ownership_hist']
        for i in range(1, len(hist)):
            years_diff = hist['year'].iloc[i] - hist['year'].iloc[i-1]
            val_diff = hist['value'].iloc[i] - hist['value'].iloc[i-1]
            cagr = ((hist['value'].iloc[i] / hist['value'].iloc[i-1]) ** (1/years_diff) - 1) * 100
            growth_data.append({
                'Period': f"{hist['year'].iloc[i-1]}-{hist['year'].iloc[i]}",
                'Change (pp)': f"+{val_diff:.1f}",
                'CAGR': f"{cagr:.1f}%", 'Years': years_diff
            })
        growth_df = pd.DataFrame(growth_data)
        st.dataframe(growth_df, use_container_width=True, hide_index=True)
        st.info("""
        **Note on the 2021-2024 slowdown**: Account ownership grew only +3pp despite massive mobile money
        expansion (65M+ accounts opened). This deceleration may reflect: (1) mobile money accounts being
        opened by already-banked individuals; (2) survey timing capturing lag effects; (3) the fact that
        Ethiopia's mobile money-only users are extremely rare (~0.5% of adults); and (4) Findex measures
        *active* account ownership, not just registration.
        """)

    with trend_tab2:
        st.markdown("#### Mobile Money Penetration")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=data['mm_hist']['year'], y=data['mm_hist']['value'],
            name='Mobile Money Account Rate (Findex)', marker_color='#1a5f2a',
            text=[f"{v}%" for v in data['mm_hist']['value']], textposition='outside'
        ))
        fig2.add_trace(go.Scatter(
            x=[2024, 2024], y=[9.45, 60],
            mode='markers+text', name='Supply-side: Registered Users/Adults',
            marker=dict(size=14, color='#f9a825', symbol='star'),
            text=['Findex: 9.45%', 'Supply-side: ~60%'],
            textposition=['bottom center', 'top center']
        ))
        fig2.update_layout(
            title='Mobile Money Account Rate: Demand vs. Supply Side View',
            xaxis_title='Year', yaxis_title='Percentage (%)',
            yaxis_range=[0, 70], height=450, template='plotly_white', barmode='group'
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""
        <div class="info-box">
            <b>Key Insight:</b> There's a massive gap between supply-side registered users (~60% of adults)
            and demand-side Findex-reported mobile money accounts (9.45%). This suggests many Telebirr/M-Pesa
            accounts are held by already-banked individuals, or that "registered" != "actively used as primary account."
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Mobile Money Platform Comparison (2024)")
        platform_data = pd.DataFrame({
            'Platform': ['Telebirr', 'M-Pesa'],
            'Registered Users (M)': [54.84, 10.8],
            'Active Users (M)': [36.2, 7.1],
            'Activity Rate (%)': [66, 66],
            'Market Share (%)': [83.5, 16.5]
        })
        fig_platform = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "bar"}]])
        fig_platform.add_trace(go.Pie(
            labels=platform_data['Platform'], values=platform_data['Registered Users (M)'],
            hole=0.4, marker_colors=['#1a5f2a', '#f9a825'], name="Market Share"
        ), row=1, col=1)
        fig_platform.add_trace(go.Bar(
            x=platform_data['Platform'], y=platform_data['Registered Users (M)'],
            name='Registered', marker_color='#1a5f2a'
        ), row=1, col=2)
        fig_platform.add_trace(go.Bar(
            x=platform_data['Platform'], y=platform_data['Active Users (M)'],
            name='Active (90-day)', marker_color='#90EE90'
        ), row=1, col=2)
        fig_platform.update_layout(
            title_text='Mobile Money Platform Landscape', height=400, template='plotly_white',
            barmode='group', showlegend=True
        )
        st.plotly_chart(fig_platform, use_container_width=True)

    with trend_tab3:
        st.markdown("#### P2P vs ATM: The Digital Crossover")
        fig3 = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Transaction Count (Millions)', 'Transaction Value (Billion ETB)'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        fig3.add_trace(go.Bar(
            x=['FY2023/24', 'FY2024/25'], y=[49.7, 128.3],
            name='P2P Count', marker_color='#1a5f2a'
        ), row=1, col=1)
        fig3.add_trace(go.Bar(
            x=['FY2023/24', 'FY2024/25'], y=[94.7, 119.3],
            name='ATM Count', marker_color='#1976d2'
        ), row=1, col=1)
        fig3.add_trace(go.Bar(
            x=['FY2024/25'], y=[577.7],
            name='P2P Value', marker_color='#1a5f2a', showlegend=False
        ), row=1, col=2)
        fig3.add_trace(go.Bar(
            x=['FY2024/25'], y=[156.1],
            name='ATM Value', marker_color='#1976d2', showlegend=False
        ), row=1, col=2)
        fig3.update_layout(
            title_text='P2P Digital Transactions vs. ATM Cash Transactions',
            height=450, template='plotly_white', barmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("#### P2P/ATM Crossover Ratio Indicator")
        crossover_fig = go.Figure()
        crossover_fig.add_trace(go.Indicator(
            mode="gauge+number+delta", value=1.08,
            title={'text': "P2P/ATM Crossover Ratio"},
            delta={'reference': 1.0, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 2]},
                'bar': {'color': "#1a5f2a"},
                'steps': [
                    {'range': [0, 1], 'color': "lightgray"},
                    {'range': [1, 2], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 'value': 1.0
                }
            }
        ))
        crossover_fig.update_layout(height=350)
        st.plotly_chart(crossover_fig, use_container_width=True)
        st.success("""
        **Historic Milestone**: In FY2024/25, P2P transaction count (128.3M) surpassed ATM transaction count (119.3M)
        for the first time in Ethiopia's history. The crossover ratio of **1.08** signals that digital payments have
        overtaken cash withdrawals as the dominant transaction channel.
        """)

    with trend_tab4:
        st.markdown("#### Gender Gap in Financial Inclusion")
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=['2021', '2024'], y=[56, 58], name='Male', marker_color='#1976d2'
        ))
        fig4.add_trace(go.Bar(
            x=['2021', '2024'], y=[36, 40], name='Female', marker_color='#e91e63'
        ))
        fig4.update_layout(
            title='Account Ownership by Gender',
            xaxis_title='Year', yaxis_title='Account Ownership (%)',
            barmode='group', height=400, template='plotly_white'
        )
        st.plotly_chart(fig4, use_container_width=True)

        fig_gap = go.Figure()
        fig_gap.add_trace(go.Scatter(
            x=data['gender_gap_hist']['year'], y=data['gender_gap_hist']['value'],
            mode='lines+markers+text', name='Gender Gap (pp)',
            line=dict(color='#e91e63', width=3), marker=dict(size=12),
            text=[f"{v}pp" for v in data['gender_gap_hist']['value']], textposition='top center'
        ))
        fig_gap.add_hline(y=10, line_dash="dot", line_color="green",
                          annotation_text="NFIS-II Target: 10pp", annotation_position="right")
        fig_gap.update_layout(
            title='Account Ownership Gender Gap Trend',
            xaxis_title='Year', yaxis_title='Gap (Percentage Points)',
            height=350, template='plotly_white'
        )
        st.plotly_chart(fig_gap, use_container_width=True)
        st.markdown("""
        <div class="warning-box">
            <b>Gender Alert:</b> Ethiopia has the <b>second-highest gender gap</b> in account ownership among
            benchmarked SSA countries. The gap widened from 2pp (2014) to 20pp (2021), before slightly narrowing
            to 18pp (2024). At current pace, the NFIS-II target of 10pp by 2025 will be missed. Closing this gap
            requires gender-intentional interventions, not generic inclusion programs.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Channel Comparison View</div>', unsafe_allow_html=True)
    channels = st.multiselect(
        "Select indicators to compare:",
        ['Account Ownership', 'Mobile Money Accounts', 'Digital Payments', '4G Coverage', 'Gender Gap'],
        default=['Account Ownership', 'Mobile Money Accounts', 'Digital Payments']
    )
    if channels:
        channel_data = pd.DataFrame({
            'Year': [2014, 2017, 2021, 2024],
            'Account Ownership': [22, 35, 46, 49],
            'Mobile Money Accounts': [None, None, 4.7, 9.45],
            'Digital Payments': [None, None, 24, 42],
            '4G Coverage': [None, None, 37.5, 70.8],
            'Gender Gap': [None, None, 20, 18]
        })
        fig_ch = go.Figure()
        colors = {'Account Ownership': '#1a5f2a', 'Digital Payments': '#1976d2',
                  'Mobile Money': '#f9a825', 'Gender Gap': '#e91e63'}
        for i, ch in enumerate(channels):
            if ch in channel_data.columns:
                fig_ch.add_trace(go.Scatter(
                    x=channel_data['Year'], y=channel_data[ch],
                    mode='lines+markers', name=ch,
                    line=dict(color=colors.get(ch, '#888'), width=2), connectgaps=True
                ))
        fig_ch.update_layout(
            title='Multi-Channel Comparison',
            xaxis_title='Year', yaxis_title='Value',
            height=450, template='plotly_white', hovermode='x unified'
        )
        st.plotly_chart(fig_ch, use_container_width=True)

# ============================================================
# FORECASTS PAGE
# ============================================================
elif page == "Forecasts":
    st.markdown('<div class="section-title">Forecast Visualizations with Confidence Intervals</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">
        Currently viewing: <span class="scenario-{scen_col}">{scenario.upper()}</span> scenario projections
        for 2025-2027. Use the sidebar to switch scenarios.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Model Selection")
    model_choice = st.selectbox(
        "Select forecasting approach:",
        ["Event-Augmented Trend Model (Recommended)",
         "Logistic Growth Model",
         "Linear Regression",
         "Comparable Country Benchmark"],
        index=0,
        help="Event-Augmented model combines trend continuation with estimated event impacts from the impact_link data."
    )
    st.markdown("---")

    st.markdown("#### Account Ownership Rate Forecast")
    fig_f1 = go.Figure()
    fig_f1.add_trace(go.Scatter(
        x=data['acc_ownership_hist']['year'], y=data['acc_ownership_hist']['value'],
        mode='lines+markers', name='Observed',
        line=dict(color='#1a5f2a', width=3), marker=dict(size=10)
    ))
    for scen, color, dash in [('base', '#1976d2', 'dash'),
                               ('optimistic', '#2d8a3e', 'dot'),
                               ('pessimistic', '#d32f2f', 'dashdot')]:
        fig_f1.add_trace(go.Scatter(
            x=data['acc_forecast']['year'], y=data['acc_forecast'][scen],
            mode='lines+markers', name=f'{scen.title()} Scenario',
            line=dict(color=color, width=2, dash=dash), marker=dict(size=8),
            opacity=0.8 if scen != scen_col else 1.0,
            line_width=4 if scen == scen_col else 2
        ))
    fig_f1.add_trace(go.Scatter(
        x=list(data['acc_forecast']['year']) + list(data['acc_forecast']['year'][::-1]),
        y=list(data['acc_forecast']['ci_upper']) + list(data['acc_forecast']['ci_lower'][::-1]),
        fill='toself', fillcolor='rgba(25, 118, 210, 0.15)',
        line=dict(color='rgba(0,0,0,0)'), name='95% CI (Base)'
    ))
    fig_f1.add_hline(y=70, line_dash="dot", line_color="red", opacity=0.5,
                     annotation_text="NFIS-II Target", annotation_position="right")
    fig_f1.add_hline(y=60, line_dash="dot", line_color="orange", opacity=0.5,
                     annotation_text="Revised Realistic Target", annotation_position="right")
    fig_f1.update_layout(
        title='Account Ownership: Historical & Forecast (2025-2027)',
        xaxis_title='Year', yaxis_title='Account Ownership (%)',
        height=500, template='plotly_white', hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_f1, use_container_width=True)

    st.markdown("#### Digital Payment Usage Forecast")
    fig_f2 = go.Figure()
    fig_f2.add_trace(go.Scatter(
        x=data['digital_pay_hist']['year'], y=data['digital_pay_hist']['value'],
        mode='lines+markers', name='Observed/Estimated',
        line=dict(color='#1a5f2a', width=3), marker=dict(size=10)
    ))
    for scen, color, dash in [('base', '#1976d2', 'dash'),
                               ('optimistic', '#2d8a3e', 'dot'),
                               ('pessimistic', '#d32f2f', 'dashdot')]:
        fig_f2.add_trace(go.Scatter(
            x=data['digital_forecast']['year'], y=data['digital_forecast'][scen],
            mode='lines+markers', name=f'{scen.title()} Scenario',
            line=dict(color=color, width=2, dash=dash), marker=dict(size=8),
            line_width=4 if scen == scen_col else 2
        ))
    fig_f2.add_hline(y=49, line_dash="dot", line_color="red", opacity=0.5,
                     annotation_text="NFIS-II Target: 49%", annotation_position="right")
    fig_f2.update_layout(
        title='Digital Payment Usage: Historical & Forecast',
        xaxis_title='Year', yaxis_title='Digital Payment Usage (%)',
        height=450, template='plotly_white', hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_f2, use_container_width=True)

    st.markdown("#### Mobile Money Account Rate Forecast")
    fig_f3 = go.Figure()
    fig_f3.add_trace(go.Scatter(
        x=data['mm_hist']['year'], y=data['mm_hist']['value'],
        mode='lines+markers', name='Observed (Findex)',
        line=dict(color='#1a5f2a', width=3), marker=dict(size=10)
    ))
    for scen, color, dash in [('base', '#1976d2', 'dash'),
                               ('optimistic', '#2d8a3e', 'dot'),
                               ('pessimistic', '#d32f2f', 'dashdot')]:
        fig_f3.add_trace(go.Scatter(
            x=data['mm_forecast']['year'], y=data['mm_forecast'][scen],
            mode='lines+markers', name=f'{scen.title()} Scenario',
            line=dict(color=color, width=2, dash=dash), marker=dict(size=8),
            line_width=4 if scen == scen_col else 2
        ))
    fig_f3.update_layout(
        title='Mobile Money Account Rate: Historical & Forecast',
        xaxis_title='Year', yaxis_title='Mobile Money Account Rate (%)',
        height=450, template='plotly_white', hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_f3, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Key Projected Milestones</div>', unsafe_allow_html=True)
    milestones = pd.DataFrame({
        'Milestone': [
            'Account Ownership reaches 55%',
            'Account Ownership reaches 60% (Revised Target)',
            'Digital Payments reach 50%',
            'Gender Gap falls below 15pp',
            'Mobile Money Accounts reach 15%',
            'Account Ownership reaches 60% (Base Case)'
        ],
        'Base Case Year': ['2025', '2027', '2026', '2026', '2026', '2027'],
        'Optimistic Year': ['2025', '2026', '2025', '2025', '2025', '2026'],
        'Pessimistic Year': ['2026', '2028+', '2027+', '2027+', '2027+', '2028+'],
        'Confidence': ['High', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium']
    })
    st.dataframe(milestones, use_container_width=True, hide_index=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        all_forecasts = pd.DataFrame({
            'Year': [2025, 2026, 2027],
            'Account_Ownership_Base': data['acc_forecast']['base'],
            'Account_Ownership_Opt': data['acc_forecast']['optimistic'],
            'Account_Ownership_Pess': data['acc_forecast']['pessimistic'],
            'Digital_Payments_Base': data['digital_forecast']['base'],
            'Digital_Payments_Opt': data['digital_forecast']['optimistic'],
            'Digital_Payments_Pess': data['digital_forecast']['pessimistic'],
        })
        st.download_button(
            label="Download All Forecasts",
            data=all_forecasts.to_csv(index=False),
            file_name="ethiopia_fi_forecasts_2025_2027.csv",
            mime="text/csv"
        )

# ============================================================
# INCLUSION PROJECTIONS PAGE
# ============================================================
elif page == "Inclusion Projections":
    st.markdown('<div class="section-title">Financial Inclusion Rate Projections</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">
        Scenario: <span class="scenario-{scen_col}">{scenario.upper()}</span> |
        Target: 60% account ownership by 2027 (revised from NFIS-II 70% by 2025)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Progress Toward 60% Inclusion Target")
    hist_values = [22, 35, 46, 49]
    hist_years = [2014, 2017, 2021, 2024]
    forecast_vals = data['acc_forecast'][scen_col].tolist()
    forecast_yrs = data['acc_forecast']['year'].tolist()

    fig_target = go.Figure()
    fig_target.add_trace(go.Scatter(
        x=hist_years, y=hist_values,
        mode='lines+markers', name='Observed',
        line=dict(color='#1a5f2a', width=4), marker=dict(size=12)
    ))
    fig_target.add_trace(go.Scatter(
        x=forecast_yrs, y=forecast_vals,
        mode='lines+markers', name=f'{scenario} Forecast',
        line=dict(color='#f9a825', width=4, dash='dash'), marker=dict(size=12, symbol='diamond')
    ))
    fig_target.add_hline(y=60, line_dash="solid", line_color="green", line_width=3,
                         annotation_text="Target: 60%", annotation_position="right", annotation_font_size=14)
    fig_target.add_hline(y=70, line_dash="dot", line_color="red", line_width=2,
                         annotation_text="Original: 70% (NFIS-II)", annotation_position="right")
    fig_target.add_trace(go.Scatter(
        x=[2024, 2025, 2026, 2027, 2027, 2026, 2025, 2024],
        y=[49, forecast_vals[0], forecast_vals[1], forecast_vals[2], 60, 60, 60, 60],
        fill='toself', fillcolor='rgba(249, 168, 37, 0.1)',
        line=dict(color='rgba(0,0,0,0)'), name='Gap to 60% Target'
    ))
    fig_target.update_layout(
        title='Path to 60% Financial Inclusion Target',
        xaxis_title='Year', yaxis_title='Account Ownership (%)',
        yaxis_range=[0, 80], height=500, template='plotly_white', hovermode='x unified'
    )
    st.plotly_chart(fig_target, use_container_width=True)

    current = 49.0
    target = 60.0
    gap = target - current
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current (2024)", f"{current}%")
    with col2:
        st.metric("Target (2027)", f"{target}%")
    with col3:
        delta_str = f"Projected: {forecast_vals[-1]:.1f}%" if forecast_vals[-1] >= target else f"Shortfall: {target - forecast_vals[-1]:.1f}pp"
        delta_color = "normal" if forecast_vals[-1] >= target else "inverse"
        st.metric("Gap to Close", f"{gap:.1f}pp", delta=delta_str, delta_color=delta_color)

    st.markdown("---")
    st.markdown("### Scenario Comparison: Account Ownership 2025-2027")
    comparison_df = pd.DataFrame({
        'Year': [2025, 2026, 2027],
        'Optimistic': data['acc_forecast']['optimistic'],
        'Base Case': data['acc_forecast']['base'],
        'Pessimistic': data['acc_forecast']['pessimistic'],
        'Target': [60, 60, 60]
    })
    def status(row, col):
        if row[col] >= 60: return "Met"
        elif row[col] >= 55: return "Close"
        else: return "Gap"
    comparison_df['Optimistic Status'] = comparison_df.apply(lambda r: status(r, 'Optimistic'), axis=1)
    comparison_df['Base Case Status'] = comparison_df.apply(lambda r: status(r, 'Base Case'), axis=1)
    comparison_df['Pessimistic Status'] = comparison_df.apply(lambda r: status(r, 'Pessimistic'), axis=1)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Multi-Indicator Projection Dashboard")
    indicators = ['Account Ownership', 'Digital Payments', 'Mobile Money', 'Gender Gap']
    selected_ind = st.multiselect("Select indicators to project:", indicators,
                                   default=['Account Ownership', 'Digital Payments'])
    fig_multi = go.Figure()
    colors = {'Account Ownership': '#1a5f2a', 'Digital Payments': '#1976d2',
              'Mobile Money': '#f9a825', 'Gender Gap': '#e91e63'}
    if 'Account Ownership' in selected_ind:
        fig_multi.add_trace(go.Scatter(
            x=data['acc_forecast']['year'], y=data['acc_forecast'][scen_col],
            mode='lines+markers', name='Account Ownership',
            line=dict(color=colors['Account Ownership'], width=3)
        ))
    if 'Digital Payments' in selected_ind:
        fig_multi.add_trace(go.Scatter(
            x=data['digital_forecast']['year'], y=data['digital_forecast'][scen_col],
            mode='lines+markers', name='Digital Payments',
            line=dict(color=colors['Digital Payments'], width=3)
        ))
    if 'Mobile Money' in selected_ind:
        fig_multi.add_trace(go.Scatter(
            x=data['mm_forecast']['year'], y=data['mm_forecast'][scen_col],
            mode='lines+markers', name='Mobile Money',
            line=dict(color=colors['Mobile Money'], width=3)
        ))
    if 'Gender Gap' in selected_ind:
        fig_multi.add_trace(go.Scatter(
            x=data['ggap_forecast']['year'], y=data['ggap_forecast'][scen_col],
            mode='lines+markers', name='Gender Gap (pp)',
            line=dict(color=colors['Gender Gap'], width=3)
        ))
    fig_multi.update_layout(
        title=f'Multi-Indicator Projection - {scenario} Scenario',
        xaxis_title='Year', yaxis_title='Value',
        height=450, template='plotly_white', hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_multi, use_container_width=True)

    st.markdown("---")
    st.markdown("### Scenario Narratives")
    if scenario == "Optimistic":
        st.markdown("""
        <div class="info-box">
            <b>Optimistic Scenario</b><br><br>
            Assumes strong implementation of NFIS-II programs, rapid Fayda ID adoption reaching 50M+ users,
            successful EthioPay integration driving merchant acceptance, and continued M-Pesa/Telebirr competition
            lowering prices. Gender-intentional campaigns close the gap faster than historical trends.
            <b>Account ownership reaches 67% by 2027.</b>
        </div>
        """, unsafe_allow_html=True)
    elif scenario == "Base Case":
        st.markdown("""
        <div class="info-box">
            <b>Base Case Scenario</b><br><br>
            Assumes moderate event effects with typical implementation delays. Fayda ID continues rollout at
            current pace (~15M enrolled). Mobile money growth continues but decelerates as early adopters are
            saturated. Some policy targets are partially met. <b>Account ownership reaches 60% by 2027.</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
            <b>Pessimistic Scenario</b><br><br>
            Assumes weak event effects due to implementation challenges, economic headwinds from FX liberalization
            raising costs, Safaricom price hikes reducing affordability, and limited gender-intentional action.
            Growth largely follows natural trend without significant event boosts.
            <b>Account ownership reaches only 54% by 2027.</b>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# KEY QUESTIONS PAGE
# ============================================================
elif page == "Key Questions":
    st.markdown('<div class="section-title">Answers to Consortium Key Questions</div>', unsafe_allow_html=True)
    st.markdown("""
    This section addresses the critical questions facing the Ethiopia financial inclusion consortium,
    drawing on insights from Tasks 1-4 and the integrated dashboard analysis.
    """)

    q1 = st.expander("Q1: Will Ethiopia reach the NFIS-II target of 70% account ownership by 2025?")
    with q1:
        st.markdown("""
        **Short Answer: No.** Based on current trajectory, Ethiopia will miss the 70% target by a significant margin.

        **Evidence:**
        - Account ownership reached only **49%** in late 2024 (Findex), vs. the NFIS-II interim target of **63%** for 2024
        - The 2021-2024 period saw only **+3pp growth**, despite massive mobile money expansion
        - To reach 70% by end of 2025 would require **+21pp in one year** - unprecedented in Ethiopia's history

        **Revised Assessment:**
        - **Base Case**: ~53-54% by end of 2025
        - **Optimistic**: ~56% by end of 2025
        - A **revised target of ~60% by 2027** is more realistic and achievable

        **Key Insight:** The gap between supply-side registered accounts (~60% of adults have mobile money)
        and demand-side Findex ownership (49%) suggests that many digital accounts are held by already-banked
        individuals, not newly included adults.
        """)

    q2 = st.expander("Q2: Why did account ownership grow only +3pp (2021-2024) despite 65M+ mobile money accounts?")
    with q2:
        st.markdown("""
        This is the **central puzzle** of Ethiopia's financial inclusion landscape. Several factors explain the decoupling:

        1. **Mobile Money != Financial Inclusion**: In Ethiopia, only ~0.5% of adults are mobile money-only users.
           Most mobile money accounts are held by people who already have bank accounts. Findex measures *any*
           formal account - so registering for Telebirr does not increase the ownership rate if you already bank.

        2. **P2P Dominance**: Unlike Kenya's M-Pesa ecosystem, Ethiopia's digital payments are heavily P2P
           (person-to-person transfers). Many "payments" on P2P rails are actually commerce transactions, but
           Findex captures this differently.

        3. **Survey Timing Lag**: The Findex 2024 survey was conducted Oct-Nov 2024. Some event impacts
           (e.g., Fayda ID full rollout, EthioPay launch) had not yet materialized.

        4. **Activity vs. Ownership Gap**: Findex asks about *active* accounts. Many registered mobile money
           users may not be actively transacting, or may have dormant accounts.

        5. **Infrastructure Gaps**: Despite 4G coverage reaching 70.8%, mobile phone gender gaps (24pp) and
           digital literacy constraints limit conversion from access to ownership.
        """)

    q3 = st.expander("Q3: What is the single most impactful event for financial inclusion?")
    with q3:
        st.markdown("""
        Based on the event impact modeling (Task 3), **Telebirr Launch (May 2021)** ranks as the most impactful event:

        | Impact | Magnitude | Evidence |
        |--------|-----------|----------|
        | Account Ownership | +15pp over 12 months | Literature (Kenya M-Pesa showed +20pp over 5 years) |
        | P2P Transactions | +25% over 6 months | Empirical (EthSwitch data) |
        | Telebirr Users | Direct acquisition | Empirical (54.8M users by 2025) |

        **However**, the *cumulative* impact of **Fayda Digital ID (Jan 2024)** may exceed Telebirr over the
        longer term because:
        - It affects multiple pillars (Access, Gender, Trust)
        - It enables KYC at scale, reducing onboarding friction
        - Literature from India (Aadhaar) shows +15-20% account opening
        - The 24-month lag means peak impact is still unfolding

        **Runner-up**: **Safaricom Market Entry (Aug 2022)** - ended the state telecom monopoly and
        accelerated 4G coverage from 37.5% to 70.8% in two years.
        """)

    q4 = st.expander("Q4: What are the biggest risks to achieving 60% inclusion by 2027?")
    with q4:
        st.markdown("""
        | Risk | Severity | Likelihood | Mitigation |
        |------|----------|------------|------------|
        | **Gender gap persistence** | High | High | Gender-intentional campaigns, women-focused agent networks |
        | **Affordability deterioration** | High | Medium | Monitor data costs; promote competition |
        | **Rural infrastructure gaps** | Medium | High | Agent network expansion; offline capabilities |
        | **Activity/ownership decoupling** | Medium | High | Focus on usage, not just registration |
        | **FX volatility effects** | Medium | Medium | Macro-stabilization; protect consumer purchasing power |
        | **Low formal credit penetration** | Medium | Medium | Credit infrastructure; movable collateral framework |

        **Critical Risk**: The gender gap is the second-highest in SSA and widening until recently.
        Without gender-intentional interventions, generic inclusion programs will not close this gap.
        """)

    q5 = st.expander("Q5: How should stakeholders prioritize interventions?")
    with q5:
        st.markdown("""
        Based on the integrated analysis, recommended priority ranking:

        **Tier 1 - Immediate (2025-2026):**
        1. **Gender-intentional onboarding**: Target women with dedicated campaigns, female agents,
           and simplified KYC via Fayda ID
        2. **Agent network densification**: Expand to rural/underserved areas where physical access is the barrier
        3. **Digital literacy programs**: Bridge the gap between infrastructure access and actual usage

        **Tier 2 - Medium-term (2026-2027):**
        4. **Merchant acceptance expansion**: Move beyond P2P to merchant payments (bill pay, retail, wages)
        5. **Interoperability completion**: Full M-Pesa/EthSwitch integration + EthioPay adoption
        6. **Affordability monitoring**: Ensure data and transaction costs don't outpace income growth

        **Tier 3 - Structural:**
        7. **Credit ecosystem development**: Address very low formal credit penetration
        8. **Sharia-compliant products**: Serve the significant Muslim population
        9. **Micro-insurance scaling**: Protect vulnerable populations and deepen inclusion

        **Expected Impact of Tier 1 Interventions:**
        - Could accelerate account ownership by an additional **3-5pp annually**
        - Would close the gender gap from 18pp to ~12pp by 2027
        - Would convert supply-side access (60% have mobile money) into demand-side ownership
        """)

    q6 = st.expander("Q6: What data gaps most limit our analysis?")
    with q6:
        st.markdown("""
        | Data Gap | Impact on Analysis | Priority to Fill |
        |----------|-------------------|------------------|
        | **No 2022-2023 Findex points** | Cannot validate event impacts in real-time | High |
        | **Limited regional disaggregation** | Cannot identify geographic hotspots | High |
        | **No urban/rural breakdown post-2021** | Cannot track rural inclusion progress | Medium |
        | **Supply-side vs. demand-side reconciliation** | Cannot explain the 49% vs 60% gap | High |
        | **Digital payment use case breakdown** | Cannot assess beyond P2P | Medium |
        | **Credit/insurance depth metrics** | Cannot measure inclusion quality | Medium |
        | **Agent network quality data** | Cannot assess last-mile access | Medium |

        **Recommendation**: Advocate for annual Findex-style surveys or at least bi-annual LSMS
        financial inclusion modules to close the temporal data gap.
        """)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown('<div class="footer">Ethiopia Financial Inclusion Dashboard | Built for Task 5 | Data: Global Findex, EthSwitch, Ethio Telecom, Safaricom, NBE, GSMA, ITU, World Bank</div>', unsafe_allow_html=True)