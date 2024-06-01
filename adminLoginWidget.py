import qrc
import bcrypt
import pymysql
import logInWidget
import adminWidget

from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from mysql.connector import cursor
from ui.adminLoginWidgetUi import Ui_Widget

try:

    conn = pymysql.connect(host='localhost', user='root', password='111111', database='users_and_passwords')
    cursor = conn.cursor()
except pymysql.MySQLError as e:
    exit()


class adminLoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # 提取要操作的控件
        self.frame_pic=self.ui.frame_pic
        self.frame_backgroud = self.ui.frame_background
        self.label_pwd=self.ui.label_pwd
        self.label_user_name=self.ui.label_user_name
        self.username_QLineEdit = self.ui.lineE_user_name  # 用户名输入框
        self.password_QLineEdit = self.ui.password  # 密码输入框
        self.login_QPushButton = self.ui.btn_login  # 登录按钮
        self.return_QPushButton = self.ui.btn_Return  # 返回按钮
        self.btn_admin=self.ui.btn_login # 管理员登录按钮

        self.password_QLineEdit.setEchoMode(2)  # 设置密码输入框为密码模式
        self.btn_admin.setShortcut("Return")  # 设置登录按钮快捷键为回车

        self.label_user_name.setScaledContents(True); #图片自适应label大小
        self.label_pwd.setScaledContents(True);# 图片自适应label大小

        # 设置登录返回按钮槽函数
        self.btn_admin.clicked.connect(self.login_verify)
        self.return_QPushButton.clicked.connect(self.open_login_page)

    def login_verify(self):
        # 计算屏幕的中心点坐标
        screen_geometry = QApplication.desktop().screenGeometry()
        center_x = screen_geometry.width() // 2
        center_y = screen_geometry.height() // 2

        username = self.username_QLineEdit.text()
        password = self.password_QLineEdit.text()
        try:
            cursor.execute('SELECT password FROM users WHERE username = %s AND is_admin = 1', (username,))
            result = cursor.fetchone()
            if result and self.verify_password(password, result[0]):
                self.open_admin_page()
            else:
                login_failed_message_box = QMessageBox()
                login_failed_message_box.setIcon(QMessageBox.Warning)
                login_failed_message_box.setWindowTitle("登录失败")
                login_failed_message_box.setText("管理员系统登录失败，请检查用户名和密码。")

                # 设置对话框的几何属性
                login_failed_message_box.setGeometry(center_x - login_failed_message_box.width() // 2,
                                                     center_y - login_failed_message_box.height() // 2, 300,
                                                     300)  # 设置对话框的位置和大小

                # 显示警告对话框
                login_failed_message_box.exec_()
                return False
        except pymysql.MySQLError as e:
            login_failed_message_box = QMessageBox()
            login_failed_message_box.setIcon(QMessageBox.Warning)
            login_failed_message_box.setWindowTitle("登录失败")
            login_failed_message_box.setText("数据库查询失败：", e)

            # 设置对话框的几何属性
            login_failed_message_box.setGeometry(center_x - login_failed_message_box.width() // 2,
                                                 center_y - login_failed_message_box.height() // 2, 300,
                                                 300)  # 设置对话框的位置和大小
            # print("数据库查询失败：", e)


    def open_login_page(self):
        self.close()
        self.login_page = logInWidget.logInWidget()
        self.login_page.show()

    def open_admin_page(self):
        self.close()
        self.admin_page = adminWidget.adminWidget()
        self.admin_page.ui.show()

    def verify_password(self,provided_password, stored_hash):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))