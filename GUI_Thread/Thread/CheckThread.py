from PyQt6.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from Common.utils import count_files_in_folder, calculate_total_size, string2byte, byte2string
import time

class CheckThread(QThread):
    value_changed = pyqtSignal(int)

    def __init__(self, root_path, checkType, shared_object):
        super().__init__()
        self.total_size = 0
        self.file_count = 0
        self.root_path = root_path
        self.checkType = checkType
        self._running = True
        self._paused = False
        self.shared_object = shared_object

    def run(self):
        self.total_size = 0
        self.file_count = 0
        self._running = True
        self._paused = False

        while self._running:

            if self._paused:
                time.sleep(0.1)
                continue

            if self.checkType == "byNumber":
                self.file_count = count_files_in_folder(self.root_path)
                print("CheckThread，ByNumber: 得到的file_count是: " + str(self.file_count))
                self.value_changed.emit(self.file_count)
            elif self.checkType == "bySize":
                self.total_size = calculate_total_size(self.root_path)
                print("CheckThread，bySize: 得到的total_size是: " + byte2string(str(self.total_size)))
                self.value_changed.emit(self.total_size)
            else:
                raise ValueError("Unknown checkType: {}".format(self.checkType))

            time.sleep(0.1)

            self.shared_object.status_changed.connect(self.handle_status_changed)
        print("———————————————————— CheckThread 终止 ————————————————————")

    def handle_status_changed(self, new_status):
        if new_status:
            self._running = False

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._running = False
        self.file_count = 0
        self.total_size = 0
        if self.checkType == "byNumber":
            self.value_changed.emit(self.file_count)
        elif self.checkType == "bySize":
            self.value_changed.emit(self.total_size)
        else:
            raise ValueError("Unknown checkType: {}".format(self.checkType))
