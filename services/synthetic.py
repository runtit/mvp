import numpy as np
import pandas as pd

def generate_synthetic_company_data(
        num_months: int = 24,
        seed: int = 40,
)-> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start_date = "2023-01"
    months = pd.date_range(start=start_date, periods=24, freq='M').strftime('%Y-%m')


    # ─── Financial ──────────────────────────────────────────────────
    revenue_growth_rate = rng.normal(10, 3, num_months).clip(-10, 30)
    burn_rate = rng.normal(50, 20, num_months).clip(5)
    cac = rng.normal(200, 50, num_months).clip(50)
    ltv = rng.normal(3000, 800, num_months).clip(500)
    gross_margin = rng.normal(60, 5, num_months).clip(10, 90)
    net_margin = rng.normal(20, 5, num_months).clip(-10, 50)
    mrr = rng.normal(100, 30, num_months).clip(5)
    cash_flow_stability = rng.normal(70, 10, num_months).clip(0, 100)

    # ─── Sales / Marketing ─────────────────────────────────────────
    lead_conv_rate = rng.normal(5, 2, num_months).clip(0, 20)
    sales_cycle_len = rng.normal(30, 5, num_months).clip(10)
    retention_rate = rng.normal(80, 5, num_months).clip(0, 100)
    churn_rate = 100 - retention_rate
    market_pen = rng.normal(2, 1, num_months).clip(0, 100)

    # ─── Ops / Product ─────────────────────────────────────────────
    prod_adopt = rng.normal(50, 10, num_months).clip(0, 100)
    user_engage = rng.normal(70, 10, num_months).clip(0, 100)
    downtime = rng.normal(2, 1, num_months).clip(0)
    op_eff = rng.normal(80, 5, num_months).clip(0, 100)

    # ─── Talent / HR ───────────────────────────────────────────────
    hire_vel = rng.normal(10, 3, num_months).clip(0)
    emp_turn = rng.normal(5, 2, num_months).clip(0, 100)
    emp_prod = rng.normal(150, 30, num_months).clip(50)
    diversity = rng.normal(70, 10, num_months).clip(0, 100)

    # ─── Customer / Brand ──────────────────────────────────────────
    nps = rng.normal(30, 10, num_months).clip(-100, 100)
    support_time = rng.normal(24, 8, num_months).clip(1)
    pr_sent = rng.normal(60, 10, num_months).clip(0, 100)

    # ─── Risk ──────────────────────────────────────────────────────
    reg_risk = rng.normal(20, 5, num_months).clip(0, 100)
    market_trend = rng.normal(50, 10, num_months).clip(0, 100)
    debt_equity = rng.normal(1, 0.4, num_months).clip(0)

    df = pd.DataFrame(
        {
            # time axis
            "Month": months,
            # financial
            "RevenueGrowthRate_%": revenue_growth_rate,
            "BurnRate_kUSD": burn_rate,
            "CAC_USD": cac,
            "LTV_USD": ltv,
            "GrossMargin_%": gross_margin,
            "NetMargin_%": net_margin,
            "MRR_kUSD": mrr,
            "CashFlowStability": cash_flow_stability,
            # sales / marketing
            "LeadConversionRate_%": lead_conv_rate,
            "SalesCycleLength_days": sales_cycle_len,
            "CustomerRetentionRate_%": retention_rate,
            "ChurnRate_%": churn_rate,
            "MarketPenetration_%": market_pen,
            # ops / product
            "ProductAdoptionRate_%": prod_adopt,
            "UserEngagement_%": user_engage,
            "SystemDowntime_hrs": downtime,
            "OperationalEfficiency_%": op_eff,
            # talent / HR
            "HiringVelocity_hires": hire_vel,
            "EmployeeTurnoverRate_%": emp_turn,
            "EmployeeProductivity": emp_prod,
            "DiversityInclusion_%": diversity,
            # customer / brand
            "NPS": nps,
            "SupportResolutionTime_hrs": support_time,
            "PRSentiment_%": pr_sent,
            # risk
            "RegulatoryComplianceRisk_%": reg_risk,
            "MarketCompetitiveTrends_%": market_trend,
            "DebtToEquityRatio": debt_equity,
        }
    )

    return df

#df = generate_synthetic_company_data()
#print(df.head())