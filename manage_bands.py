# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducationDialog
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin               : 2014-04-30
        copyright           : (C) 2014 by CS SI
        email               : alexia.mondot@c-s.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtGui import QDialog, QButtonGroup, QMessageBox
from PyQt4.QtCore import QObject, SIGNAL, Qt

from ui_bands import Ui_Dialog

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()


class manage_bands:

    def __init__(self, type_image=None, nb_bands=None):

        # creating interface
        Dialog = QDialog()
        self.bandsUi = Ui_Dialog()
        self.bandsUi.setupUi(Dialog)
        # screen = QApplication.desktop().screenGeometry()
        # self.move( screen.center() - self.rect().center() )

        groupButton1 = QButtonGroup()
        groupButton1.addButton(self.bandsUi.radioButton_formosat)
        groupButton1.addButton(self.bandsUi.radioButton_pleiades)
        groupButton1.addButton(self.bandsUi.radioButton_spot)
        groupButton1.addButton(self.bandsUi.radioButton_autre)

        self.red = None
        self.green = None
        self.blue = None
        self.pir = None
        self.mir = None

        # connect the qdialog button box
        # QObject.connect(self.bandsUi.buttonBox, SIGNAL("accepted()"), self.set_bands)
        # QObject.connect(self.bandsUi.buttonBox, SIGNAL("rejected()"), self.reset_bands)
        self.bandsUi.checkBox_blue.stateChanged.connect(self.blue_checkbox_changed)
        self.bandsUi.checkBox_mir.stateChanged.connect(self.mir_checkbox_changed)
        self.bandsUi.radioButton_formosat.toggled.connect(self.define_formosat)
        self.bandsUi.radioButton_pleiades.toggled.connect(self.define_pleiade)
        self.bandsUi.radioButton_spot.toggled.connect(self.define_spot)
        self.bandsUi.radioButton_autre.toggled.connect(self.define_other)

        QObject.connect(self.bandsUi.spinBox_blue, SIGNAL("valueChanged(int)"), self.update_blue)
        QObject.connect(self.bandsUi.spinBox_red, SIGNAL("valueChanged(int)"), self.update_red)
        QObject.connect(self.bandsUi.spinBox_green, SIGNAL("valueChanged(int)"), self.update_green)
        QObject.connect(self.bandsUi.spinBox_pir, SIGNAL("valueChanged(int)"), self.update_pir)
        QObject.connect(self.bandsUi.spinBox_mir, SIGNAL("valueChanged(int)"), self.update_mir)
        # QObject.connect( spinBox_mir, SIGNAL( "valueChanged(int)" ), lambda x:self.mir = x)
        QObject.connect(self.bandsUi.buttonBox, SIGNAL("rejected()"), self.cancel)

        # settrace()

        if nb_bands:
            self.nb_bands = nb_bands
            self.custom_from_nb_of_bands(nb_bands)
        else:
            self.nb_bands = -1

        gray_other = False
        if type_image:
            if type_image == "Spot 5" or type_image == "spot":
                logger.info("define spot")
                # self.define_spot(False)
                self.bandsUi.radioButton_spot.setChecked(True)
                self.bandsUi.radioButton_formosat.setEnabled(False)
                self.bandsUi.radioButton_pleiades.setEnabled(False)
                gray_other = True
            elif type_image == "PHR 1A":
                logger.info("define pleiade")
                # self.define_pleiade()
                self.bandsUi.radioButton_pleiades.setChecked(True)
                self.bandsUi.radioButton_formosat.setEnabled(False)
                self.bandsUi.radioButton_spot.setEnabled(False)
                gray_other = True
            elif type_image == "Formosat 2":
                logger.info("define formosat")
                # self.define_formosat(False)
                self.bandsUi.radioButton_formosat.setChecked(True)
                self.bandsUi.radioButton_spot.setEnabled(False)
                self.bandsUi.radioButton_pleiades.setEnabled(False)
                gray_other = True
            else:
                logger.info("define others")
                self.bandsUi.radioButton_autre.setChecked(True)
                self.set_spinbox_read_only(False)
            if gray_other:
                self.gray_other()

        # execute the dialog
        Dialog.exec_()

    def cancel(self):
        self.blue = -1
        self.green = -1
        self.red = -1
        self.pir = -1
        self.mir = -1
        return None

    def update_red(self, value):
        self.red = value

    def update_green(self, value):
        self.green = value

    def update_blue(self, value):
        self.blue = value

    def update_pir(self, value):
        self.pir = value

    def update_mir(self, value):
        self.mir = value

    def custom_from_nb_of_bands(self, number_of_bands):
        self.bandsUi.spinBox_red.setMaximum(number_of_bands)
        self.bandsUi.spinBox_green.setMaximum(number_of_bands)
        self.bandsUi.spinBox_blue.setMaximum(number_of_bands)
        self.bandsUi.spinBox_pir.setMaximum(number_of_bands)
        self.bandsUi.spinBox_mir.setMaximum(number_of_bands)
        self.bandsUi.spinBox_red.setMinimum(1)
        self.bandsUi.spinBox_green.setMinimum(1)
        self.bandsUi.spinBox_blue.setMinimum(1)
        self.bandsUi.spinBox_pir.setMinimum(1)
        self.bandsUi.spinBox_mir.setMinimum(1)
        if number_of_bands == 1:
            self.bandsUi.spinBox_red.setMinimum(0)
            self.bandsUi.spinBox_green.setMinimum(0)
            self.bandsUi.spinBox_blue.setMinimum(0)
            self.bandsUi.spinBox_pir.setMinimum(0)
            self.bandsUi.spinBox_mir.setMinimum(0)
            self.red = 0
            self.green = 0
            self.blue = 0
            self.pir = 0
            self.mir = 0

            self.bandsUi.radioButton_formosat.setEnabled(False)
            self.bandsUi.radioButton_spot.setEnabled(False)
            self.bandsUi.radioButton_pleiades.setEnabled(False)
            self.update_spin_box()
        elif number_of_bands == 3:
            self.bandsUi.spinBox_blue.setMinimum(0)
            self.bandsUi.spinBox_mir.setMinimum(0)
            self.blue = 0
            self.green = 1
            self.red = 2
            self.pir = 3
            self.mir = 0
            self.bandsUi.radioButton_formosat.setEnabled(False)
            self.bandsUi.radioButton_pleiades.setEnabled(False)
            self.update_spin_box()
            self.update_blue_mir("none")
        elif number_of_bands == 4:
            self.bandsUi.spinBox_blue.setMinimum(0)
            self.bandsUi.spinBox_mir.setMinimum(0)
            self.blue = 1
            self.green = 2
            self.red = 3
            self.pir = 4
            self.mir = 0
            self.update_spin_box()
            self.update_blue_mir("blue")
        else:
            QMessageBox.critical(None , "Erreur", "L'image en entrée doit avoir 1, 3 ou 4 bandes !", QMessageBox.Ok)
        # print "define by bands"
        # self.debug()

    def debug(self, message=""):
        print message
        print "self.blue", self.blue
        print "self.green", self.green
        print "self.red", self.red
        print "self.pir", self.pir
        print "self.mir", self.mir


    def set_spinbox_read_only(self, state):
        self.bandsUi.spinBox_blue.setReadOnly(state)
        self.bandsUi.spinBox_red.setReadOnly(state)
        self.bandsUi.spinBox_green.setReadOnly(state)
        self.bandsUi.spinBox_pir.setReadOnly(state)
        self.bandsUi.spinBox_mir.setReadOnly(state)


    def blue_checkbox_changed(self):
        if self.bandsUi.checkBox_blue.checkState() == Qt.Checked:
            self.update_blue_mir("blue")
        else:
            self.bandsUi.label_mir.setEnabled(True)
            self.bandsUi.spinBox_mir.setEnabled(True)


    def mir_checkbox_changed(self):
        if self.bandsUi.checkBox_mir.checkState() == Qt.Checked:
            self.update_blue_mir("mir")
        else:
            self.bandsUi.label_blue.setEnabled(True)
            self.bandsUi.spinBox_blue.setEnabled(True)

    def define_other(self):
        self.bandsUi.groupBox_other.setEnabled(True)
        self.bandsUi.radioButton_autre.setEnabled(True)

    def gray_other(self):
        self.bandsUi.groupBox_other.setEnabled(False)
        self.bandsUi.radioButton_autre.setEnabled(False)


    def update_blue_mir(self, keyword):
        if keyword == "blue":
            self.bandsUi.label_mir.setEnabled(False)
            self.bandsUi.spinBox_mir.setEnabled(False)
            self.bandsUi.checkBox_mir.setCheckState(Qt.Unchecked)
            self.bandsUi.label_blue.setEnabled(True)
            self.bandsUi.spinBox_blue.setEnabled(True)
            self.bandsUi.spinBox_mir.setValue(0)
        if keyword == "mir":
            self.bandsUi.label_blue.setEnabled(False)
            self.bandsUi.spinBox_blue.setEnabled(False)
            self.bandsUi.checkBox_blue.setCheckState(Qt.Unchecked)
            self.bandsUi.label_mir.setEnabled(True)
            self.bandsUi.spinBox_mir.setEnabled(True)
            self.bandsUi.spinBox_blue.setValue(0)
        if keyword == "all":
            self.bandsUi.label_blue.setEnabled(True)
            self.bandsUi.spinBox_blue.setEnabled(True)
            self.bandsUi.checkBox_blue.setCheckState(Qt.Unchecked)
            self.bandsUi.checkBox_mir.setCheckState(Qt.Unchecked)
            self.bandsUi.label_mir.setEnabled(True)
            self.bandsUi.spinBox_mir.setEnabled(True)
        if keyword == "none":
            self.bandsUi.label_blue.setEnabled(False)
            self.bandsUi.spinBox_blue.setEnabled(False)
            self.bandsUi.checkBox_blue.setCheckState(Qt.Unchecked)
            self.bandsUi.checkBox_mir.setCheckState(Qt.Unchecked)
            self.bandsUi.label_mir.setEnabled(False)
            self.bandsUi.spinBox_mir.setEnabled(False)


    def update_spin_box(self):
        # print self.red
        self.bandsUi.spinBox_red.setValue(self.red)
        if self.red == -1:
            self.bandsUi.spinBox_red.setEnabled(False)
        self.bandsUi.spinBox_green.setValue(self.green)
        if self.green == -1:
            self.bandsUi.spinBox_green.setEnabled(False)
        self.bandsUi.spinBox_blue.setValue(self.blue)
        if self.blue == -1 or self.blue == 0:
            self.bandsUi.spinBox_blue.setEnabled(False)
            if self.nb_bands:
                if self.nb_bands > 3:
                    self.bandsUi.checkBox_mir.setCheckState(Qt.Checked)
        self.bandsUi.spinBox_pir.setValue(self.pir)
        if self.pir == -1:
            self.bandsUi.spinBox_pir.setEnabled(False)
        self.bandsUi.spinBox_mir.setValue(self.mir)
        if self.mir == -1 or self.mir == 0:
            self.bandsUi.spinBox_mir.setEnabled(False)
            if self.nb_bands:
                if self.nb_bands > 3:
                    self.bandsUi.checkBox_blue.setCheckState(Qt.Checked)



    def define_formosat(self):
        """
        B1: 0,45 – 0,52 µm (Bleu)
        B2: 0,52 – 0,60 µm (Vert)
        B3: 0,63 – 0,69 µm (Rouge)
        B4: 0,76 – 0,90 µm (proche Infra Rouge)
        """
        self.blue = 3
        self.green = 2
        self.red = 1
        self.pir = 4
        self.mir = -1
        self.update_blue_mir("blue")
        self.update_spin_box()
        self.bandsUi.radioButton_formosat.setEnabled(True)

    def define_pleiade(self):
        """
        Multispectral ???
        1     430 – 550 nm (bleu)
        2     490 – 610 nm (vert)
        3     600 – 720 nm (rouge)
        4     750 – 950 nm (proche infrarouge)
        """
        self.blue = 1
        self.green = 2
        self.red = 3
        self.pir = 4
        self.mir = -1
        self.update_blue_mir("blue")
        self.update_spin_box()
        self.bandsUi.radioButton_pleiades.setEnabled(True)


    def define_spot(self):
        """
        Bande 1: Vert (0,50 - 0,59 µm)
        Bande 2: Rouge (0,61 - 0,68 µm)
        Bande 3: Proche infrarouge (0,78 - 0,89 µm)
        Bande 4: Moyen infrarouge (MIR) (1,58 - 1,75 µm)
        """
        # print "define spot"
        # spot 4-5
        self.blue = -1
        self.green = 3
        self.red = 2
        self.pir = 1
        if self.nb_bands:
            if self.nb_bands > 3:
                self.mir = 4
                self.update_blue_mir("mir")
            else:
                self.update_blue_mir("none")
        self.update_spin_box()
        self.bandsUi.radioButton_spot.setEnabled(True)


    def get_values(self):
#         self.red = self.bandsUi.spinBox_red.value()
#         self.green = self.bandsUi.spinBox_green.value()
#         self.blue = self.bandsUi.spinBox_blue.value()
#         self.pir = self.bandsUi.spinBox_pir.value()
#         self.mir = self.bandsUi.spinBox_mir.value()
        # print self.red
        return self.red, self.green, self.blue, self.pir, self.mir
