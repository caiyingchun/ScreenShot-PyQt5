#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame, QSlider
from PyQt5.QtWidgets import QPushButton, QComboBox, QSpinBox
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPalette, QColor

from color_picker import ColorPicker


class BaseLayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = (__screen_geo.height(),
                                                        __screen_geo.width(),
                                                        __screen_geo.left(),
                                                        __screen_geo.top())

        self.setGeometry(0, 0, self.width, self.height)
        self.rectx, self.recty, self.rectw, self.recth = [0 for _ in range(4)]
        self.setCursor(QtGui.QCursor(QtGui.QCursor(QtCore.Qt.CrossCursor)))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.X11BypassWindowManagerHint)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()


class BaseLayerCanvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = (__screen_geo.height(),
                                                        __screen_geo.width(),
                                                        __screen_geo.left(),
                                                        __screen_geo.top())

        self.setGeometry(0, 0, self.width, self.height)
        self.rectx, self.recty, self.rectw, self.recth = [0 for _ in range(4)]
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.X11BypassWindowManagerHint)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.last_x, self.last_y = None, None


class ToolsConfig(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = (__screen_geo.height(),
                                                        __screen_geo.width(),
                                                        __screen_geo.left(),
                                                        __screen_geo.top())
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.X11BypassWindowManagerHint)

        self.widget_width, self.widget_height = 600, 260
        self.setFixedSize(self.widget_width, self.widget_height)
        self.setGeometry((self.width // 2) - (self.widget_width // 2),
                         self.parent.pos().y() + 36,
                         self.widget_width, self.widget_height)

        self.color_picker = None
        self.init_ui()

    def init_ui(self):
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        hbox_left = QHBoxLayout()
        hbox_right = QHBoxLayout()

        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
        inner_wrap = QVBoxLayout()

        vb_0 = QVBoxLayout()
        vb_1 = QHBoxLayout()
        vb_2 = QHBoxLayout()
        vb_3 = QHBoxLayout()

        pen_size = QLabel("Pen size")
        pen_hbox = QHBoxLayout()

        self.qsl_pen = QSlider(Qt.Horizontal)
        self.qsl_pen.setTickInterval(1)
        self.qsl_pen.setTickPosition(QSlider.TicksAbove)
        self.qsl_pen.setRange(0, 20)
        self.qsl_pen.valueChanged.connect(
            lambda x: self.update_pen_value(self.qsl_pen.value())
        )

        self.qsp = QSpinBox()
        self.qsp.setFixedWidth(46)
        self.qsp.setRange(0, 20)
        self.qsp.valueChanged.connect(
            lambda x: self.update_pen_value(self.qsp.value())
        )

        self.qsl_pen.setValue(self.parent.pen_size)

        pen_hbox.addWidget(self.qsl_pen)
        pen_hbox.addWidget(self.qsp)

        vb_0.addWidget(pen_size)
        vb_0.addItem(pen_hbox)

        line_cap = QLabel("Line cap")
        self.line_qcomb = QComboBox()
        self.line_qcomb.addItem("Square")
        self.line_qcomb.addItem("Round")
        self.line_qcomb.currentIndexChanged.connect(self.update_pen_cap)

        ind = 0
        if self.parent.cap == Qt.RoundCap:
            ind = 1
        self.line_qcomb.setCurrentIndex(ind)

        vb_1.addWidget(line_cap)
        vb_1.addWidget(self.line_qcomb)

        line_joint = QLabel("Line joint style")
        self.line_joint_qcomb = QComboBox()
        self.line_joint_qcomb.addItem("Round")
        self.line_joint_qcomb.addItem("Bevel")
        self.line_joint_qcomb.addItem("Acute")
        self.line_joint_qcomb.currentIndexChanged.connect(self.update_pen_joint)

        ind = 0
        if self.parent.joint == Qt.BevelJoin:
            ind = 1
        elif self.parent.joint == Qt.MiterJoin:
            ind = 2
        self.line_joint_qcomb.setCurrentIndex(ind)

        vb_2.addWidget(line_joint)
        vb_2.addWidget(self.line_joint_qcomb)

        pen_style = QLabel("Line style")
        self.style_qcomb = QComboBox()
        self.style_qcomb.addItem("Solid")
        self.style_qcomb.addItem("Dashed")
        self.style_qcomb.addItem("Dotted")
        self.style_qcomb.addItem("Dash-Dot")
        self.style_qcomb.currentIndexChanged.connect(self.update_pen_style)

        ind = 0
        if self.parent.pen_style == Qt.DashLine:
            ind = 1
        elif self.parent.pen_style == Qt.DotLine:
            ind = 2
        elif self.parent.pen_style == Qt.DashDotLine:
            ind = 3
        self.style_qcomb.setCurrentIndex(ind)

        vb_3.addWidget(pen_style)
        vb_3.addWidget(self.style_qcomb)

        vb_4 = QHBoxLayout()
        out_lab = QLabel("Outline")
        self.outline = QComboBox()
        self.outline.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLength)
        self.outline.addItem("Disabled")
        self.outline.addItem("Black")
        self.outline.addItem("Background")
        curr_out = self.parent.config.parse['config']['canvas']['outline']
        if curr_out == 'black':
            self.outline.setCurrentIndex(1)
        elif curr_out == 'background':
            self.outline.setCurrentIndex(2)
        self.outline.currentIndexChanged.connect(self.update_outline)
        vb_4.addWidget(out_lab)
        vb_4.addWidget(self.outline)

        inner_wrap.addItem(vb_0)
        inner_wrap.addItem(vb_1)
        inner_wrap.addItem(vb_2)
        inner_wrap.addItem(vb_3)
        inner_wrap.addItem(vb_4)
        inner_wrap.addStretch(1)

        right_frame.setLayout(inner_wrap)
        right_wrap = QVBoxLayout()
        right_wrap.addWidget(right_frame)
        hbox_right.addItem(right_wrap)

        vbox.addStretch(1)
        vbox_vert = QVBoxLayout()

        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
        left_inner_wrap = QVBoxLayout()

        self.color_picker = ColorPicker(self.parent.config)
        left_inner_wrap.addWidget(self.color_picker)
        left_frame.setLayout(left_inner_wrap)
        left_wrap = QVBoxLayout()
        left_wrap.addWidget(left_frame)
        hbox_left.addItem(left_wrap)

        hbox_lq = QWidget()
        hbox_lq.setLayout(hbox_left)
        hbox_lq.setFixedWidth(300)
        hbox_lq.setFixedHeight(260)

        hbox_q = QWidget()
        hbox_q.setLayout(hbox_right)
        hbox_q.setFixedWidth(300)
        hbox_q.setFixedHeight(260)

        hbox.addWidget(hbox_lq)
        hbox.addWidget(hbox_q)

        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.setAlignment(Qt.AlignLeft)
        vbox_vert.addItem(hbox)
        vbox_vert.setContentsMargins(0, 0, 0, 0)
        vbox_vert.setSpacing(0)
        self.setLayout(vbox_vert)

    def update_pen_style(self):
        ind = self.style_qcomb.currentIndex()
        styles = [
                  ["solid", Qt.SolidLine],
                  ["dash", Qt.DashLine],
                  ["dot", Qt.DotLine],
                  ["dashdot", Qt.DashDotLine]
                ]
        for i in range(4):
            if ind == i:
                self.parent.pen_style = styles[i][1]
        
        self.parent.config.change_config("canvas", "last_style", styles[ind][0])

    def update_pen_value(self, value):
        if type(value) is int:
            self.qsl_pen.setValue(value)
            self.qsp.setValue(value)
            self.parent.pen_size = value

            self.parent.config.change_config("canvas", "last_size", value)

    def update_pen_cap(self):
        ind = self.line_qcomb.currentIndex()
        caps = ["square", "round"]
        if ind == 0:
            self.parent.cap = Qt.SquareCap
        else:
            self.parent.cap = Qt.RoundCap
        
        self.parent.config.change_config("canvas", "last_cap", caps[ind])

    def update_outline(self):
        self.parent.config.change_config('canvas', 'outline', self.outline.currentText().lower())

    def update_pen_joint(self):
        ind = self.line_joint_qcomb.currentIndex()
        joints = ["round", "bevel", "miter"]
        if ind == 0:
            self.parent.joint = Qt.RoundJoin
        elif ind == 1:
            self.parent.joint = Qt.BevelJoin
        else:
            self.parent.joint = Qt.MiterJoin

        self.parent.config.change_config("canvas", "last_joint", joints[ind])

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor('#8EB3E4'), 3))
        painter.drawRect(0, 0, self.widget_width-1, self.widget_height-1)
        painter.end()


