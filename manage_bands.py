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
from PyQt4.QtCore import QObject, SIGNAL, QSettings

from ui_bands import Ui_Dialog


import logging
logger = logging.getLogger( 'manage_bands' )

class manage_bands:
    
    def __init__(self):
        
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
        
        #execute the dialog
        Dialog.exec_()
    
    
    
    
    
    def set_bands(self):
        
        if self.bandsUi.radioButton_formosat.isChecked():
            self.red = 3
            self.green = 2
            self.blue = 1
            self.pir = 4
            self.mir = None
        elif self.bandsUi.radioButton_pleiades.isChecked():
            self.red = 3
            self.green = 2
            self.blue = 1
            self.pir = 4
            self.mir = None
        elif self.bandsUi.radioButton_spot.isChecked():
            #spot 4-5
            self.red = 2
            self.green = 1
            self.blue = None
            self.pir = 3
            self.mir = 4
        elif self.bandsUi.radioButton_autre.isChecked():
            
            self.red = self.bandsUi.spinBox_red.value()
            self.green = self.bandsUi.spinBox_green.value()
            self.blue = self.bandsUi.spinBox_blue.value()
            self.pir = self.bandsUi.spinBox_pir.value()
            self.mir = self.bandsUi.spinBox_mir.value()
        
    def get_values(self):
        return self.red, self.green, self.blue, self.pir, self.mir
        
        