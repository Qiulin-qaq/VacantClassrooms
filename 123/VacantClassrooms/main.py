import pymysql
from datetime import datetime

import tkinter as tk
from tkinter import messagebox
import pymysql
from datetime import datetime
import hashlib
import bcrypt

# 连接数据库
try:

    conn = pymysql.connect(host='localhost', user='root', password='123456', database='users_and_passwords')
    cursor = conn.cursor()
    print("数据库连接成功")
except pymysql.MySQLError as e:
    print("数据库连接失败", e)
    exit()

# 使用 bcrypt 加密密码
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# 对照哈希进行密码验证
def verify_password(provided_password, stored_hash):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))

def register_user():
    username = input("请输入用户名：")
    password = input("请输入密码：")
    if username and password:  # 确保用户名和密码不为空
        try:
            # 加密密码
            hashed_password = hash_password(password)
            cursor.execute('INSERT INTO users(username, password) VALUES(%s, %s)', (username, hashed_password))
            conn.commit()
            print("注册成功！")
        except pymysql.MySQLError as e:
            print("注册失败：", e)
            conn.rollback()
    else:
        print("用户名和密码不能为空！")

def login_verify():
    username = input("请输入用户名：")
    password = input("请输入密码：")
    try:
        cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
        result = cursor.fetchone()
        if result and verify_password(password, result[0]):
            print('登录成功！')
            return True
        else:
            print('登录失败，请检查用户名和密码。')
            return False
    except pymysql.MySQLError as e:
        print("数据库查询失败：", e)

def manager_login():
    username = input("请输入管理员用户名：")
    password = input("请输入管理员密码：")
    try:
        cursor.execute('SELECT password FROM users WHERE username = %s AND is_admin = 1', (username,))
        result = cursor.fetchone()
        if result and verify_password(password, result[0]):
            print('管理员系统登录成功！')
            admin_operations()  # 确保你有一个函数定义为 admin_operations
        else:
            print('管理员系统登录失败，请检查用户名和密码。')
    except pymysql.MySQLError as e:
        print("数据库查询失败：", e)

# #管理员登录
# def manager_login():
#     username = input("请输入管理员用户名：")
#     password = input("请输入管理员密码：")
#     try:
#         cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s AND is_admin = 1', (username, password))
#         result = cursor.fetchone()
#         if result:
#             print('管理员系统登录成功！')
#             admin_operations()
#         else:
#             print('管理员系统登录失败，请检查用户名和密码。')
#     except pymysql.MySQLError as e:
#         print("数据库查询失败：", e)
def username_delete():
    username_to_delete = input()
    # 提醒用户确认删除操作
    confirm = input(f"确认要删除账号 {username_to_delete} 吗？此操作不可恢复。请输入yes确认: ")
    if confirm.lower() != 'yes':
        print("操作已取消。")
        return

    # 建立数据库连接
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='users_and_passwords'
    )

    try:
        with connection.cursor() as cursor:
            # SQL语句，删除指定用户名的用户
            sql = "DELETE FROM users WHERE username = %s"
            cursor.execute(sql, (username_to_delete,))

            # 提交更改
            connection.commit()

            if cursor.rowcount > 0:
                print(f"用户 {username_to_delete} 的账号已成功注销。")
            else:
                print(f"找不到用户：{username_to_delete}。可能该用户已经被删除。")

    except pymysql.MySQLError as e:
        print("数据库错误：", e)
    finally:
        connection.close()

def admin_management():
    print("1. 授权新的管理员")
    print("2. 删除管理员")
    choice1 = input("请输入你的选择:")
    if choice1 == '1':
        print("授权新的管理员:")
        username_to_promote = input()
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='users_and_passwords'
        )

        try:
            with connection.cursor() as cursor:
                # SQL查询，设置is_admin字段为1
                sql = "UPDATE users SET is_admin = 1 WHERE username = %s"
                cursor.execute(sql, (username_to_promote,))

                # 提交更改
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"用户 {username_to_promote} 成功设置为管理员。")
                else:
                    print(f"找不到用户或用户已是管理员：{username_to_promote}")

        except pymysql.MySQLError as e:
            print("数据库错误：", e)
        finally:
            connection.close()
    elif choice1 == '2':
        print("取消管理员授权:")
        amdin_to_delete = input()
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='users_and_passwords'
        )

        try:
            with connection.cursor() as cursor:
                # SQL查询，设置is_admin字段为0
                sql = "UPDATE users SET is_admin = 0 WHERE username = %s"
                cursor.execute(sql, (amdin_to_delete,))

                # 提交更改
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"用户 {amdin_to_delete} 已被取消管理员授权。")
                else:
                    print(f"找不到用户或用户已不是管理员：{amdin_to_delete}")

        except pymysql.MySQLError as e:
            print("数据库错误：", e)
        finally:
            connection.close()

