from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDesktopWidget, QMessageBox, QLabel
from PyQt5.Qt import QThread
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSignal
from pickleshare import PickleShareDB

import argparse
import requests
import ctypes
import os
import win32com.client as client
import sys

__version__ = "2.0"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
shell = client.Dispatch("WScript.Shell")

class Setting:
    def __init__(self, file_name, config={}, config_path="~/.duck_game/ys/"):
        super().__init__()
        self.file_name = file_name
        self.db = PickleShareDB(config_path)
        if file_name not in self.db:
            self.db[file_name] = config

    def add(self, key, value):
        """添加新值"""
        new = self.db[self.file_name]
        if value:
            new[key] = value
            self.db[self.file_name] = new

    def read(self, config=None):
        """读文件"""
        if config:
            return self.db[self.file_name][config]
        return self.db[self.file_name]

config = Setting("ys_resources")

class ChackNetwork(QThread):
    done = pyqtSignal()

    def run(self):
        try:
            requests.get("https://webstatic.mihoyo.com", verify=False)
        except Exception as e:
            QMessageBox.critical(None, str(type(e)), "请连接网络")
            sys.exit()
        self.done.emit()

class StartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(50, 50)

class Web(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.show()
        self.load(QtCore.QUrl("https://webstatic.mihoyo.com/app/ys-map-cn/index.html"))



def createShortCut(filename, lnkname, commands: list = None):
    shortcut = shell.CreateShortCut(lnkname)
    shortcut.TargetPath = filename 
    if commands:
        shortcut.Arguments = " ".join(commands)
    shortcut.WorkingDirectory = os.path.dirname(filename)
    shortcut.save()

def get_file():
    if os.path.isfile(os.path.abspath(__file__)):
        return os.path.abspath(__file__)
    else:
        return os.path.abspath(__file__).replace('.py', '.exe')

def create_link():
    createShortCut(get_file(), f"{os.path.expanduser('~')}/Desktop/原神 [资源查询器].lnk")

def read_argvs():
    parser = argparse.ArgumentParser(get_file().replace('\\', '/').split("/")[-1])
    parser.add_argument("--link", help="设置桌面快捷方式", action='store_true')
    return parser.parse_args()


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.net = ChackNetwork()
        self.net.start()
        self.net.done.connect(self.start_server)
        self.screen = QDesktopWidget().screenGeometry()
        self.setWindowTitle("网络检测中")
        self.start_label = QLabel("等一会~一会就启动好了", self)
        self.start_widget = StartWidget(self)
        self.web = Web(self)
        self.web.hide()
        self.web.resize(self.screen.width() - 120, self.screen.height() - 100)
        self.start_widget.resize(50, 50)
        self.net_done = False
        self.tp = 0
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)

    def start_server(self):
        self.setWindowTitle("《原神》资源查询器 (by:鸭皇) version={}".format(__version__))
        self.net_done = True
        self.start_label.setText("点击任意位置启动")

    def mouseReleaseEvent(self, a0):
        self.start_web()

    def start_web(self):
        if not self.net_done:
            QMessageBox.warning(self, "提示", "正在检测网络，等一会儿就好了")
            return
        self.tp = 1
        self.move(0, 0)
        self.resize(self.screen.width() - 120, self.screen.height() - 100)
        self.web.show()
        self.start_label.hide()
        self.start_widget.hide()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self.tp == 1:
            self.resize(self.screen.width() - 120, self.screen.height() - 100)
    
    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
        if not self.tp:
            super().moveEvent(a0)
        else:
            self.move(0, 0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.tp == 1:
            self.tp = 0
            self.web.hide()
            self.start_widget.show()
            self.start_label.show()
            self.resize(50, 50)
            a0.ignore()



def run_gui():
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec_()
    sys.exit()

def main():
    print("《原神》游戏资源查询器")
    print("工具version: {}".format(__version__))
    argv = read_argvs()
    if argv.link:
        create_link()
    else:
        run_gui()

if __name__ == '__main__':
    main()
