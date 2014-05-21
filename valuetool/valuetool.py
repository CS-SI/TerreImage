"""
/***************************************************************************
         Value Tool       - A QGIS plugin to get values at the mouse pointer
                             -------------------
    begin                : 2008-08-26
    copyright            : (C) 2008 by G. Picard
    email                : 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


from valuewidget import ValueWidget

#from selectPointTool import *
# initialize Qt resources from file resouces.py
#import resources

class ValueTool:
  def __init__(self, iface):
    # save reference to the QGIS interface
    self.iface = iface

  def initGui(self):
    # create action that will start plugin configuration
    #self.action = QAction(QIcon(":/plugins/valuetool/icon.png"), "Value Tool", self.iface.getMainWindow())
    #self.action.setWhatsThis("Value Tool")
    #QObject.connect(self.action, SIGNAL("activated()"), self.run)
    ## add toolbar button and menu item
    #self.iface.addToolBarIcon(self.action)
    #self.iface.addPluginMenu("Analyses", self.action)
    ## add the tool to select feature
    #self.tool = selectPointTool(self.iface.getMapCanvas(),self.action)

    # create the widget to display information
    self.valuewidget = ValueWidget(self.iface)
    # create the dockwidget with the correct parent and add the valuewidget
    self.valuedockwidget=QDockWidget("Value Tool" , self.iface.mainWindow() )
    self.valuedockwidget.setObjectName("Value Tool")
    self.valuedockwidget.setWidget(self.valuewidget)
    QObject.connect(self.valuedockwidget, SIGNAL('visibilityChanged ( bool )'), self.showHideDockWidget)
    
    # add the dockwidget to iface
    self.iface.addDockWidget(Qt.LeftDockWidgetArea,self.valuedockwidget)
    #self.valuewidget.show()

###Qt.AllDockWidgetAreas
  def unload(self):
    self.valuedockwidget.close()
    self.valuewidget.disconnect()
    # remove the dockwidget from iface
    self.iface.removeDockWidget(self.valuedockwidget)
    # remove the plugin menu item and icon
    #self.iface.removePluginMenu("Analyses",self.action)
    #self.iface.removeToolBarIcon(self.action)


  def showHideDockWidget( self ):
    if self.valuedockwidget.isVisible() and self.valuewidget.cbxActive.isChecked():
      state = Qt.Checked
    else:
      state = Qt.Unchecked
    self.valuewidget.changeActive( state )
