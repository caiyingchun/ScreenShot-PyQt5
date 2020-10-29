from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QStylePainter, QStyleOptionTab, QCheckBox, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QTabBar, QStyle, QLabel, QLineEdit, QFrame, QTabWidget
from PyQt5.QtWidgets import QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import os

from datetime import datetime
import json


class LabelBoundToCheckbox(QtWidgets.QLabel):
    """
    Toggle checkbox when its label is clicked
    """

    def __init__(self, checkbox, text):
        super().__init__(text)
        self.checkbox = checkbox

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.checkbox.click()


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(list)
    console = QtCore.pyqtSignal(list)

    def __init__(self, fn, args, _type):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.type = _type

    @QtCore.pyqtSlot()
    def run(self):
        """
        Accepts one of the upload methods present in image_toolkit.
        Emits returned values when finished.
        """
        self.args.append(self.console)
        if self.type == 'Imgur':
            try:
                ret_val, del_hash = self.fn(*self.args)
            except (ValueError, TypeError):
                self.finished.emit([])
                return
            self.finished.emit([self.args[1], ret_val, del_hash])
        else:
            ret_val = self.fn(*self.args)
            self.finished.emit([self.args[1], ret_val, None])


class Help(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent

        self.setGeometry(0, 0, 400, 500)
        self.setWindowTitle("Chizuhoru")
        self.move(self.p.pos().x() + 150, self.p.pos().y() - 100)
        self.init_layout()
        self.setWindowTitle("Available patterns")
        self.setWindowIcon(self.p.parent.chz_ico)
        self.show()

    def init_layout(self):
        qv = QtWidgets.QVBoxLayout()

        tips = {
            "%Y": "Year with century (1980, 2020, ..., 9999)",
            "%y": "Year shortened (80, 20, ..., 99)",
            "%m": "Month as decimal (01, 02, ..., 12)",
            "%B": "Month as full name (January, February)",
            "%b": "Month abbreviated (Jan, Feb)",
            "%H": "Hour (24-hour) (00, 15, 23)",
            "%I": "Hour (12-hour) (00, 03, 12)",
            "%M": "Minute (00, 30, ..., 59)",
            "%S": "Second (00, 30, ..., 59)",
            "%p": "AM/PM",
            "%w": "Weekday as decimal (0, 1, ..., 6)",
            "%A": "Weekday as full name (Sunday, Monday)",
            "%a": "Weekday abbreviated (Sun, Mon)",
            "%d": "Day of the month in decimal (01, 02, ..., 31)",
            "%f": "Microsecond (000000, ..., 999999)",
            "%Z": "Time zone name (UTC, EST, CST)",
            "%j": "Day of the year (001, 100, ..., 366)",
            "%U": "Week number from Sunday (00, 01, ..., 53)",
            "%W": "Week number from Monday (00, 01, ..., 53)",
            "%%": "A literal % character."
        }

        for key, val in tips.items():
            _tx = QtWidgets.QLineEdit(key)
            _tx.setReadOnly(True)
            _tx.setFixedWidth(50)
            _tx.selectAll()
            _ds = QtWidgets.QLabel(val)
            _wl = QtWidgets.QHBoxLayout()
            _wl.addWidget(_tx)
            space = QtWidgets.QSpacerItem(10, 0)
            _wl.addItem(space)
            _wl.addWidget(_ds)
            qv.addItem(_wl)

        scroll_frame = QFrame()
        scroll_frame.setLayout(qv)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_frame)

        scroll_wrap = QVBoxLayout()
        scroll_wrap.addWidget(scroll)
        self.setLayout(scroll_wrap)


class TabBar(QtWidgets.QTabBar):

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QtWidgets.QTabWidget.West)


class ProxyStyle(QtWidgets.QProxyStyle):
    def drawControl(self, element, opt, painter, widget):
        if element == QStyle.CE_TabBarTabLabel:
            self.pixelMetric(QStyle.PM_TabBarIconSize)
            r = QtCore.QRect(opt.rect)
            w = 0 if opt.icon.isNull() else opt.rect.width() + self.pixelMetric(QStyle.PM_TabBarIconSize)
            r.setHeight(opt.fontMetrics.width(opt.text) + w)
            r.moveBottom(opt.rect.bottom())
            opt.rect = r
        QtWidgets.QProxyStyle.drawControl(self, element, opt, painter, widget)


