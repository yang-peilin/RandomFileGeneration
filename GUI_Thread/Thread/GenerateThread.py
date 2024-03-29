
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

from Common.generateFolders import generate_folders

class GenerateThread(QThread):
    value_changed = pyqtSignal(bool)

    def __init__(self, root_path, N, folder_number_min, folder_number_max,
                 folder_size_max, file_number_max,
                 file_size_mean, file_size_min, file_size_max, file_size_standard_deviation,
                 generate_limit_way, file_distribution_place, file_size_generate_way,
                 shared_object):
        super().__init__()

        self.root_path = root_path
        self.N = N
        self.folder_number_min = folder_number_min
        self.folder_number_max = folder_number_max
        self.folder_size_max = folder_size_max
        self.file_number_max = file_number_max
        self.file_size_mean = file_size_mean
        self.file_size_min = file_size_min
        self.file_size_max = file_size_max
        self.file_size_standard_deviation = file_size_standard_deviation
        self.generate_limit_way = generate_limit_way
        self.file_distribution_place = file_distribution_place
        self.file_size_generate_way = file_size_generate_way
        self._running = True
        self._paused = False
        self.shared_object = shared_object

    def run(self):
        print("———————————————————— GenerateThread 线程起点开始了 ————————————————————")

        self._running = True
        self._paused = False

        # 文件夹列表
        folder_path_list = []
        # 记录所有文件夹的编号和路径
        folder_map = {}
        folder_leaf_map = {}
        # 记录文件夹的编号
        index = 1

        # 1. 创建文件结构
        generate_folders(self.root_path, folder_path_list, self.folder_number_min, self.folder_number_max, self.N, folder_map,
                         folder_leaf_map, index)

        # 用来记录当前文件数量的变量
        file_number = 0
        # 用来记录当前文件的总大小
        current_size = 0

        while self._running:
            if self.generate_limit_way == "byNumber":
                while file_number < self.file_number_max:

                    # 如果进程已经终止了，那么需要跳出循环
                    if not self._running:
                        break

                    # 选取文件要生成的目录
                    file_generate_folder = ""
                    if self.file_distribution_place == "all":
                        # 从映射中随机选择一个键值对
                        selected_key, file_generate_folder = random.choice(list(folder_map.items()))
                    elif self.file_distribution_place == "leaf":
                        selected_key, file_generate_folder = random.choice(list(folder_leaf_map.items()))
                    else:
                        print(
                            "config file exists error, file_distribution_place: " + self.file_distribution_place + " not defined.")
                        sys.exit()

                    # 选定文件的名称以及文件的位置
                    new_file_name = "file_" + str(file_number) + ".txt"
                    file_path = os.path.join(file_generate_folder, new_file_name)

                    # 确定文件的大小并且写入文件
                    if self.file_size_generate_way == "average":
                        file_size = self.file_size_mean

                        # 如果进程被暂停，则不会继续生成文件，会卡在这里
                        while self._paused:
                            print("byNumber average 暂停")
                            time.sleep(0.1)
                            continue

                        # 写入一个文件
                        with open(file_path, 'w') as f:
                            remaining_size = file_size
                            while remaining_size > 0:
                                # 每次迭代生成 1KB 或剩余大小中较小的部分
                                content = ''.join(
                                    random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,
                                                   k=min(remaining_size, 1024)))
                                f.write(content)
                                remaining_size -= len(content)

                    elif self.file_size_generate_way == "normal":
                        file_size = generate_normal_random_number(self.file_size_mean, self.file_size_standard_deviation,
                                                                  self.file_size_min, self.file_size_max)

                        # 如果进程被暂停，则不会继续生成文件，会卡在这里
                        while self._paused:
                            print("byNumber normal 暂停")
                            time.sleep(0.1)
                            continue

                        # 写入单个文件
                        with open(file_path, 'w') as f:
                            remaining_size = file_size
                            while remaining_size > 0:
                                # 每次迭代生成 1KB 或剩余大小中较小的部分
                                content = ''.join(
                                    random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,
                                                   k=min(remaining_size, 1024)))
                                f.write(content)
                                remaining_size -= len(content)
                    else:
                        print(
                            "config file exists error, file_size_generate_way " + self.file_size_generate_way + " not defined.")
                        sys.exit()
                    file_number += 1
                # 终止条件
                print("文件生成完毕")
                self._running = False

            elif self.generate_limit_way == "bySize":
                while current_size < self.folder_size_max:

                    # 如果进程已经终止了，那么需要跳出循环
                    if not self._running:
                        break

                    # 选取文件要生成的目录
                    file_generate_folder = ""
                    if self.file_distribution_place == "all":
                        # 从映射中随机选择一个键值对
                        selected_key, file_generate_folder = random.choice(list(folder_map.items()))
                    elif self.file_distribution_place == "leaf":
                        selected_key, file_generate_folder = random.choice(list(folder_leaf_map.items()))
                    else:
                        print(
                            "config file exists error, file_distribution_place: " + self.file_distribution_place + " not defined.")
                        sys.exit()

                    # 选定文件的名称以及文件的位置
                    new_file_name = "file_" + str(file_number) + ".txt"
                    file_path = os.path.join(file_generate_folder, new_file_name)

                    # 确定文件的大小并且写入文件
                    if self.file_size_generate_way == "average":
                        file_size = self.file_size_mean
                        if file_size + current_size < self.folder_size_max:
                            current_size += file_size

                            # 如果进程被暂停，则不会继续生成文件，会卡在这里
                            while self._paused:
                                print("bySize average 暂停")
                                time.sleep(0.1)
                                continue

                            with open(file_path, 'w') as f:
                                remaining_size = file_size
                                while remaining_size > 0:
                                    # 每次迭代生成 1KB 或剩余大小中较小的部分
                                    content = ''.join(
                                        random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,
                                                       k=min(remaining_size, 1024)))
                                    f.write(content)
                                    remaining_size -= len(content)
                        else:
                            break

                    elif self.file_size_generate_way == "normal":
                        file_size = generate_normal_random_number(self.file_size_mean, self.file_size_standard_deviation,
                                                                  self.file_size_min, self.file_size_max)
                        if file_size + current_size < self.folder_size_max:
                            current_size += file_size

                            # 如果进程被暂停，则不会继续生成文件，会卡在这里
                            while self._paused:
                                print("bySize normal 暂停")
                                time.sleep(0.1)
                                continue

                            with open(file_path, 'w') as f:
                                remaining_size = file_size
                                while remaining_size > 0:
                                    # 每次迭代生成 1KB 或剩余大小中较小的部分
                                    content = ''.join(
                                        random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits,
                                                       k=min(remaining_size, 1024)))
                                    f.write(content)
                                    remaining_size -= len(content)
                        else:
                            break
                    else:
                        print(
                            "config file exists error, file_size_generate_way " + self.file_size_generate_way + " not defined.")
                        sys.exit()
                    file_number += 1

                print("文件生成完毕")
                self._running = False

            else:
                print("config file exists error, generate_limit_way " + self.generate_limit_way + " not defined.")
                sys.exit()

        print("———————————————————— GenerateThread 线程终止了 ————————————————————")

        time.sleep(0.5)
        self.shared_object.updateStatus(True)
        print("self.generationFileStatus: " + str(self.shared_object.getStatus()))

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._paused = False
        self._running = False