class Toolkit(BaseLayer):
    def __init__(self, parent, config, fallback):
        super().__init__()
        self.config = config
        self.parent = parent
        self.last_pos = None

        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.setMouseTracking(True)

        # E1E1E1
        self.setStyleSheet('background-color: #E1E1E1;')

        self.widget_width, self.widget_height = 600, 32
        self.setFixedSize(self.widget_width, self.widget_height)
        self.setGeometry((self.width - self.widget_width) / 2,
                         30,
                         self.widget_width, self.widget_height)

        self.switch = 0
        self.switches = [['blur', 6], 
                         ['free', 5], ['line', 4],
                         ['rect', 3], ['circle', 2],
                         ['pen', 1], ['sel', 0]]

        self.brush_selection_color = QtGui.QColor(103, 150, 188, 80)
        self.pen_selection_color = QtGui.QColor(103, 150, 188, 255)

        self.pen_size = self.config.parse["config"]["canvas"]["last_size"]

        styles = [["solid", Qt.SolidLine],
                  ["dash", Qt.DashLine],
                  ["dot", Qt.DotLine],
                  ["dashdot", Qt.DashDotLine]]

        caps = [["square", Qt.SquareCap], ["round", Qt.RoundCap]]

        joints = [["round", Qt.RoundJoin],
                  ["bevel", Qt.RoundJoin],
                  ["miter", Qt.MiterJoin]]

        style = self.config.parse["config"]["canvas"]["last_style"]
        for s in styles:
            if style == s[0]:
                self.pen_style = s[1]
        
        joint = self.config.parse["config"]["canvas"]["last_joint"]
        for j in joints:
            if joint == j[0]:
                self.joint = j[1]
        
        cap = self.config.parse["config"]["canvas"]["last_cap"]
        for c in caps:
            if cap == c[0]:
                self.cap = c[1]

        self.tools_config = ToolsConfig(self)
        _app_palette = QPalette()
        _app_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        _app_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        _app_palette.setColor(QPalette.Light, QColor(180, 180, 180))
        _app_palette.setColor(QPalette.Midlight, QColor(200, 200, 200))
        _app_palette.setColor(QPalette.Dark, QColor(225, 225, 225))
        _app_palette.setColor(QPalette.Text, QColor(0, 0, 0))
        _app_palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
        _app_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        _app_palette.setColor(QPalette.Base, QColor(237, 237, 237))
        _app_palette.setColor(QPalette.Window, QColor('#E1E1E1'))
        _app_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        _app_palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
        _app_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        _app_palette.setColor(QPalette.Link, QColor(0, 162, 232))
        _app_palette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
        _app_palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
        _app_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        _app_palette.setColor(QPalette.LinkVisited, QColor(222, 222, 222))
        _app_palette.setColor(QPalette.Disabled, QPalette.WindowText,
                              QColor(115, 115, 115))
        _app_palette.setColor(QPalette.Disabled, QPalette.Text,
                              QColor(115, 115, 115))
        _app_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                              QColor(115, 115, 115))
        _app_palette.setColor(QPalette.Disabled, QPalette.Highlight,
                              QColor(190, 190, 190))
        _app_palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                              QColor(115, 115, 115))
        _font = QtGui.QFont()
        _font.setPointSize(10)
        self.tools_config.setFont(_font)

        self.tools_config.setPalette(_app_palette)
        self.color = self.tools_config.color_picker

        self.init_ui()

    def init_ui(self):
        grid = QHBoxLayout()
        grid.setContentsMargins(4, 0, 4, 0)
        grid.setSpacing(1)
        grid.setAlignment(Qt.AlignCenter)

        _tools = ['sel', 'rect', 'line', 'pen', 'circle',
                  'free', 'blur', 'close', 'save']
        if self.config.parse['config']['canvas']['upload_service'] != 'Disabled':
            _tools.append('upload')

        left_grid = QHBoxLayout()
        left_grid.setContentsMargins(0, 0, 0, 0)
        left_grid.setSpacing(4)
        left_grid.setAlignment(Qt.AlignLeft)
        right_grid = QHBoxLayout()
        right_grid.setContentsMargins(0, 0, 0, 0)
        right_grid.setSpacing(12)
        right_grid.setAlignment(Qt.AlignRight)

        self.tools = {x: QPushButton() for x in _tools}

        # 8EB3E4
        self.btn_css = (
            """
            QPushButton {
                qproperty-icon: url(" ");
                background-color: white;
                background-image: url(%s/img/%s.png);
                background-repeat: no-repeat;
                background-position: center;
                border: 1px solid #8EB3E4;
            }
            QPushButton:hover {
                background-color: #E9E9E9;
            }
            """)

        self.btn_css_act = (
            """
            QPushButton {
                qproperty-icon: url(" ");
                qproperty-iconSize: 24px 24px;
                background-color: white;
                background-image: url(%s/img/%s.png);
                background-repeat: no-repeat;
                margin: 0;
                background-position: center;
                border: 2px solid #1070EF;
            }
            QPushButton:hover {
                background-color: #E9E9E9;
            }
            """)

        for key in self.tools.keys():
            self.tools[key].setFixedSize(24, 24)
            self.tools[key].setStyleSheet(self.btn_css % (sys.path[0], key))
            self.tools[key].clicked.connect(self.tool_sel)
            self.tools[key].installEventFilter(self)

        left_spacer = QtWidgets.QSpacerItem(40, self.widget_height)
        left_grid.addWidget(self.tools['sel'])
        left_grid.addWidget(self.tools['pen'])
        left_grid.addWidget(self.tools['circle'])
        left_grid.addWidget(self.tools['rect'])
        left_grid.addWidget(self.tools['line'])
        left_grid.addWidget(self.tools['free'])
        left_grid.addWidget(self.tools['blur'])
        left_grid.addItem(left_spacer)

        right_spacer = QtWidgets.QSpacerItem(40, self.widget_height)
        right_grid.addItem(right_spacer)
        right_grid.addWidget(self.tools['save'])
        if self.config.parse['config']['canvas']['upload_service'] != 'Disabled':
            right_grid.addWidget(self.tools['upload'])
        right_grid.addWidget(self.tools['close'])

        grid.addItem(left_grid)
        grid.addItem(right_grid)
        self.setLayout(grid)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.HoverMove:
            self.parent.move_magnifier(QtGui.QCursor.pos())
        return super().eventFilter(source, event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor('#8EB3E4'), 3))
        painter.drawRect(0, 0, self.widget_width-1, self.widget_height-1)
        painter.end()

    def get_css(self, key, active=False):
        _css = self.btn_css

        if not active:
            return self.btn_css % (sys.path[0], key)
        else:
            return self.btn_css_act % (sys.path[0], key)

    def close_clicked(self):
        self.close()
        self.tools_config.close()
        self.parent.close()

    def showEvent(self, event):
        self.show()
        self.redefine_css()

    def mousePressEvent(self, event):
        self.last_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        cords = self.mapToParent(QPoint(event.x(), event.y()))
        self.parent.move_magnifier(cords)
        if not self.last_pos:
            return
        delta = QPoint(event.globalPos() - self.last_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.tools_config.move(self.x(), self.y() + 36)
        self.last_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.last_pos = None

    def save_action(self):
        if self.config.parse['config']['canvas']['save_action'] == 'dir':
            self.parent.save_image()
            return
        qdialog_filter = 'Pictures (*.png *.jpg *.jpeg *.bmp *.ico *.tiff)'
        filedial = QtWidgets.QFileDialog()
        filedial.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

        self.parent.hide()
        tc_vis = self.tools_config.isVisible()
        if tc_vis:
            self.tools_config.hide()
        self.hide()

        # file picker call
        fd = filedial.getSaveFileName(self, "Save to", '', qdialog_filter)

        filepath = fd[0] if fd[0] else None
        if filepath:
            if not filepath.endswith('.png'):
                filepath += '.png'
            self.parent.save_image(filepath)
        else:
            self.parent.showFullScreen()
            self.parent.activateWindow()
            self.show()
            if tc_vis:
                self.tools_config.show()

    def reset_css(self):
        for key in self.tools.keys():
            self.tools[key].setStyleSheet(self.get_css(key))

    def redefine_css(self):
        self.reset_css()
        for item in self.switches:
            if item[1] == self.switch:
                self.tool_sel(item[0])

    @QtCore.pyqtSlot()
    def tool_sel(self, key=False):
        def submit(key):
            self.reset_css()
            self.tools[key].setStyleSheet(self.get_css(key, True))
            for switch in self.switches:
                if key == switch[0]:
                    self.switch = switch[1]

        if key:
            submit(key)
            return

        for key in self.tools.keys():
            if self.sender() == self.tools[key]:
                if key == 'save':
                    self.save_action()
                    return
                elif key == 'upload':
                    self.parent.upload_image()
                    return
                elif key == 'close':
                    self.close_clicked()
                    return
                else:
                    self.reset_css()
                    submit(key)
                    return
