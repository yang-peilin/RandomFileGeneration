from PyQt6.QtCore import Qt, pyqtSignal, QObject

class ShareObject(QObject):
    status_changed = pyqtSignal(bool)

    def __init__(self, isCompleted = False):
        super().__init__()
        self.isCompleted = isCompleted

    def getStatus(self):
        return self.isCompleted

    def setStatus(self, new_status):
        self.isCompleted = new_status

    def updateStatus(self, new_status):
        self.isCompleted = new_status
        self.status_changed.emit(new_status)