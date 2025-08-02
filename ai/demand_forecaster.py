import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

model_path = os.path.join(os.path.dirname(__file__), "demand_model.pkl")

def train_demand_model(df: pd.DataFrame):
    features = ["TrendScore", "Stock Level", "Competitor Price"]
    target = "Demand"

    df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)
    X = df[features]
    y = df[target]

    model = LinearRegression()
    model.fit(X, y)
    joblib.dump(model, model_path)
    print("✅ Demand model trained and saved.")

def predict_demand(row):
    try:
        model = joblib.load(model_path)
        features = [[
            row["TrendScore"],
            row["Stock Level"],
            min(row["Amazon Price"], row["Flipkart Price"], row["Croma Price"])
        ]]
        demand = model.predict(features)[0]
        return round(demand)
    except:
        return row["Demand"]
