from functools import reduce

from datetime import timedelta

import pymysql, sys
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon

# 连接数据库
try:

    conn = pymysql.connect(host='localhost', user='root', password='3260.hxs', database='users_and_passwords')
    cursor = conn.cursor()
    print("数据库连接成功")
except pymysql.MySQLError as e:
    print("数据库连接失败", e)
    exit()


# 查询指定教学楼在指定时间段的空闲教室
def query_empty_classrooms(building, time):
    conn = pymysql.connect(host='localhost', user='root', password='3260.hxs', database='vacantclassrooms')
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


class logInWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/logInPage.ui")

        # 提取要操作的控件
        self.badge_QLabel = self.ui.lbl_badgePicture  # 校徽图片
        self.SysName_QLabel = self.ui.lbl_SystemName  # 系统名称
        self.username_QLineEdit = self.ui.username  # 用户名输入框
        self.password_QLineEdit = self.ui.password  # 密码输入框
        self.login_QPushButton = self.ui.Btn_login  # 登录按钮
        self.register_QPushButton = self.ui.Btn_register  # 注册按钮

        self.password_QLineEdit.setEchoMode(2)  # 设置密码输入框为密码模式
        self.login_QPushButton.setShortcut("Return")  # 设置登录按钮快捷键为回车

        # 设置登录按钮
        self.login_QPushButton.clicked.connect(self.login_verify)
        self.register_QPushButton.clicked.connect(self.open_register_page)

        self.setWindowIcon(QIcon('./image/searchIcon.png'))
        self.badge_QLabel.setPixmap(QPixmap('./image/schoolBadge.png'))
        self.badge_QLabel.setScaledContents(True)
        self.setGeometry(300, 300, 300, 300)

    def login_verify(self):
        # 计算屏幕的中心点坐标
        screen_geometry = QApplication.desktop().screenGeometry()
        center_x = screen_geometry.width() // 2
        center_y = screen_geometry.height() // 2

        username = self.username_QLineEdit.text()
        password = self.password_QLineEdit.text()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        result = cursor.fetchone()
        if result:
            print('登录成功！')
            lofIn_succeed_message_box = QMessageBox()
            lofIn_succeed_message_box.setIcon(QMessageBox.Information)
            lofIn_succeed_message_box.setWindowTitle("登录成功")
            lofIn_succeed_message_box.setText("登录成功！")

            # 设置对话框的几何属性
            lofIn_succeed_message_box.setGeometry(center_x - lofIn_succeed_message_box.width() // 2,
                                                  center_y - lofIn_succeed_message_box.height() // 2, 300,
                                                  300)  # 设置对话框的位置和大小

            # 显示警告对话框
            api_logInSucceed = lofIn_succeed_message_box.exec_()
            # 进入主界面
            if api_logInSucceed == QMessageBox.Ok:
                self.open_main_page()
            return True
        else:
            print('登录失败，请检查用户名和密码。')
            login_failed_message_box = QMessageBox()
            login_failed_message_box.setIcon(QMessageBox.Warning)
            login_failed_message_box.setWindowTitle("登录失败")
            login_failed_message_box.setText("登录失败，请检查用户名和密码。")

            # 设置对话框的几何属性
            login_failed_message_box.setGeometry(center_x - login_failed_message_box.width() // 2,
                                                 center_y - login_failed_message_box.height() // 2, 300,
                                                 300)  # 设置对话框的位置和大小

            # 显示警告对话框
            login_failed_message_box.exec_()
            return False

    def open_register_page(self):
        self.ui.close()
        self.register_page = registerWidget()
        self.register_page.ui.show()

    def open_main_page(self):
        self.ui.close()
        self.main_page = mainWidget()
        self.main_page.ui.show()


