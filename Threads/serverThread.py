from PyQt5.QtCore import QThread, pyqtSignal
from process import updateTrackServer


class ServerThread(QThread):
    def __int__(self):
        super().__init__()
        self.setting = None

    def run(self):
        updateTrackServer(self.setting)