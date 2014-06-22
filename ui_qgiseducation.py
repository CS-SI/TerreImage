# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_qgiseducation.ui'
#
# Created: Sun Jun 22 01:33:22 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_QGISEducation(object):
    def setupUi(self, QGISEducation):
        QGISEducation.setObjectName(_fromUtf8("QGISEducation"))
        QGISEducation.resize(323, 502)
        self.verticalLayout = QtGui.QVBoxLayout(QGISEducation)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.comboBox_sprectral_band_display = QtGui.QComboBox(QGISEducation)
        self.comboBox_sprectral_band_display.setObjectName(_fromUtf8("comboBox_sprectral_band_display"))
        self.verticalLayout.addWidget(self.comboBox_sprectral_band_display)
        self.comboBox_processing = QtGui.QComboBox(QGISEducation)
        self.comboBox_processing.setObjectName(_fromUtf8("comboBox_processing"))
        self.verticalLayout.addWidget(self.comboBox_processing)
        self.comboBox_histogrammes = QtGui.QComboBox(QGISEducation)
        self.comboBox_histogrammes.setObjectName(_fromUtf8("comboBox_histogrammes"))
        self.verticalLayout.addWidget(self.comboBox_histogrammes)
        self.pushButton_histogramme = QtGui.QPushButton(QGISEducation)
        self.pushButton_histogramme.setObjectName(_fromUtf8("pushButton_histogramme"))
        self.verticalLayout.addWidget(self.pushButton_histogramme)
        self.pushButton_profil_spectral = QtGui.QPushButton(QGISEducation)
        self.pushButton_profil_spectral.setObjectName(_fromUtf8("pushButton_profil_spectral"))
        self.verticalLayout.addWidget(self.pushButton_profil_spectral)
        self.groupBox_5 = QtGui.QGroupBox(QGISEducation)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.pushButton_kmeans = QtGui.QPushButton(self.groupBox_5)
        self.pushButton_kmeans.setObjectName(_fromUtf8("pushButton_kmeans"))
        self.horizontalLayout_2.addWidget(self.pushButton_kmeans)
        self.spinBox_kmeans = QtGui.QSpinBox(self.groupBox_5)
        self.spinBox_kmeans.setProperty("value", 5)
        self.spinBox_kmeans.setObjectName(_fromUtf8("spinBox_kmeans"))
        self.horizontalLayout_2.addWidget(self.spinBox_kmeans)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.pushButton_plugin_classification = QtGui.QPushButton(self.groupBox_5)
        self.pushButton_plugin_classification.setObjectName(_fromUtf8("pushButton_plugin_classification"))
        self.verticalLayout_3.addWidget(self.pushButton_plugin_classification)
        self.verticalLayout.addWidget(self.groupBox_5)
        self.groupBox = QtGui.QGroupBox(QGISEducation)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEdit_working_dir = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_working_dir.setObjectName(_fromUtf8("lineEdit_working_dir"))
        self.horizontalLayout.addWidget(self.lineEdit_working_dir)
        self.pushButton_working_dir = QtGui.QPushButton(self.groupBox)
        self.pushButton_working_dir.setObjectName(_fromUtf8("pushButton_working_dir"))
        self.horizontalLayout.addWidget(self.pushButton_working_dir)
        self.verticalLayout.addWidget(self.groupBox)
        self.pushButton_kmz = QtGui.QPushButton(QGISEducation)
        self.pushButton_kmz.setObjectName(_fromUtf8("pushButton_kmz"))
        self.verticalLayout.addWidget(self.pushButton_kmz)
        self.pushButton_status = QtGui.QPushButton(QGISEducation)
        self.pushButton_status.setObjectName(_fromUtf8("pushButton_status"))
        self.verticalLayout.addWidget(self.pushButton_status)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_a_s = QtGui.QLabel(QGISEducation)
        self.label_a_s.setObjectName(_fromUtf8("label_a_s"))
        self.horizontalLayout_3.addWidget(self.label_a_s)
        self.label_a_s_img = QtGui.QLabel(QGISEducation)
        self.label_a_s_img.setText(_fromUtf8(""))
        self.label_a_s_img.setObjectName(_fromUtf8("label_a_s_img"))
        self.horizontalLayout_3.addWidget(self.label_a_s_img)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(QGISEducation)
        QtCore.QMetaObject.connectSlotsByName(QGISEducation)

    def retranslateUi(self, QGISEducation):
        QGISEducation.setWindowTitle(QtGui.QApplication.translate("QGISEducation", "QGISEducation", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_histogramme.setText(QtGui.QApplication.translate("QGISEducation", "Histogramme", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_profil_spectral.setText(QtGui.QApplication.translate("QGISEducation", "Profil spectral", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("QGISEducation", "Classification", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_kmeans.setText(QtGui.QApplication.translate("QGISEducation", "Classification non supervisée", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_plugin_classification.setText(QtGui.QApplication.translate("QGISEducation", "Classification supervisée", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("QGISEducation", "Répertoire de sortie", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_working_dir.setText(QtGui.QApplication.translate("QGISEducation", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_kmz.setText(QtGui.QApplication.translate("QGISEducation", "Export KMZ", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_status.setText(QtGui.QApplication.translate("QGISEducation", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.label_a_s.setText(QtGui.QApplication.translate("QGISEducation", "Légende de l\'angle spectral:", None, QtGui.QApplication.UnicodeUTF8))

