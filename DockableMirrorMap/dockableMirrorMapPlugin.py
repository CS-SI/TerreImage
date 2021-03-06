# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Dockable MirrorMap
Description          : Creates a dockable map canvas
Date                 : February 1, 2011
copyright            : (C) 2011 by Giuseppe Sucameli (Faunalia)
                     : (C) 2014 by CNES
email                : brush.tyler@gmail.com

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

from PyQt4.QtCore import QObject, Qt, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QGridLayout

# from qgis.core import
# from qgis.gui import

import resources_rc

# import logging for debug messages
from TerreImage import terre_image_logging
logger = terre_image_logging.configure_logger()


class DockableMirrorMapPlugin(QObject):
    __pyqtSignals__ = ("mirrorClosed(PyQt_PyObject)")

    def __init__(self, iface):

        QObject.__init__(self)
        # Save a reference to the QGIS iface
        self.iface = iface

    def initGui(self):
        self.dockableMirrors = []
        self.lastDockableMirror = 0
#         self.dockableAction = QAction(QIcon(":/plugins/DockableMirrorMap/icons/dockablemirrormap.png"), "Dockable MirrorMap", self.iface.mainWindow())
#         QObject.connect(self.dockableAction, SIGNAL("triggered()"), self.runDockableMirror)

        self.aboutAction = QAction(QIcon(":/plugins/DockableMirrorMap/icons/about.png"), "About", self.iface.mainWindow())
        QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)


        # Add to the plugin menu and toolbar
#         self.iface.addPluginToMenu("Dockable MirrorMap", self.dockableAction)
        self.iface.addPluginToMenu("Dockable MirrorMap", self.aboutAction)
#         self.iface.addToolBarIcon(self.dockableAction)

        # QObject.connect(self.iface, SIGNAL("projectRead()"), self.onProjectLoaded)
        # QObject.connect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.onWriteProject)

        QObject.connect(self.iface.mapCanvas(), SIGNAL("extentsChanged()"), self.onExtentsChanged)
        QObject.connect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.onScaleChanged)

    def unload(self):
        # QObject.disconnect(self.iface, SIGNAL("projectRead()"), self.onProjectLoaded)
        # QObject.disconnect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.onWriteProject)
        self.removeDockableMirrors()
        # Remove the plugin
#         self.iface.removePluginMenu("Dockable MirrorMap",self.dockableAction)
        self.iface.removePluginMenu("Dockable MirrorMap", self.aboutAction)
#         self.iface.removeToolBarIcon(self.dockableAction)

    def about(self):
        from DlgAbout import DlgAbout
        DlgAbout(self.iface.mainWindow()).exec_()

    def removeDockableMirrors(self):
        for d in list(self.dockableMirrors):
            d.close()
        self.dockableMirrors = []
        self.lastDockableMirror = 0

    def runDockableMirror(self, title = None):
        from dockableMirrorMap import DockableMirrorMap
        wdg = DockableMirrorMap(self.iface.mainWindow(), self.iface, title)

        minsize = wdg.minimumSize()
        maxsize = wdg.maximumSize()

        self.setupDockWidget(wdg)
        self.addDockWidget(wdg)

        wdg.setMinimumSize(minsize)
        wdg.setMaximumSize(maxsize)

        if wdg.isFloating():
            wdg.move(50, 50)  # move the widget to the center

        # QObject.connect(wdg.mainWidget.canvas, SIGNAL( "extentsChanged()" ), wdg.mainWidget.mirror_extent_changed)
        # QObject.connect(wdg.mainWidget, SIGNAL("extentChanged( QgsRectangle )"), self.extentChanged )
        return wdg

    def onExtentsChanged(self):
        for view in self.dockableMirrors :
            prevFlag = view.mainWidget.canvas.renderFlag()
            view.mainWidget.canvas.setRenderFlag(False)

            view.mainWidget.canvas.setExtent(self.iface.mapCanvas().extent())

            view.mainWidget.canvas.setRenderFlag(prevFlag)

    def onScaleChanged(self):
        pass
