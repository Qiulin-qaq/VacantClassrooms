import pymysql
from datetime import datetime

import tkinter as tk
from tkinter import messagebox
import pymysql
from datetime import datetime

# 连接数据库
try:

    conn = pymysql.connect(host='localhost', user='root', password='123456', database='users_and_passwords')
    cursor = conn.cursor()
    print("数据库连接成功")
except pymysql.MySQLError as e:
    print("数据库连接失败", e)
    exit()

# 注册新用户
def register_user():
    username = input("请输入用户名：")
    password = input("请输入密码：")
    if username and password:  # 简单的验证
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES(%s, %s)', (username, password))
            conn.commit()
            print("注册成功！")
        except pymysql.MySQLError as e:
            print("注册失败：", e)
    else:
        print("用户名和密码不能为空！")

# 验证登录
def login_verify():
    username = input("请输入用户名：")
    password = input("请输入密码：")
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    result = cursor.fetchone()
    if result:
        print('登录成功！')
        return True
    else:
        print('登录失败，请检查用户名和密码。')
        return False



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
    choice = input("请选择(1/2)：")
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
    else:
        print("无效的选择，退出程序。")

    # 主程序
if __name__ == '__main__':
    user_interface()


    conn.close()
