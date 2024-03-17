# datainsert.py

import data_processing
import database


def main():
    file_path = 'static/course.xls'
    df = data_processing.process_data(file_path)

    conn = database.connect_to_database(host='localhost', user='root', password='111111', database='vacantclassrooms')

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
