# coding:utf-8
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (setTheme, FluentWindow,
                            SubtitleLabel, setFont, Theme)
from qfluentwidgets import FluentIcon as FIF

from UI.Interface.CodeCompletionInterface import CodeCompletionInterface
from UI.Interface.CodeInterface import CodeInterface
from UI.Interface.home_interface import HomeInterface



class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class mainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.code_completion_Interface = CodeCompletionInterface(self)
        self.code_Interface = CodeInterface(self)


        self.navigationInterface.setExpandWidth(250)
        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        self.addSubInterface(self.code_completion_Interface, FIF.CODE, '函数名补全')
        self.addSubInterface(self.code_Interface, FIF.MESSAGE, '代码段补全')

        self.navigationInterface.addSeparator()



    def initWindow(self):
        self.resize(1000, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('代码智能补全工具')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)



if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    setTheme(Theme.DARK)
    w = mainWindow()
    w.show()
    app.exec_()
