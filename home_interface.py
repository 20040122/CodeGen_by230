from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from qfluentwidgets import SubtitleLabel, setFont

class HomeInterface(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 设置窗口大小限制
        self.resize(1000, 700)  # 设置窗口大小为1000x700

        # 创建子界面组件
        self.label = SubtitleLabel(self)
        self.sub_label = QLabel(self)  # 创建第二行文字标签
        self.image_label = QLabel(self)  # 创建 QLabel 用于显示图片

        # 使用 QVBoxLayout 来布局
        self.layout = QVBoxLayout(self)

        # 设置字体和对齐方式
        setFont(self.label, 38)
        self.label.setAlignment(Qt.AlignCenter)  # 居中文本
        setFont(self.sub_label, 20)  # 设置第二行文字的字体
        self.sub_label.setAlignment(Qt.AlignCenter)  # 居中对齐

        # 设置文字内容
        self.label.setText("代码智能补全工具")

        # 第二行逐字显示的内容
        self.full_sub_text = "Python开发效率提升神器"
        self.current_sub_text = ""
        self.sub_label.setText(self.current_sub_text)

        self.sub_label.setStyleSheet("color: cyan;")  # 设置字体颜色为浅蓝色
        # 加载图片
        self.pixmap = QPixmap(r'D:\PythonCode\CodeBERT\UI\resource\images\header1.png')  # 修改为你的图片路径

        # 设置 QLabel 的大小策略
        self.image_label.setAlignment(Qt.AlignCenter)  # 图片居中显示
        self.image_label.setPixmap(
            self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 初始化图片尺寸

        # 设置透明度效果
        opacity_effect = QGraphicsOpacityEffect(self.label)
        opacity_effect.setOpacity(0.8)  # 设置透明度为0.7，可以根据需要调整
        self.label.setGraphicsEffect(opacity_effect)

        # 使用 QVBoxLayout 添加控件
        self.layout.addWidget(self.label)  # 添加标题
        self.layout.addSpacing(6)  # 增加标题和第二行文字之间的间距
        self.layout.addWidget(self.sub_label)  # 添加第二行文字
        self.layout.addWidget(self.image_label)  # 添加图片

        # 设置布局的边距
        self.layout.setContentsMargins(0, 0, 0, 0)  # 去除边距

        # 设置布局
        self.setLayout(self.layout)
        self.setObjectName('主页')

        # 动态显示第二行文字
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sub_text)
        self.timer.start(200)  # 每300ms更新一次文字

    def update_sub_text(self):
        # 如果当前文字还没有完全显示
        if len(self.current_sub_text) < len(self.full_sub_text):
            self.current_sub_text += self.full_sub_text[len(self.current_sub_text)]
            self.sub_label.setText(self.current_sub_text)  # 更新显示的文字
        else:
            # 当文字显示完全后，停一会再清空
            self.timer.stop()  # 停止定时器

            # 使用 QTimer.singleShot 来延迟2秒后清空文字
            QTimer.singleShot(3000, self.clear_text)  # 延迟2秒后调用 clear_text 方法

    def clear_text(self):
        # 清空文字
        self.current_sub_text = ""
        self.sub_label.setText(self.current_sub_text)  # 清空显示的文字

        # 重新开始显示文字
        self.timer.start(200)  # 重启定时器，每250ms更新一次文字

    def resizeEvent(self, event):
        """窗口大小调整时重新缩放图片"""
        # 获取当前可用的宽高，并保持图片比例
        available_width = self.width()
        available_height = self.height()

        # 设置缩放比例，比如缩小到原来的80%
        scale_factor = 0.8
        # 设置缩放比例，比如增加宽度并保持高度适应
        scale_factor_width = 2  # 宽度增大20%
        scaled_width = available_width * scale_factor_width  # 增加宽度
        scaled_height = available_height * scale_factor

        # 设置图片的最大宽高为缩小后的尺寸
        pixmap_scaled = self.pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation)

        # 设置新的图片
        self.image_label.setPixmap(pixmap_scaled)

        super().resizeEvent(event)


