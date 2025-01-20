from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QMessageBox, QSizePolicy
from qfluentwidgets import SearchLineEdit, TextEdit, StateToolTip
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtCore import Qt, QRegExp, QThread, pyqtSignal
import requests
from PyQt5.QtCore import QTimer


class FlowLayout(QVBoxLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(10, 10, 10, 10)  # 增加边距
        self.setSpacing(10)  # 设置合理的控件间距

    def addWidget(self, widget):
        """Override the addWidget method to allow flow behavior."""
        super().addWidget(widget)
        # 延迟调整控件位置，确保父控件已经设置好
        QTimer.singleShot(0, self._adjustWidgets)

    def _adjustWidgets(self):
        """Rearrange widgets when adding new ones."""
        parent = self.parentWidget()
        if parent is None:
            return

        current_x = 0
        max_y = 0
        for i in range(self.count()):
            widget = self.itemAt(i).widget()
            if widget is None:
                continue

            widget_width = widget.sizeHint().width()
            widget.move(current_x, max_y)
            current_x += widget_width + self.spacing()

            if current_x > parent.width():
                max_y += widget.sizeHint().height() + self.spacing()
                current_x = widget_width + self.spacing()


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document, function_name=None):
        super().__init__(document)

        # 定义Python关键字颜色
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("cyan"))

        # 定义字符串颜色
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("green"))

        # 定义注释颜色
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("gray"))

        # 定义Python关键字
        self.keywords = [
            "def", "class", "import", "from", "return", "if", "else", "elif", "for", "while",
            "try", "except", "finally", "with", "as", "yield", "break", "continue", "pass"
        ]

        # 定义橘色高亮
        self.function_name_format = QTextCharFormat()
        self.function_name_format.setForeground(QColor("orange"))

        # 定义正则表达式
        self.highlighting_rules = []

        # 关键词高亮
        for keyword in self.keywords:
            pattern = r"\b" + keyword + r"\b"  # \b表示单词边界
            regex = QRegExp(pattern)
            self.highlighting_rules.append((regex, self.keyword_format))

        # 字符串高亮
        self.highlighting_rules.append((QRegExp(r'".*"'), self.string_format))
        self.highlighting_rules.append((QRegExp(r"'[^']*'"), self.string_format))

        # 注释高亮
        self.highlighting_rules.append((QRegExp(r'#.*'), self.comment_format))

        # 如果提供了函数名，加入函数名高亮规则
        if function_name:
            pattern = r"\b" + function_name + r"\b"
            regex = QRegExp(pattern)
            self.highlighting_rules.append((regex, self.function_name_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, format)
                index = pattern.indexIn(text, index + length)


class RequestThread(QThread):
    result_signal = pyqtSignal(dict)  # 定义信号，传递请求结果

    def __init__(self, function_name):
        super().__init__()
        self.function_name = function_name  # 保存函数名

    def run(self):
        """线程中的代码，发送网络请求并返回结果"""
        try:
            url = "http://127.0.0.1:8000/generate_code/"
            response = requests.post(url, json={"function_name": self.function_name})

            if response.status_code == 200:
                data = response.json()
                # 发射信号，将返回的数据传递给主线程
                self.result_signal.emit(data)
            else:
                # 如果请求失败，传递错误信息
                self.result_signal.emit({"error": response.json().get("detail", "未知错误")})
        except Exception as e:
            # 异常处理
            self.result_signal.emit({"error": str(e)})


class CodeCompletionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("code_completion_interface")

        # 创建布局
        self.vBoxLayout = FlowLayout(self)

        # 创建搜索框
        self.function_input = SearchLineEdit(self)
        self.function_input.setPlaceholderText("输入函数名")
        self.function_input.setFixedHeight(40)
        self.function_input.setFixedWidth(350)
        self.function_input.searchSignal.connect(self.on_function_search)  # 连接信号
        self.vBoxLayout.addWidget(self.function_input)

        # 创建代码显示框
        self.generated_code_display = TextEdit(self)
        self.generated_code_display.setFont(QFont("Consolas", 22))  # 设置代码字体
        self.generated_code_display.setReadOnly(True)  # 设置只读
        self.generated_code_display.setFixedHeight(350)
        # self.generated_code_display.setFixedWidth(1000)
        self.highlighter = PythonHighlighter(self.generated_code_display.document())  # 初始化时传入高亮器
        self.vBoxLayout.addWidget(self.generated_code_display)

        self.state_tooltip = None  # 状态提示初始化为空

        self.resize(800, 600)

    def on_function_search(self, text):
        """当用户输入函数名时触发事件，发送请求生成代码"""
        function_name = text.strip()
        if not function_name.isidentifier():
            QMessageBox.warning(self, "输入错误", "请输入有效的函数名")
            return

        # 显示“正在训练模型”状态提示
        if not self.state_tooltip:
            self.state_tooltip = StateToolTip('正在生成代码中', '请耐心等待哦~~', self)
            self.state_tooltip.move(650, 30)
            self.state_tooltip.show()

        # 更新高亮器中的函数名
        self.highlighter = PythonHighlighter(self.generated_code_display.document(), function_name)  # 更新高亮规则
        self.generated_code_display.repaint()  # 刷新显示

        # 使用线程发送请求
        self.request_thread = RequestThread(function_name)  # 创建线程对象
        self.request_thread.result_signal.connect(self.on_request_result)  # 连接信号
        self.request_thread.start()  # 启动线程

    def on_request_result(self, result):
        """处理请求返回的结果"""
        if "error" in result:
            QMessageBox.warning(self, "错误", result["error"])  # 请求失败时弹出错误消息
        else:
            generated_code = result.get("generated_code")
            self.generated_code_display.setPlainText(generated_code)  # 显示生成的代码

            # 更新状态提示为“模型训练完成”
            if self.state_tooltip:
                self.state_tooltip.setContent('代码生成成功😆')
                self.state_tooltip.setState(True)
                self.state_tooltip = None  # 请求完成后隐藏状态提示
