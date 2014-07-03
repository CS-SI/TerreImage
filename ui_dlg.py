# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dlg.ui'
#
# Created: Thu Jul  3 11:10:34 2014
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
        DlgAbout.resize(547, 654)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DlgAbout.sizePolicy().hasHeightForWidth())
        DlgAbout.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(DlgAbout)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.logo = QtGui.QLabel(DlgAbout)
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
        self.verticalLayout.addWidget(self.logo)
        self.txt = QtGui.QTextBrowser(DlgAbout)
        self.txt.setOpenExternalLinks(True)
        self.txt.setObjectName(_fromUtf8("txt"))
        self.verticalLayout.addWidget(self.txt)
        self.buttonBox = QtGui.QDialogButtonBox(DlgAbout)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgAbout)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DlgAbout.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DlgAbout.accept)
        QtCore.QMetaObject.connectSlotsByName(DlgAbout)

    def retranslateUi(self, DlgAbout):
        DlgAbout.setWindowTitle(QtGui.QApplication.translate("DlgAbout", "About Terre Image", None, QtGui.QApplication.UnicodeUTF8))
        self.txt.setHtml(QtGui.QApplication.translate("DlgAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt;\">La version actuelle de $PLUGIN_NAME$ est : $PLUGIN_VERSION$.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt;\">Ce travail est disponible sous les licences </span><a href=\"http://www.gnu.org/copyleft/gpl.html\"><span style=\" text-decoration: underline; color:#0000ff;\">GPL</span></a><span style=\" font-family:\'Sans\'; font-size:10pt;\"> et </span><a href=\"http://www.cecill.info/licences/Licence_CeCILL_V2-fr.html\"><span style=\" text-decoration: underline; color:#0000ff;\">CeCILL v2</span></a><span style=\" font-family:\'Sans\'; font-size:10pt;\">. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt;\">$PLUGIN_NAME$ s\'appuie sur la librairie </span><a href=\"http://orfeo-toolbox.org/otb/\"><span style=\" text-decoration: underline; color:#0000ff;\">Orfeo Toolbox</span></a><span style=\" font-family:\'Sans\'; font-size:10pt;\"> et sur les plugins suivants:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:10pt;\">- </span><a href=\"https://github.com/faunalia/dockablemirrormap\"><span style=\" text-decoration: underline; color:#0000ff;\">DockableMirrorMap</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- <a href=\"http://hub.qgis.org/projects/valuetool\"><span style=\" text-decoration: underline; color:#0000ff;\">ValueTool</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
