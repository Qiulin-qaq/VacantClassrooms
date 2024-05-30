import bcrypt
import pymysql

import registerWidget
import mainWidget
import adminLoginWidget
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox


from ui.loginWidgetUi import Ui_Widget

try:

    conn = pymysql.connect(host="localhost", user="root", password="3260.hxs", database="users_and_passwords")
    cursor = conn.cursor()
except pymysql.MySQLError as e:
    exit()


class logInWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # self.ui = uic.loadUi("./ui/loginWidget.ui")
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # 提取要操作的控件
        self.frame_pic = self.ui.frame_pic
        self.frame_backgroud = self.ui.frame_background
        self.label_pwd = self.ui.label_pwd
        self.label_user_name = self.ui.label_user_name
        # self.badge_QLabel = self.ui.lbl_badgePicture  # 校徽图片
        # self.SysName_QLabel = self.ui.lbl_SystemName  # 系统名称
        self.username_QLineEdit = self.ui.lineE_user_name  # 用户名输入框
        self.password_QLineEdit = self.ui.password  # 密码输入框
        self.login_QPushButton = self.ui.Btn_login  # 登录按钮
        self.register_QPushButton = self.ui.btn_register  # 注册按钮
        self.btn_admin = self.ui.btn_admin  # 管理员登录按钮

        self.password_QLineEdit.setEchoMode(2)  # 设置密码输入框为密码模式
        self.login_QPushButton.setShortcut("Return")  # 设置登录按钮快捷键为回车

        self.label_user_name.setScaledContents(True);  # 图片自适应label大小
        self.label_pwd.setScaledContents(True);  # 图片自适应label大小

        # 设置登录注册管理员按钮槽函数
        self.login_QPushButton.clicked.connect(self.login_verify)
        self.register_QPushButton.clicked.connect(self.open_register_page)
        self.btn_admin.clicked.connect(self.open_admin_login_page)

        # self.setWindowIcon(QIcon('./image/searchIcon.png'))
        # self.badge_QLabel.setPixmap(QPixmap('./image/schoolBadge.png'))
        # self.badge_QLabel.setScaledContents(True)
        # self.setGeometry(300, 300, 300, 300)

        # 皮肤设置
        # file = QFile("VacantClassrooms-master/qss/style.qss")  # QSS文件所在的路径
        # if file.open(QFile.ReadOnly):
        #     file_text = QTextStream(file)
        #     stylesheet = file_text.readAll()
        #     self.setStyleSheet(self,stylesheet)
        #     file.close()

    def login_verify(self):
        # 计算屏幕的中心点坐标
        screen_geometry = QApplication.desktop().screenGeometry()
        center_x = screen_geometry.width() // 2
        center_y = screen_geometry.height() // 2

        username = self.username_QLineEdit.text()
        password = self.password_QLineEdit.text()
        cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
        result = cursor.fetchone()
        if result and self.verify_password(password, result[0]):
            self.open_main_page()
        else:
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
        self.close()
        self.register_page = registerWidget.registerWidget()
        self.register_page.show()

    def open_main_page(self):
        self.close()
        self.main_page = mainWidget.mainWidget()
        self.main_page.show()

    def open_admin_login_page(self):
        self.close()
        self.admin_login_page = adminLoginWidget.adminLoginWidget()
        self.admin_login_page.show()

    # 对照哈希进行密码验证
    def verify_password(self, provided_password, stored_hash):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
