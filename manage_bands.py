"""
/***************************************************************************
 QGISEducationDialog
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-04-30
        copyright            : (C) 2014 by CS SI
        email                : alexia.mondot@c-s.fr
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


from PyQt4.QtGui import QDialog, QButtonGroup
from PyQt4.QtCore import QObject, SIGNAL, Qt

from ui_bands import Ui_Dialog


import logging
logger = logging.getLogger( 'manage_bands' )

class manage_bands:
    
    def __init__(self, type_image=None):
        
        #creating interface
        Dialog = QDialog()
        self.bandsUi = Ui_Dialog()
        self.bandsUi.setupUi( Dialog )
        
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
        
        #connect the qdialog button box
        QObject.connect(self.bandsUi.buttonBox, SIGNAL("accepted()"), self.set_bands)
        #QObject.connect(self.bandsUi.buttonBox, SIGNAL("rejected()"), self.reset_bands)
        self.bandsUi.checkBox_red.stateChanged.connect(self.red_checkbox_changed)
        self.bandsUi.checkBox_mir.stateChanged.connect(self.mir_checkbox_changed)
        self.bandsUi.radioButton_formosat.toggled.connect(self.define_formosat)
        self.bandsUi.radioButton_pleiades.toggled.connect(self.define_pleiade)
        self.bandsUi.radioButton_spot.toggled.connect(self.define_spot)
        self.bandsUi.radioButton_autre.toggled.connect(self.define_other)
        
        print "type from manage_bands", type_image
        if type_image :
            if type_image == "spot":
                print "define spot"
                self.bandsUi.radioButton_spot.setChecked(True)
                self.define_spot()
            #test type pleiade
            #test type formosat
            else :
                self.bandsUi.radioButton_autre.setChecked(True)
        
        #execute the dialog
        Dialog.exec_()
    
    
    def red_checkbox_changed(self):
        if self.bandsUi.checkBox_red.checkState() == Qt.Checked:
            self.bandsUi.label_mir.setEnabled(False)
            self.bandsUi.spinBox_mir.setEnabled(False)
            self.bandsUi.checkBox_mir.setCheckState(Qt.Unchecked)
            self.bandsUi.label_red.setEnabled(True)
            self.bandsUi.spinBox_red.setEnabled(True)
        else :
            self.bandsUi.label_mir.setEnabled(True)
            self.bandsUi.spinBox_mir.setEnabled(True)
        
    
    def mir_checkbox_changed(self):
        if self.bandsUi.checkBox_mir.checkState() == Qt.Checked:
            self.bandsUi.label_red.setEnabled(False)
            self.bandsUi.spinBox_red.setEnabled(False)
            self.bandsUi.checkBox_red.setCheckState(Qt.Unchecked)
            self.bandsUi.label_mir.setEnabled(True)
            self.bandsUi.spinBox_mir.setEnabled(True)
            
        else :
            self.bandsUi.label_red.setEnabled(True)
            self.bandsUi.spinBox_red.setEnabled(True)
    
    def define_other(self):
        self.bandsUi.spinBox_red.setEnabled(True)
        self.bandsUi.spinBox_green.setEnabled(True)
        self.bandsUi.spinBox_blue.setEnabled(True)
        self.bandsUi.spinBox_pir.setEnabled(True)
        self.bandsUi.spinBox_mir.setEnabled(True)
    
    
    def set_bands(self):
        
        if self.bandsUi.radioButton_formosat.isChecked():
            self.define_formosat()
        elif self.bandsUi.radioButton_pleiades.isChecked():
            self.define_pleiade()
        elif self.bandsUi.radioButton_spot.isChecked():
            self.define_spot()
        elif self.bandsUi.radioButton_autre.isChecked():
            self.red = self.bandsUi.spinBox_red.value()
            self.green = self.bandsUi.spinBox_green.value()
            self.blue = self.bandsUi.spinBox_blue.value()
            self.pir = self.bandsUi.spinBox_pir.value()
            self.mir = self.bandsUi.spinBox_mir.value()
        self.update_spin_box()

        
    def update_spin_box(self):
        self.bandsUi.spinBox_red.setValue(self.red)
        if not self.red:
            self.bandsUi.spinBox_red.setEnabled(False)
        self.bandsUi.spinBox_green.setValue(self.green)
        if not self.green:
            self.bandsUi.spinBox_green.setEnabled(False)
        self.bandsUi.spinBox_blue.setValue(self.blue)
        if not self.blue:
            self.bandsUi.spinBox_blue.setEnabled(False)
        self.bandsUi.spinBox_pir.setValue(self.pir)
        if not self.pir:
            self.bandsUi.spinBox_pir.setEnabled(False)
        self.bandsUi.spinBox_mir.setValue(self.mir)
        if not self.mir:
            self.bandsUi.spinBox_mir.setEnabled(False)
        
    def define_formosat(self):
        self.red = 3
        self.green = 2
        self.blue = 1
        self.pir = 4
        self.mir = 0
        self.update_spin_box()
        
        
    def define_pleiade(self):
        self.red = 3
        self.green = 2
        self.blue = 1
        self.pir = 4
        self.mir = 0
        self.update_spin_box()
        
    def define_spot(self):
        #spot 4-5
        self.red = 2
        self.green = 1
        self.blue = 0
        self.pir = 3
        self.mir = 4
        self.update_spin_box()
    
        
    def get_values(self):
        return self.red, self.green, self.blue, self.pir, self.mir
        
        