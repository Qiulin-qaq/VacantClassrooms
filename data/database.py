# database.py

import pymysql


def connect_to_database(host, user, password, database):
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    return conn


def create_table(conn, table_name):
    cursor = conn.cursor()
    create_table_query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Mon varchar(255) ,
        Tues varchar(255) ,
        Wed varchar(255) ,
        Thur varchar(255) ,
        Fri varchar(255) ,
        Sat varchar(255) ,
        Sun varchar(255) ,
        info LONGTEXT,
        start_time DATETIME,
        end_time DATETIME
    )
    """
    cursor.execute(create_table_query)
    cursor.close()


def insert_data(conn, table_name, data):
    cursor = conn.cursor()
    insert_query = f"INSERT INTO {table_name} (Mon, Tues, Wed, Thur, Fri, Sat, Sun, info, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, data)
    cursor.close()


def close_connection(conn):
    conn.commit()
    conn.close()