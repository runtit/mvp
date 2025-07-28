# constants.py
APP_NAME = "Perpetual Velocity"

QUADRANT_LABELS = {
    "q1": "Technologically Elite",
    "q2": "Feasible",
    "q3": "Pre-Concept Barrier",
    "q4": "Failing",
    "q0": "Incomplete",
}

QUADRANT_COLORS = {
    "Technologically Elite": "#1f77b4",
    "Feasible": "#4d4d4d",
    "Pre-Concept Barrier": "#aaaaaa",
    "Failing": "#d62728",
    "Incomplete": "#ff7f0e"
}

QUADRANT_CONFIG = {
    "Technologically Elite": {
        "label": " Tech Elite",
        "color": "#1f77b4",
        "desc": "High score, mature stage"
    },
    "Feasible": {
        "label": " Feasible",
        "color": "#4d4d4d",
        "desc": "High score, early stage"
    },
    "Pre-Concept Barrier": {
        "label": " Pre-Concept Barrier",
        "color": "#aaaaaa",
        "desc": "Low score, early stage"
    },
    "Failing": {
        "label": " Failing",
        "color": "#d62728",
        "desc": "Low score, mature stage"
    },
    "Incomplete": {
        "label": " Incomplete",
        "color": "#ff7f0e",
        "desc": "Missing data"
    }
}

TREND_COLORS = {
    "up": "#2ca02c",
    "flat": "#999999",
    "down": "#d62728"
}

# Dashboard Sections: grouped metrics
DASHBOARD_TITLES = {
    "financial": "📈 Financial ",
    "sales": "💼 Sales / Marketing ",
    "operational": "⚙️ Operations & Product",
    "talent": "👥 Talent / HR",
    "customer": "🌟 Customer / Brand",
    "risk": "🚨 Risk "
}

# Score Labels (Y-axis title, tooltips, etc.)
SCORE_LABELS = {
    "composite": "Composite Score",
    "delta": "Momentum",
    "trend": {
        "up": "📈 Up", "flat": "→ Flat", "down": "📉 Down"
    }
}

TEXT_LABELS = {
    "velocity_map_title": "📊 Velocity Map (Cartesian Quadrants)",
    "x_axis_label": "Startup Age (Months)",
    "y_axis_label": "Composite Score",
    "export_button": "📤 Export CSV",
    "composite_score_delta": "Difference in Composite Score",
    "snapshots_section": "🗂 Snapshots",
    "early_stage_cutoff": "🕐 Early-Stage Cutoff (months)",
    "weight_section_title": "🎯 Actual propotion(%)",
    "weight_expander_title": "❔ How do the weights work?",
    "default_score_threshold": "60",
    "score_threshold_label": "Score Threshold",
    "trend_up": "Trend: up",
    "trend_flat": "Trend: flat",
    "trend_down": "Trend: down",
    "quadrant_title_prefix": "Quadrant: ",
    "metric_score_breakdown": "Metric / W% / Score",
    "compare_with_prefix": "📊 Compare with ",
}

SCORING_RULES = {
    "RevenueGrowthRate_%": {"good": 30, "bad": -10, "hib": True},
    "MRR_kUSD": {"good": 500, "bad": 0, "hib": True},
    "BurnRate_kUSD": {"good": 10, "bad": 150, "hib": False},
    "GrossMargin_%": {"good": 80, "bad": 20, "hib": True},
    "CustomerRetentionRate_%": {"good": 90, "bad": 50, "hib": True},
    "ChurnRate_%": {"good": 2, "bad": 30, "hib": False},
    "OperationalEfficiency_%": {"good": 90, "bad": 50, "hib": True},
    "UserEngagement_%": {"good": 85, "bad": 40, "hib": True},
    "RegulatoryComplianceRisk_%": {"good": 0, "bad": 60, "hib": False},
}

