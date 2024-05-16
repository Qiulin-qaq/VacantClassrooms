# data_processing.py

import pandas as pd
import numpy as np

def process_data(file_path):
    df = pd.read_excel(file_path)

    indexes_to_drop = list(range(2, 6317, 18))
    df = df.drop(indexes_to_drop)
    df = df.reset_index(drop=True)
    indexes_to_drop = list(range(1, 5966, 17))
    df = df.drop(indexes_to_drop)
    df = df.reset_index(drop=True)
    df = df.dropna(subset=['time'])
    df = df.reset_index(drop=True)
    df['info'] = df['time']
    df[['start_time', 'end_time']] = df['time'].str.extract(r'(\d{2}:\d{2})-(\d{2}:\d{2})')
    df = df.drop(columns=['time'])

    df.iloc[list(range(1, 5265, 15)), df.columns.get_loc('info')] = np.nan
    for i in range(2, 15):
        df.iloc[list(range(i, 5265, 15)), df.columns.get_loc('info')] = np.nan

    def add_c_prefix(data):
        if data[0].isdigit():  # 判断第一个字符是否为数字
            return 'c' + data
        else:
            return data

    df['info'] = df['info'].str.extract(r'北京邮电大学\s+(.*?)\s+教室课表')
    df.loc[:, 'info'] = df['info'].ffill()
    df['info'] = df['info'].apply(add_c_prefix)
    df = df.drop(list(range(0, 5265, 15)))
    df = df.reset_index(drop=True)
    df['info'] = df['info'].str.replace('-', '_')
    df[['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']] = df[
        ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']].notna().astype(int)

    time_columns = ['start_time', 'end_time']
    specified_time = '05:00:00'
    df[time_columns] = df[time_columns].fillna(specified_time)
    for col in time_columns:
        df[col] = pd.to_datetime(df[col])

    return df