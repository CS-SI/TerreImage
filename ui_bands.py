# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_bands.ui'
#
# Created: Mon Jun  6 08:25:23 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(294, 360)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.radioButton_spot = QtGui.QRadioButton(Dialog)
        self.radioButton_spot.setObjectName(_fromUtf8("radioButton_spot"))
        self.verticalLayout.addWidget(self.radioButton_spot)
        self.radioButton_pleiades = QtGui.QRadioButton(Dialog)
        self.radioButton_pleiades.setObjectName(_fromUtf8("radioButton_pleiades"))
        self.verticalLayout.addWidget(self.radioButton_pleiades)
        self.radioButton_formosat = QtGui.QRadioButton(Dialog)
        self.radioButton_formosat.setObjectName(_fromUtf8("radioButton_formosat"))
        self.verticalLayout.addWidget(self.radioButton_formosat)
        self.radioButton_autre = QtGui.QRadioButton(Dialog)
        self.radioButton_autre.setChecked(True)
        self.radioButton_autre.setObjectName(_fromUtf8("radioButton_autre"))
        self.verticalLayout.addWidget(self.radioButton_autre)
        self.groupBox_other = QtGui.QGroupBox(Dialog)
        self.groupBox_other.setTitle(_fromUtf8(""))
        self.groupBox_other.setObjectName(_fromUtf8("groupBox_other"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_other)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_4 = QtGui.QLabel(self.groupBox_other)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 1, 1, 1)
        self.label_mir = QtGui.QLabel(self.groupBox_other)
        self.label_mir.setObjectName(_fromUtf8("label_mir"))
        self.gridLayout.addWidget(self.label_mir, 4, 1, 1, 1)
        self.spinBox_mir = QtGui.QSpinBox(self.groupBox_other)
        self.spinBox_mir.setProperty("value", 5)
        self.spinBox_mir.setObjectName(_fromUtf8("spinBox_mir"))
        self.gridLayout.addWidget(self.spinBox_mir, 4, 2, 1, 1)
        self.spinBox_pir = QtGui.QSpinBox(self.groupBox_other)
        self.spinBox_pir.setProperty("value", 4)
        self.spinBox_pir.setObjectName(_fromUtf8("spinBox_pir"))
        self.gridLayout.addWidget(self.spinBox_pir, 3, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.checkBox_blue = QtGui.QCheckBox(self.groupBox_other)
        self.checkBox_blue.setText(_fromUtf8(""))
        self.checkBox_blue.setObjectName(_fromUtf8("checkBox_blue"))
        self.gridLayout.addWidget(self.checkBox_blue, 0, 3, 1, 1)
        self.checkBox_mir = QtGui.QCheckBox(self.groupBox_other)
        self.checkBox_mir.setText(_fromUtf8(""))
        self.checkBox_mir.setObjectName(_fromUtf8("checkBox_mir"))
        self.gridLayout.addWidget(self.checkBox_mir, 4, 3, 1, 1)
        self.label_blue = QtGui.QLabel(self.groupBox_other)
        self.label_blue.setObjectName(_fromUtf8("label_blue"))
        self.gridLayout.addWidget(self.label_blue, 0, 1, 1, 1)
        self.spinBox_blue = QtGui.QSpinBox(self.groupBox_other)
        self.spinBox_blue.setProperty("value", 3)
        self.spinBox_blue.setObjectName(_fromUtf8("spinBox_blue"))
        self.gridLayout.addWidget(self.spinBox_blue, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_other)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.label_red = QtGui.QLabel(self.groupBox_other)
        self.label_red.setObjectName(_fromUtf8("label_red"))
        self.gridLayout.addWidget(self.label_red, 2, 1, 1, 1)
        self.spinBox_green = QtGui.QSpinBox(self.groupBox_other)
        self.spinBox_green.setProperty("value", 2)
        self.spinBox_green.setObjectName(_fromUtf8("spinBox_green"))
        self.gridLayout.addWidget(self.spinBox_green, 1, 2, 1, 1)
        self.spinBox_red = QtGui.QSpinBox(self.groupBox_other)
        self.spinBox_red.setEnabled(True)
        self.spinBox_red.setProperty("value", 1)
        self.spinBox_red.setObjectName(_fromUtf8("spinBox_red"))
        self.gridLayout.addWidget(self.spinBox_red, 2, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_other)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Terre Image", None))
        self.radioButton_spot.setText(_translate("Dialog", "Mode image spot 4-5", None))
        self.radioButton_pleiades.setText(_translate("Dialog", "Mode image Pleiades - SPOT 6/7", None))
        self.radioButton_formosat.setText(_translate("Dialog", "Mode image Formosat", None))
        self.radioButton_autre.setText(_translate("Dialog", "Autre (mode avancé)", None))
        self.label_4.setText(_translate("Dialog", "Bande proche IR", None))
        self.label_mir.setText(_translate("Dialog", "Bande moyen IR", None))
        self.label_blue.setText(_translate("Dialog", "Bande bleue", None))
        self.label_2.setText(_translate("Dialog", "Bande verte", None))
        self.label_red.setText(_translate("Dialog", "Bande rouge", None))

