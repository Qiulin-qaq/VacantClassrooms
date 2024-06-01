# data_processing.py

import pandas as pd
import numpy as np
import re


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

    def course_weeks(text):
        # 正则表达式查找形式为“数字-数字周”或“单个数字周”的模式

        matches = re.findall(r'\b\d+(?:-\d+)?周\b', text)
        if matches:
            return ', '.join(matches)  # 返回匹配到的所有周数信息，以逗号分隔的字符串形式
        return np.nan  # 如果没有找到匹配，返回NaN

    # 应用函数到DataFrame的指定列
    columns_to_update = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
    for col in columns_to_update:
        df[col] = df[col].apply(lambda x: course_weeks(x) if pd.notnull(x) else np.nan)

    df.loc[:, columns_to_update] = df[columns_to_update].replace(r'(\d+-\d+|\d+)周', r'\1', regex=True)

    df['info'] = df['info'].str.extract(r'北京邮电大学\s+(.*?)\s+教室课表')
    df.loc[:, 'info'] = df['info'].ffill()
    df['info'] = df['info'].apply(add_c_prefix)
    df = df.drop(list(range(0, 5265, 15)))
    df = df.reset_index(drop=True)
    df['info'] = df['info'].str.replace('-', '_')
    # df[['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']] = df[
    #     ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']].notna().astype(int)


    df.fillna(0, inplace=True)

    time_columns = ['start_time', 'end_time']
    specified_time = '05:00:00'

    df[time_columns] = df[time_columns].fillna(specified_time)
    for col in time_columns:
        df[col] = pd.to_datetime(df[col])

    return df