import pymysql

# 连接数据库
conn = pymysql.connect(host='localhost', user='root', password='3260.hxs', database='vacantclassrooms')
cursor = conn.cursor()

# 查询指定教学楼在指定时间段的空闲教室
def query_empty_classrooms(building, time_slot):
    # 获取指定教学楼的所有教室列表
    cursor.execute(f"SHOW TABLES LIKE '{building}_%'")
    all_classrooms = [row[0] for row in cursor.fetchall()]

    # 查询指定时间段内被占用的教室
    occupied_classrooms = []
    for classroom in all_classrooms:
        cursor.execute(f'''
            SELECT {time_slot} FROM {classroom}
            WHERE id = 1
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
    time_slot = input('请选择时间段（例如：Mon, Tue, Wed, Thu, Fri, Sat, Sun）：')

    empty_classrooms = query_empty_classrooms(building, time_slot)

    if empty_classrooms:
        print(f'{building} 教学楼在 {time_slot} 有空闲教室：', empty_classrooms)
    else:
        print(f'{building} 教学楼在 {time_slot} 没有空闲教室。')

# 主程序
if __name__ == '__main__':
    user_interface()
    conn.close()