#         logger.debug("on scale changed")
#         for view in self.dockableMirrors :
#             prevFlag = view.mainWidget.canvas.renderFlag()
#             view.mainWidget.canvas.setRenderFlag( False )
#
#             view.mainWidget.canvas.zoomScale( 1.0 / self.iface.mapCanvas().scale() )
#
#             view.mainWidget.canvas.setRenderFlag( prevFlag )

    def extentChanged(self):
        logger.debug("extent changed")
        for view in self.dockableMirrors :
            view.mainWidget.canvas.setExtent(self.iface.mapCanvas().extent())

    def setupDockWidget(self, wdg):
        othersize = QGridLayout().verticalSpacing()

        if len(self.dockableMirrors) <= 0:
            width = self.iface.mapCanvas().size().width() / 2 - othersize
            wdg.setLocation(Qt.RightDockWidgetArea)
            wdg.setMinimumWidth(width)
            wdg.setMaximumWidth(width)

        elif len(self.dockableMirrors) == 1:
            height = self.dockableMirrors[0].size().height() / 2 - othersize / 2
            wdg.setLocation(Qt.RightDockWidgetArea)
            wdg.setMinimumHeight(height)
            wdg.setMaximumHeight(height)

        elif len(self.dockableMirrors) == 2:
            height = self.iface.mapCanvas().size().height() / 2 - othersize / 2
            wdg.setLocation(Qt.BottomDockWidgetArea)
            wdg.setMinimumHeight(height)
            wdg.setMaximumHeight(height)

        else:
            wdg.setLocation(Qt.BottomDockWidgetArea)
            wdg.setFloating(True)

    def addDockWidget(self, wdg, position = None):
        if position is None:
            position = wdg.getLocation()
        else:
            wdg.setLocation(position)

        mapCanvas = self.iface.mapCanvas()
        oldSize = mapCanvas.size()

        prevFlag = mapCanvas.renderFlag()
        mapCanvas.setRenderFlag(False)
        self.iface.addDockWidget(position, wdg)

        wdg.setNumber(self.lastDockableMirror)
        self.lastDockableMirror = self.lastDockableMirror + 1
        self.dockableMirrors.append(wdg)

        QObject.connect(wdg, SIGNAL("closed(PyQt_PyObject)"), self.onCloseDockableMirror)

        newSize = mapCanvas.size()
        if newSize != oldSize:
            # trick: update the canvas size
            mapCanvas.resize(newSize.width() - 1, newSize.height())
            mapCanvas.setRenderFlag(prevFlag)
            mapCanvas.resize(newSize)
        else:
            mapCanvas.setRenderFlag(prevFlag)

    def onCloseDockableMirror(self, wdg):

        logger.debug("mirror_map_tool 2 {}".format(id(self)))
        title = wdg.title
        if self.dockableMirrors.count(wdg) > 0:
            self.dockableMirrors.remove(wdg)

        if len(self.dockableMirrors) <= 0:
            self.lastDockableMirror = 0
        del wdg
        self.emit(SIGNAL("mirrorClosed(PyQt_PyObject)"), title)


#     def onWriteProject(self, domproject):
#         if len(self.dockableMirrors) <= 0:
#             return
#
#         QgsProject.instance().writeEntry( "DockableMirrorMap", "/numMirrors", len(self.dockableMirrors) )
#         for i, dockwidget in enumerate(self.dockableMirrors):
#             # save position and geometry
#             floating = dockwidget.isFloating()
#             QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/floating" % i, floating )
#             if floating:
#                 position = "%s %s" % (dockwidget.pos().x(), dockwidget.pos().y())
#             else:
#                 position = u"%s" % dockwidget.getLocation()
#             QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/position" % i, str(position) )
#
#             size = "%s %s" % (dockwidget.size().width(), dockwidget.size().height())
#             QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/size" % i, str(size) )
#
#             # save the layer list
#             layerIds = dockwidget.getMirror().getLayerSet()
#             QgsProject.instance().writeEntry( "DockableMirrorMap", "/mirror%s/layers" % i, layerIds )
#
#
#     def onProjectLoaded(self):
#         # restore mirrors?
#         num, ok = QgsProject.instance().readNumEntry("DockableMirrorMap", "/numMirrors")
#         if not ok or num <= 0:
#             return
#
#         # remove all mirrors
#         self.removeDockableMirrors()
#
#         mirror2lids = {}
#         # load mirrors
#         for i in range(num):
#             if num >= 2:
#                 if i == 0:
#                     prevFlag = self.iface.mapCanvas().renderFlag()
#                     self.iface.mapCanvas().setRenderFlag(False)
#                 elif i == num-1:
#                     self.iface.mapCanvas().setRenderFlag(True)
#
#             from dockableMirrorMap import DockableMirrorMap
#             dockwidget = DockableMirrorMap(self.iface.mainWindow(), self.iface)
#
#             minsize = dockwidget.minimumSize()
#             maxsize = dockwidget.maximumSize()
#
#             # restore position
#             floating, ok = QgsProject.instance().readBoolEntry("DockableMirrorMap", "/mirror%s/floating" % i)
#             if ok:
#                 dockwidget.setFloating( floating )
#                 position, ok = QgsProject.instance().readEntry("DockableMirrorMap", "/mirror%s/position" % i)
#                 if ok:
#                     try:
#                         if floating:
#                             parts = position.split(" ")
#                             if len(parts) >= 2:
#                                 dockwidget.move( int(parts[0]), int(parts[1]) )
#                         else:
#                             dockwidget.setLocation( int(position) )
#                     except ValueError:
#                         pass
#
#             # restore geometry
#             dockwidget.setFixedSize( dockwidget.geometry().width(), dockwidget.geometry().height() )
#             size, ok = QgsProject.instance().readEntry("DockableMirrorMap", "/mirror%s/size" % i)
#             if ok:
#                 try:
#                     parts = size.split(" ")
#                     dockwidget.setFixedSize( int(parts[0]), int(parts[1]) )
#                 except ValueError:
#                     pass
#
#
#             # get layer list
#             layerIds, ok = QgsProject.instance().readListEntry("DockableMirrorMap", "/mirror%s/layers" % i)
#             if ok: dockwidget.getMirror().setLayerSet( layerIds )
#
#             self.addDockWidget( dockwidget )
#             dockwidget.setMinimumSize(minsize)
#             dockwidget.setMaximumSize(maxsize)
