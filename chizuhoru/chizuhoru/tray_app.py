from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore, QtNetwork
from time import sleep
import os
import gc

from screen_window import ScreenWindow
from image_toolkit import ImageToolkit
from main_window import MainWindow

import sys
import signal
import socket


class SignalWakeupHandler(QtNetwork.QAbstractSocket):

    def __init__(self, parent, parent_emit):
        """
        Catch up SIGCONT to invoke capture window instead.
        Without custom handlers SIGCONT is ignored anyway,
        so we may as well take advantage of it.
        https://stackoverflow.com/a/37229299
        """
        super().__init__(QtNetwork.QAbstractSocket.UdpSocket, parent)
        self.parent_emit = parent_emit
        self.old_fd = None
        self.wsock, self.rsock = socket.socketpair(type=socket.SOCK_DGRAM)
        self.setSocketDescriptor(self.rsock.fileno())
        self.wsock.setblocking(False)
        self.old_fd = signal.set_wakeup_fd(self.wsock.fileno())
        self.readyRead.connect(lambda: None)
        # Second handler does the real handling
        self.readyRead.connect(self._read_signal)

    def __del__(self):
        if self.old_fd is not None and signal and signal.set_wakeup_fd:
            signal.set_wakeup_fd(self.old_fd)

    def _read_signal(self):
        data = self.readData(1)
        self.signalReceived.emit(data[0])

    signalReceived = QtCore.pyqtSignal(int)


class OnclickOverlay(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        __current_screen = QtWidgets.QApplication.desktop().cursor().pos()
        __screen = QtWidgets.QDesktopWidget().screenNumber(__current_screen)
        __screen_geo = QtWidgets.QApplication.desktop().screenGeometry(__screen)

        self.setGeometry(0, 0, __screen_geo.width(), __screen_geo.height())
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.X11BypassWindowManagerHint)
        self.move(__screen_geo.left(), __screen_geo.top())
        self.setWindowOpacity(0)

    def mousePressEvent(self, event):
        self.parent.init_capture_check(False, 0)
        self.close()


class Tray(QtWidgets.QWidget):
    trigger = QtCore.pyqtSignal()
    
    def __init__(self, app, app_config, fallback):
        super().__init__()
        self.app = app
        self.config = app_config
        self.fallback = fallback
        self.window = None
        self.main_window = None
        self.onclick_overlay = OnclickOverlay(self)

        SignalWakeupHandler(self.app, self)
        
        signal.signal(signal.SIGCONT, lambda x, _: self.init_capture_check(False, 0))

        self.chz_ico = QtGui.QIcon(os.path.join(
                            sys.path[0], 'img', 'ico_colored.png')
                        )
        _set_ico = self.config.parse['config']['icon']
        self.chz_ico_tray = QtGui.QIcon(os.path.join(
                                sys.path[0], 'img', f'ico_{_set_ico}.png')
                            )
        self.img_toolkit = ImageToolkit(self.app, self.config)

        self.last_out = ''
        self.last_url = ''

        self.setGeometry(0, 0, 0, 0)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.X11BypassWindowManagerHint)
        self.trigger.connect(self.init_capture)
        self.init_tray()
        self.init_capture()
        # self.init_screen()

    def init_tray(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.chz_ico_tray)
        self.app.setApplicationName('Chizuhoru')

        self.tray_icon.activated.connect(self.tray_clicked)
        capture_action = QtWidgets.QAction("Capture", self)
        show_action = QtWidgets.QAction("Show", self)
        quit_action = QtWidgets.QAction("Exit", self)

        capture_action.triggered.connect(self.init_capture_check)
        show_action.triggered.connect(self.init_main_check)
        quit_action.triggered.connect(self.close)

        tray_menu = QtWidgets.QMenu()
        capture_menu = QtWidgets.QMenu("Delay", tray_menu)
        _5_sec = QtWidgets.QAction("5 sec.", capture_menu)
        _5_sec.triggered.connect(lambda _: self.init_capture_check(delay=5))
        _10_sec = QtWidgets.QAction("10 sec.", capture_menu)
        _10_sec.triggered.connect(lambda _: self.init_capture_check(delay=10))
        _15_sec = QtWidgets.QAction("15 sec.", capture_menu)
        _15_sec.triggered.connect(lambda _: self.init_capture_check(delay=15))
        onclick = QtWidgets.QAction("On click", capture_menu)
        onclick.triggered.connect(self.invoke_onclick)
        capture_menu.addAction(_5_sec)
        capture_menu.addAction(_10_sec)
        capture_menu.addAction(_15_sec)
        capture_menu.addAction(onclick)

        tray_menu.addAction(capture_action)
        tray_menu.addMenu(capture_menu)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        exit(0)

    def invoke_onclick(self):
        self.onclick_overlay.show()

    def tray_clicked(self, reason):
        if reason == 3:
            self.init_capture_check(default_delay=False)

    @QtCore.pyqtSlot()
    def init_capture_check(self, default_delay=True, delay=0):
        gc.collect()
        try:
            if self.window and self.window.isVisible():
                print("Dialog already exists")
            elif self.window and self.window.thread:
                if self.window.thread.isRunning():
                    pass
            else:
                if delay:
                    sleep(delay)
                elif default_delay:
                    sleep(self.config.parse["config"]["default_delay"])
                self.init_capture()
        except RuntimeError:
            # C++ window destroyed
            if delay:
                sleep(delay)
            elif default_delay:
                sleep(self.config.parse["config"]["default_delay"])
            self.init_capture()

    def init_main_check(self):
        gc.collect()
        if self.main_window and self.main_window.isVisible():
            print("Dialog already exists")
        elif self.main_window and self.main_window.was_hidden:
            self.main_window.show()
        else:
            self.init_screen()

    def init_capture(self):
        try:
            del self.window
        except AttributeError:
            pass
        self.window = ScreenWindow(self, self.app, self.config,
                                   self.img_toolkit, self.fallback)
        self.window.show()
        self.window.activateWindow()
        self.window.raise_()

    def init_screen(self):
        try:
            del self.main_window
        except AttributeError:
            pass
        self.main_window = MainWindow(self, self.app, self.config, self.img_toolkit)
        self.main_window.setWindowIcon(self.chz_ico)
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()
