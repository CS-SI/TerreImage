# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from qgiseducationwidget import QGISEducationWidget
import os.path


class QGISEducation:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface


    def initGui(self):
        """
        Initialisation on the widget interface
        """
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/qgiseducation/icon.png"),
            u"QGIS Education", self.iface.mainWindow())
        self.action.setWhatsThis("QGIS_Education")
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&QGISEducation", self.action)
        
        self.dockOpened = False
        
        # create the widget to display information
        self.educationWidget = QGISEducationWidget(self.iface)
        
        # create the dockwidget with the correct parent and add the valuewidget
        self.valuedockwidget = QDockWidget("QGIS Education", self.iface.mainWindow() )
        self.valuedockwidget.setObjectName("QGIS Education")
        self.valuedockwidget.setWidget(self.educationWidget)
        QObject.connect(self.valuedockwidget, SIGNAL('visibilityChanged ( bool )'), self.showHideDockWidget)
        
        # add the dockwidget to iface
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.valuedockwidget)
        #self.educationWidget.show()

    def unload(self):
        """
        Defines the unload of the plugin
        """
        self.valuedockwidget.close()
        self.educationWidget.disconnectP()
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&QGISEducation", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        """
        Defines the behavior of the plugin
        """
        #if dock not already opened, open the dock and all the necessary thing (model,doProfile...)
        if self.dockOpened == False:
            self.educationWidget.show()
            # add the dockwidget to iface
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.valuedockwidget)
            self.dockOpened = True
        else :
            self.educationWidget.hide()
            self.dockOpened = False
            self.iface.removeDockWidget(self.valuedockwidget)


    def showHideDockWidget( self ):
        """
        Change the state of the widget, and run the connections of signals of the widget
        """
#         if self.valuedockwidget.isVisible() and self.educationWidget.cbxActive.isChecked():
#             state = Qt.Checked
#         else:
#             state = Qt.Unchecked
#         self.educationWidget.changeActive( state )
        pass