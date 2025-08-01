import pandas as pd
import numpy as np
from config import DATA_PATH

def load_product_data():
    df = pd.read_excel(DATA_PATH)

    # ✅ Ensure required columns for rule engine exist
    if 'Stock Level' not in df.columns:
        df['Stock Level'] = np.random.randint(10, 100, size=len(df))

    if 'Demand' not in df.columns:
        df['Demand'] = np.random.randint(50, 100, size=len(df))

    return df




