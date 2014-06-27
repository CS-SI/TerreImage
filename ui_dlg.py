# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dlg.ui'
#
# Created: Fri Jun 27 11:38:15 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DlgAbout(object):
    def setupUi(self, DlgAbout):
        DlgAbout.setObjectName(_fromUtf8("DlgAbout"))
        DlgAbout.resize(703, 677)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DlgAbout.sizePolicy().hasHeightForWidth())
        DlgAbout.setSizePolicy(sizePolicy)
        self.logo = QtGui.QLabel(DlgAbout)
        self.logo.setGeometry(QtCore.QRect(9, 9, 520, 520))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(sizePolicy)
        self.logo.setMinimumSize(QtCore.QSize(85, 70))
        self.logo.setMaximumSize(QtCore.QSize(520, 520))
        self.logo.setText(_fromUtf8(""))
        self.logo.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/qgiseducation/img/splash.jpg")))
        self.logo.setScaledContents(True)
        self.logo.setObjectName(_fromUtf8("logo"))
        self.title = QtGui.QLabel(DlgAbout)
        self.title.setGeometry(QtCore.QRect(420, 20, 271, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName(_fromUtf8("title"))
        self.description = QtGui.QLabel(DlgAbout)
        self.description.setGeometry(QtCore.QRect(490, 120, 211, 121))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.description.setFont(font)
        self.description.setWordWrap(True)
        self.description.setObjectName(_fromUtf8("description"))
        self.txt = QtGui.QTextBrowser(DlgAbout)
        self.txt.setGeometry(QtCore.QRect(50, 510, 631, 111))
        self.txt.setOpenExternalLinks(True)
        self.txt.setObjectName(_fromUtf8("txt"))
        self.buttonBox = QtGui.QDialogButtonBox(DlgAbout)
        self.buttonBox.setGeometry(QtCore.QRect(590, 640, 85, 27))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(DlgAbout)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DlgAbout.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DlgAbout.accept)
        QtCore.QMetaObject.connectSlotsByName(DlgAbout)

    def retranslateUi(self, DlgAbout):
        DlgAbout.setWindowTitle(QtGui.QApplication.translate("DlgAbout", "About Terre Image", None, QtGui.QApplication.UnicodeUTF8))
        self.title.setText(QtGui.QApplication.translate("DlgAbout", "$PLUGIN_NAME$", None, QtGui.QApplication.UnicodeUTF8))
        self.description.setText(QtGui.QApplication.translate("DlgAbout", "$PLUGIN_DESCRIPTION$", None, QtGui.QApplication.UnicodeUTF8))
        self.txt.setHtml(QtGui.QApplication.translate("DlgAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt;\">$PLUGIN_NAME$ est développé par le CNES. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt;\">Il s\'appuie sur les plugins suivants:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt;\">  - DockableMirrorMap (</span><a href=\"http://github.com/faunalia/dockablemirrormap\"><span style=\" text-decoration: underline; color:#0000ff;\">Dépôt du plugin</span></a>) <img src=\":/plugins/DockableMirrorMap/icons/dockablemirrormap.png\" /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">   - ValueTool (<a href=\"http://hub.qgis.org/projects/valuetool\"><span style=\" text-decoration: underline; color:#0000ff;\">Page d\'accueil</span></a>)</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
