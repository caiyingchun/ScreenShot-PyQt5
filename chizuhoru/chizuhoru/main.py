#!/usr/bin/python3
from argparse import ArgumentParser

from screenshot import ScreenshotCLI
from config import Config

from datetime import datetime
from os.path import join

from PyQt5 import QtWidgets
from PyQt5 import Qt, QtGui
import setproctitle
import sys

if __name__ == '__main__':
    setproctitle.setproctitle('chizuhoru')

    ap = ArgumentParser()
    ap.add_argument("-s", "--screenshot", required=False, action='store_true',
                    help=("Take a screenshot, save to default directory. "
                          "Use -d to provide custom directory for saving."))
    ap.add_argument("-dir", "--directory", required=False,
                    help="Save screenshot to path provided.")
    ap.add_argument("-dis", "--display", required=False,
                    help=("Select a display to grab. "
                          "[-1, 0, 1, 2, n] Default: -1 (all displays)"))
    args = vars(ap.parse_args())

    app_config = Config()

    display = -1 if not args["display"] else int(args["display"])
    if args["directory"]:
        app_config.change_config("default_dir", value=f"{args['directory']}",
                                 save_changes=False)
    
    app = QtWidgets.QApplication(sys.argv)
    styles = QtWidgets.QStyleFactory.keys()
    fallback = False
    # Qt5CTProxyStyle
    if not app.style().metaObject().className() == 'Breeze::Style':
        # If breeze is not available, use Fusion as fallback
        app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        _app_palette = Qt.QPalette()
        _app_palette.setColor(Qt.QPalette.Window, Qt.QColor(53,53,53))
        _app_palette.setColor(Qt.QPalette.WindowText, Qt.QColor('white'))
        _app_palette.setColor(Qt.QPalette.Base, Qt.QColor(25,25,25))
        _app_palette.setColor(Qt.QPalette.AlternateBase, Qt.QColor(53,53,53))
        _app_palette.setColor(Qt.QPalette.ToolTipBase, Qt.QColor('white'))
        _app_palette.setColor(Qt.QPalette.ToolTipText, Qt.QColor('white'))
        _app_palette.setColor(Qt.QPalette.Text, Qt.QColor('white'))
        _app_palette.setColor(Qt.QPalette.Button, Qt.QColor(53,53,53))
        _app_palette.setColor(Qt.QPalette.ButtonText, Qt.QColor('white'))
        _app_palette.setColor(Qt.QPalette.BrightText, Qt.QColor('red'))
        _app_palette.setColor(Qt.QPalette.Link, Qt.QColor(42, 130, 218))
        _font = QtGui.QFont()
        _font.setPointSize(10)
        app.setFont(_font)

        _app_palette.setColor(Qt.QPalette.Highlight, Qt.QColor(42, 130, 218))
        app.setPalette(_app_palette)
        fallback = True

    screen_unit = ScreenshotCLI()

    if args["screenshot"]:
        save_dir = app_config.parse['config']['default_dir']
        filename_format = app_config.parse['config']['filename_format']
        filename = "{}.png".format(datetime.now().strftime(filename_format))
        filepath = join(save_dir, filename)

        image = screen_unit.shot(mon=display)
        screen_unit.save(image, filepath)
        sys.exit()
    else:
        from chizuhoru import ChzInit
        ChzInit(app, app_config, fallback)