class HistoryItem(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.del_hash = None

        self.parent = parent
        self.main_v = QVBoxLayout()
        self.date = QLabel()
        self.type = QLabel()

        info_wrap = QHBoxLayout()
        self.info = QLineEdit()
        self.info_copy_open = QPushButton("Copy")
        info_wrap.addWidget(self.info_copy_open, 20)
        info_wrap.addWidget(self.info, 80)
        self.info.setReadOnly(True)

        self.main_v.addWidget(self.date)
        self.main_v.addWidget(self.type)
        self.main_v.addStretch(1)
        self.main_v.addItem(info_wrap)
        self.main_h_wrap = QHBoxLayout()

        self.thumb = QLabel()

        self.main_h_wrap.addLayout(self.main_v, 1)
        self.main_h_wrap.addWidget(self.thumb, 0)

        w = QFrame()
        w.setFrameStyle(QFrame().StyledPanel | QFrame().Raised)
        w.setLayout(self.main_h_wrap)
        w.setFixedHeight(110)
        framewrap = QVBoxLayout()
        framewrap.addWidget(w)

        self.setLayout(framewrap)

    def show_context_menu(self, event):
        qm = QtWidgets.QMenu()
        act_0 = QtWidgets.QAction("Remove from history")
        act_0.triggered.connect(lambda x: self.parent.remove_from_hist(self))
        qm.addAction(act_0)

        if 'Imgur' in self.type.text():
            act_1 = QtWidgets.QAction("Remove from Imgur")
            act_1.triggered.connect(self.open_imgur)
            qm.addAction(act_1)
        qm.exec(self.mapToGlobal(event))

    def set_info_path(self):
        self.info_copy_open.setText("Open")
        self.info_copy_open.clicked.connect(self.open_dir)

    def set_info_url(self):
        self.info_copy_open.setText("Copy")
        self.info_copy_open.clicked.connect(self.copy_url)

    def open_imgur(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(f"https://imgur.com/delete/{self.del_hash}"))

    def open_dir(self, fpath=None):
        if not fpath:
            fpath = self.info.text()
        os.popen(
            """
            dbus-send --session --print-reply \
            --dest=org.freedesktop.FileManager1 \
            --type=method_call /org/freedesktop/FileManager1 \
            org.freedesktop.FileManager1.ShowItems \
            array:string:"file://%s" string:\"\"
            """ % fpath)

    def copy_url(self):
        self.parent.app.clipboard().setText(self.info.text())

    def set_icon(self, image_path):
        self.thumb.setPixmap(QtGui.QPixmap(image_path))


class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent, app, config, image_toolkit):
        super().__init__()
        self.app = app
        self.parent = parent
        self.config = config
        self.image_toolkit = image_toolkit

        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.screen = __screen
        self.height, self.width, self.left, self.top = (__screen_geo.height(),
                                                        __screen_geo.width(),
                                                        __screen_geo.left(),
                                                        __screen_geo.top())
        self.setGeometry((self.left + (self.width / 2 - 300)),
                         (self.top + (self.height / 2 - 175)),
                         600, 350)

        self.setFixedSize(600, 350)
        self.setWindowTitle("Chizuhoru")

        self.file_filter = 'png'
        self.typed_dir_hint_list = []

        _dirpath = os.path.dirname(os.path.realpath(__file__))
        self.hist_dir = os.path.join(_dirpath, '../.history')
        self.hist = os.path.join(self.hist_dir, 'index.json')
        self.mime_db = QtCore.QMimeDatabase()
        self.thread = None

        self.init_layout()

    def init_layout(self):
        self.setStyle(ProxyStyle())
        self.layout = QtWidgets.QVBoxLayout(self)
        self.tabs = TabWidget()

        self.tab_capture, self.tab_upload, self.tab_settings, self.tab_history = [
            QtWidgets.QWidget() for _ in range(4)
        ]

        self.tabs.addTab(self.tab_capture, "Capture")
        self.tabs.addTab(self.tab_upload, "Upload")
        self.tabs.addTab(self.tab_history, "History")
        self.tabs.addTab(self.tab_settings, "Settings")

        self.init_tab_capture()
        self.init_tab_upload()
        self.init_tab_history()
        self.init_tab_settings()

        self.tabs.setCurrentIndex(1)
        self.tabs.currentChanged.connect(self.capture_init)

        self.layout.addWidget(self.tabs)
        self.was_hidden = False

        # help window
        self.helpw = None

        self.setLayout(self.layout)

    @QtCore.pyqtSlot()
    def capture_init(self):
        if self.tabs.currentIndex() == 0:
            self.setWindowOpacity(0)
            self.setFixedSize(0, 0)
            self.resize(0, 0)
            self.move(self.height, self.width)
            self.setVisible(False)
            self.close()
            self.parent.init_capture_check()

    def init_tab_capture(self):
        pass

    def init_tab_upload(self):
        main_v = QtWidgets.QVBoxLayout()

        inner_q_up = QFrame()
        inner_q_down = QFrame()
        inner_q_up.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
        inner_q_down.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)

        inner_v_up = QVBoxLayout()

        in_hb_1 = QHBoxLayout()
        file_l = QLabel("File: ")

        self.ql_f = QComboBox()
        self.ql_f.setEditable(True)
        self.ql_f.setInsertPolicy(QComboBox.NoInsert)
        self.ql_f.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.ql_f.setMinimumWidth(340)
        self.ql_f.setDuplicatesEnabled(False)
        usr_dir = self.config.parse['config']['default_dir']
        if not usr_dir:
            usr_dir = os.environ['USER']
        self.update_file_box(usr_dir)
        self.ql_f.setCurrentIndex(-1)

        self.ql_f.currentTextChanged.connect(self.update_file_box_typing)

        self.ql_b = QPushButton("Browse")
        self.ql_b.clicked.connect(self.call_file_dialog)
        in_hb_1.addWidget(file_l)
        in_hb_1.addWidget(self.ql_f)
        in_hb_1.addWidget(self.ql_b)

        in_hb_2 = QHBoxLayout()
        in_hb_left = QVBoxLayout()
        in_hb_left_q = QFrame()
        in_hb_left_q.setStyleSheet('QCheckBox { margin: 2px; }')

        copy_h = QHBoxLayout()
        self.copy_check = QCheckBox()
        self.copy_check.setChecked(bool(self.config.parse['config']['upload']['clipboard_state']))
        self.copy_check.stateChanged.connect(self.update_upload_copyclip_state)
        copy_lab = LabelBoundToCheckbox(self.copy_check, "Copy link after upload")
        copy_h.addWidget(self.copy_check)
        copy_h.addWidget(copy_lab)
        copy_h.addStretch(1)

        name_h = QHBoxLayout()
        self.name_check = QCheckBox()
        self.name_check.setChecked(bool(self.config.parse['config']['upload']['random_fname_state']))
        self.name_check.stateChanged.connect(self.update_upload_randname_state)
        name_lab = LabelBoundToCheckbox(self.name_check, "Send random filename")
        name_h.addWidget(self.name_check)
        name_h.addWidget(name_lab)
        name_h.addStretch(1)

        in_hb_left.addStretch(1)
        in_hb_left.addItem(copy_h)
        in_hb_left.addItem(name_h)
        in_hb_left.addStretch(1)
        in_hb_left_q.setLayout(in_hb_left)

        tab_v = QtWidgets.QVBoxLayout()

        hb_left_tab = QTabWidget()
        tab_set = QtWidgets.QWidget()
        tab_v.addWidget(in_hb_left_q)
        tab_set.setLayout(tab_v)

        tab_up = QtWidgets.QWidget()
        in_hb_right = QVBoxLayout()

        self.up_btn = QPushButton("Upload")
        self.up_btn.clicked.connect(self.file_upload)

        up_hbox = QHBoxLayout()
        up_lab = QLabel("Service: ")
        self.up_comb = QComboBox()
        self.up_comb.addItem("Imgur")
        self.up_comb.addItem("catbox.moe")
        self.up_comb.addItem("uguu.se")
        last_item = self.config.parse['config']['upload']['last_service']
        if last_item == 'catbox.moe':
            self.up_comb.setCurrentIndex(1)
        elif last_item == 'uguu.se':
            self.up_comb.setCurrentIndex(2)
        self.up_comb.currentIndexChanged.connect(self.update_last_serv)
        up_hbox.addWidget(up_lab)
        up_hbox.addWidget(self.up_comb)
        in_hb_right.addItem(up_hbox)
        in_hb_right.addWidget(self.up_btn)

        tab_up.setLayout(in_hb_right)
        hb_left_tab.addTab(tab_up, "General")
        hb_left_tab.addTab(tab_set, "Settings")

        inner_q_res = QFrame()
        result_b = QVBoxLayout()
        self.result_f = QtWidgets.QTextEdit("")
        self.result_f.setFixedHeight(50)
        self.result_f.setReadOnly(True)
        self.result_f.setTextInteractionFlags(self.result_f.textInteractionFlags()
                                              | Qt.TextSelectableByKeyboard)
        if self.parent.last_url:
            self.result_f.setText(self.parent.last_url)
        result_btn = QPushButton("Copy")
        result_btn.clicked.connect(self.copy_to_clipboard)
        result_b.addStretch(1)
        result_b.addWidget(self.result_f)
        result_b.addWidget(result_btn)

        inner_q_res.setLayout(result_b)

        in_hb_2.addWidget(hb_left_tab, 50)
        in_hb_2.addWidget(inner_q_res, 50)
        inner_v_up.addItem(in_hb_1)
        inner_v_up.addItem(in_hb_2)

        inner_v_down = QVBoxLayout()
        self.out = QtWidgets.QTextEdit("Idle")
        self.out.setReadOnly(True)
        self.out.setTextInteractionFlags(self.out.textInteractionFlags()
                                         | Qt.TextSelectableByKeyboard)
        self.out.setStyleSheet(("QTextEdit { background-color: black; color: white; "
                                "border: 0; padding-left: 4px; padding-top: 4px;"
                                "font-family: monospace; }"))
        if self.parent.last_out:
            self.out.setText(self.parent.last_out)
        inner_v_down.addWidget(self.out)

        inner_q_up.setLayout(inner_v_up)
        inner_q_down.setLayout(inner_v_down)

        main_v.addWidget(inner_q_up, 30)
        main_v.addWidget(inner_q_down, 70)
        self.tab_upload.setLayout(main_v)

    def init_tab_history(self):
        main_wrap = QVBoxLayout()

        data = ''
        if not os.path.isdir(self.hist_dir):
            os.mkdir(self.hist_dir)

        if os.path.isfile(self.hist):
            with open(self.hist, 'r') as file:
                data = file.read()
        else:
            with open(self.hist, 'w'):
                pass

        self.history_list = QtWidgets.QListWidget(self)
        self.history_list.setSortingEnabled(True)
        if not data:
            main_wrap.addWidget(self.history_list)
            self.tab_history.setLayout(main_wrap)
            return

        data = json.loads(data)

        for item in data.keys():
            date = item
            type_ = data[item]['Type']
            path = data[item]['Path']
            url = data[item]['URL']
            icon = data[item]['Thumb']

            hitem = HistoryItem(self)

            if 'del_hash' in data[item]:
                hitem.del_hash = data[item]['del_hash']
            hitem.date.setText(date)
            hitem.type.setText(type_)
            if url:
                hitem.info.setText(url)
                hitem.set_info_url()
            else:
                hitem.info.setText(path)
                hitem.set_info_path()
            hitem.set_icon(icon)

            widget = QtWidgets.QListWidgetItem()

            widget.setSizeHint(hitem.sizeHint())

            self.history_list.insertItem(0, widget)
            self.history_list.setItemWidget(widget, hitem)

        main_wrap.addWidget(self.history_list)
        # self.history_list.sortItems(Qt.DescendingOrder)
        self.tab_history.setLayout(main_wrap)

    def init_tab_settings(self):
        main_wrap = QVBoxLayout()

        dir_lab = QLabel("Save directory: ")
        up_dir = QHBoxLayout()
        self.dirline = QLineEdit()
        self.dirline.setText(self.config.parse['config']['default_dir'])
        self.dirline.setReadOnly(True)
        self.dirbtn = QPushButton("Browse")
        self.dirbtn.clicked.connect(self.browse_directories)

        up_dir.addWidget(dir_lab)
        up_dir.addWidget(self.dirline)
        up_dir.addWidget(self.dirbtn)

        general_frame = QFrame()
        general_frame.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)
        general_frame.setStyleSheet('QCheckBox { margin: 2px; }')

        general_wrap = QVBoxLayout()

        delay_wrap = QHBoxLayout()
        self.del_check = QtWidgets.QDoubleSpinBox()
        self.del_check.setSingleStep(0.05)
        self.del_check.setDecimals(2)
        del_lab = QLabel("Default delay (seconds): ")
        self.del_check.setValue(self.config.parse['config']['default_delay'])
        self.del_check.valueChanged.connect(self.update_delay)
        delay_wrap.addWidget(del_lab)
        delay_wrap.addWidget(self.del_check)

        name_wrap = QHBoxLayout()
        fmt_lab = QLabel("Name pattern: ")
        self.name_pattern = QLineEdit()
        self.name_pattern_help = QPushButton('?')
        self.name_pattern_help.setFixedWidth(30)
        self.name_pattern_help.clicked.connect(self.show_name_pattern_help_dialog)
        self.name_pattern.setText(self.config.parse['config']['filename_format'])
        self.name_pattern.textChanged.connect(self.update_file_format)
        name_wrap.addWidget(fmt_lab)
        name_wrap.addWidget(self.name_pattern)
        name_wrap.addWidget(self.name_pattern_help)

        icon_wrap = QHBoxLayout()
        ico_lab = QLabel("Tray icon style: ")
        self.ico_comb = QComboBox()
        self.ico_comb.addItem("Colored")
        self.ico_comb.addItem("White")
        self.ico_comb.addItem("Black")
        curr_ico = self.config.parse['config']['icon']
        if curr_ico == 'white':
            self.ico_comb.setCurrentIndex(1)
        elif curr_ico == 'black':
            self.ico_comb.setCurrentIndex(2)
        self.ico_comb.currentIndexChanged.connect(self.update_ico)
        icon_wrap.addWidget(ico_lab)
        icon_wrap.addWidget(self.ico_comb)

        general_wrap.addItem(up_dir)
        general_wrap.addItem(name_wrap)
        general_wrap.addItem(delay_wrap)
        general_wrap.addItem(icon_wrap)
        general_frame.setLayout(general_wrap)

        canvas_frame = QFrame()
        canvas_frame.setStyleSheet('QCheckBox { margin: 2px; }')
        canvas_wrap = QVBoxLayout()
        canvas_frame.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)

        upload_wrap = QHBoxLayout()
        up_lab = QLabel("Upload button service: ")
        box = ['Imgur', 'catbox.moe', 'uguu.se', 'Disabled']
        self.set_up_comb = QComboBox()
        for item in box:
            self.set_up_comb.addItem(item)

        curr_serv = self.config.parse['config']['canvas']['upload_service']
        for count, item in enumerate(box):
            if curr_serv == item:
                self.set_up_comb.setCurrentIndex(count)
                break

        self.set_up_comb.currentIndexChanged.connect(self.update_canvas_upload)
        upload_wrap.addWidget(up_lab)
        upload_wrap.addWidget(self.set_up_comb)

        save_btn_wrap = QHBoxLayout()
        save_lab = QLabel("Save button: ")
        self.set_save = QComboBox()
        self.set_save.addItem("Saves to default directory")
        self.set_save.addItem("Invokes save dialog")
        if self.config.parse['config']['canvas']['save_action'] == 'dialog':
            self.set_save.setCurrentIndex(1)
        self.set_save.currentIndexChanged.connect(self.update_canvas_save)
        save_btn_wrap.addWidget(save_lab)
        save_btn_wrap.addWidget(self.set_save)

        copy_img_wrap = QHBoxLayout()
        self.img_check = QCheckBox()
        self.img_check.setChecked(bool(self.config.parse['config']['canvas']['img_clip']))
        self.img_check.stateChanged.connect(self.update_img_clip)
        img_clip_lab = LabelBoundToCheckbox(self.img_check, "Copy image to clipboard on save")
        copy_img_wrap.addWidget(self.img_check)
        copy_img_wrap.addWidget(img_clip_lab)
        copy_img_wrap.addStretch(1)

        magn_wrap = QHBoxLayout()
        self.magn_defaults = QCheckBox()
        self.magn_defaults.setChecked(bool(self.config.parse['config']['canvas']['magnifier']))
        self.magn_defaults.stateChanged.connect(self.update_magnifier_state)
        magn_lab = LabelBoundToCheckbox(self.magn_defaults, "Show magnifier on startup")
        magn_wrap.addWidget(self.magn_defaults)
        magn_wrap.addWidget(magn_lab)
        magn_wrap.addStretch(1)

        canvas_wrap.addItem(upload_wrap)
        canvas_wrap.addItem(save_btn_wrap)
        canvas_wrap.addItem(copy_img_wrap)
        canvas_wrap.addItem(magn_wrap)
        canvas_frame.setLayout(canvas_wrap)

        history_frame = QFrame()
        history_wrap = QHBoxLayout()
        clear_btn = QPushButton("Clear history")
        clear_btn.clicked.connect(self.clear_history_list)
        history_wrap.addWidget(clear_btn)
        history_frame.setLayout(history_wrap)
        history_frame.setStyleSheet('QCheckBox { margin: 2px; }')
        history_frame.setFrameStyle(QFrame().StyledPanel | QFrame().Sunken)

        bot_wrap = QVBoxLayout()
        lab_0 = QLabel(" General")
        lab_1 = QLabel(" Paint window")
        lab_2 = QLabel(" History")
        lab_0.setFixedHeight(30)
        lab_1.setFixedHeight(30)
        lab_2.setFixedHeight(30)
        bot_wrap.addWidget(lab_0)
        bot_wrap.addWidget(general_frame)
        bot_wrap.addStretch(1)
        bot_wrap.addWidget(lab_1)
        bot_wrap.addWidget(canvas_frame)
        bot_wrap.addStretch(1)
        bot_wrap.addWidget(lab_2)
        bot_wrap.addWidget(history_frame)

        main_wrap.addItem(bot_wrap)

        scroll_frame = QFrame()
        scroll_frame.setLayout(main_wrap)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_frame)

        scroll_wrap = QVBoxLayout()
        scroll_wrap.addWidget(scroll)
        self.tab_settings.setLayout(scroll_wrap)

    def closeEvent(self, event):
        self.parent.last_out = self.out.toPlainText()
        self.parent.last_url = self.result_f.toPlainText()
        if self.thread and self.thread.isRunning():
            self.was_hidden = True
            self.hide()
        else:
            self.was_hidden = False
            self.close()

    def show_name_pattern_help_dialog(self):
        if not self.helpw:
            self.helpw = Help(self)
        self.helpw.show()

    def file_upload(self):
        if self.thread and self.thread.isRunning():
            exit(1)

        get_file = self.ql_f.currentText().strip()
        if get_file.startswith('file://'):
            get_file = get_file.replace('file://', '')
        if not os.path.isfile(get_file):
            if get_file:
                self.out.setText(f"File not found: {get_file}")
            return

        self.out.clear()
        self.result_f.clear()

        args = [self.config, get_file, self.name_check.isChecked()]

        if self.up_comb.currentText() == 'Imgur':
            self.worker = Worker(self.image_toolkit.imgur_upload, args, 'Imgur')
        elif self.up_comb.currentText() == 'catbox.moe':
            self.worker = Worker(self.image_toolkit.catbox_upload, args, 'catbox.moe')
        else:
            self.worker = Worker(self.image_toolkit.uguu_upload, args, 'uguu.se')

        self.thread = QtCore.QThread()
        self.worker.console.connect(self.set_console_text)
        self.worker.finished.connect(self.get_ret_val)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.up_btn.setStyleSheet('background-color: #851313;')
        self.up_btn.clearFocus()
        self.up_btn.setText('Terminate')

    def set_console_text(self, val):
        if len(val) > 1:
            self.out.clear()
        val = val[0]
        text = self.out.toPlainText()
        time = datetime.now()
        if len(val) == 1:
            text += '\n'
        text += f'[{time.hour:02d}:{time.minute:02d}:{time.second:02d}] {val}'
        self.out.setText(text)
        _cur = self.out.textCursor()
        _cur.beginEditBlock()
        _cur.movePosition(QtGui.QTextCursor().End)
        _cur.endEditBlock()
        self.out.verticalScrollBar().setSliderPosition(self.out.verticalScrollBar().maximum())

    def get_ret_val(self, response):
        if response:
            self.result_f.setText(response[1])
            filename = response[0]
            del_hash = response[2]
            response = response[1]
            type_ = self.up_comb.currentText()
            self.push_to_history(filename, response, type_, del_hash)
            if self.copy_check.isChecked():
                self.copy_to_clipboard()
        self.thread.quit()
        self.up_btn.setText('Upload')
        self.up_btn.setStyleSheet('')

    def push_to_history(self, get_file, response, type_, delete_hash=None):
        curr_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        filetype = self.mime_db.mimeTypeForFile(get_file)
        if 'image' not in filetype.iconName():
            thumb = QtGui.QIcon.fromTheme(filetype.iconName())
            thumb = thumb.pixmap(thumb.actualSize(QtCore.QSize(100, 100)))
        else:
            thumb = QtGui.QImage(get_file)
            thumb = thumb.scaled(100, 100, Qt.KeepAspectRatioByExpanding,
                                 Qt.SmoothTransformation)
            if thumb.width() > 100:
                rect = QtCore.QRect(
                    (thumb.width() - 100) // 2,
                    (thumb.height() - 100) // 2,
                    100,
                    100,
                )
                thumb = thumb.copy(rect)

        data = {}
        if not os.path.isfile(self.hist):
            with open(self.hist, 'w'):
                pass
        else:
            with open(self.hist, 'r') as file:
                fdata = file.read()
                if fdata:
                    data = json.loads(fdata)

        if curr_date in data:
            from time import time_ns
            curr_date += ('-' + str(time_ns()))

        thumb_name = os.path.join(self.hist_dir, 'thumb_' + curr_date + '.png')
        thumb.save(thumb_name)

        data[curr_date] = {
            "Type": "Upload — " + type_,
            "URL": response,
            "Path": get_file,
            "Thumb": thumb_name
        }
        if delete_hash:
            data[curr_date]['del_hash'] = delete_hash

        with open(self.hist, 'w') as file:
            file.write(str(json.dumps(data)))

        item = HistoryItem(self)
        if delete_hash:
            item.del_hash = delete_hash
        item.date.setText(curr_date)
        item.type.setText("Upload — " + type_)
        item.info.setText(response)
        item.set_info_url()

        item.set_icon(thumb_name)

        widget = QtWidgets.QListWidgetItem()

        widget.setSizeHint(item.sizeHint())

        self.history_list.insertItem(0, widget)
        self.history_list.setItemWidget(widget, item)

    def remove_from_hist(self, item):
        with open(self.hist, 'r') as file:
            fdata = file.read()
            if not fdata:
                return
        fdata = json.loads(fdata)

        thumb = fdata[item.date.text()]['Thumb']
        os.remove(thumb)
        del fdata[item.date.text()]

        if self.history_list.count() > 1:
            for i in range(0, self.history_list.count()):
                h_item = self.history_list.item(i)
                w_item = self.history_list.itemWidget(h_item)
                if w_item == item:
                    self.history_list.takeItem(i)
        else:
            self.history_list.takeItem(0)
        with open(self.hist, 'w') as file:
            file.write(str(json.dumps(fdata)))

    def clear_history_list(self):
        self.history_list.clear()
        for file in os.listdir(self.hist_dir):
            if file.startswith('thumb_') and file.endswith('.png'):
                os.remove(os.path.join(self.hist_dir, file))
        with open(self.hist, 'w'):
            pass

    def browse_directories(self):
        filedialog = QtWidgets.QFileDialog()
        filedialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        filedialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        fd = filedialog.getExistingDirectory(self, 'Select directory')
        dirpath = fd if fd else None
        if dirpath and os.path.isdir(dirpath):
            self.dirline.setText(dirpath)
            self.config.change_config('default_dir', value=dirpath)

    def call_file_dialog(self):
        qdialog_filter = ('All files (*.*)'
                          ';;Pictures (*.png *.jpg *.jpeg *.bmp *.gif *.ico *.tiff)'
                          ';;Videos (*.mp4 *.webm *.mkv *.mov)'
                          ';;Text (*.txt)'
                          )
        if self.up_comb.currentData(self.up_comb.currentIndex()) == 'Imgur':
            qdialog_filter = 'Pictures (*.png *.jpg *.jpeg *.bmp *.gif *.ico *.tiff)'
        fd = QtWidgets.QFileDialog().getOpenFileName(self, 'Select file',
                                                     '', qdialog_filter)

        filepath = fd[0] if fd[0] else None
        if filepath:
            self.file_filter = fd[0].split('.')[1]
            last_dir = os.path.split(filepath)[0]
            self.ql_f.insertItem(0, filepath)
            self.ql_f.setCurrentIndex(0)
            self.update_file_box(last_dir)

    def update_file_box(self, usr_dir, signal='keep'):
        if signal == 'reset':
            # disconnect comboBox to avoid recursion
            self.ql_f.currentTextChanged.disconnect()
        else:
            curr_item = None
            if self.ql_f.currentText().strip():
                curr_item = self.ql_f.currentText().strip()
            self.ql_f.clear()
            if curr_item and os.path.isfile(curr_item):
                self.ql_f.addItem(curr_item)
                self.ql_f.setCurrentIndex(0)
        if os.path.isdir(usr_dir):
            files = [f for f in os.listdir(usr_dir) if os.path.isfile(os.path.join(usr_dir, f))]
            for f in files:
                if not f.startswith('.'):
                    if self.file_filter and f.endswith(self.file_filter):
                        check = self.ql_f.findText(os.path.join(usr_dir, f))
                        if check == -1:
                            self.ql_f.addItem(os.path.join(usr_dir, f))
                    elif not self.file_filter:
                        check = self.ql_f.findText(os.path.join(usr_dir, f))
                        if check == -1:
                            self.ql_f.addItem(os.path.join(usr_dir, f))
        if signal == 'reset':
            self.ql_f.currentTextChanged.connect(self.update_file_box_typing)

    def update_file_box_typing(self):
        filepath = self.ql_f.currentText().strip()
        if filepath:
            filedir = os.path.split(filepath)[0]
            if filedir in self.typed_dir_hint_list:
                return
            self.typed_dir_hint_list.append(filedir)
            if os.path.isdir(filedir):
                self.update_file_box(filedir, signal='reset')

    def copy_to_clipboard(self):
        value = self.result_f.toPlainText()
        if value.strip():
            self.app.clipboard().setText(value)

    def update_upload_copyclip_state(self):
        self.config.change_config('upload', 'clipboard_state',
                                  int(self.copy_check.isChecked()))

    def update_upload_randname_state(self):
        self.config.change_config('upload', 'random_fname_state',
                                  int(self.name_check.isChecked()))

    def update_last_serv(self):
        self.config.change_config('upload', 'last_service', self.up_comb.currentText())

    def update_delay(self):
        self.config.change_config('default_delay', value=self.del_check.value())

    def update_file_format(self):
        new_format = self.name_pattern.text()
        self.config.change_config('filename_format', value=new_format)

    def update_canvas_upload(self):
        new = self.set_up_comb.currentText()
        self.config.change_config('canvas', 'upload_service', new)

    def update_canvas_save(self):
        new = self.set_save.currentText()
        if 'dialog' in new:
            new = 'dialog'
        else:
            new = 'dir'
        self.config.change_config('canvas', 'save_action', new)

    def update_img_clip(self):
        self.config.change_config('canvas', 'img_clip',
                                  int(self.img_check.isChecked()))

    def update_magnifier_state(self):
        self.config.change_config('canvas', 'magnifier',
                                  int(self.magn_defaults.isChecked()))

    def update_ico(self):
        new_ico = self.ico_comb.currentText()
        self.config.change_config('icon', value=new_ico.lower())
