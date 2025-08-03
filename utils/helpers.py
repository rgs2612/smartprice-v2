import pandas as pd

def filter_products_needing_attention(df):
    """
    Filters products that need manual review or rule-based overrides:
    - Low stock (< 5)
    - Price gap > ₹2000
    - Low AI confidence (< 0.5)
    """
    return df[
        (df['Stock Level'] < 5) |
        (abs(df['Our Price'] - df['Competitor Price']) > 2000) |
        (df['Confidence Score'] < 0.5)
    ]


def get_alert_reason(row):
    reasons = []
    if row['Stock Level'] < 5:
        reasons.append("📦 Low Stock")
    if abs(row['Our Price'] - row['Competitor Price']) > 2000:
        reasons.append("⚠️ Price Gap")
    if row['Confidence Score'] < 0.5:
        reasons.append("🧠 Low AI Confidence")
    return ", ".join(reasons)


def add_alert_reasons_column(df):
    """
    Adds 'AlertReason' column to products that need review.
    """
    df['AlertReason'] = df.apply(get_alert_reason, axis=1)
    return df
