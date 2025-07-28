# ──────────────────────────────────────────────────────────────────────────
# app.py ─ Perpetual Velocity dashboard (pure Streamlit, no external HTML)
# ──────────────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ╭───────────────────────────────────────────────────────────────────────╮
# │ 1.  DATA-GENERATION UTILITIES                                        │
# ╰───────────────────────────────────────────────────────────────────────╯
def generate_synthetic_company_data(num_months: int = 24, seed: int = 40) -> pd.DataFrame:
    """Return a DataFrame that mimics Perpetual-Velocity tracking."""
    rng = np.random.default_rng(seed)
    months = np.arange(1, num_months + 1)

    # Financial ----------------------------------------------------------
    revenue_growth_rate = rng.normal(10, 3, num_months).clip(-10, 30)
    burn_rate            = rng.normal(50, 20, num_months).clip(5)
    cac                  = rng.normal(200, 50, num_months).clip(50)
    ltv                  = rng.normal(3000, 800, num_months).clip(500)
    gross_margin         = rng.normal(60, 5,  num_months).clip(10, 90)
    net_margin           = rng.normal(20, 5,  num_months).clip(-10, 50)
    mrr                  = rng.normal(100, 30, num_months).clip(5)
    cash_flow_stability  = rng.normal(70, 10, num_months).clip(0, 100)

    # Sales/Marketing ----------------------------------------------------
    lead_conv_rate  = rng.normal(5, 2,  num_months).clip(0, 20)
    sales_cycle_len = rng.normal(30, 5, num_months).clip(10)
    retention_rate  = rng.normal(80, 5, num_months).clip(0, 100)
    churn_rate      = 100 - retention_rate
    market_pen      = rng.normal(2, 1,  num_months).clip(0, 100)

    # Ops/Product --------------------------------------------------------
    prod_adopt      = rng.normal(50, 10, num_months).clip(0, 100)
    user_engage     = rng.normal(70, 10, num_months).clip(0, 100)
    downtime        = rng.normal(2, 1,  num_months).clip(0)
    op_eff          = rng.normal(80, 5,  num_months).clip(0, 100)

    # Talent/HR ----------------------------------------------------------
    hire_vel        = rng.normal(10, 3,  num_months).clip(0)
    emp_turn        = rng.normal(5,  2,  num_months).clip(0, 100)
    emp_prod        = rng.normal(150,30, num_months).clip(50)
    diversity       = rng.normal(70, 10, num_months).clip(0, 100)

    # Customer/Brand -----------------------------------------------------
    nps             = rng.normal(30, 10, num_months).clip(-100, 100)
    support_time    = rng.normal(24, 8,  num_months).clip(1)
    pr_sent         = rng.normal(60, 10, num_months).clip(0, 100)

    # Risk ---------------------------------------------------------------
    reg_risk        = rng.normal(20, 5,  num_months).clip(0, 100)
    market_trend    = rng.normal(50, 10, num_months).clip(0, 100)
    debt_equity     = rng.normal(1,  0.4, num_months).clip(0)

    df = pd.DataFrame({
        "Month":                    months,
        "RevenueGrowthRate_%":      revenue_growth_rate,
        "BurnRate_kUSD":            burn_rate,
        "CAC_USD":                  cac,
        "LTV_USD":                  ltv,
        "GrossMargin_%":            gross_margin,
        "NetMargin_%":              net_margin,
        "MRR_kUSD":                 mrr,
        "CashFlowStability":        cash_flow_stability,
        "LeadConversionRate_%":     lead_conv_rate,
        "SalesCycleLength_days":    sales_cycle_len,
        "CustomerRetentionRate_%":  retention_rate,
        "ChurnRate_%":              churn_rate,
        "MarketPenetration_%":      market_pen,
        "ProductAdoptionRate_%":    prod_adopt,
        "UserEngagement_%":         user_engage,
        "SystemDowntime_hrs":       downtime,
        "OperationalEfficiency_%":  op_eff,
        "HiringVelocity_hires":     hire_vel,
        "EmployeeTurnoverRate_%":   emp_turn,
        "EmployeeProductivity":     emp_prod,
        "DiversityInclusion_%":     diversity,
        "NPS":                      nps,
        "SupportResolutionTime_hrs":support_time,
        "PRSentiment_%":            pr_sent,
        "RegulatoryComplianceRisk_%":reg_risk,
        "MarketCompetitiveTrends_%":market_trend,
        "DebtToEquityRatio":        debt_equity
    })

    # Health score (simple weighting) -----------------------------------
    df["HealthScore"] = (
        df["RevenueGrowthRate_%"] * 0.2
        + (100 - df["BurnRate_kUSD"]) * 0.05
        + df["CustomerRetentionRate_%"] * 0.15
        + df["UserEngagement_%"] * 0.15
        + df["GrossMargin_%"] * 0.10
        + df["OperationalEfficiency_%"] * 0.10
        + df["NPS"] * 0.10
        - df["RegulatoryComplianceRisk_%"] * 0.05
        - df["DebtToEquityRatio"] * 0.10
    )

    # Quadrant classification -------------------------------------------
    def quadrant(row):
        if row.HealthScore >= 50:
            return 1
        if 20 <= row.HealthScore < 50:
            return 2 if row.Month < num_months / 2 else 4
        return 3 if row.Month < num_months / 2 else 4

    df["Quadrant"] = df.apply(quadrant, axis=1)
    df["MarketInfluence"] = (df["MRR_kUSD"] + df["RevenueGrowthRate_%"]).clip(lower=0)
    return df


