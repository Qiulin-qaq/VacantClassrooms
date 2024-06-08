import re
from datetime import datetime
from functools import partial
import logInWidget


import pymysql
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QCheckBox, QHBoxLayout, QPushButton, QVBoxLayout, QComboBox, \
    QCompleter, QMessageBox, QMenu
from ui.ExtendedComboBox import ExtendedComboBox


class adminWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/adminWidget.ui")

        # 提取要操作的控件
        self.list=self.ui.listWidget
        self.Btn_return=self.ui.Btn_return
        self.stackedWidget=self.ui.stackedWidget
        self.table_feedback=self.ui.table_feedback
        self.Btn_refresh=self.ui.Btn_refresh
        self.Btn_refresh_2=self.ui.Btn_refresh_2
        self.table_class=self.ui.table_class
        self.frame_combobox=self.ui.frame_combobox
        self.pcomboBox=self.ui.pcomboBox
        self.current_week=self.ui.current_week
        self.table_user=self.ui.table_user
        self.user_name=self.ui.user_name
        self.Btn_refresh_user=self.ui.Btn_refresh_user
        self.user_name_2=self.ui.user_name_2
        self.table_admin=self.ui.table_admin
        self.Btn_refresh_admin=self.ui.Btn_refresh_admin

        self.list.currentRowChanged.connect(self.switch_widget)
        self.Btn_refresh.clicked.connect(self.refresh_feedback)
        self.Btn_refresh_2.clicked.connect(self.refresh_classroom)
        self.Btn_return.clicked.connect(self.return_login)
        self.Btn_refresh_user.clicked.connect(self.refresh_user)
        self.user_name.textChanged.connect(self.locate)
        self.user_name_2.textChanged.connect(self.locate_admin)
        self.Btn_refresh_admin.clicked.connect(self.refresh_admin)


        self.table_user.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_user.customContextMenuRequested.connect(self.on_tableWidget_customContextMenuRequested)

    def switch_widget(self):
        sender=self.sender()
        self.stackedWidget.setCurrentIndex(sender.currentRow())
        if sender.currentRow()==0:
            self.init_page_0()
        if sender.currentRow()==1:
            self.init_page_1()
        if sender.currentRow()==2:
            self.init_page_2()
        if sender.currentRow()==3:
            self.init_page_3()

    def init_page_2(self):
        self.table_feedback.clearContents()
        self.table_feedback.setColumnWidth(0, 150)  # 第一列宽度为 100 像素
        self.table_feedback.setColumnWidth(1, 250)
        self.table_feedback.setColumnWidth(2, 500)
        self.table_feedback.setColumnWidth(3, 150)
        self.table_feedback.setColumnWidth(4, 150)
        self.table_feedback.setColumnWidth(5, 200)
        # 初始化连接和游标
        conn = None
        cursor = None

        try:
            # 尝试连接数据库
            conn = pymysql.connect(host='localhost', user='root', password='111111', database='feedback')
            cursor = conn.cursor()
            print("数据库连接成功")

            # 执行查询
            query = "SELECT info,send_time,text,is_verified,id FROM feedback"
            cursor.execute(query)

            # 获取查询结果
            results = cursor.fetchall()
            row=0
            for record in results:
                info,send_time,text,is_verified,id = record  # 包括 id 在解包中
                send_time = send_time.strftime('%Y-%m-%d %H:%M')
                if is_verified == 1:
                    continue  # 如果is_verified为1，则跳过该记录，不存入表格中
                self.table_feedback.insertRow(row)
                self.table_feedback.setItem(row, 0, QTableWidgetItem(info))
                self.table_feedback.setItem(row, 1, QTableWidgetItem(send_time))
                self.table_feedback.setItem(row, 2, QTableWidgetItem(text))
                id_item = QTableWidgetItem(str(id))
                id_item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中对齐
                self.table_feedback.setItem(row, 3, id_item)
                # 设置第五列为复选框
                checkbox = QCheckBox()
                checkbox.setObjectName("checkSelect")
                cell_widget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(layout)
                layout.addWidget(checkbox)
                layout.setAlignment(checkbox, Qt.AlignCenter)
                self.table_feedback.setCellWidget(row, 4, cell_widget)
                # 设置第六列为按钮
                button = QPushButton()
                button.setObjectName("modifyClassroom")
                cell_widget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(layout)
                layout.addWidget(button)
                layout.setAlignment(button, Qt.AlignCenter)

                button_text = "修改空闲状态"
                button.setStyleSheet("text-decoration: underline; color: blue;")
                button.setText(button_text)
                button.clicked.connect(partial(self.modify_classroom,row))
                self.table_feedback.setCellWidget(row, 5, cell_widget)
                row=row+1

        except pymysql.MySQLError as e:
            print("数据库连接失败或查询错误: ", e)
        finally:
            # 关闭游标和连接
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def refresh_feedback(self):
        for row in range(self.table_feedback.rowCount()):
            pWidget = self.table_feedback.cellWidget(row, 4)
            if pWidget is not None:
                childWidgets = pWidget.findChildren(QCheckBox, "checkSelect")
                pCheckBox = childWidgets[0]
                if pCheckBox.isChecked():
                    id = self.table_feedback.item(row, 3).text()
                    #不能按照row查需要删除的数据
                    #根据反馈更新数据库中的是否处理反馈
                    try:
                        # 尝试连接数据库
                        conn = pymysql.connect(host='localhost', user='root', password='111111', database='feedback')
                        cursor = conn.cursor()
                        print("数据库连接成功")

                        # 执行查询
                        query = "UPDATE `feedback`.`feedback` SET `is_verified` = '1' WHERE (`id` = %s);"
                        cursor.execute(query, (id,))
                        conn.commit()  # 提交事务
                    except pymysql.MySQLError as e:
                        print("数据库连接失败或查询错误: ", e)
                    finally:
                        # 关闭游标和连接
                        if cursor:
                            cursor.close()
                        if conn:
                            conn.close()
                    # 从表格中删除选中行(删除已经处理过的反馈)
                    self.table_feedback.removeRow(row)

    def modify_classroom(self,row):
        item = self.table_feedback.item(row, 0)
        if item is not None:
            classroom_name = item.text()
            print(classroom_name)
            pattern = r'^[c]\d{1}[_]\d{3}\w?$'
            match = re.match(pattern, classroom_name)
            if not match:
                QMessageBox.critical(None, "错误", "classroom_name 格式不正确")
                return
            self.list.setCurrentRow(3)
            self.stackedWidget.setCurrentIndex(3)
            self.init_page_3()
            self.pcomboBox.setCurrentText(classroom_name)
            self.choose_classroom()


    def get_current_week_number(self):
        # 设置第一周的第一天日期
        first_day_of_first_week = datetime(2024, 2, 26)
        # 获取当前日期
        current_date = datetime.now()
        # 计算当前日期与第一周的第一天之间的天数差
        days_diff = (current_date - first_day_of_first_week).days
        # 计算当前是第几周
        current_week = (days_diff // 7) + 1
        return current_week

    def init_page_3(self):
        self.current_week.setText(str(self.get_current_week_number())+"周")
        self.pcomboBox.setEditable(True)
        pCompleter = QCompleter(self.pcomboBox.model())
        pCompleter.setFilterMode(Qt.MatchContains)
        self.pcomboBox.setCompleter(pCompleter)

        self.table_class.clearContents()
        self.table_class.setColumnWidth(0, 150)
        self.table_class.setColumnWidth(1, 150)
        self.table_class.setColumnWidth(2, 150)
        self.table_class.setColumnWidth(3, 150)
        self.table_class.setColumnWidth(4, 150)
        self.table_class.setColumnWidth(5, 150)
        self.table_class.setColumnWidth(6, 150)
        self.table_class.setColumnWidth(7, 250)
        self.table_class.setColumnWidth(8, 250)
        
        self.pcomboBox.setCurrentIndex(-1)
        self.pcomboBox.currentTextChanged.connect(self.choose_classroom)
        
    def choose_classroom(self):
        self.table_class.clearContents()
        classroom_name=self.pcomboBox.currentText()
        if classroom_name=="":
            return
        conn = None
        cursor = None

        try:
            # 尝试连接数据库
            conn = pymysql.connect(host='localhost', user='root', password='111111', database='vacantclassrooms')
            cursor = conn.cursor()
            print("数据库连接成功")

            # 执行查询
            query = "SELECT Mon, Tues, Wed, Thur, Fri, Sat, Sun, start_time, end_time FROM {}".format(classroom_name)
            cursor.execute(query)

            # 获取查询结果
            results = cursor.fetchall()
            row = 0
            for record in results:
                Mon, Tues, Wed, Thur, Fri, Sat, Sun, start_time, end_time  = record  # 包括 id 在解包中
                start_time = start_time.strftime('%H:%M')
                end_time = end_time.strftime('%H:%M')
                self.table_class.insertRow(row)
                item=QTableWidgetItem(Mon)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 0, item)
                item=QTableWidgetItem(Tues)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 1, item)
                item=QTableWidgetItem(Wed)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 2, item)
                item=QTableWidgetItem(Thur)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 3, item)
                item=QTableWidgetItem(Fri)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 4, item)
                item=QTableWidgetItem(Sat)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 5, item)
                item=QTableWidgetItem(Sun)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 6, item)
                item=QTableWidgetItem(start_time)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 7, item)
                item=QTableWidgetItem(end_time)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_class.setItem(row, 8, item)
                row = row + 1
        except pymysql.MySQLError as e:
            print("数据库连接失败或查询错误: ", e)
        finally:
            # 关闭游标和连接
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        while self.table_class.rowCount() > 14:
            self.table_class.removeRow(14)

    def refresh_classroom(self):
        classroom_name=self.pcomboBox.currentText()
        for row in range(self.table_feedback.rowCount()):
            Mon = self.table_class.item(row, 0).text()
            Tues = self.table_class.item(row, 1).text()
            Wed = self.table_class.item(row, 2).text()
            Thur = self.table_class.item(row, 3).text()
            Fri = self.table_class.item(row, 4).text()
            Sat = self.table_class.item(row, 5).text()
            Sun = self.table_class.item(row, 6).text()
            #根据反馈更新数据库中的是否处理反馈
            try:
                # 尝试连接数据库
                conn = pymysql.connect(host='localhost', user='root', password='111111', database='vacantclassrooms')
                cursor = conn.cursor()
                print("数据库连接成功")

                # 执行查询
                query = "UPDATE `vacantclassrooms`.`{}` SET `Mon` = %s, `Tues` = %s, `Wed` = %s, `Thur` = %s, `Fri` = %s, `Sat` = %s, `Sun` = %s WHERE `id` = %s;"
                cursor.execute(query.format(classroom_name), (Mon, Tues, Wed, Thur, Fri, Sat, Sun, row+1))
                conn.commit()  # 提交事务
            except pymysql.MySQLError as e:
                print("数据库连接失败或查询错误: ", e)
            finally:
                # 关闭游标和连接
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def return_login(self):
        self.ui.close()
        self.loginWidget=logInWidget.logInWidget()
        self.loginWidget.show()

    def init_page_0(self):
        self.list.setCurrentRow(0)
        self.table_user.clearContents()
        self.table_user.setColumnWidth(0, 200)  # 第一列宽度为 100 像素
        self.table_user.setColumnWidth(1, 500)
        self.table_user.setColumnWidth(2, 150)
        self.table_user.setColumnWidth(3, 150)
        # 初始化连接和游标
        conn = None
        cursor = None

        try:
            # 尝试连接数据库
            conn = pymysql.connect(host='localhost', user='root', password='111111', database='users_and_passwords')
            cursor = conn.cursor()
            print("数据库连接成功")

            # 执行查询
            query = "SELECT username,password,is_admin,id FROM users"
            cursor.execute(query)

            # 获取查询结果
            results = cursor.fetchall()
            row = 0
            for record in results:
                username,password,is_admin,id = record  # 包括 id 在解包中
                self.table_user.insertRow(row)
                item=QTableWidgetItem(username)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_user.setItem(row, 0, item)
                self.table_user.setItem(row, 1, QTableWidgetItem(password))
                id_item = QTableWidgetItem(str(id))
                id_item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中对齐
                self.table_user.setItem(row, 3, id_item)
                # 设置第五列为复选框
                checkbox = QCheckBox()
                checkbox.setObjectName("checkAdmin")
                cell_widget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(layout)
                layout.addWidget(checkbox)
                layout.setAlignment(checkbox, Qt.AlignCenter)
                if is_admin==1:
                    checkbox.setChecked(True)
                self.table_user.setCellWidget(row, 2, cell_widget)
                row = row + 1
        except pymysql.MySQLError as e:
            print("数据库连接失败或查询错误: ", e)
        finally:
            # 关闭游标和连接
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def refresh_user(self):
        for row in range(self.table_user.rowCount()):
            item = self.table_user.item(row, 0)
            if item is None:
                continue
            username = item.text()
            item = self.table_user.item(row, 1)
            password = item.text()
            pWidget = self.table_user.cellWidget(row, 2)
            if pWidget is not None:
                childWidgets = pWidget.findChildren(QCheckBox, "checkAdmin")
                pCheckBox = childWidgets[0]
                if pCheckBox.isChecked():
                    is_admin = 1
                else:
                    is_admin = 0
            item = self.table_user.item(row, 3)
            id = item.text()
            #根据反馈更新数据库中的是否处理反馈
            try:
                # 尝试连接数据库
                conn = pymysql.connect(host='localhost', user='root', password='111111', database='users_and_passwords')
                cursor = conn.cursor()
                print("数据库连接成功")

                # 执行查询
                query = "UPDATE `users_and_passwords`.`users` SET `username` = %s, `password` = %s, `is_admin` = %s,  `id` = %s WHERE `id` = %s;"
                cursor.execute(query, (username, password, is_admin, id,id))
                conn.commit()  # 提交事务
            except pymysql.MySQLError as e:
                print("数据库连接失败或查询错误: ", e)
            finally:
                # 关闭游标和连接
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def locate(self):
        input_name = self.user_name.text()
        row_num = self.table_user.rowCount()

        if input_name == "":
            for i in range(row_num):
                self.table_user.setRowHidden(i, False)
        else:
            items = self.table_user.findItems(self.user_name.text(), Qt.MatchContains)
            for i in range(row_num):
                self.table_user.setRowHidden(i, True)

            if items:
                for item in items:
                    self.table_user.setRowHidden(item.row(), False)

    def on_tableWidget_customContextMenuRequested(self, pos):
        menu = QMenu(self)
        add_user = menu.addAction("添加行")
        menu.addSeparator()
        delete_user = menu.addAction("删除行")

        add_user.triggered.connect(partial(self.add_row,pos))
        delete_user.triggered.connect(partial(self.delete_row,pos))

        menu.exec_(self.table_user.mapToGlobal(pos))

    def add_row(self,pos):
        clicked_row = self.table_user.indexAt(pos).row()
        self.table_user.insertRow(clicked_row + 1)
        self.table_user.setItem(clicked_row + 1, 0, QTableWidgetItem(""))
        self.table_user.setItem(clicked_row + 1, 1, QTableWidgetItem(""))
        self.table_user.setItem(clicked_row + 1, 2, QTableWidgetItem(""))
        self.table_user.setItem(clicked_row + 1, 3, QTableWidgetItem(""))

    def delete_row(self,pos):
        clicked_row = self.table_user.indexAt(pos).row()
        self.table_user.removeRow(clicked_row)

    def init_page_1(self):
        self.table_admin.clearContents()
        self.table_admin.setColumnWidth(0, 200)  # 第一列宽度为 100 像素
        self.table_admin.setColumnWidth(1, 500)
        self.table_admin.setColumnWidth(2, 150)
        self.table_admin.setColumnWidth(3, 150)
        # 初始化连接和游标
        conn = None
        cursor = None

        try:
            # 尝试连接数据库
            conn = pymysql.connect(host='localhost', user='root', password='111111', database='users_and_passwords')
            cursor = conn.cursor()
            print("数据库连接成功")

            # 执行查询
            query = "SELECT username,password,is_admin,id FROM users"
            cursor.execute(query)

            # 获取查询结果
            results = cursor.fetchall()
            row = 0
            for record in results:
                username, password, is_admin, id = record  # 包括 id 在解包中
                print(is_admin)
                if is_admin == 0:
                    continue
                else:
                    self.table_admin.insertRow(row)
                    item = QTableWidgetItem(username)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_admin.setItem(row, 0, item)
                    self.table_admin.setItem(row, 1, QTableWidgetItem(password))
                    id_item = QTableWidgetItem(str(id))
                    id_item.setTextAlignment(Qt.AlignCenter)  # 设置文本居中对齐
                    self.table_admin.setItem(row, 3, id_item)
                    # 设置第五列为复选框
                    checkbox = QCheckBox()
                    checkbox.setObjectName("checkAdmin")
                    checkbox.setChecked(True)
                    cell_widget = QWidget()
                    layout = QHBoxLayout()
                    layout.setContentsMargins(0, 0, 0, 0)
                    cell_widget.setLayout(layout)
                    layout.addWidget(checkbox)
                    layout.setAlignment(checkbox, Qt.AlignCenter)
                    self.table_admin.setCellWidget(row, 2, cell_widget)
                    row = row + 1
        except pymysql.MySQLError as e:
            print("数据库连接失败或查询错误: ", e)
        finally:
            # 关闭游标和连接
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def refresh_admin(self):
        for row in range(self.table_admin.rowCount()):
            item = self.table_admin.item(row, 0)
            if item is None:
                continue
            username = item.text()
            item = self.table_admin.item(row, 1)
            password = item.text()
            pWidget = self.table_admin.cellWidget(row, 2)
            if pWidget is not None:
                childWidgets = pWidget.findChildren(QCheckBox, "checkAdmin")
                pCheckBox = childWidgets[0]
                if pCheckBox.isChecked():
                    is_admin = 1
                else:
                    is_admin = 0
            item = self.table_admin.item(row, 3)
            id = item.text()
            # 根据反馈更新数据库中的是否处理反馈
            try:
                # 尝试连接数据库
                conn = pymysql.connect(host='localhost', user='root', password='111111', database='users_and_passwords')
                cursor = conn.cursor()
                print("数据库连接成功")

                # 执行查询
                query = "UPDATE `users_and_passwords`.`users` SET `username` = %s, `password` = %s, `is_admin` = %s,  `id` = %s WHERE `id` = %s;"
                cursor.execute(query, (username, password, is_admin, id, id))
                conn.commit()  # 提交事务
            except pymysql.MySQLError as e:
                print("数据库连接失败或查询错误: ", e)
            finally:
                # 关闭游标和连接
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def locate_admin(self):
        input_name = self.user_name_2.text()
        row_num = self.table_admin.rowCount()

        if input_name == "":
            for i in range(row_num):
                self.table_admin.setRowHidden(i, False)
        else:
            items = self.table_admin.findItems(self.user_name_2.text(), Qt.MatchContains)
            for i in range(row_num):
                self.table_admin.setRowHidden(i, True)

            if items:
                for item in items:
                    self.table_admin.setRowHidden(item.row(), False)


