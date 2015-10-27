# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_qgiseducation.ui'
#
# Created: Tue Oct 27 18:49:32 2015
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

class Ui_QGISEducation(object):
    def setupUi(self, QGISEducation):
        QGISEducation.setObjectName(_fromUtf8("QGISEducation"))
        QGISEducation.resize(410, 894)
        self.verticalLayout = QtGui.QVBoxLayout(QGISEducation)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_travail_en_cours = QtGui.QLabel(QGISEducation)
        self.label_travail_en_cours.setText(_fromUtf8(""))
        self.label_travail_en_cours.setObjectName(_fromUtf8("label_travail_en_cours"))
        self.verticalLayout.addWidget(self.label_travail_en_cours)
        self.tabWidget = QtGui.QTabWidget(QGISEducation)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_4.addWidget(self.label_2)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.treeWidget = QtGui.QTreeWidget(self.tab_2)
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.treeWidget.headerItem().setText(1, _fromUtf8("2"))
        self.verticalLayout_7.addWidget(self.treeWidget)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.comboBox_sprectral_band_display = QtGui.QComboBox(QGISEducation)
        self.comboBox_sprectral_band_display.setObjectName(_fromUtf8("comboBox_sprectral_band_display"))
        self.verticalLayout.addWidget(self.comboBox_sprectral_band_display)
        self.comboBox_histogrammes = QtGui.QComboBox(QGISEducation)
        self.comboBox_histogrammes.setObjectName(_fromUtf8("comboBox_histogrammes"))
        self.verticalLayout.addWidget(self.comboBox_histogrammes)
        self.comboBox_processing = QtGui.QComboBox(QGISEducation)
        self.comboBox_processing.setObjectName(_fromUtf8("comboBox_processing"))
        self.verticalLayout.addWidget(self.comboBox_processing)
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
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_a_s = QtGui.QLabel(QGISEducation)
        self.label_a_s.setObjectName(_fromUtf8("label_a_s"))
        self.verticalLayout_2.addWidget(self.label_a_s)
        self.label_a_s_img = QtGui.QLabel(QGISEducation)
        self.label_a_s_img.setMaximumSize(QtCore.QSize(400, 16777215))
        self.label_a_s_img.setText(_fromUtf8(""))
        self.label_a_s_img.setObjectName(_fromUtf8("label_a_s_img"))
        self.verticalLayout_2.addWidget(self.label_a_s_img)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(QGISEducation)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(QGISEducation)

    def retranslateUi(self, QGISEducation):
        QGISEducation.setWindowTitle(_translate("QGISEducation", "QGISEducation", None))
        self.label_2.setText(_translate("QGISEducation", "Fausses couleurs:            Couleurs naturelles:\n"
"Plan R <- BS_PIR              Plan R <- BS_R \n"
"Plan V <- BS_R                  Plan V <- BS_V \n"
"Plan B <- BS_V                  Plan B <- BS_B", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("QGISEducation", "Informations sur les bandes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("QGISEducation", "Informations sur l\'image", None))
        self.pushButton_histogramme.setText(_translate("QGISEducation", "Histogramme", None))
        self.pushButton_profil_spectral.setText(_translate("QGISEducation", "Profil spectral", None))
        self.groupBox_5.setTitle(_translate("QGISEducation", "Classification", None))
        self.pushButton_kmeans.setText(_translate("QGISEducation", "Classification non supervisée", None))
        self.pushButton_plugin_classification.setText(_translate("QGISEducation", "Classification supervisée", None))
        self.groupBox.setTitle(_translate("QGISEducation", "Répertoire de sortie", None))
        self.pushButton_working_dir.setText(_translate("QGISEducation", "...", None))
        self.pushButton_kmz.setText(_translate("QGISEducation", "Export KMZ", None))
        self.pushButton_status.setText(_translate("QGISEducation", "Status", None))
        self.label_a_s.setText(_translate("QGISEducation", "Légende de l\'angle spectral:", None))