def enhance_analysis_no_statsmodels(df: pd.DataFrame):
    """Return (feature_importances_df, correlation_matrix, mrr_forecast_next1)."""
    X = df[["Month"]]
    y = df["MRR_kUSD"]
    linreg = LinearRegression().fit(X, y)
    mrr_future = linreg.predict([[df["Month"].max() + 1]])[0]

    # Random-forest driver features -------------------------------------
    num_df = df.select_dtypes(np.number).dropna()
    X_all  = num_df.drop(columns=["HealthScore"])
    y_all  = num_df["HealthScore"]
    Xtr, Xts, ytr, yts = train_test_split(X_all, y_all, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=80, random_state=42).fit(Xtr, ytr)
    feat_df = pd.DataFrame({"Feature": X_all.columns,
                            "Importance": rf.feature_importances_})\
              .sort_values("Importance", ascending=False)

    return feat_df, num_df.corr(), mrr_future


# ╭───────────────────────────────────────────────────────────────────────╮
# │ 2.  STREAMLIT UI                                                     │
# ╰───────────────────────────────────────────────────────────────────────╯
st.set_page_config("Perpetual Velocity", layout="wide", page_icon="📊")
PAL = {"green": "#10B981", "blue": "#3B82F6", "yellow": "#F59E0B",
       "red": "#EF4444", "indigo": "#6366F1"}

# ── Sidebar: load data --------------------------------------------------
with st.sidebar:
    st.title("Perpetual Velocity")
    file = st.file_uploader("Upload CSV / XLSX", ["csv", "xlsx"])
    if st.button("Generate demo data"):
        df = generate_synthetic_company_data(seed=42)
    elif file:
        df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)
    else:
        st.info("→ Upload a file or click *Generate demo data*")
        st.stop()

# Validate required cols -------------------------------------------------
needed = {"Month", "HealthScore", "MRR_kUSD", "MarketInfluence", "Quadrant",
          "RevenueGrowthRate_%", "BurnRate_kUSD", "CustomerRetentionRate_%",
          "ChurnRate_%", "OperationalEfficiency_%", "ProductAdoptionRate_%",
          "UserEngagement_%", "EmployeeProductivity", "DiversityInclusion_%",
          "RegulatoryComplianceRisk_%", "MarketCompetitiveTrends_%", "CashFlowStability"}
missing = needed - set(df.columns)
if missing:
    st.error(f"Missing columns: {', '.join(missing)}")
    st.stop()

feat_imp_df, corr_mtx, mrr_next = enhance_analysis_no_statsmodels(df)
latest = df.iloc[-1]
quad_color = {1: PAL["green"], 2: PAL["blue"], 3: PAL["yellow"], 4: PAL["red"]}

# ── Header bar ----------------------------------------------------------
st.markdown(
    f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:.4rem 0">
        <div style="display:flex;align-items:center">
            <div style="width:2.2rem;height:2.2rem;background:{PAL['indigo']};
                        border-radius:50%;color:white;font-weight:700;
                        display:flex;align-items:center;justify-content:center">PV</div>
            <span style="font-size:1.5rem;font-weight:700;margin-left:.6rem">Perpetual Velocity</span>
        </div>
        <span style="background:#D1FAE5;color:#065F46;font-weight:600;
                     padding:.25rem .9rem;border-radius:9999px;font-size:.8rem">
              ● Live&nbsp;Data
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI cards -----------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Health Score", f"{latest.HealthScore:.1f}",
          f"{latest.HealthScore - df.HealthScore.iloc[-2]:+.1f}")
c2.metric("MRR (k USD)",  f"{latest.MRR_kUSD:.0f}", f"{mrr_next-latest.MRR_kUSD:+.0f}")
cust_growth = int(latest["CustomerRetentionRate_%"] * 0.01 * 1000)
c3.metric("Customer Growth", f"{cust_growth:,}", "+5.3%")
c4.markdown(f"### Q{int(latest.Quadrant)}")
c4.markdown(
    f"<span style='color:{quad_color[int(latest.Quadrant)]};font-weight:600'>"
    f"{['Scaling','Potential','Struggling','Declining'][int(latest.Quadrant)-1]}</span>",
    unsafe_allow_html=True,
)
st.divider()

