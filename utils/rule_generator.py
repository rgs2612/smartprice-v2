import json
from datetime import datetime, timedelta

def generate_rule_based_overrides(df):
    now = datetime.now()
    expires = now + timedelta(days=7)

    overrides = []

    for _, row in df.iterrows():
        competitor_price = row["Competitor Price"]
        our_price = row["Our Price"]
        pid = row["ProductID"]

        # Example condition: competitor is 10% cheaper
        if competitor_price < 0.9 * our_price:
            new_price = round(competitor_price * 0.98, 2)  # Undercut by 2%
            overrides.append({
                "product_id": pid,
                "new_price": new_price,
                "scheduled_for": now.strftime("%Y-%m-%d %H:%M:%S"),
                "expires_on": expires.strftime("%Y-%m-%d %H:%M:%S")
            })

    # Save to file
    with open("data/rule_scheduled_changes.json", "w") as f:
        json.dump(overrides, f, indent=2)

    print(f"✅ Rule-based overrides written: {len(overrides)}")
