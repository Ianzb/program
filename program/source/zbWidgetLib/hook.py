from .base import *

""" 基于Pyside6-Fluent-Widget同名称组件修改，修复了主窗口关闭时异常退出的问题 """


def hook_InfoBar__fadeOut(self):
    """ fade out """
    self.opacityAni.setDuration(200)
    self.opacityAni.setStartValue(1)
    self.opacityAni.setEndValue(0)
    self.opacityAni.finished.connect(self.close)
    self.opacityAni.start()


def hook_InfoBar_close(self):
    self.hide()
    self.closedSignal.emit()
    self.deleteLater()


InfoBar.__fadeOut = hook_InfoBar__fadeOut
InfoBar.close = hook_InfoBar_close


class FixedExpandLayout(QLayout):
    """ 基于Pyside6-Fluent-Widget同名称组件修改，修复了无法遍历组件的问题 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__items = []
        self.__widgets = []

    def addWidget(self, widget: QWidget):
        if widget in self.__widgets:
            return

        self.__widgets.append(widget)
        widget.installEventFilter(self)

    def removeWidget(self, widget: QWidget):
        if widget in self.__widgets:
            self.__widgets.remove(widget)
            widget.removeEventFilter(self)

    def addItem(self, item):
        self.__items.append(item)

    def count(self):
        return len(self.__widgets)

    def itemAt(self, index):
        if 0 <= index < len(self.__items):
            return self.__items[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self.__widgets):
            return self.__widgets.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation.Vertical

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        """ get the minimal height according to width """
        return self.__doLayout(QRect(0, 0, width, 0), False)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.__doLayout(rect, True)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for w in self.__widgets:
            size = size.expandedTo(w.minimumSize())

        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())

        return size

    def __doLayout(self, rect, move):
        """ adjust widgets position according to the window size """
        margin = self.contentsMargins()
        x = rect.x() + margin.left()
        y = rect.y() + margin.top() + margin.bottom()
        width = rect.width() - margin.left() - margin.right()

        for i, w in enumerate(self.__widgets):
            if w.isHidden():
                continue

            y += (i > 0) * self.spacing()
            if move:
                w.setGeometry(QRect(QPoint(x, y), QSize(width, w.height())))

            y += w.height()

        return y - rect.y()

    def eventFilter(self, obj, e):
        if obj in self.__widgets:
            if e.type() == QEvent.Type.Resize:
                ds = e.size() - e.oldSize()  # type:QSize
                if ds.height() != 0 and ds.width() == 0:
                    w = self.parentWidget()
                    w.resize(w.width(), w.height() + ds.height())

        return super().eventFilter(obj, e)

    def clearWidget(self):
        """
        自定义清空组件函数
        """
        while self.count():
            widget = self.takeAt(0)
            if widget is not None:
                widget.deleteLater()