# 注册界面
class registerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/registerPage.ui")

        # 提取要操作的控件
        self.badge_QLabel = self.ui.lbl_badgePicture  # 校徽图片
        self.SysName_QLabel = self.ui.lbl_SystemName  # 系统名称
        self.username_QLineEdit = self.ui.username  # 用户名输入框
        self.password_QLineEdit = self.ui.password  # 密码输入框
        self.password_QLineEdit.setEchoMode(3)  # 设置密码输入框为密码模式
        self.register_QPushButton = self.ui.Btn_register  # 注册按钮
        self.return_QPushButton = self.ui.Btn_Return  # 返回按钮
        self.register_QPushButton.setShortcut("Return")  # 设置注册按钮快捷键为回车

        # 设置注册按钮
        self.register_QPushButton.clicked.connect(self.register_user)
        # 设置返回按钮
        self.return_QPushButton.clicked.connect(self.open_login_page)

        # 设置窗口图标
        self.setWindowIcon(QIcon('./image/searchIcon.png'))
        self.badge_QLabel.setPixmap(QPixmap('./image/schoolBadge.png'))
        self.badge_QLabel.setScaledContents(True)

    def register_user(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        center_x = screen_geometry.width() // 2
        center_y = screen_geometry.height() // 2

        username = self.username_QLineEdit.text()
        password = self.password_QLineEdit.text()
        if username and password:  # 简单的验证
            try:
                cursor.execute('INSERT INTO users(username, password) VALUES(%s, %s)', (username, password))
                conn.commit()
                print("注册成功！")

                register_succeed_message_box = QMessageBox()
                register_succeed_message_box.setIcon(QMessageBox.Information)
                register_succeed_message_box.setWindowTitle("注册成功")
                register_succeed_message_box.setText("注册成功！")

                # 设置对话框的几何属性
                register_succeed_message_box.setGeometry(center_x - register_succeed_message_box.width() // 2,
                                                         center_y - register_succeed_message_box.height() // 2, 300,
                                                         300)  # 设置对话框的位置和大小

                # 显示警告对话框
                api = register_succeed_message_box.exec_()
                if api == QMessageBox.Ok:
                    self.open_login_page()
            except pymysql.MySQLError as e:
                print("注册失败：", e)
                registe_failed_message_box = QMessageBox()
                registe_failed_message_box.setIcon(QMessageBox.Warning)
                registe_failed_message_box.setWindowTitle("注册失败")
                registe_failed_message_box.setText("注册失败：" + str(e))

                # 设置对话框的几何属性
                registe_failed_message_box.setGeometry(center_x - registe_failed_message_box.width() // 2,
                                                       center_y - registe_failed_message_box.height() // 2, 300,
                                                       300)  # 设置对话框的位置和大小

                # 显示警告对话框
                registe_failed_message_box.exec_()
        else:
            print("用户名和密码不能为空！")
            reister_failed_message_box = QMessageBox()
            reister_failed_message_box.setIcon(QMessageBox.Warning)
            reister_failed_message_box.setWindowTitle("注册失败")
            reister_failed_message_box.setText("用户名和密码不能为空！")

            # 设置对话框的几何属性
            reister_failed_message_box.setGeometry(center_x - reister_failed_message_box.width() // 2,
                                                   center_y - reister_failed_message_box.height() // 2, 300,
                                                   300)  # 设置对话框的位置和大小

            # 显示警告对话框
            reister_failed_message_box.exec_()

    def open_login_page(self):
        self.ui.close()
        self.login_page = logInWidget()
        self.login_page.ui.show()


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
        self.ui = uic.loadUi("./ui/mainPage.ui")

        # 提取要操作的控件
        self.badge_QLabel = self.ui.lbl_badgePicture  # 校徽图片
        self.SysName_QLabel = self.ui.lbl_sysName  # 系统名称
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

        self.setWindowIcon(QIcon('./image/searchIcon.png'))
        self.badge_QLabel.setPixmap(QPixmap('./image/schoolBadge.png'))
        self.badge_QLabel.setScaledContents(True)

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
            self.show_empty_classrooms()

    def show_empty_classrooms(self):
        self.vacantClassrooms.setRowCount(len(self.empty_classrooms))
        # self.vacantClassrooms.setVerticalHeaderLabels(self.empty_classrooms)
        for row, classroom in enumerate(self.empty_classrooms):
            item = QTableWidgetItem(classroom)
            item.setTextAlignment(Qt.AlignCenter)
            self.vacantClassrooms.setItem(row, 0, item)

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
        else:
            self.building_All_QPushButton.setText("全选")
            self.building1_QPushButton.setChecked(False)
            self.building2_QPushButton.setChecked(False)
            self.building3_QPushButton.setChecked(False)
            self.building4_QPushButton.setChecked(False)

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
        else:
            self.time_All_QPushButton.setText("全选")
            for button in self.time_Enable_Buttons:
                button.setChecked(False)


# 主程序
if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = logInWidget()
    w.ui.show()

    app.exec_()

    conn.close()