# 管理员操作示例
def admin_operations():
    print("欢迎进入管理员操作区域")
    # 这里可以添加具体的管理操作，例如添加用户、查看所有用户、删除用户等
    print("1. 查看所有用户")
    print("2. 添加新用户")
    print("3. 注销账号")
    print("4. 管理员管理")
    print("选择其他数字退出")
    choice = input("请输入您的选择：")
    if choice == '1':
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='users_and_passwords')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE is_admin = 0')
        # 确保在函数结束时关闭连接和游标
        users = cursor.fetchall()
        for user in users:
            print(user[0])
        cursor.close()
        conn.close()
    elif choice == '2':
        print("添加新用户")
        register_user()
    elif choice =='3':
        print("注销账号")
        username_delete()
    elif choice=='4':
        print("管理员管理界面")
        admin_management()
    else:
        print("退出管理员操作区域")

# 查询指定教学楼在指定时间段的空闲教室
def query_empty_classrooms(building, time):
    conn = pymysql.connect(host='localhost', user='root', password='123456', database='vacantclassrooms')
    cursor = conn.cursor()

    current_datetime = datetime.now()
    weekday = current_datetime.weekday()
    weekday_names = ["Mon", "Tues", "Wed", "Thur", "Fri", "Sat", "Sun"]
    current_weekday_name = weekday_names[weekday]

    # 获取指定教学楼的所有教室列表
    cursor.execute(f"SHOW TABLES LIKE '{building}_%'")
    all_classrooms = [row[0] for row in cursor.fetchall()]
    time_mapping = {
        "8:00": 1,
        "8:50": 2,
        "9:50": 3,
        "10:40": 4,
        "11:30": 5,
        "13:00": 6,
        "13:50": 7,
        "14:45": 8,
        "15:40": 9,
        "16:35": 10,
        "17:25": 11,
        "18:30": 12,
        "19:20": 13,
        "20:10": 14
    }

    time_id = time_mapping.get(time)
    # 查询指定时间段内被占用的教室
    occupied_classrooms = []
    for classroom in all_classrooms:
        cursor.execute(
            f'''
            SELECT {current_weekday_name} FROM {classroom}
            WHERE id = {time_id}
        ''')
        if cursor.fetchone()[0] == 1:
            occupied_classrooms.append(classroom)

    # 计算空闲教室
    empty_classrooms = [room for room in all_classrooms if room not in occupied_classrooms]
    return empty_classrooms

def user_interface():
    print('欢迎使用系统，请选择操作：')
    print('1. 登录')
    print('2. 注册')
    print('3.管理员登录')
    choice = input("请选择(1/3)：")
    if choice == '1':
        if login_verify():
            print('欢迎使用空教室查询系统！')
            building = input('请输入要查询的教学楼（例如 c1, c2, c3, c4 等）：')
            time = input(
                '请选择时间段（例如：8:00,8: 50,9: 50,10: 40,11: 30,13: 00,13: 50,14: 45,15: 40,16: 35,17: 25,18: 30,19: 20,20: 10)')

            empty_classrooms = query_empty_classrooms(building, time)
            print(empty_classrooms)

            #if empty_classrooms:
                #print(empty_classrooms)

    elif choice == '2':
        register_user()
    elif choice=='3':
        manager_login()
    else:
        print("无效的选择，退出程序。")

    # 主程序
if __name__ == '__main__':
    user_interface()
    conn.close()

# mysql> use users_and_passwords
# Database changed
# mysql> show tables;
# +-------------------------------+
# | Tables_in_users_and_passwords |
# +-------------------------------+
# | users                         |
# +-------------------------------+
# 1 row in set (0.01 sec)
#
# mysql> describe users;
# +----------+--------------+------+-----+---------+----------------+
# | Field    | Type         | Null | Key | Default | Extra          |
# +----------+--------------+------+-----+---------+----------------+
# | id       | int          | NO   | PRI | NULL    | auto_increment |
# | username | varchar(255) | NO   |     | NULL    |                |
# | password | varchar(255) | NO   |     | NULL    |                |
# | is_admin | tinyint(1)   | NO   |     | 0       |                |
# +----------+--------------+------+-----+---------+----------------+
# 4 rows in set (0.00 sec)
#
# mysql> select * from users;
# +----+------------+----------+----------+
# | id | username   | password | is_admin |
# +----+------------+----------+----------+
# |  5 | 0000000000 | 654321   |        1 |
# |  6 | 2022211503 | 123456   |        0 |
# |  7 | 2022211501 | 123456   |        0 |
# |  8 | 0000000001 | 654321   |        0 |
# +----+------------+----------+----------+
# 4 rows in set (0.00 sec)

# mysql> SHOW CREATE TABLE users;
# +-------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
# | Table | Create Table
#
#                                                     |
# +-------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
# | users | CREATE TABLE `users` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `username` varchar(255) NOT NULL,
#   `password` varchar(255) NOT NULL,
#   `is_admin` tinyint(1) NOT NULL DEFAULT '0',
#   PRIMARY KEY (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci |
# +-------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
# 1 row in set (0.01 sec)