import pymysql

def create_table(conn, table_name):
    cursor = conn.cursor()
    create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_admin TINYINT(1) NOT NULL DEFAULT 0
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    )
    """
    cursor.execute(create_table_query)
    cursor.close()