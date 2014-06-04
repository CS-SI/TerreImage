# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_terre_image_curve.ui'
#
# Created: Fri May 23 18:14:42 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(535, 72)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_delete_curve = QtGui.QPushButton(Form)
        self.pushButton_delete_curve.setObjectName(_fromUtf8("pushButton_delete_curve"))
        self.horizontalLayout.addWidget(self.pushButton_delete_curve)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lineEdit_curve_name = QtGui.QLineEdit(Form)
        self.lineEdit_curve_name.setObjectName(_fromUtf8("lineEdit_curve_name"))
        self.verticalLayout.addWidget(self.lineEdit_curve_name)
        self.label_coordinates = QtGui.QLabel(Form)
        self.label_coordinates.setText(_fromUtf8(""))
        self.label_coordinates.setObjectName(_fromUtf8("label_coordinates"))
        self.verticalLayout.addWidget(self.label_coordinates)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.pushButton_color = QtGui.QPushButton(Form)
        self.pushButton_color.setText(_fromUtf8(""))
        self.pushButton_color.setObjectName(_fromUtf8("pushButton_color"))
        self.horizontalLayout.addWidget(self.pushButton_color)
        self.checkBox_curve_visible = QtGui.QCheckBox(Form)
        self.checkBox_curve_visible.setText(_fromUtf8(""))
        self.checkBox_curve_visible.setChecked(True)
        self.checkBox_curve_visible.setObjectName(_fromUtf8("checkBox_curve_visible"))
        self.horizontalLayout.addWidget(self.checkBox_curve_visible)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Curve", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_delete_curve.setText(QtGui.QApplication.translate("Form", "X", None, QtGui.QApplication.UnicodeUTF8))

