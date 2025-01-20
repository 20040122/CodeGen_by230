from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSignal, QRegExp, QTimer
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import requests
from qfluentwidgets import TextEdit  # 假设 TextEdit 来自 qfluentwidgets


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # 定义Python关键字颜色和字体样式
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("cyan"))
        self.keyword_format.setFontWeight(QFont.Bold)  # 设置字体加粗

        # 定义字符串颜色和字体样式
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("green"))
        self.string_format.setFontItalic(True)  # 设置字体斜体

        # 定义注释颜色和字体样式
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("gray"))
        self.comment_format.setFontItalic(True)  # 设置字体斜体

        # 定义Python关键字
        self.keywords = [
            "def", "class", "import", "from", "return", "if", "else", "elif", "for", "while",
            "try", "except", "finally", "with", "as", "yield", "break", "continue", "pass"
        ]

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

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, format)
                index = pattern.indexIn(text, index + length)


class CodeCompletionThread(QThread):
    # 定义信号，补全代码、进度和错误信号
    completed_code_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt  # 要补全的代码

    def run(self):
        """ 线程运行的代码 """
        url = "http://127.0.0.1:8000/complete_code/"
        payload = {"prompt": self.prompt}

        try:
            response = requests.post(url, json=payload, stream=True)

            # 模拟进度更新
            for i in range(0, 101, 10):  # 每10%更新一次进度
                self.progress_signal.emit(i)
                self.msleep(200)  # 模拟延时，实际可以根据实际情况调整

            if response.status_code == 200:
                data = response.json()
                completed_code = data.get("completed_code", "")
                self.completed_code_signal.emit(completed_code)  # 发射信号到主线程
            else:
                error_detail = response.json().get("detail", "未知错误")
                self.error_signal.emit(error_detail)  # 如果有错误，发射错误信号
        except requests.exceptions.ConnectionError:
            self.error_signal.emit("无法连接到后端服务，请确保 FastAPI 服务器正在运行")
        except Exception as e:
            self.error_signal.emit(f"生成代码时出错: {e}")


class CodeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("CodeInterface")

        # 创建布局和控件
        self.layout = QVBoxLayout(self)

        # 创建进度条，设置较细的高度并放置在顶部
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)  # 设置进度条的范围
        self.progressBar.setValue(0)  # 初始值为0
        self.progressBar.setFixedHeight(4)  # 设置进度条的高度，调节为更细
        self.progressBar.setTextVisible(False)  # 隐藏进度条上的数字
        self.progressBar.setStyleSheet("""
            QProgressBar {
                background-color: transparent;  /* 设置背景透明 */
                border: 1px solid #ccc;          /* 设置边框 */
                border-radius: 5px;              /* 设置圆角 */
            }
            QProgressBar::chunk {
                background-color: cyan;      /* 设置进度条的颜色 */
                border-radius: 5px;              /* 设置圆角 */
            }
        """)
        self.layout.addWidget(self.progressBar)

        # 创建代码编辑框，使用 qfluentwidgets 的 TextEdit
        self.code_edit = TextEdit(self)
        self.code_edit.setFont(QFont("Consolas", 19))  # 设置代码字体
        self.code_edit.setPlaceholderText("输入代码片段按CTRL自动补全")  # 设置提示文本
        self.code_edit.setFixedHeight(600)
        self.layout.addWidget(self.code_edit)

        # 安装事件过滤器来捕获键盘事件
        self.code_edit.installEventFilter(self)

        # 设置代码高亮
        self.highlighter = PythonHighlighter(self.code_edit.document())

    def eventFilter(self, obj, event):
        """ 监听 Ctrl 键按下事件 """
        if obj == self.code_edit and event.type() == QEvent.KeyPress:
            if event.modifiers() == Qt.ControlModifier:  # 判断是否按下了Ctrl键
                print("Ctrl 键按下，触发补全")
                self.complete_code()
                return True  # 返回 True 表示事件已经被处理
        return super().eventFilter(obj, event)

    def complete_code(self):
        """ 触发代码段补全 """
        prompt = self.code_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "输入错误", "请输入代码段")
            return

        # 禁用编辑框，防止用户在补全过程中修改内容
        self.code_edit.setDisabled(True)

        # 创建并启动后台线程
        self.completion_thread = CodeCompletionThread(prompt)
        self.completion_thread.completed_code_signal.connect(self.on_code_completed)
        self.completion_thread.error_signal.connect(self.on_error)
        self.completion_thread.progress_signal.connect(self.update_progress_bar)  # 连接进度信号
        self.completion_thread.start()

    def on_code_completed(self, completed_code):
        """ 处理补全后的代码 """
        self.code_edit.setPlainText(completed_code)  # 显示补全后的代码
        self.code_edit.setEnabled(True)  # 启用编辑框
        self.progressBar.setValue(100)  # 设置进度条为100%

        # 使用QTimer延迟2秒后刷新进度条
        QTimer.singleShot(2000, self.reset_progress_bar)  # 2000毫秒后调用reset_progress_bar方法

    def on_error(self, error_message):
        """ 处理错误信息 """
        QMessageBox.warning(self, "错误", error_message)
        self.code_edit.setEnabled(True)  # 启用编辑框
        self.progressBar.setValue(0)  # 设置进度条为0%

    def update_progress_bar(self, value):
        """ 更新进度条的值 """
        self.progressBar.setValue(value)  # 设置进度条的当前值

    def reset_progress_bar(self):
        """ 重置进度条 """
        self.progressBar.setValue(0)  # 重置进度条
