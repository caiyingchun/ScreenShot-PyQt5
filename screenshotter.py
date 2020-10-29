#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

"""
    Author: Talha Can Havadar
    Description:
"""


import sys
from PyQt5.QtCore import QDir, Qt, QTimer, QLine, QEvent, QRect, QSize
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QKeySequence, QImage, QCursor
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFileDialog, QGridLayout,
        QGroupBox, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpinBox,QRubberBand,
        QVBoxLayout, QWidget, QDesktopWidget, QDialog, QMessageBox, QShortcut, QScrollArea)


class EditScreenshot(QDialog):
    """docstring for EditScreenshot"""

    painter = None
    pressBeginPoint = None
    prevState = list()

    def __init__(self, parent):
        super(EditScreenshot, self).__init__(parent= parent)
        self.parent = parent
        self.painter = QPainter()
        orgSize = self.parent.screenPixmap.size()
        availableSize = QDesktopWidget().availableGeometry().size()
        print("imagesize: " + str(orgSize) + " availableSize: " + str(availableSize))
        if orgSize.width() > availableSize.width() or orgSize.height() > availableSize.height():
            image = self.parent.screenPixmap.scaled(availableSize, Qt.KeepAspectRatio, Qt.SmoothTransformation).toImage()
        else:
            image = self.parent.screenPixmap.toImage()

        self.imageHolder = ImageHolder(image)
        self.imageHolder.resize(image.size())
        self.imageHolder.setMinimumSize(image.size())
        self.imageHolder.show()

        mainLayout = QVBoxLayout()

        closeBtn = QPushButton("Close")
        closeBtn.clicked.connect(self.close)
        saveBtn = QPushButton("Save Changes")
        saveBtn.clicked.connect(self.saveChanges)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.imageHolder)

        btnLayout = QHBoxLayout()
        btnLayout.addStretch()
        btnLayout.addWidget(saveBtn)
        btnLayout.addWidget(closeBtn)

        mainLayout.addLayout(btnLayout)
        mainLayout.addWidget(scroll)

        save = QShortcut(QKeySequence("Ctrl+s"), self)
        save.activated.connect(self.saveChanges)

        self.setLayout(mainLayout)
        self.resize(QDesktopWidget().availableGeometry().size())
        self.setWindowTitle("Edit Screenshot")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if hasattr(self, "imageHolder"):
                self.imageHolder.applyState()
        elif event.key() == Qt.Key_Escape:
            if hasattr(self, "imageHolder"):
                self.imageHolder.cancelState()
        else:
            super(EditScreenshot, self).keyPressEvent(event)

    def closeEvent(self, event):
        QApplication.restoreOverrideCursor()

    def saveChanges(self):
        reply = QMessageBox.question(self, 'Message', 'Are you sure you save?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            image = self.imageHolder.saveChanges()
            format = 'png'
            initialPath = QDir.currentPath() + "/untitled." + format
            fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                    "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
            if fileName:
                image.save(fileName)
                self.screenPixmap = QPixmap.fromImage(image)
                self.parent.screenshotHolder.setPixmap(QPixmap.fromImage(image).scaled(
                    self.parent.screenshotHolder.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            self.close()

class ImageHolder(QWidget):

    foregroundState = list()
    foreground = None
    mousePressPoint = None
    cropMode = False
    def __init__(self, image):
        super(ImageHolder, self).__init__()
        self.image = image
        self.setMinimumSize(self.image.size())
        self.resize(self.image.size())
        self.foreground = QImage(self.image.size(),QImage.Format_ARGB32_Premultiplied)
        undo = QShortcut(QKeySequence("Ctrl+z"), self)
        undo.activated.connect(self.undo)

        crop = QShortcut(QKeySequence("c"), self)
        crop.activated.connect(self.toggleCropMode)


    def applyState(self):
        print("apply state")
        if self.cropMode:
            rect = self.currentQRubberBand.geometry()
            self.image = self.image.copy(rect)
            self.setMinimumSize(self.image.size())
            self.resize(self.image.size())
            QApplication.restoreOverrideCursor()
            self.toggleCropMode()
            self.currentQRubberBand.hide()
            self.repaint()

    def cancelState(self):
        if cropMode:
            self.currentQRubberBand.hide()

    def toggleCropMode(self):
        self.cropMode = not self.cropMode
        if self.cropMode:
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        else:
            QApplication.restoreOverrideCursor()

    def mousePressEvent(self, event):
        print("ImageHolder: " + str(event.pos()))
        self.mousePressPoint = event.pos();
        if self.cropMode:
            if hasattr(self, "currentQRubberBand"):
                self.currentQRubberBand.hide()
            self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.currentQRubberBand.setGeometry(QRect(self.mousePressPoint, QSize()))
            self.currentQRubberBand.show()

    def mouseMoveEvent(self, event):
        print("mouseMove: " + str(event.pos()))
        if self.cropMode:
            self.currentQRubberBand.setGeometry(QRect(self.mousePressPoint, event.pos()).normalized())

    def undo(self):
        if self.cropMode:
            self.currentQRubberBand.hide()
        elif len(self.foregroundState) > 0:
            self.foreground = self.foregroundState.pop()
            self.repaint()

    def mouseReleaseEvent(self, event):
        if not self.cropMode:
            self.foregroundState.append(QImage(self.foreground))
            self.painter.begin(self.foreground)
            self.painter.setPen(QPen(QBrush(QColor(255,241,18,100)), 15, Qt.SolidLine, Qt.RoundCap))
            self.painter.drawLine(QLine(self.mousePressPoint.x(),self.mousePressPoint.y(),
             event.pos().x(), event.pos().y()))
            self.painter.end()
            self.repaint()

    def saveChanges(self):
        newImage = QImage(self.image.size(), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(newImage)
        painter.drawImage(0,0, self.image)
        painter.drawImage(0,0, self.foreground)
        painter.end()
        return newImage

    def paintEvent(self, event):
        self.painter = QPainter(self)
        self.painter.setPen(QPen(QBrush(QColor(255,241,18,100)), 15, Qt.SolidLine, Qt.RoundCap))
        self.painter.drawImage(0,0, self.image)
        self.painter.drawImage(0,0, self.foreground)
        self.painter.end()

class ScreenShotter(QWidget):
    """docstring for ScreenShotter"""
    def __init__(self):
        super(ScreenShotter, self).__init__()

        self.screenshotHolder = QLabel(parent = self)
        self.screenshotHolder.setSizePolicy(QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        self.screenshotHolder.setAlignment(Qt.AlignCenter)
        self.screenshotHolder.setMinimumSize(400, 300)

        mainLayout = QVBoxLayout()

        label = QLabel("This window will be hidden when you press Take Screenshot button.")
        label.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(label)
        mainLayout.addLayout(self.createButtonGroup())
        mainLayout.addWidget(self.screenshotHolder)


        self.setLayout(mainLayout)
        self.takeScreenshot()
        self.resize(500,400)
        self.center()
        self.setWindowTitle("ScreenShotter")


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def resizeEvent(self, event):
        scaledSize = self.screenPixmap.size()
        scaledSize.scale(self.screenshotHolder.size(), Qt.KeepAspectRatio)
        if not self.screenshotHolder.pixmap() or scaledSize != self.screenshotHolder.pixmap().size():
            self.updateScreenshotHolder()

    def createButtonGroup(self):
        layout = QHBoxLayout()

        self.openSS = self.createButton("Open", self.openScreenshot)
        self.takeSS = self.createButton("Take Screenshot", self.newScreenshot)
        self.editSS = self.createButton("Edit Screenshot", self.editScreenshot)
        self.quit = self.createButton("Quit", self.close)

        layout.addStretch()
        layout.addWidget(self.openSS)
        layout.addWidget(self.takeSS)
        layout.addWidget(self.editSS)
        layout.addWidget(self.quit)
        return layout

    def createButton(self, text, onClick):
        button = QPushButton(text)
        button.clicked.connect(onClick)
        return button

    def updateScreenshotHolder(self):
        self.screenshotHolder.setPixmap(self.screenPixmap.scaled(
            self.screenshotHolder.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def openScreenshot(self):
        format = "png"
        initialPath = QDir.currentPath() + "/"
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", initialPath,
         "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
        image = QImage(fileName, format)
        self.screenPixmap = QPixmap.fromImage(image)
        self.updateScreenshotHolder()
        self.editScreenshot()

    def newScreenshot(self):
        self.hide()
        self.takeScreenshot()
        self.show()
        self.editScreenshot()

    def editScreenshot(self):
        edit = EditScreenshot(parent = self)
        edit.show()

    def takeScreenshot(self):
        QApplication.instance().beep()
        print("screenshot taking..")
        screen = QApplication.primaryScreen()
        if screen is not None:
            self.screenPixmap = screen.grabWindow(0)
        else:
            self.screenPixmap = QPixmap()
        self.updateScreenshotHolder()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    shotter = ScreenShotter()
    shotter.show()
    sys.exit(app.exec_())
