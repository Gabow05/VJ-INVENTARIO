import pandas as pd
import os

def load_data():
    """
    Load inventory data from CSV file
    """
    try:
        df = pd.read_csv('data/inventory.csv')
        return df
    except:
        return None

def save_data(df):
    """
    Save inventory data to CSV file
    """
    try:
        df.to_csv('data/inventory.csv', index=False)
        return True
    except:
        return False
