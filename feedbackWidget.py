import datetime

import pymysql
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QButtonGroup, QTableWidgetItem
import mainWidget


class feedbackWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()


    def init_ui(self):
        self.ui = uic.loadUi("./ui/feedbackWidget.ui")

        # 提取要操作的控件
        self.c1=self.ui.C1
        self.c2=self.ui.C2
        self.c3=self.ui.C3
        self.c4=self.ui.C4
        self.classrooms=self.ui.tableWidget
        self.textEdit=self.ui.textEdit
        self.Btn_return=self.ui.Btn_return
        self.Btn_clean=self.ui.Btn_clean
        self.Btn_send=self.ui.Btn_send


        self.c1.clicked.connect(self.show_classrooms)
        self.c2.clicked.connect(self.show_classrooms)
        self.c3.clicked.connect(self.show_classrooms)
        self.c4.clicked.connect(self.show_classrooms)
        self.Btn_clean.clicked.connect(self.textEdit.clear)
        self.Btn_send.clicked.connect(self.send_feedback)
        self.Btn_return.clicked.connect(self.open_mainWidget)
        self.classrooms.clicked.connect(self.get_classrooms)

        # 设置单选按钮组
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(self.c1)
        self.buttonGroup.addButton(self.c2)
        self.buttonGroup.addButton(self.c3)
        self.buttonGroup.addButton(self.c4)
        self.buttonGroup.setExclusive(True)

    def show_classrooms(self):
        sender=self.sender()
        building=sender.objectName().lower()
        conn = pymysql.connect(host='localhost', user='root', password='3260.hxs', database='vacantclassrooms')
        cursor = conn.cursor()

        # 获取指定教学楼的所有教室列表
        cursor.execute(f"SHOW TABLES LIKE '{building}_%'")
        all_classrooms = [row[0] for row in cursor.fetchall()]

        self.classrooms.setRowCount(len(all_classrooms))

        for row, classroom in enumerate(all_classrooms):
            item = QTableWidgetItem(classroom)
            item.setTextAlignment(Qt.AlignCenter)
            self.classrooms.setItem(row, 0, item)
        self.update()
        cursor.close()
        conn.close()


    def get_classrooms(self):
        selected_rows = self.classrooms.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            row_content = ""
            for column in range(self.classrooms.columnCount()):
                item = self.classrooms.item(row, column)
                if item is not None:
                    row_content += item.text() + " "
                else:
                    row_content += " "
            return row_content.strip()
        else:
            return ""

    def open_mainWidget(self):
        self.ui.close()
        self.mainWidget=mainWidget.mainWidget()
        self.mainWidget.show()


    def send_feedback(self):
        #排除没有输入的情况和没有选中的情况
        if self.textEdit.toPlainText()=="":
            self.textEdit.clear()
            self.textEdit.append("请输入反馈内容")
        elif self.get_classrooms()=="":
            self.textEdit.clear()
            self.textEdit.append("请选择教室")
        else:
            info=self.get_classrooms()
            send_time=datetime.datetime.now()
            text=self.textEdit.toPlainText()


            conn = pymysql.connect(host='localhost', user='root', password='3260.hxs', database='feedback')
            cursor = conn.cursor()

            # 准备SQL插入语句
            sql_insert = """
                            INSERT INTO feedback (info, send_time,text, is_verified)
                            VALUES (%s, %s, %s, 0)
                            """
            try:
                # 执行sql语句
                cursor.execute(sql_insert, (info, send_time ,text))
                conn.commit()  # 提交到数据库执行
                print("感谢您的反馈，我们将尽快核实。")
            except pymysql.MySQLError as e:
                # 发生错误时回滚
                conn.rollback()
                print("提交失败： ", e)
            #清除选中的行
            self.classrooms.selectionModel().clearSelection()
            cursor.close()
            conn.close()
            self.textEdit.clear()
            self.textEdit.append("反馈已上传，感谢您的反馈！")