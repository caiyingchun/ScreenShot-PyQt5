# Thanks to: avazevfx (https://github.com/avazevfx/pyqt-colorpicker)
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtCore
import colorsys
import sys


def hsv_to_rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v


class RingSelector(QtWidgets.QLabel):
    def __init__(self, parent):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('black'), 1))
        painter.drawRect(1, 1, 8, 8)
        painter.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        painter.drawRect(2, 2, 6, 6)
        painter.end()


class ColorButton(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('white'), 1))
        painter.drawRect(1, 1, self.width()-3, self.height()-3)
        painter.setPen(QtGui.QPen(QtGui.QColor('black'), 1))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        painter.end()


class ForegroundColor:
    def __init__(self, color, hsv, sel):
        self.color = color
        self.hsv = hsv
        self.sel = sel

    def rgba(self):
        return 'rgba({}, {}, {}, {})'.format(*self.color)


class BackgroundColor:
    def __init__(self, color, hsv, sel):
        self.color = color
        self.hsv = hsv
        self.sel = sel

    def rgba(self):
        return 'rgba({}, {}, {}, {})'.format(*self.color)


class PaletteButton(QtWidgets.QLabel):
    def __init__(self, parent, color):
        super().__init__()
        self.parent = parent
        self.color = color

    def mousePressEvent(self, event):
        self.parent.update_hex_value(self.color)


