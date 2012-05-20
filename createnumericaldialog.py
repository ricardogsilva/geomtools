#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from createnumerical import Ui_Dialog

from base import Point

class CreateNumericalDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super(CreateNumericalDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.point = None
        QObject.connect(self.sendCoordsPB, SIGNAL('released()'), self.create_point)

    def create_point(self):
        x = QVariant(self.xCoordLE.text()).toFloat()[0]
        y = QVariant(self.yCoordLE.text()).toFloat()[0]
        self.point = Point(x, y)
        self.emit(SIGNAL('point_selected'), self.point)
