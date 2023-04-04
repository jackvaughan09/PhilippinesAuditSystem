import pandas as pd
from philformat import standardize_columns, overflow_repair

if __name__ == "__main__":
    test_data_url = '/Users/jackvaughan/Documents/IPD/IPDCode/Philipines/phil/test_data/csv/wtf.csv'
    df = pd.read_csv(test_data_url)
    df = df.drop(columns='Unnamed: 0')
    df = standardize_columns(df)
    df = overflow_repair(df)
    df['source'] = test_data_url.split('/')[-1]
    print('hi')