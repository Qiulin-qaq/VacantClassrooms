import pymysql
from datetime import datetime

# 连接数据库
conn = pymysql.connect(host='localhost', user='root', password='3260.hxs', database='vacantclassrooms')
cursor = conn.cursor()


# 查询指定教学楼在指定时间段的空闲教室
def query_empty_classrooms(building, time):
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


# 用户界面
def user_interface():
    print('欢迎使用空教室查询系统！')
    building = input('请输入要查询的教学楼（例如 c1, c2, c3, c4 等）：')
    time = input(
        '请选择时间段（例如：8:00,8: 50,9: 50,10: 40,11: 30,13: 00,13: 50,14: 45,15: 40,16: 35,17: 25,18: 30,19: 20,20: 10')

    empty_classrooms = query_empty_classrooms(building, time)

    if empty_classrooms:
        print(empty_classrooms)

    # 主程序


if __name__ == '__main__':
    user_interface()
    conn.close()
