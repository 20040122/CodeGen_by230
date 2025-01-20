# coding:utf-8
import sys

from PyQt5.QtCore import Qt, QEventLoop, QTimer, QSize, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDesktopWidget

from qfluentwidgets import SplashScreen, setTheme, Theme
from qframelesswindow import FramelessWindow, StandardTitleBar

# 导入LoginWindow类
from Login import LoginWindow  # 根据你的文件路径导入


class Demo(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.resize(1000, 580)
        self.setWindowTitle('')
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))

        # create splash screen and show window
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))
        titleBar = StandardTitleBar(self.splashScreen)
        titleBar.setIcon(self.windowIcon())
        titleBar.setTitle(self.windowTitle())
        self.splashScreen.setTitleBar(titleBar)
        # 显示 Demo 窗口之前，先居中
        self.show()
        self.center_window(self)

        self.createSubInterface()
        # close splash screen
        self.splashScreen.finish()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(1000, loop.quit)  # 1秒后退出事件循环
        loop.exec()

        # 显示登录窗口
        self.show_login_window()

    def show_login_window(self):
        """显示登录窗口"""
        self.loginWindow = LoginWindow()  # 创建LoginWindow实例
        self.loginWindow.show()  # 显示登录窗口
        self.loginWindow.connect_signals()  # 确保登录窗口的信号连接
        # 设置 LoginWindow 窗口的居中位置
        self.center_window(self.loginWindow)

        self.close()  # 关闭当前窗口（闪屏窗口）

    def center_window(self, window):
        """使窗口居中"""
        frame_geometry = window.frameGeometry()
        screen = QDesktopWidget().availableGeometry()
        frame_geometry.moveCenter(screen.center())
        window.move(frame_geometry.topLeft())

if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    setTheme(Theme.DARK)  # 设置主题为暗色主题
    app = QApplication(sys.argv)
    w = Demo()  # 创建 Demo 实例，并自动显示
    app.exec_()
