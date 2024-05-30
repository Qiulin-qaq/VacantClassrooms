# datainsert.py

import data_processing
import database
from config import config


def main():
    file_path = '../static/course.xls'
    df = data_processing.process_data(file_path)

    conn = database.connect_to_database(host=config.host, user=config.db_user, password=config.db_pwd,
                                        database=config.db_name_data)

    for name, group_data in df.groupby('info'):
        database.create_table(conn, name)
        for _, row in group_data.iterrows():
            data = (
                row['Mon'], row['Tues'], row['Wed'], row['Thur'], row['Fri'], row['Sat'], row['Sun'], row['info'],
                row['start_time'], row['end_time']
            )
            database.insert_data(conn, name, data)

    database.close_connection(conn)


if __name__ == "__main__":
    main()
