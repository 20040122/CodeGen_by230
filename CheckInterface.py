import requests
import keyword
import re
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from qfluentwidgets import TextEdit, PrimaryToolButton, ProgressRing, Dialog


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_lines = []

        # 设置不同类型的高亮
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(0, 255, 255))  # 关键字：青色

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(0, 255, 0))  # 注释：绿色

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(0, 255, 0))  # 字符串：绿色

        self.default_format = QTextCharFormat()
        self.default_format.setForeground(QColor(255, 255, 255))  # 其余是白色

    def highlightBlock(self, text):
        # 清除之前的高亮
        self.setFormat(0, len(text), self.default_format)

        # 高亮关键字
        words = text.split()
        for word in words:
            if word in keyword.kwlist:  # 检查是否为 Python 关键字
                self.setFormat(text.find(word), len(word), self.keyword_format)

        # 高亮注释
        comment_pattern = r'#.*'
        comment_matches = re.finditer(comment_pattern, text)
        for match in comment_matches:
            self.setFormat(match.start(), len(match.group(0)), self.comment_format)

        # 高亮字符串
        string_pattern = r'".*?"|\'.*?\''
        string_matches = re.finditer(string_pattern, text)
        for match in string_matches:
            self.setFormat(match.start(), len(match.group(0)), self.string_format)


class ApiRequestThread(QThread):
    # 定义信号来传递进度和最终结果
    update_progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.code = code
        self.url = "http://localhost:11434/api/generate"
        self.data = {
            "model": "codellama",  # 使用codellama模型
            "prompt": f"{code}这段Python函数是否存在明显错误?",
            "stream": False,
            "options": {
                "temperature": 0.5
            }
        }

    def run(self):
        try:
            # 发送请求前更新进度环
            self.update_progress.emit(30)

            # 发送POST请求到后端
            response = requests.post(self.url, json=self.data)
            response.raise_for_status()  # 如果请求失败，会抛出异常
            result = response.json()  # 获取返回的JSON数据

            # 更新进度到 60%
            self.update_progress.emit(60)

            # 提取返回的 response 字段内容
            if "response" in result:
                response_text = result["response"]
                cleaned_response = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL)

                # 完成进度，发送结果
                self.update_progress.emit(100)
                self.finished.emit(cleaned_response)
            else:
                self.finished.emit("没有找到返回的 'response' 字段")

        except requests.exceptions.RequestException as e:
            self.finished.emit(f"请求失败: {e}")


class CheckInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CheckInterface")

        # 创建布局
        self.layout = QVBoxLayout(self)

        # 创建按钮和布局
        self.button_layout = QHBoxLayout()

        # 使用 PrimaryToolButton 作为检查按钮
        self.check_button = PrimaryToolButton(self)  # 按钮样式
        self.check_button.setText("检查代码")
        self.check_button.clicked.connect(self.check_code)

        self.button_layout.addWidget(self.check_button, alignment=Qt.AlignLeft)
        self.layout.addLayout(self.button_layout)

        # 创建代码编辑框，使用 qfluentwidgets 的 TextEdit
        self.code_edit = TextEdit(self)
        self.code_edit.setFont(QFont("Consolas", 22))  # 设置代码字体
        self.code_edit.setPlaceholderText("输入Python代码")  # 设置提示文本
        self.code_edit.setFixedHeight(450)
        self.layout.addWidget(self.code_edit)
        # 创建一个顶部的右对齐布局
        self.top_layout = QHBoxLayout()
        # 创建进度环
        self.ring = ProgressRing(self)
        self.ring.setRange(0, 100)
        self.ring.setValue(0)
        self.ring.setTextVisible(True)
        self.ring.setFixedSize(80, 80)
        self.ring.setStrokeWidth(4)
        # 将进度环添加到顶部布局，并使其右对齐
        self.top_layout.addWidget(self.ring, alignment=Qt.AlignRight)
        self.layout.addLayout(self.top_layout)
        # 创建语法高亮器实例
        self.highlighter = SyntaxHighlighter(self.code_edit.document())

    def keyPressEvent(self, event):
        # 如果按下 Tab 键，插入 4 个空格
        if event.key() == Qt.Key_Tab:
            self.code_edit.insertPlainText(' ' * 4)  # 插入四个空格
        else:
            super().keyPressEvent(event)  # 调用父类的处理方法，处理其他按键事件


    def check_code(self):
        code = self.code_edit.toPlainText()  # 获取代码文本
        if not code.strip():  # 检查是否为空
            self.show_message("提示", "请输入代码！")
            return

        # 启动 API 请求线程
        self.api_thread = ApiRequestThread(code)
        self.api_thread.update_progress.connect(self.update_progress)  # 连接进度更新信号
        self.api_thread.finished.connect(self.show_result)  # 连接线程完成信号
        self.api_thread.start()

    def update_progress(self, value):
        # 更新进度环的值
        self.ring.setValue(value)

    def show_result(self, message):
        # 使用自定义 Dialog 显示消息框
        w = Dialog("", message, self)
        w.exec()