# ╭───────────────────────────────────────────────────────────────────────╮
# │  Quadrant bubble chart                                               │
# ╰───────────────────────────────────────────────────────────────────────╯
fig_bubble = px.scatter(
    df, x="Month", y="HealthScore",
    size=df.MarketInfluence * 4,
    color="Quadrant", color_discrete_map=quad_color,
    hover_data={"Quadrant": True, "MarketInfluence": True}, height=420)
fig_bubble.update_layout(showlegend=False, yaxis=dict(range=[0, 100]))
for q, col in quad_color.items():
    y0, y1 = (50, 100) if q == 1 else ((20, 50) if q in (2, 4) else (0, 20))
    fig_bubble.add_shape(type="rect", x0=0, x1=df.Month.max()+1,
                         y0=y0, y1=y1, fillcolor=col,
                         opacity=.05, line_width=0, layer="below")
st.plotly_chart(fig_bubble, use_container_width=True)

# ╭───────────────────────────────────────────────────────────────────────╮
# │  Four cluster panels                                                 │
# ╰───────────────────────────────────────────────────────────────────────╯
st.subheader("Metric Clusters")

# Financial
col_fin, col_cust = st.columns(2)
with col_fin:
    st.markdown("#### 💰 Financial")
    fin_fig = px.line(df, x="Month",
                      y=["RevenueGrowthRate_%", "MRR_kUSD", "BurnRate_kUSD"],
                      height=300)
    st.plotly_chart(fin_fig, use_container_width=True)

# Customer
with col_cust:
    st.markdown("#### 🧑‍🤝‍🧑 Customer")
    cust_fig = px.bar(df, x="Month",
                      y=["CustomerRetentionRate_%", "ChurnRate_%"],
                      height=300, barmode="group")
    st.plotly_chart(cust_fig, use_container_width=True)

# Operational & Risk
col_op, col_risk = st.columns(2)

with col_op:
    st.markdown("#### ⚙️ Operational")
    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(
        theta=["Efficiency", "Adoption", "Engagement",
               "Productivity", "Diversity"],
        r=[
            latest["OperationalEfficiency_%"],
            latest["ProductAdoptionRate_%"],
            latest["UserEngagement_%"],
            latest["EmployeeProductivity"] / 3,
            latest["DiversityInclusion_%"],
        ],fill="toself", name="Current"))
    radar.update_layout(height=300, polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    st.plotly_chart(radar, use_container_width=True)

with col_risk:
    st.markdown("#### ⚠️ Risk")
    risk_vals = [
    latest["RegulatoryComplianceRisk_%"],
    latest["MarketCompetitiveTrends_%"],
    max(0, 100 - latest["CashFlowStability"]),
    latest["DebtToEquityRatio"] * 25,
]
    risk_fig = go.Figure(go.Pie(values=risk_vals, hole=.55,
                                labels=["Regulatory", "Market", "Financial", "Operational"]))
    risk_fig.update_layout(height=300, showlegend=True)
    st.plotly_chart(risk_fig, use_container_width=True)

# ╭───────────────────────────────────────────────────────────────────────╮
# │  Health-score timeline                                               │
# ╰───────────────────────────────────────────────────────────────────────╯
st.subheader("📈 Health-Score Timeline")
tl_fig = px.line(df, x="Month", y="HealthScore", height=350)
tl_fig.update_traces(line_color=PAL["indigo"],
                     marker=dict(size=7,
                                 color=df.Quadrant.map(quad_color),
                                 line=dict(color="white", width=1)))
tl_fig.update_layout(showlegend=False, yaxis=dict(range=[0, 100]))
st.plotly_chart(tl_fig, use_container_width=True)

# ╭───────────────────────────────────────────────────────────────────────╮
# │  Feature importance & correlations (optional expander)               │
# ╰───────────────────────────────────────────────────────────────────────╯
with st.expander("🔍 Advanced analysis"):
    st.markdown("##### Feature importances for **Health Score** (Random-Forest)")
    st.dataframe(feat_imp_df.head(10), use_container_width=True)

    st.markdown("##### Correlation matrix (numeric cols)")
    st.dataframe(corr_mtx.style.background_gradient("RdBu", axis=None),
                 use_container_width=True)

# ╭───────────────────────────────────────────────────────────────────────╮
# │  Data preview                                                        │
# ╰───────────────────────────────────────────────────────────────────────╯
st.subheader("Detailed Monthly Metrics (first 12 rows)")
st.dataframe(df.head(12), use_container_width=True, height=320)