class ColorPicker(QtWidgets.QWidget):

    def __init__(self, config):
        super(ColorPicker, self).__init__()
        self.size = 240
        self.box_size = 140
        self.config = config

        self.inverse = [abs(i) for i in range(-100, 1)]

        fg_c = self.config.parse['config']['canvas']['pen_color']
        fg_h = self.config.parse['config']['canvas']['pen_hsv']
        fg_s = self.config.parse['config']['canvas']['pen_sel']

        bg_c = self.config.parse['config']['canvas']['brush_color']
        bg_h = self.config.parse['config']['canvas']['brush_hsv']
        bg_s = self.config.parse['config']['canvas']['brush_sel']

        self.fg = ForegroundColor([int(i) for i in fg_c.split()],
                                          [int(i) for i in fg_h.split()],
                                          [int(i) for i in fg_s.split()])
        self.bg = BackgroundColor([int(i) for i in bg_c.split()],
                                  [int(i) for i in bg_h.split()],
                                  [int(i) for i in bg_s.split()])

        self.init_layout()
        self.releaseKeyboard()
        self.activateWindow()

    def init_layout(self):
        self.resize(self.size, self.size)

        widget_layout_main = QtWidgets.QVBoxLayout(self)
        widget_layout_main.setSpacing(0)
        widget_layout_main.setContentsMargins(0, 0, 0, 0)

        # layout_main -> content_frame
        content_frame = QtWidgets.QFrame()
        content_frame.setStyleSheet('margin: 0; padding: 0;')
        content_frame.setContentsMargins(0, 0, 0, 0)

        # content_frame -> gradient_wrap
        gradient_wrap = QtWidgets.QHBoxLayout()

        # gradient_wrap -> gradient_box
        self.gradient_box = QtWidgets.QLabel()
        self.gradient_box.setFixedHeight(self.box_size)
        self.gradient_box.setFixedWidth(self.box_size)
        self.gradient_box.setStyleSheet("""
            background-color: qlineargradient(x1:1, x2:0,
                                              stop:0 hsl(0%,100%,50%),
                                              stop:1 rgba(255, 255, 255, 255));
            margin: 0;
            padding: 0;
        """)

        gradient_box_child_overlay = QtWidgets.QVBoxLayout()
        gradient_box_child_overlay.setContentsMargins(0, 0, 0, 0)
        gradient_box_child_overlay.setSpacing(0)
        shades_overlay = QtWidgets.QFrame()
        shades_overlay.setStyleSheet("""
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0,
                                              y2:1, stop:0 rgba(0, 0, 0, 0),
                                              stop:1 rgba(0, 0, 0, 255));
            margin: 0;
            padding: 0;
        """)

        self.selector = RingSelector(shades_overlay)
        self.selector.setGeometry(QtCore.QRect(self.box_size-10, 0, 10, 10))
        self.selector.setStyleSheet("background-color: none; border: 0;")

        gradient_box_child_overlay.addWidget(shades_overlay)
        self.gradient_box.setLayout(gradient_box_child_overlay)

        self.hue_slider = QtWidgets.QSlider()

        self.hue_slider.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.hue_slider.setFixedHeight(self.box_size)
        self.hue_slider.setStyleSheet("""
            QSlider{
                margin-left: 4px;
                margin-right: 4px;
                border-radius: 6px;
                padding-top: 4px;
                padding-bottom: 4px;
            }
            QSlider:groove{
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-radius: 8px;
                width: 12px;
                background-color: qlineargradient(
                                        spread:pad,
                                        x1:0, y1:1,
                                        x2:0, y2:0,
                                        stop:0 rgba(255, 0, 0, 255),
                                        stop:0.166 rgba(255, 255, 0, 255),
                                        stop:0.333 rgba(0, 255, 0, 255),
                                        stop:0.5 rgba(0, 255, 255, 255),
                                        stop:0.666 rgba(0, 0, 255, 255),
                                        stop:0.833 rgba(255, 0, 255, 255),
                                        stop:1 rgba(255, 0, 0, 255)
                                    );
            }
            QSlider:handle{
                height: 6px;
                margin-left: -3px;
                margin-right: -3px;
                margin-top: -1px;
                margin-bottom: -1px;
                border: 1px solid rgba(0, 0, 0, 0.4);
                background-color: #aaaaaa;
            }
        """)
        self.hue_slider.setMaximum(100)
        self.hue_slider.setSingleStep(3)
        self.hue_slider.setPageStep(3)
        self.hue_slider.setOrientation(QtCore.Qt.Vertical)
        self.hue_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.hue_slider.setTickInterval(0)

        self.opacity_slider = QtWidgets.QSlider()
        self.opacity_slider.setFixedHeight(self.box_size)
        self.opacity_slider.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.opacity_slider.setStyleSheet("""
            QSlider{
                margin-left: 4px;
                margin-right: 4px;
                border-radius: 6px;
                padding-top: 4px;
                padding-bottom: 4px;
            }
            QSlider:groove{
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-radius: 8px;
                width: 12px;
                background-color: qlineargradient(
                                        spread:pad,
                                        x1:0, y1:1,
                                        x2:0, y2:0,
                                        stop:0 rgba(255, 0, 0, 0),
                                        stop:0.5 rgba(255, 0, 0, 45)
                                        stop:1 rgba(255, 0, 0, 255)
                                    );
            }
            QSlider:handle{
                height: 6px;
                margin-left: -3px;
                margin-right: -3px;
                margin-top: -1px;
                margin-bottom: -1px;
                border: 2px solid rgba(0, 0, 0, 0.4);
                background-color: #aaaaaa;
            }
        """)
        self.opacity_slider.setMaximum(255)
        self.opacity_slider.setSingleStep(6)
        self.opacity_slider.setPageStep(12)
        self.opacity_slider.setOrientation(QtCore.Qt.Vertical)
        self.opacity_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.opacity_slider.setTickInterval(0)
        self.opacity_slider.setValue(self.fg.color[-1])

        gradient_wrap.addWidget(self.gradient_box)
        gradient_wrap.addWidget(self.hue_slider)
        gradient_wrap.addWidget(self.opacity_slider)

        colors_wrap = QtWidgets.QHBoxLayout()
        colors_wrap.setSpacing(10)
        colors_wrap.setAlignment(Qt.AlignLeft)
        colors_wrap.setContentsMargins(20, 0, 20, 0)

        main_color_widget = QtWidgets.QWidget()
        main_color_widget.setFixedSize(64, 45)

        bg_btn_underlayer = ColorButton(main_color_widget)
        bg_btn_underlayer.setStyleSheet("""
            background-image: url(%s/img/ts.png); 
        """ % sys.path[0])
        bg_btn_underlayer.setFixedSize(30, 30)
        bg_btn_underlayer.move(0, 0)
        self.bg_btn = ColorButton(main_color_widget)
        self.bg_btn.setStyleSheet("""
            background-color: %s;
        """ % self.bg.rgba())
        self.bg_btn.setFixedSize(30, 30)
        self.bg_btn.move(0, 0)

        fg_btn_underlayer = ColorButton(main_color_widget)
        fg_btn_underlayer.setStyleSheet("""
            background-image: url(%s/img/ts.png); 
        """ % sys.path[0])
        fg_btn_underlayer.setFixedSize(30, 30)
        fg_btn_underlayer.move(15, 15)
        self.fg_btn = ColorButton(main_color_widget)
        self.fg_btn.setStyleSheet("""
            background-color: %s;
        """ % self.fg.rgba())
        self.fg_btn.setFixedSize(30, 30)
        self.fg_btn.move(15, 15)

        self.switch_btn = QtWidgets.QLabel(main_color_widget)
        self.switch_btn.setFixedSize(25, 30)
        self.switch_btn.setStyleSheet("""
            background-color: transparent;
            background-image: url(%s/img/swap.png);
        """ % sys.path[0])
        self.switch_btn.move(35, 0)
        self.switch_btn.lower()
        self.switch_btn.mousePressEvent = self.color_swap

        palette_vb = QtWidgets.QVBoxLayout()
        palette_vb.setContentsMargins(0, 0, 0, 0)
        palette_vb.setAlignment(Qt.AlignCenter)

        colorgrid_frame = QtWidgets.QFrame()

        colorgrid = QtWidgets.QHBoxLayout()
        colorgrid.setSpacing(0)
        colorgrid.setContentsMargins(0, 0, 0, 0)
        colorgrid.setAlignment(Qt.AlignCenter)

        pal = self.config.parse['config']['palette']
        pal = list(pal.values())
        for i in range(7):
            obj = PaletteButton(self, pal[i])
            obj.setStyleSheet('background-color: %s' % pal[i])
            obj.setFixedSize(21, 18)
            obj.setObjectName(pal[i])
            colorgrid.addWidget(obj)

        colorgrid_frame.setLayout(colorgrid)
        colorgrid_frame.setFrameStyle(QtWidgets.QFrame().StyledPanel
                                      | QtWidgets.QFrame().Sunken)
        colorgrid_frame.setStyleSheet('padding: 4px; margin:0;')

        self.hex_field = QtWidgets.QLineEdit()
        self.hex_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                     QtWidgets.QSizePolicy.Expanding)
        self.hex_field.setAlignment(Qt.AlignCenter)
        self.hex_field.setStyleSheet('QLineEdit { background-color: #F6F6F6; color: black; }')
        self.hex_field.setMinimumHeight(26)
        self.hex_field.mouseDoubleClickEvent = self.set_focus
        self.hex_field.returnPressed.connect(self.hex_keypress_event)

        hex_hb = QtWidgets.QHBoxLayout()
        hex_hb.setContentsMargins(0, 0, 0, 0)
        hex_hb.addWidget(self.hex_field)

        hex_frame = QtWidgets.QFrame()
        hex_frame.setLayout(hex_hb)
        hex_frame.setFrameStyle(QtWidgets.QFrame().StyledPanel
                                | QtWidgets.QFrame().Sunken)
        hex_frame.setStyleSheet('margin: 0; padding: 0;')

        palette_vb.addWidget(colorgrid_frame)
        palette_vb.addWidget(hex_frame)

        palette_frame = QtWidgets.QFrame()
        palette_frame.setLayout(palette_vb)
        palette_frame.setStyleSheet('margin: 0; padding-top: 8px; padding-bottom: 8px;')

        colors_wrap.addWidget(main_color_widget)
        colors_wrap.addWidget(palette_frame)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addItem(gradient_wrap)
        vlayout.addItem(colors_wrap)
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0, 0, 0, 0)

        content_frame.setLayout(vlayout)
        content_frame.setStyleSheet("margin: 0; padding: 0; padding-top: 8px;")
        widget_layout_main.addWidget(content_frame)

        self.hue_slider.valueChanged.connect(self.calculate_hsv)
        self.opacity_slider.valueChanged.connect(self.opacity_update)
        shades_overlay.mouseMoveEvent = self.selector_drag_action
        shades_overlay.mousePressEvent = self.selector_drag_action

        self.setStyleSheet("margin: 0; padding: 0;")
        self.render_from_color()

    def calculate_hsv(self):
        """
        Get HSV from selector coordinates and slider value.
        Given x = 70 and size of 140, 70/140*100 = 50%, value = 50
        5 = offset from RingSelector bounding box
        """
        hue = int(self.hue_slider.value())
        saturation = int(((self.selector.x() + 5) / self.box_size) * 100)
        value = int(((self.selector.y() + 5) / self.box_size) * 100)
        # Since values come upside down (shades on top, whites on bottom),
        # inverse value to have shades on bottom        
        value = self.inverse[value]

        r, g, b = hsv_to_rgb(hue / 100, saturation / 100, value / 100)
        self.fg.color = [r, g, b, self.opacity_slider.value()]
        self.fg.hsv = [hue, saturation, value]
        self.update_css()

    def update_css(self):
        hue = int(self.hue_slider.value())
        r, g, b, a = self.fg.color
        new_st = """
            QSlider{
                margin-left: 4px;
                margin-right: 4px;
                border-radius: 6px;
                padding-top: 4px;
                padding-bottom: 4px;
            }
            QSlider:groove{
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-radius: 8px;
                width: 12px;
                background-color: qlineargradient(
                                        spread:pad,
                                        x1:0, y1:1,
                                        x2:0, y2:0,
                                        stop:0 rgba(%s,%s,%s, 0),
                                        stop:0.5 rgba(%s, %s, %s, 45)
                                        stop:1 rgba(%s, %s, %s, 255)
                                    );
            }
            QSlider:handle{
                height: 6px;
                margin-left: -3px;
                margin-right: -3px;
                margin-top: -1px;
                margin-bottom: -1px;
                border: 1px solid rgba(0, 0, 0, 0.4);
                background-color: #aaaaaa;
            }
        """ % (r, g, b, r, g, b, r, g, b)
        self.opacity_slider.setStyleSheet(new_st)
        self.gradient_box.setStyleSheet("""
            background-color: qlineargradient(x1:1, x2:0,
                                              stop:0 hsl(%s%%,100%%,50%%),
                                              stop:1 #fff);
            margin: 0;
            padding: 0;
            border: 1px solid rgba(0, 0, 0, 0.6);
        """ % hue)
        self.fg_btn.setStyleSheet("background-color: %s" % self.fg.rgba())
        self.bg_btn.setStyleSheet("background-color: %s" % self.bg.rgba())
        hex_val = '#{:02x}{:02x}{:02x}'.format(*self.fg.color)
        self.hex_field.setText(hex_val.upper())
        self.update_last_used_colors()

    def render_from_color(self):
        """
        Render current colors in gradient box and color buttons.
        Move selector to coordinate with approximation error
        of 1 (one) pixel.

        Trigger of calculate_hsv() avoided due to this inaccuracy,
        since it may or may not display the neighbour hex color instead.
        """
        self.selector.move(*self.fg.sel)
        self.hue_slider.valueChanged.disconnect()
        self.hue_slider.setValue(self.fg.hsv[0])
        self.hue_slider.valueChanged.connect(self.calculate_hsv)
        self.update_css()

    def move_slider_selector(self):
        """
        Updates values using current HSV color.
        Triggers calculate_hsv().
        """
        h, s, v = self.fg.hsv
        self.selector.move(*self.fg.sel)
        self.hue_slider.setValue(h)

    def update_last_used_colors(self):
        obj = self.fg
        key = 'pen'
        for i in range(2):
            if i > 0:
                obj = self.bg
                key = 'brush'
            self.config.change_config('canvas', key+'_color',
                                      ' '.join([str(i) for i in obj.color]))
            self.config.change_config('canvas', key+'_hsv',
                                      ' '.join([str(i) for i in obj.hsv]))
            self.config.change_config('canvas', key+'_sel',
                                      ' '.join([str(i) for i in obj.sel]))

    def opacity_update(self):
        self.fg.color[-1] = self.opacity_slider.value()
        self.render_from_color()

    def selector_drag_action(self, event):
        if event.buttons() == Qt.LeftButton:
            pos = event.pos()
            if pos.x() < 0:
                pos.setX(0)
            if pos.y() < 0:
                pos.setY(0)
            if pos.x() > self.box_size:
                pos.setX(self.box_size)
            if pos.y() > self.box_size:
                pos.setY(self.box_size)
            self.selector.move(pos - QPoint(5, 5))
            self.fg.sel = [self.selector.x(), self.selector.y()]

            self.calculate_hsv()

    def color_swap(self, _):
        color, hsv, sel = (self.fg.color,
                           self.fg.hsv,
                           self.fg.sel)
        bgcolor, bghsv, bgsel = (self.bg.color,
                                 self.bg.hsv,
                                 self.bg.sel)

        self.fg.color = bgcolor
        self.opacity_slider.setValue(bgcolor[-1])
        self.fg.hsv = bghsv
        self.fg.sel = bgsel

        self.bg.color = color
        self.bg.hsv = hsv
        self.bg.sel = sel

        self.render_from_color()

    def set_focus(self, _):
        """
        Activates current window to set focus to self.hex_field
        """
        self.releaseKeyboard()
        self.raise_()
        self.activateWindow()

    def hex_keypress_event(self):
        """
        Capture Enter keypress and calculate input.
        """
        color = self.hex_field.text().strip('#')

        try:
            if len(color) > 6:
                raise ValueError
            # hex to rgb
            rgb = list(int(color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            self.update_css()
            return

        hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[-1])
        hsv = [round(i) for i in hsv]

        # Map max HSV value of 360 to hue slider of max value 100
        hsv[0] = round((hsv[0] / 360) * 100)

        sat = (hsv[1] * self.box_size) / 100
        sat = round(sat) - 4

        val = self.inverse[hsv[2]]
        val = (val * self.box_size) / 100
        val = round(val) - 5
        sel = [int(i) for i in [sat, val]]

        rgb.append(self.opacity_slider.value())
        self.fg.color = [int(i) for i in rgb]
        self.fg.hsv = [int(i) for i in hsv]
        self.fg.sel = sel

        self.render_from_color()

    def update_hex_value(self, color):
        self.hex_field.setText(color)
        self.hex_keypress_event()