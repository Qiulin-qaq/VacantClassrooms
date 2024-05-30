from functools import reduce
from datetime import timedelta
from datetime import datetime

import re
import pymysql
import requests

from PyQt5.QtCore import Qt
import feedbackWidget
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from ui.mainPage2Ui import Ui_Widget

userno = 2022211500
pwd = "Ww12345678"
login_url = "http://jwglweixin.bupt.edu.cn/bjyddx/login"
query_url = "http://jwglweixin.bupt.edu.cn/bjyddx/todayClassrooms?campusId=01"


def get_current_week_number():
    # 设置第一周的第一天日期
    first_day_of_first_week = datetime(2024, 2, 26)

    # 获取当前日期
    current_date = datetime.now()

    # 计算当前日期与第一周的第一天之间的天数差
    days_diff = (current_date - first_day_of_first_week).days

    # 计算当前是第几周
    current_week = (days_diff // 7) + 1

    return current_week


def extract_numbers(text):
    # 使用正则表达式匹配数字和数字范围
    matches = re.findall(r'\d+-\d+|\d+', str(text))
    # 如果只有一个数字或数字范围，则将范围中的数字全部提取
    numbers = []
    for match in matches:
        if '-' in match:
            start, end = map(int, match.split('-'))
            numbers.extend(range(start, end + 1))
        else:
            numbers.append(int(match))
    # 返回整数列表
    return numbers


# 通过jw查
def login():
    payload = {
        'userNo': userno,
        'pwd': pwd,

    }

    response = requests.post(login_url, data=payload)

    # 检查HTTP响应状态码
    if response.status_code == 200:
        try:
            # 尝试解析响应JSON数据
            response_data = response.json()

            global token
            token = response_data['data']['token']
            return token
        except requests.exceptions.JSONDecodeError:
            # 处理JSON解析错误
            print("Failed to decode JSON from response. Response content:", response.text)
    else:
        # 输出非200状态码的响应内容
        print("Login failed, HTTP status code:", response.status_code)
        print("Response content:", response.text)
        return None


def extract(classrooms, prefix):
    full_prefix = prefix + '-'
    parts = classrooms.split(',')

    match = []
    for part in parts:
        part = part.strip()
        if part.startswith(full_prefix):
            match.append(part)
    return match


def query(data):
    payload = {
        'userNo': userno,
        'pwd': pwd,
        'token': token,

    }
    response = requests.post(query_url, data=payload)

    # 检查HTTP响应状态码
    if response.status_code == 200:
        try:
            # 尝试解析响应JSON数据
            response_data = response.json()

            classtable = []
            for item in response_data['data']:
                classtable.append(item)

            queryFirst = []

            for item in classtable:
                if item.get('NODENAME') == data['NODENAME']:
                    queryFirst.append(item)

            matchString = queryFirst[0]['CLASSROOMS']

            result = extract(matchString, data['CLASSROOMS'])

            return result





        except requests.exceptions.JSONDecodeError:
            # 处理JSON解析错误
            print("Failed to decode JSON from response. Response content:", response.text)
    else:
        # 输出非200状态码的响应内容
        print("Login failed, HTTP status code:", response.status_code)
        print("Response content:", response.text)
        return None


def query_empty_classrooms_local(building, time):
    conn = pymysql.connect(host='localhost', user='root', password='3260.hxs', database='vacantclassrooms')
    cursor = conn.cursor()

    current_week = get_current_week_number()  # 获取当前周数

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

        # 提取教室占用情况字段，并作为参数传递给 extract_numbers 函数
        occupied_status = cursor.fetchone()[0]
        if current_week in extract_numbers(occupied_status):
            occupied_classrooms.append(classroom)
        # if cursor.fetchone()[0] == 1:
        #     occupied_classrooms.append(classroom)

    # 计算空闲教室
    empty_classrooms = [room for room in all_classrooms if room not in occupied_classrooms]

    return empty_classrooms


def query_empty_classrooms_jw(building, time):
    login()
    time_mapping = {
        '8:00': '1',
        '8:50': '2',
        '9:50': '3',
        '10:40': '4',
        '11:30': '5',
        '13:00': '6',
        '13:50': '7',
        '14:45': '8',
        '15:40': '9',
        '16:35': '10',
        '17:25': '11',
        '18:30': '12',
        '19:20': '13',
        '20:10': '14'
    }
    building = building.replace('c', '')
    data = {
        'NODENAME': time_mapping[time],
        'CLASSROOMS': building
    }
    jw_data = query(data)

    jw_data = ['c' + classroom for classroom in jw_data]
    return query(data)


def query_empty_classrooms(building, time):
    local_data = query_empty_classrooms_local(building, time)
    jw_data = query_empty_classrooms_jw(building, time)
    jw_data_cleaned = ['c' + re.sub(r'\(\d+\)', '', re.sub(r'-', '_', classroom)) for classroom in jw_data]

    if jw_data_cleaned:
        return jw_data_cleaned
    # 教务访问失败（网络连接问题等等）使用excel课表查询
    else:
        return local_data


class mainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_time = datetime.now()
        self.building_list = []
        self.time_list = []
        self.empty_classrooms = []
        # 创建映射表
        self.building_mapping = {
            '教1': 'c1',
            '教2': 'c2',
            '教3': 'c3',
            '教4': 'c4'
        }
        self.time_mapping = {
            '8:00-8:45': '8:00',
            '8:50-9:35': '8:50',
            '9:50-10:35': '9:50',
            '10:40-11:25': '10:40',
            '11:30-12:15': '11:30',
            '13:00-13:45': '13:00',
            '13:50-14:35': '13:50',
            '14:45-15:30': '14:45',
            '15:40-16:25': '15:40',
            '16:35-17:20': '16:35',
            '17:25-18:10': '17:25',
            '18:30-19:15': '18:30',
            '19:20-20:05': '19:20',
            '20:10-20:55': '20:10'
        }
        self.init_ui()

    def init_ui(self):
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # 提取要操作的控件
        # self.badge_QLabel = self.ui.lbl_badgePicture  # 校徽图片，如果用mainPagetest.ui的话，这个要加上!!!!!
        # self.SysName_QLabel = self.ui.lbl_sysName  # 系统名称
        self.building1_QPushButton = self.ui.c1  # 教学楼1
        self.building2_QPushButton = self.ui.c2  # 教学楼2
        self.building3_QPushButton = self.ui.c3  # 教学楼3
        self.building4_QPushButton = self.ui.c4  # 教学楼4
        self.building_All_QPushButton = self.ui.pushButton_5  # 教学楼全部

        self.time1_QPushButton = self.ui.pushButton_6  # 时间段1
        self.time2_QPushButton = self.ui.pushButton_7  # 时间段2
        self.time3_QPushButton = self.ui.pushButton_8  # 时间段3
        self.time4_QPushButton = self.ui.pushButton_9  # 时间段4
        self.time5_QPushButton = self.ui.pushButton_10  # 时间段5
        self.time6_QPushButton = self.ui.pushButton_11  # 时间段6
        self.time7_QPushButton = self.ui.pushButton_12  # 时间段7
        self.time8_QPushButton = self.ui.pushButton_13  # 时间段8
        self.time9_QPushButton = self.ui.pushButton_14  # 时间段9
        self.time10_QPushButton = self.ui.pushButton_15  # 时间段10
        self.time11_QPushButton = self.ui.pushButton_16  # 时间段11
        self.time12_QPushButton = self.ui.pushButton_17  # 时间段12
        self.time13_QPushButton = self.ui.pushButton_18  # 时间段13
        self.time14_QPushButton = self.ui.pushButton_19  # 时间段14
        self.time_All_QPushButton = self.ui.pushButton_20  # 时间段全选

        self.Btn_feedback = self.ui.Btn_feedback  # 教室空闲情况反馈

        # self.setWindowIcon(QIcon('./image/searchIcon.png'))
        # self.badge_QLabel.setPixmap(QPixmap('./image/schoolBadge.png'))
        # self.badge_QLabel.setScaledContents(True)
        # 如果用mainPagetest.ui的话，这个要加上!!!!!

        self.time_Buttons = [self.time1_QPushButton, self.time2_QPushButton, self.time3_QPushButton,
                             self.time4_QPushButton,
                             self.time5_QPushButton, self.time6_QPushButton, self.time7_QPushButton,
                             self.time8_QPushButton,
                             self.time9_QPushButton, self.time10_QPushButton, self.time11_QPushButton,
                             self.time12_QPushButton,
                             self.time13_QPushButton, self.time14_QPushButton]
        self.time_Enable_Buttons = [self.time1_QPushButton, self.time2_QPushButton, self.time3_QPushButton,
                                    self.time4_QPushButton,
                                    self.time5_QPushButton, self.time6_QPushButton, self.time7_QPushButton,
                                    self.time8_QPushButton,
                                    self.time9_QPushButton, self.time10_QPushButton, self.time11_QPushButton,
                                    self.time12_QPushButton,
                                    self.time13_QPushButton, self.time14_QPushButton]

        self.vacantClassrooms = self.ui.tableWidget  # 空教室列表

        # 设置时间按钮是否可选
        for button in self.time_Buttons:
            hour = self.time_mapping.get(button.text())
            hour = datetime.strptime(hour, "%H:%M")
            hour = hour + timedelta(minutes=45)
            if self.current_time.hour > hour.hour or (
                    self.current_time.hour == hour.hour and self.current_time.minute > hour.minute):
                button.setEnabled(False)
                self.time_Enable_Buttons.remove(button)

        # 设置教学楼全选按钮
        self.building_All_QPushButton.toggled.connect(self.on_building_All_QPushButton_clicked)
        self.building1_QPushButton.toggled.connect(self.check_builidng_all)
        self.building2_QPushButton.toggled.connect(self.check_builidng_all)
        self.building3_QPushButton.toggled.connect(self.check_builidng_all)
        self.building4_QPushButton.toggled.connect(self.check_builidng_all)

        # 设置时间段全选按钮
        self.time_All_QPushButton.toggled.connect(self.on_time_All_QPushButton_clicked)
        self.time1_QPushButton.toggled.connect(self.check_time_all)
        self.time2_QPushButton.toggled.connect(self.check_time_all)
        self.time3_QPushButton.toggled.connect(self.check_time_all)
        self.time4_QPushButton.toggled.connect(self.check_time_all)
        self.time5_QPushButton.toggled.connect(self.check_time_all)
        self.time6_QPushButton.toggled.connect(self.check_time_all)
        self.time7_QPushButton.toggled.connect(self.check_time_all)
        self.time8_QPushButton.toggled.connect(self.check_time_all)
        self.time9_QPushButton.toggled.connect(self.check_time_all)
        self.time10_QPushButton.toggled.connect(self.check_time_all)
        self.time11_QPushButton.toggled.connect(self.check_time_all)
        self.time12_QPushButton.toggled.connect(self.check_time_all)
        self.time13_QPushButton.toggled.connect(self.check_time_all)
        self.time14_QPushButton.toggled.connect(self.check_time_all)

        # 设置点击教学楼按钮发送信号
        self.building1_QPushButton.toggled.connect(self.building_QPushButton_clicked)
        self.building2_QPushButton.toggled.connect(self.building_QPushButton_clicked)
        self.building3_QPushButton.toggled.connect(self.building_QPushButton_clicked)
        self.building4_QPushButton.toggled.connect(self.building_QPushButton_clicked)

        # 设置点击时间段按钮发送信号
        self.time1_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time2_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time3_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time4_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time5_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time6_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time7_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time8_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time9_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time10_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time11_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time12_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time13_QPushButton.toggled.connect(self.time_QPushButton_clicked)
        self.time14_QPushButton.toggled.connect(self.time_QPushButton_clicked)

        self.Btn_feedback.clicked.connect(self.open_feedback_page)

    # 设置点击教学楼按钮信号函数
    def building_QPushButton_clicked(self):
        if self.sender().isChecked() == True:
            sender = self.sender()  # 记录发送信号的对象
            self.building_list.append(sender.text())
            self.ready_to_query_classrooms()
        else:
            sender = self.sender()
            self.building_list.remove(sender.text())
            self.ready_to_query_classrooms()

    # 设置点击时间段按钮信号函数
    def time_QPushButton_clicked(self):
        if self.sender().isChecked() == True:
            sender = self.sender()  # 记录发送信号的对象
            self.time_list.append(sender.text())
            self.ready_to_query_classrooms()
        else:
            sender = self.sender()
            self.time_list.remove(sender.text())
            self.ready_to_query_classrooms()

    def ready_to_query_classrooms(self):
        # 排除教学楼或者时间有一个没选的情况
        if (len(self.building_list) == 0 or len(self.time_list) == 0):
            self.empty_classrooms.clear()
            self.show_empty_classrooms()
        else:
            self.empty_classrooms.clear()
            list_of_lists = [[] for _ in self.time_list]
            # 遍历时间列表和建筑列表
            # 对于每个时间，查询所有空闲教室，并将结果添加到相应的列表中
            for j in range(len(self.time_list)):
                time = self.time_list[j]
                time = self.time_mapping.get(time)
                for i in range(len(self.building_list)):
                    building = self.building_list[i]
                    building = self.building_mapping.get(building)
                    # 调用 query_empty_classrooms 函数并将结果添加到相应的列表中
                    list_of_lists[j].extend(query_empty_classrooms(building, time))

            # 将结果取交集后合并到 self.empty_classrooms 列表中
            # 将 list_of_lists 中的每个列表转换为集合类型
            set_lists = [set(lst) for lst in list_of_lists]

            # 使用 reduce 函数和集合的交集操作取得所有列表的交集
            intersection = reduce(lambda x, y: x.intersection(y), set_lists)

            # 将交集转换为列表形式 这个列表即是查询结果
            self.empty_classrooms = sorted(list(intersection))
            self.update()
            self.show_empty_classrooms()

    def show_empty_classrooms(self):
        self.vacantClassrooms.setRowCount(len(self.empty_classrooms))
        # self.vacantClassrooms.setVerticalHeaderLabels(self.empty_classrooms)
        for row, classroom in enumerate(self.empty_classrooms):
            item = QTableWidgetItem(classroom)
            item.setTextAlignment(Qt.AlignCenter)
            self.vacantClassrooms.setItem(row, 0, item)
        self.update()

    # 保证严谨，当所有选项都选上时，自动勾选上全选按钮
    def check_builidng_all(self):
        if ((self.building1_QPushButton.isChecked() == True) and (self.building2_QPushButton.isChecked() == True)
                and (self.building3_QPushButton.isChecked() == True) and (
                        self.building4_QPushButton.isChecked() == True)):
            self.building_All_QPushButton.setChecked(True)
            self.building_All_QPushButton.setText("全不选")

    # 设置全选按钮槽函数
    def on_building_All_QPushButton_clicked(self):
        if self.building_All_QPushButton.isChecked():
            self.building_All_QPushButton.setText("全不选")
            self.building1_QPushButton.setChecked(True)
            self.building2_QPushButton.setChecked(True)
            self.building3_QPushButton.setChecked(True)
            self.building4_QPushButton.setChecked(True)
            self.update()
        else:
            self.building_All_QPushButton.setText("全选")
            self.building1_QPushButton.setChecked(False)
            self.building2_QPushButton.setChecked(False)
            self.building3_QPushButton.setChecked(False)
            self.building4_QPushButton.setChecked(False)
            self.update()

    def check_time_all(self):
        for button in self.time_Enable_Buttons:
            if button.isChecked() == False:
                return
        self.time_All_QPushButton.setChecked(True)
        self.time_All_QPushButton.setText("全不选")

    def on_time_All_QPushButton_clicked(self):
        if self.time_All_QPushButton.isChecked():
            self.time_All_QPushButton.setText("全不选")
            for button in self.time_Enable_Buttons:
                button.setChecked(True)
            self.update()
        else:
            self.time_All_QPushButton.setText("全选")
            for button in self.time_Enable_Buttons:
                button.setChecked(False)
            self.update()

    def open_feedback_page(self):
        self.close()
        self.feedbackWidget = feedbackWidget.feedbackWidget()
        self.feedbackWidget.ui.show()
