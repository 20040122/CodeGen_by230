from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import BodyLabel, HyperlinkButton, LineEdit, PrimaryPushButton
import resource_rc  # 资源文件（例如图片）

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(700, 500)
        Form.setMinimumSize(QtCore.QSize(700, 500))

        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)

        # Background image label
        self.label = QtWidgets.QLabel(Form)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/images/background.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        # Widget to contain the login and registration form
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setStyleSheet("QLabel { font: 13px 'Microsoft YaHei'; }")
        self.widget.setMinimumSize(QtCore.QSize(360, 0))
        self.widget.setMaximumSize(QtCore.QSize(360, 16777215))

        # Vertical layout for the form
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(20, 10, 20, 20)  # 减少顶部间距
        self.verticalLayout_2.setSpacing(5)  # 增加间距，提升可读性

        # Spacer and Logo
        spacerItem = QtWidgets.QSpacerItem(10,5,QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)  # 调整间距
        self.verticalLayout_2.addItem(spacerItem)

        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setText("")
        pixmap = QtGui.QPixmap(":/images/logo.png")
        scaled_pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)  # 调整图标大小
        self.label_2.setPixmap(scaled_pixmap)
        self.label_2.setScaledContents(False)  # 不自动缩放，使用我们手动调整的尺寸
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter)
        self.verticalLayout_2.addWidget(self.label_2)

        # Spacer
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)

        # Create the QStackedWidget to manage login and register pages
        self.stackedWidget = QtWidgets.QStackedWidget(self.widget)
        self.stackedWidget.setObjectName("stackedWidget")

        # Login page
        self.login_page = QtWidgets.QWidget()
        self.login_layout = QtWidgets.QVBoxLayout(self.login_page)

        self.label_5 = BodyLabel(self.login_page)
        self.label_5.setText("用户名")
        self.login_layout.addWidget(self.label_5)

        self.lineEdit_3 = LineEdit(self.login_page)
        self.lineEdit_3.setClearButtonEnabled(True)
        self.login_layout.addWidget(self.lineEdit_3)

        self.label_6 = BodyLabel(self.login_page)
        self.label_6.setText("密码")
        self.login_layout.addWidget(self.label_6)

        self.lineEdit_4 = LineEdit(self.login_page)
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_4.setClearButtonEnabled(True)
        self.login_layout.addWidget(self.lineEdit_4)

        self.pushButton = PrimaryPushButton(self.login_page)
        self.pushButton.setText("登录")
        self.login_layout.addWidget(self.pushButton)

        self.pushButton_2 = HyperlinkButton(self.login_page)
        self.pushButton_2.setText("注册")
        self.pushButton_2.clicked.connect(self.show_register_page)  # Switch to the register page
        self.login_layout.addWidget(self.pushButton_2)

        # Register page
        self.register_page = QtWidgets.QWidget()
        self.register_layout = QtWidgets.QVBoxLayout(self.register_page)

        self.label_7 = BodyLabel(self.register_page)
        self.label_7.setText("用户名")
        self.register_layout.addWidget(self.label_7)

        self.lineEdit_5 = LineEdit(self.register_page)
        self.lineEdit_5.setClearButtonEnabled(True)
        self.register_layout.addWidget(self.lineEdit_5)

        self.label_8 = BodyLabel(self.register_page)
        self.label_8.setText("密码")
        self.register_layout.addWidget(self.label_8)

        self.lineEdit_6 = LineEdit(self.register_page)
        self.lineEdit_6.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_6.setClearButtonEnabled(True)
        self.register_layout.addWidget(self.lineEdit_6)

        self.label_9 = BodyLabel(self.register_page)
        self.label_9.setText("确认密码")
        self.register_layout.addWidget(self.label_9)

        self.lineEdit_7 = LineEdit(self.register_page)
        self.lineEdit_7.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_7.setClearButtonEnabled(True)
        self.register_layout.addWidget(self.lineEdit_7)

        self.pushButton_3 = PrimaryPushButton(self.register_page)
        self.pushButton_3.setText("注册")
        self.register_layout.addWidget(self.pushButton_3)

        self.pushButton_4 = HyperlinkButton(self.register_page)
        self.pushButton_4.setText("返回登录")
        self.pushButton_4.clicked.connect(self.show_login_page)  # Switch to the login page
        self.register_layout.addWidget(self.pushButton_4)

        # Add both pages to the stacked widget
        self.stackedWidget.addWidget(self.login_page)
        self.stackedWidget.addWidget(self.register_page)

        # Show the login page by default
        self.stackedWidget.setCurrentIndex(0)

        self.verticalLayout_2.addWidget(self.stackedWidget)

        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "登录"))

    def show_login_page(self):
        """切换到登录页面"""
        self.stackedWidget.setCurrentIndex(0)

    def show_register_page(self):
        """切换到注册页面"""
        self.stackedWidget.setCurrentIndex(1)