EXPLANATION_TEMPLATES = {
    "RevenueGrowthRate_%": {
        "happening": "Revenue growth has dropped significantly below healthy levels.",
        "why": "Slower growth reduces market confidence and limits scaling options.",
        "action": "Audit customer acquisition, pricing, and product-market fit."
    },
    "MRR_kUSD": {
        "happening": "Monthly Recurring Revenue (MRR) is lower than target.",
        "why": "This impacts cash predictability and valuation.",
        "action": "Push for expansion revenue, reduce churn, and improve retention."
    },
    "BurnRate_kUSD": {
        "happening": "Burn rate exceeds sustainability threshold.",
        "why": "High burn shortens runway and increases funding pressure.",
        "action": "Reduce discretionary expenses and reassess hiring plans."
    },
    "GrossMargin_%": {
        "happening": "Gross margin has fallen below healthy operating levels.",
        "why": "Poor margins indicate pricing issues or costly delivery model.",
        "action": "Re-evaluate cost structure, supplier terms, or value packaging."
    },
    "CustomerRetentionRate_%": {
        "happening": "Retention rate is lower than expected.",
        "why": "Customer churn increases acquisition pressure and reduces LTV.",
        "action": "Improve onboarding, success management, and product stickiness."
    },
    "ChurnRate_%": {
        "happening": "Churn rate is critically high.",
        "why": "Signals customer dissatisfaction and product misalignment.",
        "action": "Identify root causes through surveys and fix UX gaps."
    },
    "OperationalEfficiency_%": {
        "happening": "Operational efficiency has dropped.",
        "why": "May indicate resource bottlenecks or unclear processes.",
        "action": "Streamline workflows and invest in automation."
    },
    "UserEngagement_%": {
        "happening": "Engagement metrics are below expected usage benchmarks.",
        "why": "Low engagement often precedes churn.",
        "action": "Enhance user experience and introduce activation nudges."
    },
    "RegulatoryComplianceRisk_%": {
        "happening": "Regulatory risk exposure is high.",
        "why": "This could lead to audits, fines, or legal intervention.",
        "action": "Review compliance protocols and consult legal advisors."
    }
}


SUPPORTING_METRICS = {
    # 📈 Financial
    "RevenueGrowthRate_%": ["MRR_kUSD", "ChurnRate_%", "MarketPenetration_%"],
    "MRR_kUSD": ["CustomerRetentionRate_%", "ChurnRate_%", "BurnRate_kUSD"],
    "BurnRate_kUSD": ["GrossMargin_%", "MRR_kUSD", "CashFlowStability"],
    "GrossMargin_%": ["BurnRate_kUSD", "NetMargin_%", "RevenueGrowthRate_%"],
    "CAC_USD": ["LeadConversionRate_%", "LTV_USD", "MRR_kUSD"],
    "LTV_USD": ["CAC_USD", "CustomerRetentionRate_%"],
    "NetMargin_%": ["GrossMargin_%", "BurnRate_kUSD"],
    "CashFlowStability": ["BurnRate_kUSD", "MRR_kUSD"],

    # 💼 Sales / Marketing
    "LeadConversionRate_%": ["MarketPenetration_%", "CAC_USD", "SalesCycleLength_days"],
    "SalesCycleLength_days": ["LeadConversionRate_%", "RevenueGrowthRate_%"],
    "CustomerRetentionRate_%": ["ChurnRate_%", "NPS", "SupportResolutionTime_hrs"],
    "ChurnRate_%": ["CustomerRetentionRate_%", "ProductAdoptionRate_%", "NPS"],
    "MarketPenetration_%": ["LeadConversionRate_%", "RevenueGrowthRate_%"],

    # ⚙️ Operations & Product
    "OperationalEfficiency_%": ["SystemDowntime_hrs", "EmployeeProductivity"],
    "ProductAdoptionRate_%": ["UserEngagement_%", "ChurnRate_%"],
    "UserEngagement_%": ["ProductAdoptionRate_%", "OperationalEfficiency_%"],
    "SystemDowntime_hrs": ["OperationalEfficiency_%"],

    # 👥 Talent / HR
    "HiringVelocity_hires": ["EmployeeTurnoverRate_%"],
    "EmployeeTurnoverRate_%": ["EmployeeProductivity", "DiversityInclusion_%"],
    "EmployeeProductivity": ["OperationalEfficiency_%", "EngagementScore_%"],
    "DiversityInclusion_%": ["EmployeeTurnoverRate_%", "EmployeeProductivity"],

    # 🌟 Customer / Brand
    "NPS": ["CustomerRetentionRate_%", "ChurnRate_%"],
    "SupportResolutionTime_hrs": ["NPS", "ChurnRate_%"],
    "PRSentiment_%": ["CustomerRetentionRate_%", "NPS"],

    # 🚨 Risk
    "RegulatoryComplianceRisk_%": ["DebtToEquityRatio", "CashFlowStability"],
    "MarketCompetitiveTrends_%": ["ChurnRate_%", "MRR_kUSD"],
    "DebtToEquityRatio": ["BurnRate_kUSD", "NetMargin_%", "CashFlowStability"],
}
