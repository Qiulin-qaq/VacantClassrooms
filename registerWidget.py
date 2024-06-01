import bcrypt
import pymysql
import logInWidget
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from mysql.connector import cursor
from ui.registerWidgetUi import Ui_Widget

try:

    conn = pymysql.connect(host='localhost', user='root', password='111111', database='users_and_passwords')
    cursor = conn.cursor()
except pymysql.MySQLError as e:
    exit()


class registerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # 提取要操作的控件
        self.frame_pic = self.ui.frame_pic
        self.frame_backgroud = self.ui.frame_background
        self.label_pwd = self.ui.label_pwd
        self.label_user_name = self.ui.label_user_name
        self.username_QLineEdit = self.ui.lineE_user_name  # 用户名输入框
        self.password_QLineEdit = self.ui.password  # 密码输入框
        self.register_QPushButton = self.ui.btn_register  # 注册按钮
        self.return_QPushButton = self.ui.btn_Return  # 返回按钮
        self.register_QPushButton.setShortcut("Return")  # 设置注册按钮快捷键为回车

        # 设置注册按钮
        self.register_QPushButton.clicked.connect(self.register_user)
        # 设置返回按钮
        self.return_QPushButton.clicked.connect(self.open_login_page)

    def register_user(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        center_x = screen_geometry.width() // 2
        center_y = screen_geometry.height() // 2

        username = self.username_QLineEdit.text()
        password = self.password_QLineEdit.text()
        if username and password:  # 简单的验证
            try:
                hashed_password = self.hash_password(password)
                cursor.execute('INSERT INTO users(username, password) VALUES(%s, %s)', (username, hashed_password))
                conn.commit()

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
        self.close()
        self.login_page = logInWidget.logInWidget()
        self.login_page.show()

    def hash_password(self,password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    # 对照哈希进行密码验证
    def verify_password(self,provided_password, stored_hash):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
