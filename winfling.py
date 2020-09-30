import configparser
import subprocess
import shutil
import sys
import os
from pathlib import Path
import breeze_resources
import keyboard
from PySide2 import QtCore, QtWidgets, QtGui

#All of this code is terrible, I do not like it at all, this is ultimately a POC (stands for both piece of crap and proof of concept) for something better written in not python

home = str(Path.home())
config = configparser.ConfigParser()
config.read("config.ini")

class WinFlingPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.launch = QtWidgets.QLineEdit()
        self.launch.returnPressed.connect(self.on_launch_button)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.launch)
        self.setLayout(self.layout)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WA_TranslucentBackground | QtCore.Qt.WindowStaysOnTopHint)

    def on_launch_button(self):
        if(self.launch.text() == ""):
            self.hide()
            return

        if(self.launch.text() == "quit"):
            sys.exit(0)

        if(self.launch.text() in config["Programs"]):
            path = config["Programs"][self.launch.text()]
            os.path.expandvars(path)
            print(path)
            cwd=os.getcwd()
            if(self.launch.text() in config["WorkingDir"]):
                os.chdir(Path(config["WorkingDir"][self.launch.text()]))
            subprocess.Popen(path)
            os.chdir(cwd)
        
        path = shutil.which(self.launch.text())
        if(path != None):
            subprocess.Popen(path)
        
        self.hide()

    def round_corners(self):
        radius = 4.0
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

class WinFlingApp():
    def __init__(self):
        self.hotkeyPressed = False
        self.app = QtWidgets.QApplication([])

        desktop = self.app.desktop()

        file = QtCore.QFile(":/dark.qss")
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.app.setStyleSheet(stream.readAll())

        self.widget = WinFlingPopup()
        rec = desktop.availableGeometry(self.widget)
        self.widget.show()
        self.widget.move(rec.width()/2-self.widget.width()/2, rec.height()*0.75-self.widget.height()/2)
        self.widget.round_corners()
        self.widget.hide()

        self.trayMenu = QtWidgets.QMenu()
        self.trayMenu.addAction("launch application")
        self.trayMenu.addAction("exit")
        self.trayMenu.triggered.connect(self.trayClicked)

        self.icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon('thumbnail.png'), self.app)
        self.icon.setContextMenu(self.trayMenu)
        self.icon.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.hotkeyTimerEvent)
        self.timer.start(30)
        
        keyboard.add_hotkey('ctrl+shift+a', self.launchPopup)

    def popup(self):
        self.widget.launch.clear()
        self.widget.show()
        self.widget.activateWindow()

    def trayClicked(self, action):
        if(action.text() == "exit"):
            sys.exit(0)
        if(action.text() == "launch application"):
            self.popup()
    
    def launchPopup(self):
        self.hotkeyPressed = True

    #This is ultimately shit, I use a self.timer event and then poll for if a boolean is true since weird threading shit is going on
    def hotkeyTimerEvent(self):
        if(self.hotkeyPressed):
            self.hotkeyPressed = False
            self.popup()

if __name__ == "__main__":
    app = WinFlingApp()

    sys.exit(app.app.exec_())