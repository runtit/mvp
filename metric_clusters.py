# metric_cluster.py

#  Financial metrics
FINANCIAL_METRICS = [
    "RevenueGrowthRate_%",
    "MRR_kUSD",
    "BurnRate_kUSD",
    "CAC_USD",
    "LTV_USD",
    "GrossMargin_%",
    "NetMargin_%",
    "CashFlowStability"
]

#  Sales & Marketing metrics
SALES_MARKETING_METRICS = [
    "LeadConversionRate_%",
    "SalesCycleLength_days",
    "CustomerRetentionRate_%",
    "ChurnRate_%",
    "MarketPenetration_%"
]

# ️ Operations & Product metrics
OPERATIONS_PRODUCT_METRICS = [
    "OperationalEfficiency_%",
    "ProductAdoptionRate_%",
    "UserEngagement_%",
    "SystemDowntime_hrs"
]

#  Talent / HR metrics
TALENT_HR_METRICS = [
    "HiringVelocity_hires",
    "EmployeeTurnoverRate_%",
    "EmployeeProductivity",
    "DiversityInclusion_%"
]

#  Customer / Brand metrics
CUSTOMER_BRAND_METRICS = [
    "NPS",
    "SupportResolutionTime_hrs",
    "PRSentiment_%"
]

#  Risk metrics
RISK_METRICS = [
    "RegulatoryComplianceRisk_%",
    "MarketCompetitiveTrends_%",
    "DebtToEquityRatio"
]

# All for lookup
ALL_METRIC_CLUSTERS = {
    "financial": FINANCIAL_METRICS,
    "sales": SALES_MARKETING_METRICS,
    "operational": OPERATIONS_PRODUCT_METRICS,
    "talent": TALENT_HR_METRICS,
    "customer": CUSTOMER_BRAND_METRICS,
    "risk": RISK_METRICS,
}
