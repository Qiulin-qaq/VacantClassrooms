import pymysql

def delete_all_table_data(conn):
    cursor = conn.cursor()
    show_tables_query = "SHOW TABLES"
    cursor.execute(show_tables_query)
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        delete_query = f"DELETE FROM {table_name}"
        cursor.execute(delete_query)
    cursor.close()
    conn.commit()

# 使用示例
# 删除数据库中所有表的数据
if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', user='root', password='111111', database='vacantclassrooms')
    delete_all_table_data(conn)
    conn.close()
