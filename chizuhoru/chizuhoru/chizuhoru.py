from PyQt5 import QtWidgets
from tray_app import Tray

import sys
import os

class ChzInit():

    def __init__(self, app, config, fallback=False):
        self.config = config
        self.app = app
        self.check_pid()
        self.init_app(fallback)
    
    def check_pid(self):
        pid = str(os.getpid())
        self.pidfile = "/tmp/chizuhoru.pid"

        try:
            data = ''
            if os.path.isfile(self.pidfile):
                try:
                    with open(self.pidfile, 'r') as testcheck:
                        data = int(testcheck.read())
                        os.kill(data, 0)
                except OSError:
                    os.remove(self.pidfile)
                else:
                    print(f"Another instance is running: {data}")
                    # pass signal to the running instance
                    os.kill(data, 18)
                    sys.exit(0)
            with open(self.pidfile, 'w') as file:
                file.write(pid)
        except PermissionError as e:
            print(f"Error writing to '{self.pidfile}': {e}")
            sys.exit(1)

    def init_app(self, fallback):
        tray_inst = Tray(self.app, self.config, fallback)
        tray_inst.show()

        self.app.aboutToQuit.connect(self.app.deleteLater)
        sys.exit(self.app.exec_())

        os.unlink(self.pidfile)
