from .base import*
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

""" 基于Pyside6-Fluent-Widget同名称组件修改，修复了无法遍历组件的问题 """

#
# def hook_ExpandLayout_addWidget(self, widget: QWidget):
#     if widget in self.__widgets:
#         return
#
#     self.__widgets.append(widget)
#     widget.installEventFilter(self)
#
#
# def hook_ExpandLayout_count(self):
#     return len(self.__widgets)
#
#
# def hook_ExpandLayout_itemAt(self, index):
#     if 0 <= index < len(self.__items):
#         return self.__items[index]
#
#     return None
#
#
# def hook_ExpandLayout_takeAt(self, index):
#     if 0 <= index < len(self.__widgets):
#         return self.__widgets.pop(index)
#
#     return None
#
#
# def hook_ExpandLayout_clearWidget(self):
#     """
#     自定义清空组件函数
#     """
#     while self.count():
#         widget = self.takeAt(0)
#         if widget is not None:
#             widget.deleteLater()
#
#
# ExpandLayout.addWidget = hook_ExpandLayout_addWidget
# ExpandLayout.count = hook_ExpandLayout_count
# ExpandLayout.itemAt = hook_ExpandLayout_itemAt
# ExpandLayout.takeAt = hook_ExpandLayout_takeAt
# ExpandLayout.clearWidget = hook_ExpandLayout_clearWidget
