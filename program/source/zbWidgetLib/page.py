from .base import *


class BetterScrollArea(SmoothScrollArea):
    """
    优化样式的滚动区域
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea {background-color: rgba(0,0,0,0); border: none}")

        self.setScrollAnimation(Qt.Vertical, 500, QEasingCurve.OutQuint)
        self.setScrollAnimation(Qt.Horizontal, 500, QEasingCurve.OutQuint)

        self.view = QWidget(self)
        self.view.setStyleSheet("QWidget {background-color: rgba(0,0,0,0); border: none}")

        self.setWidget(self.view)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)


class BasicPage(BetterScrollArea):
    """
    页面模板
    """
    title = ""
    subtitle = ""
    pageIcon = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(self.title)

        self.toolBar = ToolBar(self.title, self.subtitle, self)

        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

    def setIcon(self, icon):
        """
        设置页面图标
        @param icon: 图标
        """
        self.pageIcon = icon

    def icon(self):
        """
        获取页面图标
        @return: 图标
        """
        return self.pageIcon


class BasicTabPage(BasicPage):
    """
    有多标签页的页面模板
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.toolBar.deleteLater()

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.pivot = Pivot(self)
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignHCenter)

        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.vBoxLayout.addWidget(self.stackedWidget)

    def addPage(self, widget):
        """
        添加标签页
        @param widget: 标签页对象，需设置icon属性为页面图标
        """
        name = widget.objectName()
        widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(name, name, lambda: self.stackedWidget.setCurrentWidget(widget), widget.icon)
        if self.stackedWidget.count() == 1:
            self.stackedWidget.setCurrentWidget(widget)
            self.pivot.setCurrentItem(widget.objectName())

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())


class BasicTab(BasicPage):
    """
    多标签页模板
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.toolBar.deleteLater()
        self.setViewportMargins(0, 0, 0, 0)


class ChangeableTab(BasicTab):
    """
    可切换页面的页面
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.page = {}
        self.onShowPage = None
        self.onShowName = None

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

    def addPage(self, widget, name=None, alignment: Qt.AlignmentFlag | None = None):
        """
        添加页面
        @param widget: 组件
        @param name: 组件名称（默认为objectName）
        """
        widget.setParent(self)
        widget.hide()
        if not name:
            name = widget.objectName()
        self.page[name] = widget
        if alignment:
            self.vBoxLayout.addWidget(widget, 0, alignment)
        else:
            self.vBoxLayout.addWidget(widget)

    def showPage(self, name):
        """
        展示页面
        @param name: 组件名称
        """
        self.hidePage()
        self.page[name].show()
        self.onShowPage = self.page[name]
        self.onShowName = name

    def hidePage(self):
        """
        隐藏页面
        """
        if self.onShowPage:
            self.onShowPage.hide()


class ToolBar(QWidget):
    """
    页面顶端工具栏
    """

    def __init__(self, title: str, subtitle: str, parent=None):
        """
        @param title: 主标题
        @param subtitle: 副标题
        """
        super().__init__(parent=parent)
        self.setFixedHeight(90)

        self.titleLabel = TitleLabel(title, self)
        self.subtitleLabel = CaptionLabel(subtitle, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 22, 36, 12)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
