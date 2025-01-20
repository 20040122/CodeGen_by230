import sys
import pymysql
from PyQt5.QtCore import Qt, QLocale, QRect, QTimer, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator, setTheme, Theme, SplitTitleBar, isDarkTheme, Flyout, InfoBarIcon, FlyoutAnimationType
from Ui_LoginWindow import Ui_Form
from UI.Interface.Interface import mainWindow


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000

if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window

class LoginWindow(Window, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        setThemeColor('#28afe9')

        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()


        self.label.setScaledContents(True)
        self.setWindowTitle('代码智能补全工具')
        self.setWindowIcon(QIcon(":/images/logo.png"))
        self.resize(1000, 580)

        self.windowEffect.setMicaEffect(self.winId(), isDarkMode=isDarkTheme())
        if not isWin11():
            color = QColor(25, 33, 42) if isDarkTheme() else QColor(240, 244, 249)
            self.setStyleSheet(f"LoginWindow{{background: {color.name()}}}")

        if sys.platform == "darwin":
            self.setSystemTitleBarButtonVisible(True)
            self.titleBar.minBtn.hide()
            self.titleBar.maxBtn.hide()
            self.titleBar.closeBtn.hide()

        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: white
            }
        """)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # MySQL Database connection using pymysql
        self.db_connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="codebert"
        )
        self.db_cursor = self.db_connection.cursor()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        pixmap = QPixmap(":/images/background.jpg").scaled(
            self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)


    def systemTitleBarRect(self, size):
        return QRect(size.width() - 75, 0, 75, size.height())

    def show_login_page(self):
        """切换到登录页面"""
        self.stackedWidget.setCurrentIndex(0)

    def show_register_page(self):
        """切换到注册页面"""
        self.stackedWidget.setCurrentIndex(1)

    def register_user(self):
        """用户注册功能"""
        username = self.lineEdit_5.text()
        password = self.lineEdit_6.text()
        confirm_password = self.lineEdit_7.text()

        # 检查用户名是否为空
        if not username:
            self.show_flyout("错误", "用户名不能为空!")
            return

        # 检查密码是否为空
        if not password:
            self.show_flyout("错误", "密码不能为空!")
            return

        # 确认密码输入是否一致
        if password != confirm_password:
            self.show_flyout("错误", "两次输入的密码不匹配!")
            return

        # 检查用户名是否已经存在
        self.db_cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if self.db_cursor.fetchone():
            self.show_flyout("错误", "该用户名已被注册!")
            return

        # 插入新用户到数据库
        self.db_cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        self.db_connection.commit()

        self.show_flyout("注册成功", "用户注册成功!")
        self.show_login_page()

    def login_user(self):
        """用户登录功能"""
        username = self.lineEdit_3.text()
        password = self.lineEdit_4.text()

        # 查询数据库验证用户名和密码
        self.db_cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        if self.db_cursor.fetchone():
            self.show_flyout("登录成功", "登录成功!")
            # 使用 QTimer 延时 1 秒后跳转到主窗口
            QTimer.singleShot(1000, self.open_mainwindow)  # 2000 毫秒 = 2 秒
        else:
            self.show_flyout("登录失败", "用户名或密码错误!")

    def show_flyout(self, title, content):
        """显示 Flyout 弹窗"""
        # 获取窗口中心坐标
        target_geometry = self.geometry()
        target_center = target_geometry.center()

        # 创建 Flyout
        flyout = Flyout.create(
            icon=InfoBarIcon.SUCCESS if "成功" in title else InfoBarIcon.ERROR,
            title=title,
            content=content,
            target=self,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
        # 设置 Flyout 位置为窗口中心
        flyout.move(target_center - QPoint(flyout.width() // 2, flyout.height() // 2))

    def connect_signals(self):
        """连接按钮点击事件"""
        self.pushButton.clicked.connect(self.login_user)  # 登录按钮
        self.pushButton_3.clicked.connect(self.register_user)  # 注册按钮
        self.pushButton_2.clicked.connect(self.show_register_page)  # 切换到注册页面
        self.pushButton_4.clicked.connect(self.show_login_page)  # 返回到登录页面

    def open_mainwindow(self):
        self.mainwindow = mainWindow()
        self.mainwindow.show()
        self.close()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)
    setTheme(Theme.DARK)
    w = LoginWindow()
    w.connect_signals()  # 连接信号和槽
    w.show()
    app.exec_()
