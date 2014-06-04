# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_supervisedclassification.ui'
#
# Created: Fri Jul 27 17:04:03 2012
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SupervisedClassification(object):
    def setupUi(self, SupervisedClassification):
        SupervisedClassification.setObjectName("SupervisedClassification")
        SupervisedClassification.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(SupervisedClassification)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(SupervisedClassification)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), SupervisedClassification.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), SupervisedClassification.reject)
        QtCore.QMetaObject.connectSlotsByName(SupervisedClassification)

    def retranslateUi(self, SupervisedClassification):
        SupervisedClassification.setWindowTitle(QtGui.QApplication.translate("SupervisedClassification", "SupervisedClassification", None, QtGui.QApplication.UnicodeUTF8))

