# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'createnumerical.ui'
#
# Created: Sat May 19 17:14:08 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(383, 45)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.horizontalLayout = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setText(QtGui.QApplication.translate("Dialog", "X:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.xCoordLE = QtGui.QLineEdit(Dialog)
        self.xCoordLE.setObjectName(_fromUtf8("xCoordLE"))
        self.horizontalLayout.addWidget(self.xCoordLE)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Y:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.yCoordLE = QtGui.QLineEdit(Dialog)
        self.yCoordLE.setObjectName(_fromUtf8("yCoordLE"))
        self.horizontalLayout.addWidget(self.yCoordLE)
        self.sendCoordsPB = QtGui.QPushButton(Dialog)
        self.sendCoordsPB.setText(QtGui.QApplication.translate("Dialog", "Create point", None, QtGui.QApplication.UnicodeUTF8))
        self.sendCoordsPB.setObjectName(_fromUtf8("sendCoordsPB"))
        self.horizontalLayout.addWidget(self.sendCoordsPB)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass

