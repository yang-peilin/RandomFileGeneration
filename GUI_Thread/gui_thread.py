
import os
import re
import time
import random
import shutil
import string
import numpy as np

from PyQt6.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFrame, QFileDialog, QMainWindow, QMessageBox)

from Thread.GenerateThread import GenerateThread
from Thread.CheckThread import CheckThread
from Common.ShareObject import ShareObject
from Common.utils import byte2string, string2byte
from Common.utils import generate_normal_random_number


def changePalette():
    QApplication.setPalette(QApplication.style().standardPalette())


def changeStyle(styleName):
    QApplication.setStyle(QStyleFactory.create(styleName))
    changePalette()


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        # 构造文件系统所需的变量
        self.root_path = ""
        self.root_path_temp = ""
        self.N = 5
        self.folder_number_min = 1
        self.folder_number_max = 5
        self.generate_limit_way = 'byNumber'
        self.file_number_max = 500
        self.prev_file_number_max = 500
        self.folder_size_max = 100
        self.prev_folder_size_max = 100
        self.folder_size_max_unit = 'MB'
        self.file_size_mean = 500
        self.prev_file_size_mean = 500
        self.file_size_mean_unit = 'KB'
        self.file_size_min = 200
        self.prev_file_size_min = 200
        self.file_size_min_unit = 'KB'
        self.file_size_max = 1000
        self.prev_file_size_max = 1000
        self.file_size_max_unit = 'KB'
        self.file_size_standard_deviation = 500
        self.prev_file_size_standard_deviation = 500
        self.file_distribution_place = 'all'
        self.file_size_generate_way = 'average'
        self.shared_object = ShareObject(False)

        # 创建线程
        self.generate_thread = GenerateThread(self.root_path, int(self.N), int(self.folder_number_min), int(self.folder_number_max),
                                         string2byte(str(self.folder_size_max) + self.folder_size_max_unit), int(self.file_number_max),
                                         string2byte(str(self.file_size_mean) + self.file_size_mean_unit),
                                         string2byte(str(self.file_size_min) + self.file_size_min_unit),
                                         string2byte(str(self.file_size_max) + self.file_size_max_unit),
                                         int(self.file_size_standard_deviation),
                                         self.generate_limit_way, self.file_distribution_place, self.file_size_generate_way,
                                         self.shared_object)
        self.check_thread = CheckThread(self.root_path, self.generate_limit_way, self.shared_object)

        # QComboBox：下拉列表框
        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())
        styleComboBox.textActivated.connect(changeStyle)
        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        # 创建用来选取样式的部分
        styleLayout = QHBoxLayout()
        styleLayout.addWidget(styleLabel)
        styleLayout.addWidget(styleComboBox)
        styleLayout.addStretch(1)

        # 创建用来选取文件路径的
        self.createTopGroupBox()
        self.createTopLeftBlock()
        self.createTopRightBlock()
        self.createBottomLeftBlock()
        self.createBottomRightBlock()
        self.createDecisionBlock()
        self.createProgressBlock()
        self.createProgressDecisionBlock()

        # 整体布局
        mainLayout = QGridLayout()
        mainLayout.addLayout(styleLayout, 0, 0, 1, 8)
        mainLayout.addWidget(self.topBlock, 1, 0, 1, 8)
        mainLayout.addWidget(self.topLeftBlock, 2, 0, 1, 4)
        mainLayout.addWidget(self.topRightBlock, 2, 4, 1, 4)
        mainLayout.addWidget(self.bottomLeftBlock, 3, 0, 2, 4)
        mainLayout.addWidget(self.bottomRightBlock, 3, 4, 1, 4)
        mainLayout.addWidget(self.decisionBlock, 4, 4, 1, 4)
        mainLayout.addWidget(self.progressBlock, 5, 0, 1, 6)
        mainLayout.addWidget(self.progressDecision, 5, 6, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setRowStretch(4, 1)
        mainLayout.setRowStretch(5, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        mainLayout.setColumnStretch(4, 1)
        mainLayout.setColumnStretch(5, 1)
        mainLayout.setColumnStretch(6, 1)
        mainLayout.setColumnStretch(7, 1)
        self.setLayout(mainLayout)
        self.setWindowTitle("海量小文件生成器")
        changeStyle('macOS')

        # 把暂停与继续disable
        self.button_continue.setEnabled(False)
        self.button_pause.setEnabled(False)
        self.button_terminate.setEnabled(False)

        # 窗口置于顶部
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    def createTopGroupBox(self):
        self.topBlock = QGroupBox("选取root路径【root路径默认为：该程序同一级别文件夹/root】")

        # 创建主窗口中的控件
        self.button_root_path = QPushButton("请选择一个路径")
        self.button_root_path.clicked.connect(self.choose_folder)

        self.folderLine_root_path = QLineEdit()
        self.folderLine_root_path.setReadOnly(True)  # 设置文本框为只读

        # 设置默认值
        self.folderLine_root_path.setText(self.default_root_path())
        self.root_path = self.root_path_temp

        # 创建布局并添加控件
        layout = QHBoxLayout()
        layout.addWidget(self.button_root_path)
        layout.addWidget(self.folderLine_root_path)
        self.topBlock.setLayout(layout)

    def default_root_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_path_temp = os.path.join(current_dir, "root")
        return self.root_path_temp

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")

        if folder_path:
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path)
                except OSError as e:
                    QMessageBox.critical(self, '错误', f'无法创建文件夹：{str(e)}')
                    return

            if folder_path != self.default_root_path() and os.listdir(folder_path):
                QMessageBox.warning(self, '警告', f'{folder_path}不合法，请选择一个空路径或其他路径')
            else:
                self.root_path = folder_path
                self.folderLine_root_path.setText(folder_path)
        else:
            QMessageBox.information(self, '提示', '未选择文件夹。')

        print("self.root_path:", self.root_path, "type:", type(self.root_path))

    def createTopLeftBlock(self):
        self.topLeftBlock = QGroupBox("文件结构选项")
        gridLayout = QGridLayout()

        # 需要一个水平布局，放置N
        label = QLabel('需要构建的文件层级N：')
        gridLayout.addWidget(label, 0, 0, 1, 1)

        self.spinBox_N = QSpinBox()
        self.spinBox_N.setMinimum(1)
        self.spinBox_N.setValue(self.N)
        gridLayout.addWidget(self.spinBox_N, 0, 1, 1, 1)
        # 将值绑定到本地变量
        self.N = self.spinBox_N.value()
        # 连接值更改信号到槽函数
        self.spinBox_N.valueChanged.connect(self.update_N)

        # 设置每个文件夹需要包含的子文件夹数量的下限
        label = QLabel('每个文件夹包含的子文件夹的数量下限：')
        self.spinBox_folder_number_min = QSpinBox()
        self.spinBox_folder_number_min.setMinimum(1)
        self.spinBox_folder_number_min.setValue(self.folder_number_min)
        # 将值绑定到本地变量
        self.folder_number_min = self.spinBox_folder_number_min.value()
        # 连接值更改信号到槽函数
        self.spinBox_folder_number_min.valueChanged.connect(self.update_folder_number_min)
        gridLayout.addWidget(label, 1, 0, 1, 1)
        gridLayout.addWidget(self.spinBox_folder_number_min, 1, 1, 1, 1)

        # 设置每个文件夹需要包含的子文件夹数量的上限
        label = QLabel('每个文件夹包含的子文件夹的数量上限：')
        self.spinBox_folder_number_max = QSpinBox()
        self.spinBox_folder_number_max.setValue(self.folder_number_max)
        # 将值绑定到本地变量
        self.folder_number_max = self.spinBox_folder_number_max.value()
        # 连接值更改信号到槽函数
        self.spinBox_folder_number_max.valueChanged.connect(self.update_folder_number_max)
        gridLayout.addWidget(label, 2, 0, 1, 1)
        gridLayout.addWidget(self.spinBox_folder_number_max, 2, 1, 1, 1)

        self.topLeftBlock.setLayout(gridLayout)

    def update_N(self):
        # 当值发生改变时更新本地变量
        self.N = self.spinBox_N.value()
        print(f"设置的N为：{self.N}" + " type: " + str(type(self.N)))

    def update_folder_number_min(self):
        if self.folder_number_min >= self.spinBox_folder_number_max.value():
            self.folder_number_min = self.spinBox_folder_number_max.value() - 1
            self.spinBox_folder_number_min.setValue(self.spinBox_folder_number_max.value() - 1)
            print("下限不能大于上限")
        else:
            # 当值发生改变时更新本地变量
            self.folder_number_min = self.spinBox_folder_number_min.value()
            print(f"设置的folder_number_min为：{self.folder_number_min}" + " type: " + str(type(self.folder_number_min)))

    def update_folder_number_max(self):
        if self.folder_number_max <= self.spinBox_folder_number_min.value():
            self.folder_number_max = self.spinBox_folder_number_min.value() + 1
            self.spinBox_folder_number_max.setValue(self.spinBox_folder_number_min.value() + 1)
            print("上限不能小于下限")
        self.folder_number_max = self.spinBox_folder_number_max.value()
        print(f"设置的folder_number_max为：{self.folder_number_max}" + " type: " + str(type(self.folder_number_max)))

    def createTopRightBlock(self):
        self.topRightBlock = QGroupBox("生成文件的约束方式")

        # grid布局
        gridLayout = QGridLayout()

        # 按照文件数量byNumber/文件总大小bySize 进行约束
        label = QLabel('【按照文件数量大小限制请选择byNumber，按照空间大小限制请选择bySize】')
        styleLabel = QLabel("请选择bySize/byNumber:")
        self.styleComboBox_generate_limit_way = QComboBox()
        self.styleComboBox_generate_limit_way.addItems(['byNumber', 'bySize'])
        self.styleComboBox_generate_limit_way.setCurrentText(self.generate_limit_way)
        # 将值绑定到本地变量
        self.generate_limit_way = self.styleComboBox_generate_limit_way.currentText()
        # 连接值更改信号到槽函数
        self.styleComboBox_generate_limit_way.currentTextChanged.connect(self.update_generate_limit_way)
        # 布局
        gridLayout.addWidget(label, 0, 0, 1, 3)
        gridLayout.addWidget(styleLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.styleComboBox_generate_limit_way, 1, 1, 1, 2)

        # 生成文件的最大数量
        label = QLabel('生成文件数量的最大值：')
        self.lineEdit_file_number_max = QLineEdit()
        self.lineEdit_file_number_max.setPlaceholderText("输入数字代表需要生成的文件数量 (e.g. 10000)")
        self.lineEdit_file_number_max.setText(str(self.file_number_max))
        # 将值绑定到本地变量
        self.file_number_max = self.lineEdit_file_number_max.text()
        # 连接值更改信号到槽函数
        self.lineEdit_file_number_max.textChanged.connect(self.update_file_number_max)
        # 布局
        gridLayout.addWidget(label, 2, 0, 1, 1)
        gridLayout.addWidget(self.lineEdit_file_number_max, 2, 1, 1, 2)

        # # 生成文件的总大小
        label = QLabel('生成的文件夹大小上限：')
        self.lineEdit_folder_size_max = QLineEdit()
        self.lineEdit_folder_size_max.setPlaceholderText("生成的文件占据空间总大小")
        self.lineEdit_folder_size_max.setText(str(self.folder_size_max))
        self.styleComboBox_folder_size_max = QComboBox()
        self.styleComboBox_folder_size_max.addItems(['B', 'KB', 'MB', 'GB'])
        self.styleComboBox_folder_size_max.setCurrentText(str(self.folder_size_max_unit))
        # 将值绑定到本地变量
        self.folder_size_max = self.lineEdit_folder_size_max.text()
        self.folder_size_max_unit = self.styleComboBox_folder_size_max.currentText()
        # 连接值更改信号到槽函数
        self.lineEdit_folder_size_max.textChanged.connect(self.update_folder_size_max)
        self.styleComboBox_folder_size_max.currentTextChanged.connect(self.update_folder_size_max_unit)
        # 布局
        gridLayout.addWidget(label, 3, 0, 1, 1)
        gridLayout.addWidget(self.lineEdit_folder_size_max, 3, 1, 1, 1)
        gridLayout.addWidget(self.styleComboBox_folder_size_max, 3, 2, 1, 1)

        self.topRightBlock.setLayout(gridLayout)

    def update_generate_limit_way(self):
        self.generate_limit_way = self.styleComboBox_generate_limit_way.currentText()
        print("self.generate_limit_way: ", self.generate_limit_way + " type: " + str(type(self.generate_limit_way)))

    def update_file_number_max(self):
        file_number_max_text = self.lineEdit_file_number_max.text()
        if file_number_max_text == '':
            print("file_number_max_text == null")
            return

        try:
            print('here ' + self.lineEdit_file_number_max.text())
            file_number_max = int(file_number_max_text)
            if file_number_max < 0:
                QMessageBox.information(self, '提示', '不能输入小于0的整数。')
                # 将文本框中的值恢复为之前的有效值
                self.lineEdit_file_number_max.setText(str(self.prev_file_number_max))
            else:
                self.file_number_max = file_number_max
                self.prev_file_number_max = file_number_max_text
        except ValueError:
            QMessageBox.information(self, '提示', '请输入一个有效的整数。')
            # 将文本框中的值恢复为之前的有效值
            self.lineEdit_file_number_max.setText(str(self.prev_file_number_max))

    def update_folder_size_max(self):
        folder_size_max_text = self.lineEdit_folder_size_max.text()
        if folder_size_max_text == '':
            print("folder_size_max_text == null")
            return

        try:
            file_folder_size_max = int(folder_size_max_text)
            if file_folder_size_max < 0:
                QMessageBox.information(self, '提示', '不能输入小于0的整数。')
                # 将文本框中的值恢复为之前的有效值
                self.lineEdit_folder_size_max.setText(str(self.prev_folder_size_max))
            else:
                self.folder_size_max = file_folder_size_max
                self.prev_folder_size_max = folder_size_max_text
        except ValueError:
            QMessageBox.information(self, '提示', '请输入一个有效的整数。')
            # 将文本框中的值恢复为之前的有效值
            self.lineEdit_folder_size_max.setText(str(self.prev_folder_size_max))

    def update_folder_size_max_unit(self):
        self.folder_size_max_unit = self.styleComboBox_folder_size_max.currentText()
        print("self.folder_size_max_unit: ", self.folder_size_max_unit + " type: " + str(type(self.folder_size_max_unit)))

    def createBottomLeftBlock(self):
        self.bottomLeftBlock = QGroupBox("单个文件大小的参数")

        gridLayout = QGridLayout()

        # 规定单个文件的平均大小
        label = QLabel('请输入字符串代表单个文件大小的平均值：')
        self.lineEdit_file_size_mean = QLineEdit()
        self.lineEdit_file_size_mean.setPlaceholderText("e.g. 200")
        self.lineEdit_file_size_mean.setText(str(self.file_size_mean))
        self.styleComboBox_file_size_mean = QComboBox()
        self.styleComboBox_file_size_mean.addItems(['B', 'KB', 'MB', 'GB'])
        self.styleComboBox_file_size_mean.setCurrentText(self.file_size_mean_unit)
        # 将值绑定到本地变量
        self.file_size_mean = self.lineEdit_file_size_mean.text()
        self.file_size_mean_unit = self.styleComboBox_file_size_mean.currentText()
        # 连接值更改信号到槽函数
        self.lineEdit_file_size_mean.textChanged.connect(self.update_file_size_mean)
        self.styleComboBox_file_size_mean.currentTextChanged.connect(self.update_file_size_mean_unit)
        # 布局
        gridLayout.addWidget(label, 0, 0, 1, 1)
        gridLayout.addWidget(self.lineEdit_file_size_mean, 0, 1, 1, 1)
        gridLayout.addWidget(self.styleComboBox_file_size_mean, 0, 2, 1, 1)

        # 规定单个文件的最小值
        label = QLabel('请输入字符串代表单个文件大小的最小值：')
        self.lineEdit_file_size_min = QLineEdit()
        self.lineEdit_file_size_min.setPlaceholderText("e.g. 10")
        self.lineEdit_file_size_min.setText(str(self.file_size_min))
        self.styleComboBox_file_size_min = QComboBox()
        self.styleComboBox_file_size_min.addItems(['B', 'KB', 'MB', "GB"])
        self.styleComboBox_file_size_min.setCurrentText(self.file_size_min_unit)
        # 将值绑定到本地变量
        self.file_size_min = self.lineEdit_file_size_min.text()
        self.file_size_min_unit = self.styleComboBox_file_size_min.currentText()
        # 连接值更改信号到槽函数
        self.lineEdit_file_size_min.textChanged.connect(self.update_file_size_min)
        self.styleComboBox_file_size_min.currentTextChanged.connect(self.update_file_size_min_unit)
        # 布局
        gridLayout.addWidget(label, 1, 0, 1, 1)
        gridLayout.addWidget(self.lineEdit_file_size_min, 1, 1, 1, 1)
        gridLayout.addWidget(self.styleComboBox_file_size_min, 1, 2, 1, 1)

        # 规定单个文件的最大值
        label = QLabel('请输入字符串代表单个文件大小的最大值：')
        self.lineEdit_file_size_max = QLineEdit()
        self.lineEdit_file_size_max.setPlaceholderText("e.g. 500")
        self.lineEdit_file_size_max.setText(str(self.file_size_max))
        self.styleComboBox_file_size_max = QComboBox()
        self.styleComboBox_file_size_max.addItems(['B', 'KB', 'MB', "GB"])
        self.styleComboBox_file_size_max.setCurrentText(self.file_size_max_unit)
        # 将值绑定到本地变量
        self.file_size_max = self.lineEdit_file_size_max.text()
        self.file_size_max_unit = self.styleComboBox_file_size_max.currentText()
        # 连接值更改信号到槽函数
        self.lineEdit_file_size_max.textChanged.connect(self.update_file_size_max)
        self.styleComboBox_file_size_max.currentTextChanged.connect(self.update_file_size_max_unit)
        # 布局
        gridLayout.addWidget(label, 2, 0, 1, 1)
        gridLayout.addWidget(self.lineEdit_file_size_max, 2, 1, 1, 1)
        gridLayout.addWidget(self.styleComboBox_file_size_max, 2, 2, 1, 1)

        # 规定单个文件的大小的辨准差
        label = QLabel('请输入字符串代表单个文件大小的标准差：')
        self.lineEdit_file_size_standard_deviation = QLineEdit()
        self.lineEdit_file_size_standard_deviation.setPlaceholderText("e.g. 500")
        self.lineEdit_file_size_standard_deviation.setText(str(self.file_size_standard_deviation))
        # 将值绑定到本地变量
        self.file_size_standard_deviation = self.lineEdit_file_size_standard_deviation.text()
        # 连接值更改信号到槽函数
        self.lineEdit_file_size_standard_deviation.textChanged.connect(self.update_file_size_standard_deviation)
        # 布局
        gridLayout.addWidget(label, 3, 0, 1, 1)
        gridLayout.addWidget(self.lineEdit_file_size_standard_deviation, 3, 1, 1, 1)

        self.bottomLeftBlock.setLayout(gridLayout)

    def update_file_size_mean(self):
        file_size_mean_text = self.lineEdit_file_size_mean.text()
        try:
            file_size_mean = int(file_size_mean_text)
            if file_size_mean < 0:
                QMessageBox.information(self, '提示', '不能输入小于0的整数。')
                # 将文本框中的值恢复为之前的有效值
                self.lineEdit_file_size_mean.setText(str(self.prev_file_size_mean))
            else:
                self.file_size_mean = file_size_mean
                self.prev_file_size_mean = file_size_mean_text
        except ValueError:
            QMessageBox.information(self, '提示', '请输入一个有效的整数。')
            # 将文本框中的值恢复为之前的有效值
            self.lineEdit_file_size_mean.setText(str(self.prev_file_size_mean))

    def update_file_size_mean_unit(self):
        self.file_size_mean_unit = self.styleComboBox_file_size_mean.currentText()
        print("self.file_size_mean_unit: ", self.file_size_mean_unit)

    def update_file_size_min(self):
        file_size_min_text = self.lineEdit_file_size_min.text()
        if file_size_min_text == '':
            print("file_size_min_text == null")
            return

        try:
            file_size_min = int(file_size_min_text)
            if file_size_min < 0:
                QMessageBox.information(self, '提示', '不能输入小于0的整数。')
                # 将文本框中的值恢复为之前的有效值
                self.lineEdit_file_size_min.setText(str(self.prev_file_size_min))
            else:
                self.file_size_min = file_size_min
                self.prev_file_size_min = file_size_min_text
        except ValueError:
            QMessageBox.information(self, '提示', '请输入一个有效的整数。')
            # 将文本框中的值恢复为之前的有效值
            self.lineEdit_file_size_min.setText(str(self.prev_file_size_min))

    def update_file_size_min_unit(self):
        self.file_size_min_unit = self.styleComboBox_file_size_min.currentText()
        print("self.file_size_min_unit: ", self.file_size_min_unit)

    def update_file_size_max(self):
        file_size_max_text = self.lineEdit_file_size_max.text()
        if file_size_max_text == '':
            print("file_size_max_text == null")
            return

        try:
            file_size_max = int(file_size_max_text)
            if file_size_max < 0:
                QMessageBox.information(self, '提示', '不能输入小于0的整数。')
                # 将文本框中的值恢复为之前的有效值
                self.lineEdit_file_size_max.setText(str(self.prev_file_size_max))
            else:
                self.file_size_max = file_size_max
                self.prev_file_size_max = file_size_max_text
        except ValueError:
            QMessageBox.information(self, '提示', '请输入一个有效的整数。')
            # 将文本框中的值恢复为之前的有效值
            self.lineEdit_file_size_max.setText(str(self.prev_file_size_max))

    def update_file_size_max_unit(self):
        self.file_size_max_unit = self.styleComboBox_file_size_max.currentText()
        print("self.file_size_max_unit: ", self.file_size_max_unit)

    def update_file_size_standard_deviation(self):
        file_size_standard_deviation_text = self.lineEdit_file_size_standard_deviation.text()
        if file_size_standard_deviation_text == '':
            print("file_size_standard_deviation_text == null")
            return

        try:
            file_size_standard_deviation = int(file_size_standard_deviation_text)
            if file_size_standard_deviation < 0:
                QMessageBox.information(self, '提示', '不能输入小于0的整数。')
                # 将文本框中的值恢复为之前的有效值
                self.lineEdit_file_size_standard_deviation.setText(str(self.prev_file_size_standard_deviation))
            else:
                self.file_size_standard_deviation = file_size_standard_deviation_text
                self.prev_file_size_standard_deviation = file_size_standard_deviation_text
        except ValueError:
            QMessageBox.information(self, '提示', '请输入一个有效的整数。')
            # 将文本框中的值恢复为之前的有效值
            self.lineEdit_file_size_standard_deviation.setText(str(self.prev_file_size_standard_deviation))

    def createBottomRightBlock(self):
        self.bottomRightBlock = QGroupBox("文件大小的生成方式和排布位置")

        gridLayout = QGridLayout()

        # 设置文件大小的生成方式，所有文件一致/按照正态分布
        label = QLabel('【所有文件大小一致请选择average, 文件大小符合正态分布请选择normal】')
        styleLabel = QLabel("请选择average/normal:")
        self.styleComboBox_file_size_generate_way = QComboBox()
        self.styleComboBox_file_size_generate_way.addItems(['average', 'normal'])
        self.styleComboBox_file_size_generate_way.setCurrentText(self.file_size_generate_way)
        # 将值绑定到本地变量
        self.file_size_generate_way = self.styleComboBox_file_size_generate_way.currentText()
        # 连接值更改信号到槽函数
        self.styleComboBox_file_size_generate_way.currentTextChanged.connect(self.update_file_size_generate_way)
        # 布局
        gridLayout.addWidget(label, 0, 0, 1, 3)
        gridLayout.addWidget(styleLabel, 1, 0, 1, 1)
        gridLayout.addWidget(self.styleComboBox_file_size_generate_way, 1, 1, 1, 2)

        # 设置文件的排布方式，放置在所有文件夹中 or 放置在叶子结点文件夹中
        label = QLabel('【文件随机放置在所有文件夹中请选择all，文件随机放置在叶子结点文件夹中请选择leaf】')
        styleLabel = QLabel("请选择all/leaf:")
        self.styleComboBox_file_distribution_place = QComboBox()
        self.styleComboBox_file_distribution_place.addItems(['all', 'leaf'])
        self.styleComboBox_file_distribution_place.setCurrentText(self.file_distribution_place)
        # 将值绑定到本地变量
        self.file_distribution_place = self.styleComboBox_file_distribution_place.currentText()
        # 连接值更改信号到槽函数
        self.styleComboBox_file_distribution_place.currentTextChanged.connect(self.update_file_distribution_place)
        # 布局
        gridLayout.addWidget(label, 2, 0, 1, 3)
        gridLayout.addWidget(styleLabel, 3, 0, 1, 1)
        gridLayout.addWidget(self.styleComboBox_file_distribution_place, 3, 1, 1, 2)

        self.bottomRightBlock.setLayout(gridLayout)

    def update_file_size_generate_way(self):
        self.file_size_generate_way = self.styleComboBox_file_size_generate_way.currentText()
        print("self.file_size_generate_way: ", self.file_size_generate_way + " type: " + str(type(self.file_size_generate_way)))

    def update_file_distribution_place(self):
        self.file_distribution_place = self.styleComboBox_file_distribution_place.currentText()
        print("self.file_distribution_place: ", self.file_distribution_place + " type: " + str(type(self.file_distribution_place)))

    def createDecisionBlock(self):
        self.decisionBlock = QGroupBox("确认和重置")

        gridLayout = QGridLayout()

        # 确认按钮
        self.button_confirm = QPushButton("确认")
        self.button_confirm.clicked.connect(self.on_button_confirm_click)
        gridLayout.addWidget(self.button_confirm, 0, 0, 1, 1)

        # 重置按钮
        self.button_reset = QPushButton("重置")
        self.button_reset.clicked.connect(self.on_button_reset_click)
        gridLayout.addWidget(self.button_reset, 0, 1, 1, 1)

        self.decisionBlock.setLayout(gridLayout)

    def on_button_confirm_click(self):
        # 检查变量是否符合逻辑
        result = self.check_variables()
        if not result:
            return

        # 检查 root_path 对应的文件夹是否为空
        if os.path.exists(self.root_path) and os.listdir(self.root_path):
            # 如果文件夹不为空，则删除文件夹中的内容
            shutil.rmtree(self.root_path)
            # 然后重新创建一个空的文件夹
            os.makedirs(self.root_path)

        # 禁用组件
        self.button_root_path.setEnabled(False)
        self.spinBox_N.setEnabled(False)
        self.spinBox_folder_number_min.setEnabled(False)
        self.spinBox_folder_number_max.setEnabled(False)
        self.styleComboBox_generate_limit_way.setEnabled(False)
        self.lineEdit_file_number_max.setEnabled(False)
        self.lineEdit_folder_size_max.setEnabled(False)
        self.styleComboBox_folder_size_max.setEnabled(False)
        self.lineEdit_file_size_mean.setEnabled(False)
        self.styleComboBox_file_size_mean.setEnabled(False)
        self.lineEdit_file_size_min.setEnabled(False)
        self.styleComboBox_file_size_min.setEnabled(False)
        self.lineEdit_file_size_max.setEnabled(False)
        self.styleComboBox_file_size_max.setEnabled(False)
        self.lineEdit_file_size_standard_deviation.setEnabled(False)
        self.styleComboBox_file_size_generate_way.setEnabled(False)
        self.styleComboBox_file_distribution_place.setEnabled(False)
        self.button_confirm.setEnabled(False)
        self.button_reset.setEnabled(False)
        self.button_continue.setEnabled(True)
        self.button_pause.setEnabled(True)
        self.button_terminate.setEnabled(True)
        self.progressBar.setMaximum(10000)

        # 启动两个线程
        self.start_threads()

    def start_threads(self):

        # 更新generate_thread变量的值
        self.generate_thread.root_path = self.root_path
        self.generate_thread.N = int(self.N)
        self.generate_thread.folder_number_min = int(self.folder_number_min)
        self.generate_thread.folder_number_max = int(self.folder_number_max)
        self.generate_thread.generate_limit_way = self.generate_limit_way
        self.generate_thread.file_number_max = int(self.file_number_max)
        self.generate_thread.folder_size_max = string2byte(str(self.folder_size_max) + self.folder_size_max_unit)
        self.generate_thread.file_size_mean = string2byte(str(self.file_size_mean) + self.file_size_mean_unit)
        self.generate_thread.file_size_min = string2byte(str(self.file_size_min) + self.file_size_min_unit)
        self.generate_thread.file_size_max = string2byte(str(self.file_size_max) + self.file_size_max_unit)
        self.generate_thread.file_size_standard_deviation = int(self.file_size_standard_deviation)
        self.generate_thread.file_distribution_place = self.file_distribution_place
        self.generate_thread.file_size_generate_way = self.file_size_generate_way
        self.generate_thread.shared_object.setStatus(False)

        # 更新check_thread的值
        self.check_thread.root_path = self.root_path
        self.check_thread.checkType = self.generate_limit_way
        self.check_thread.shared_object.setStatus(False)

        # 启动两个线程
        self.generate_thread.start()
        self.check_thread.start()

    # 检查变量的逻辑是否合规
    def check_variables(self):
        print('开始检查')
        if self.file_size_generate_way == 'normal':
            if self.file_size_min == 0:
                QMessageBox.information(self, '提示', '文件大小最小值不能为0')
                return False
            if self.lineEdit_file_size_min.text() == '':
                QMessageBox.information(self, '提示', '文件大小最小值不能为空')
                return False
            if self.file_size_max == 0:
                QMessageBox.information(self, '提示', '文件大小最大值不能为0')
                return False
            if self.lineEdit_file_size_max.text() == '':
                QMessageBox.information(self, '提示', '文件大小最大值不能为空')
                return False
            if self.file_size_standard_deviation == 0:
                QMessageBox.information(self, '提示', '文件大小标准差不能为0')
                return False
            if self.lineEdit_file_size_standard_deviation.text() == '':
                QMessageBox.information(self, '提示', '文件大小标准差不能为空')
                return False
            if string2byte(str(self.file_size_mean) + self.file_size_mean_unit) > string2byte(str(self.file_size_max) + self.file_size_max_unit):
                QMessageBox.information(self, '提示', '文件大小平均值不得大于文件大小上限')
                return False
            if string2byte(str(self.file_size_mean) + self.file_size_mean_unit) < string2byte(str(self.file_size_min) + self.file_size_min_unit):
                QMessageBox.information(self, '提示', '文件大小平均值不得小于文件大小下限')
                return False
        if self.generate_limit_way== 'byNumber':
            if self.lineEdit_file_number_max.text() == '':
                QMessageBox.information(self, '提示', '文件数量最大值不能为空')
                return False
            if self.file_number_max == 0:
                QMessageBox.information(self, '提示', '文件数量最大值不能为0')
                return False
        if self.generate_limit_way == 'bySize':
            if self.lineEdit_folder_size_max.text() == '':
                QMessageBox.information(self, '提示', '生成的文件占据空间总大小不能为空')
                return False
            if self.lineEdit_folder_size_max.text() == 0:
                QMessageBox.information(self, '提示', '生成的文件占据空间总大小不能为0')
                return False

        return True

    def on_button_reset_click(self):
        print("button_reset_click")

        # 规定变量的默认值
        self.N = 5
        self.folder_number_min = 1
        self.folder_number_max = 5
        self.generate_limit_way = 'byNumber'
        self.file_number_max = 500
        self.prev_file_number_max = 500
        self.folder_size_max = 100
        self.prev_folder_size_max = 100
        self.folder_size_max_unit = 'MB'
        self.file_size_mean = 500
        self.prev_file_size_mean = 500
        self.file_size_mean_unit = 'KB'
        self.file_size_min = 200
        self.prev_file_size_min = 200
        self.file_size_min_unit = 'KB'
        self.file_size_max = 1000
        self.prev_file_size_max = 1000
        self.file_size_max_unit = 'KB'
        self.file_size_standard_deviation = 500
        self.prev_file_size_standard_deviation = 500
        self.file_distribution_place = 'all'
        self.file_size_generate_way = 'average'

        # 设置默认值
        self.folderLine_root_path.setText(self.default_root_path())
        self.spinBox_N.setValue(self.N)
        self.spinBox_folder_number_min.setValue(self.folder_number_min)
        self.spinBox_folder_number_max.setValue(self.folder_number_max)
        self.styleComboBox_generate_limit_way.setCurrentText(self.generate_limit_way)
        self.lineEdit_file_number_max.setText(str(self.file_number_max))
        self.lineEdit_folder_size_max.setText(str(self.folder_size_max))
        self.styleComboBox_folder_size_max.setCurrentText(self.folder_size_max_unit)
        self.lineEdit_file_size_mean.setText(str(self.file_size_mean))
        self.styleComboBox_file_size_mean.setCurrentText(self.file_size_mean_unit)
        self.lineEdit_file_size_min.setText(str(self.file_size_min))
        self.styleComboBox_file_size_min.setCurrentText(self.file_size_min_unit)
        self.lineEdit_file_size_max.setText(str(self.file_size_max))
        self.styleComboBox_file_size_max.setCurrentText(self.file_size_max_unit)
        self.lineEdit_file_size_standard_deviation.setText(str(self.file_size_standard_deviation))
        self.styleComboBox_file_size_generate_way.setCurrentText(self.file_size_generate_way)
        self.styleComboBox_file_distribution_place.setCurrentText(self.file_distribution_place)

    def createProgressBlock(self):
        self.progressBlock = QGroupBox("文件生成进度")
        gridLayout = QGridLayout()
        self.fileGenerationStatusLabel = QLabel()  # 添加标签
        gridLayout.addWidget(self.fileGenerationStatusLabel, 0, 1, 1, 1)  # 将标签添加到布局中
        self.check_thread.value_changed.connect(self.on_value_changed)

        # 进度条
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        gridLayout.addWidget(self.progressBar, 1, 1, 1, 1)
        self.progressBlock.setLayout(gridLayout)

    def on_value_changed(self, value):
        content = ""
        if self.generate_limit_way == 'byNumber':
            content = self.file_number_max
        elif self.generate_limit_way == 'bySize':
            content = str(self.folder_size_max) + self.folder_size_max_unit
            value = byte2string(value)
        value = str(value)
        self.fileGenerationStatusLabel.setText(f"Process: Value: {value}" + "/" + str(content))

        # 更新进度条的值
        self.update_progress_bar(value)

    def update_progress_bar(self, value):
        progress_value = 0
        if self.generate_limit_way == 'byNumber':
            progress_value = int((int(value) / int(self.file_number_max)) * 10000)
        elif self.generate_limit_way == 'bySize':
            progress_value = int((string2byte(value) / string2byte(str(self.folder_size_max) + self.folder_size_max_unit)) * 10000)
        print("progress_value: " + str(progress_value))
        self.progressBar.setValue(progress_value)

    def createProgressDecisionBlock(self):
        self.progressDecision = QGroupBox("暂停与继续")

        gridLayout = QGridLayout()

        self.button_continue = QPushButton("继续")
        self.button_continue.clicked.connect(self.on_button_continue_click)
        gridLayout.addWidget(self.button_continue, 0, 0, 1, 1)

        self.button_pause = QPushButton("暂停")
        self.button_pause.clicked.connect(self.on_button_pause_click)
        gridLayout.addWidget(self.button_pause, 0, 1, 1, 1)

        self.button_terminate = QPushButton("终止")
        self.button_terminate.clicked.connect(self.on_button_terminate_click)
        gridLayout.addWidget(self.button_terminate, 0, 2, 1, 1)

        self.progressDecision.setLayout(gridLayout)

    def on_button_continue_click(self):
        self.generate_thread.resume()
        self.check_thread.resume()

    def on_button_pause_click(self):
        self.generate_thread.pause()
        self.check_thread.pause()

    def on_button_terminate_click(self):
        self.generate_thread.stop()
        self.check_thread.stop()
        
        # 启用所有按钮
        self.button_root_path.setEnabled(True)

        self.spinBox_N.setEnabled(True)
        self.spinBox_folder_number_min.setEnabled(True)
        self.spinBox_folder_number_max.setEnabled(True)

        self.styleComboBox_generate_limit_way.setEnabled(True)
        self.lineEdit_file_number_max.setEnabled(True)
        self.lineEdit_folder_size_max.setEnabled(True)
        self.styleComboBox_folder_size_max.setEnabled(True)

        self.lineEdit_file_size_mean.setEnabled(True)
        self.styleComboBox_file_size_mean.setEnabled(True)
        self.lineEdit_file_size_min.setEnabled(True)
        self.styleComboBox_file_size_min.setEnabled(True)
        self.lineEdit_file_size_max.setEnabled(True)
        self.styleComboBox_file_size_max.setEnabled(True)
        self.lineEdit_file_size_standard_deviation.setEnabled(True)

        self.styleComboBox_file_size_generate_way.setEnabled(True)
        self.styleComboBox_file_distribution_place.setEnabled(True)

        # 确认和重置组件
        self.button_confirm.setEnabled(True)
        self.button_reset.setEnabled(True)

        # 把暂停继续终止disable
        self.button_continue.setEnabled(False)
        self.button_pause.setEnabled(False)
        self.button_terminate.setEnabled(False)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec())