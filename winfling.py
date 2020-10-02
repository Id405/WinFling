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
#This is mainly just for fun so I'm writing it to work now, not be a good base for upgrades or feature additions in the future, because I shouldn't be writing something super complex
#in python, I should be using rust or go
global homeDir
global config

class shortcutType():
    def __init__(self, test, call):
        self.test = test
        self.call = call

class shortcutTypeList():
    def __init__(self):
        def reloadConfig(text, widget):
            global config
            config = loadConfig()
        
        def restart(text, widget):
            subprocess.Popen(sys.executable + " " + sys.argv[0])
            sys.exit(0)
        
        def launchFromConfig(text, widget):
            path = config["Programs"][text]
            os.path.expandvars(path)
            cwd=os.getcwd()
            if(text in config["WorkingDir"]):
                os.chdir(Path(config["WorkingDir"][text]))
            subprocess.Popen(path)
            os.chdir(cwd)
        
        def launchFromPath(text, widget):
            path = shutil.which(text)
            subprocess.Popen(path)
        
        def runCommand(text, widget):
            cwd=os.getcwd()
            os.chdir(homeDir)
            subprocess.Popen(text[1:])
            os.chdir(cwd)

        self.shortcutTypes = []
        self.shortcutTypes.append(shortcutType(lambda text, widget : text == "reload", reloadConfig))
        self.shortcutTypes.append(shortcutType(lambda text, widget : text == "restart", restart))
        self.shortcutTypes.append(shortcutType(lambda text, widget : text == "quit", lambda text, widget : sys.exit(0)))
        self.shortcutTypes.append(shortcutType(lambda text, widget : text in config['Programs'], launchFromConfig))
        self.shortcutTypes.append(shortcutType(lambda text, widget : shutil.which(text) != None, launchFromPath))
        self.shortcutTypes.append(shortcutType(lambda text, widget : text[0] == ":", runCommand))
        self.shortcutTypes.append(shortcutType(lambda text, widget : text[0] == "?", lambda text, widget : exec(text[1: ])))


def loadConfig():
    if(not Path('config.ini').is_file()):
        shutil.copyfile('config.example.ini', 'config.ini')

    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    return cfg

def addShortcut(name, cmd, wd):
    config['Programs'][name] = cmd
    if(wd != None and wd != ""):
        config['WorkingDir'][name] = wd
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

class WinFlingPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WinFling Launch Dialogue")

        self.launch = QtWidgets.QLineEdit()
        self.launch.returnPressed.connect(self.on_launch_button)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.launch)
        self.setLayout(self.layout)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WA_TranslucentBackground | QtCore.Qt.WindowStaysOnTopHint)
        self.round_corners()

    def on_launch_button(self):
        shortcuts = shortcutTypeList()

        if(self.launch.text() == ""):
            self.hide()
            return

        for i in shortcuts.shortcutTypes:
            if i.test(self.launch.text(), self):
                i.call(self.launch.text(), self)
                break
        
        self.hide()

    def round_corners(self):
        self.show()
        radius = 4.0
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)
        self.hide()
    
    def popup(self):
        self.launch.clear()
        self.show()
        self.activateWindow()

class WinFlingNewShortcut(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WinFling Shortcut Dialogue")

        self.name = QtWidgets.QLineEdit()
        self.command = QtWidgets.QLineEdit()
        self.workingDir = QtWidgets.QLineEdit()
        self.confirm = QtWidgets.QPushButton("&Add Shortcut") #TODO make styling of this button not ass

        self.name.returnPressed.connect(self.command.setFocus)
        self.command.returnPressed.connect(self.workingDir.setFocus)
        self.workingDir.returnPressed.connect(self.onConfirm)
        self.confirm.clicked.connect(self.onConfirm)

        self.layout = QtWidgets.QFormLayout()
        self.layout.addRow("Name", self.name)
        self.layout.addRow("Command", self.command)
        self.layout.addRow("Working Directory", self.workingDir)
        self.layout.addRow(self.confirm)
        self.setLayout(self.layout)

        self.name.setFocus()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WA_TranslucentBackground | QtCore.Qt.WindowStaysOnTopHint)
        self.round_corners()

    
    def onConfirm(self):
        if(self.command.text() == "" or self.name.text() == ""):
            self.hide()
            return
        addShortcut(self.name.text(), self.command.text(), self.workingDir.text())
        self.hide()

    def round_corners(self):
        self.show()
        radius = 4.0
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)
        self.hide()
    
    def popup(self):
        self.name.clear()
        self.command.clear()
        self.workingDir.clear()
        self.show()
        self.activateWindow()


class WinFlingBehaviour():
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
        self.widget.move(rec.width()/2-self.widget.width()/2, rec.height()*0.75-self.widget.height()/2)

        self.shortcut = WinFlingNewShortcut()
        self.shortcut.move(rec.width()/2-self.widget.width()/2, rec.height()*0.75-self.widget.height()/2)
        self.shortcut.hide()

        self.trayMenu = QtWidgets.QMenu()
        self.trayMenu.addAction("launch application")
        self.trayMenu.addAction("add shortcut")
        self.trayMenu.addAction("exit")
        self.trayMenu.triggered.connect(self.trayClicked)

        self.icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon('thumbnail.png'), self.app)
        self.icon.setContextMenu(self.trayMenu)
        self.icon.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.hotkeyTimerEvent)
        self.timer.start(30)
        
        keyboard.add_hotkey('ctrl+shift+a', self.launchPopup)

    def trayClicked(self, action):
        if(action.text() == "exit"):
            sys.exit(0)
        if(action.text() == "launch application"):
            self.widget.popup()
        if(action.text() == "add shortcut"):
            self.shortcut.popup()
    
    def launchPopup(self):
        self.hotkeyPressed = True

    #This is ultimately shit, I use a self.timer event and then poll for if a boolean is true since weird threading shit is going on
    def hotkeyTimerEvent(self):
        if(self.hotkeyPressed):
            self.hotkeyPressed = False
            self.widget.popup()

if __name__ == "__main__":
    config = loadConfig()
    homeDir = Path.home()

    app = WinFlingBehaviour()

    sys.exit(app.app.exec_())