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

from PyQt4.QtCore import Qt, QObject, SIGNAL, QSettings
from PyQt4.QtGui import QWidget, QGridLayout, QColor

from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer

# import logging for debug messages
from TerreImage import terre_image_logging
logger = terre_image_logging.configure_logger()


class MirrorMap(QWidget):

    def __init__(self, parent, iface):
        QWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.iface = iface
        self.layerId2canvasLayer = {}
        self.canvasLayers = []

        self.setupUi()

    def closeEvent(self, event):
        # self.scaleFactor.valueChanged.disconnect(self.onExtentsChanged)
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("extentsChanged()"), self.onExtentsChanged)
        QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL("destinationCrsChanged()"), self.onCrsChanged)
        QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL("mapUnitsChanged()"), self.onCrsChanged)
        QObject.disconnect(self.iface.mapCanvas().mapRenderer(), SIGNAL("hasCrsTransformEnabled(bool)"), self.onCrsTransformEnabled)
        QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.delLayer)
        QObject.disconnect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.refreshLayerButtons)

        self.emit(SIGNAL("closed(PyQt_PyObject)"), self)
        return QWidget.closeEvent(self, event)

    def setupUi(self):
        self.setObjectName("dockablemirrormap_mirrormap")

        gridLayout = QGridLayout(self)
        gridLayout.setContentsMargins(0, 0, gridLayout.verticalSpacing(), gridLayout.verticalSpacing())

        self.canvas = QgsMapCanvas(self)
        self.canvas.setCanvasColor(QColor(255, 255, 255))
        settings = QSettings()
        self.canvas.enableAntiAliasing(settings.value("/qgis/enable_anti_aliasing", False, type=bool))
        self.canvas.useImageToRender(settings.value("/qgis/use_qimage_to_render", False, type=bool))
        self.canvas.setWheelAction(3)
        gridLayout.addWidget(self.canvas, 0, 0, 1, 5)

        QObject.connect(self.iface.mapCanvas(), SIGNAL("extentsChanged()"), self.onExtentsChanged)
        QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL("destinationCrsChanged()"), self.onCrsChanged)
        QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL("mapUnitsChanged()"), self.onCrsChanged)
        QObject.connect(self.iface.mapCanvas().mapRenderer(), SIGNAL("hasCrsTransformEnabled(bool)"), self.onCrsTransformEnabled)
        QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.delLayer)

        self.onExtentsChanged()
        self.onCrsChanged()
        self.onCrsTransformEnabled(self.iface.mapCanvas().hasCrsTransformEnabled())

    def toggleRender(self, enabled):
        self.canvas.setRenderFlag(enabled)
        self.canvas.refresh()
        self.canvas.repaint()

    def onExtentsChanged(self):
        try :
            prevFlag = self.canvas.renderFlag()
            self.canvas.setRenderFlag(False)

            self.canvas.setExtent(self.iface.mapCanvas().extent())
            # self.canvas.zoomByFactor( self.scaleFactor.value() )

            self.canvas.setRenderFlag(prevFlag)
            self.canvas.repaint()
            self.canvas.refresh()
        except Exception:
            pass

    def mirror_extent_changed(self):
        logger.debug(self.canvas.extent())
        logger.debug(self.iface.mapCanvas().extent())
        if self.canvas.extent() != self.iface.mapCanvas().extent():
            self.emit(SIGNAL("extentChanged( QgsRectangle )"), self.canvas.extent())

    def onCrsChanged(self):
        try:
            prevFlag = self.canvas.renderFlag()
            self.canvas.setRenderFlag(False)

            renderer = self.iface.mapCanvas().mapRenderer()
            self._setRendererCrs(self.canvas.mapRenderer(), self._rendererCrs(renderer))
            self.canvas.mapRenderer().setMapUnits(renderer.mapUnits())

            self.canvas.setRenderFlag(prevFlag)
            self.canvas.repaint()
            self.canvas.refresh()

        except Exception:
            pass

    def onCrsTransformEnabled(self, enabled):
        try:
            prevFlag = self.canvas.renderFlag()
            self.canvas.setRenderFlag(False)

            self.canvas.mapRenderer().setProjectionsEnabled(enabled)

            self.canvas.setRenderFlag(prevFlag)
            self.canvas.repaint()
            self.canvas.refresh()
        except Exception:
            pass

    def getLayerSet(self):
        return map(lambda x: self._layerId(x.layer()), self.canvasLayers)

    def setLayerSet(self, layerIds=None):
        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        if layerIds is None:
            self.layerId2canvasLayer = {}
            self.canvasLayers = []
            self.canvas.setLayerSet([])

        else:
            for lid in layerIds:
                self.addLayer(lid)

        self.onExtentsChanged()

        self.canvas.setRenderFlag(prevFlag)
        self.canvas.repaint()
        self.canvas.refresh()

    def addLayer(self, layerId = None):
        if layerId is None:
            layer = self.iface.activeLayer()
        else:
            layer = QgsMapLayerRegistry.instance().mapLayer(layerId)

        if layer is None:
            return

        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        # add the layer to the map canvas layer set
        self.canvasLayers = []
        id2cl_dict = {}
        for l in self.iface.legendInterface().layers():
            lid = self._layerId(l)
            if self.layerId2canvasLayer.has_key(lid):  # previously added
                cl = self.layerId2canvasLayer[ lid ]
            elif l == layer:  # selected layer
                cl = QgsMapCanvasLayer(layer)
            else:
                continue

            id2cl_dict[ lid ] = cl
            self.canvasLayers.append(cl)

        self.layerId2canvasLayer = id2cl_dict
        self.canvas.setLayerSet(self.canvasLayers)

        self.onExtentsChanged()
        self.canvas.setRenderFlag(prevFlag)
        self.canvas.repaint()
        self.canvas.refresh()

    def delLayer(self, layerId=None):
        try :
            if layerId is None:
                layer = self.iface.activeLayer()
                if layer is None:
                    return
                layerId = self._layerId(layer)

            # remove the layer from the map canvas layer set
            if layerId not in self.layerId2canvasLayer:
                return

            prevFlag = self.canvas.renderFlag()
            self.canvas.setRenderFlag(False)

            cl = self.layerId2canvasLayer[ layerId ]
            if cl is not None:
                del self.layerId2canvasLayer[ layerId ]
            self.canvasLayers.remove(cl)
            self.canvas.setLayerSet(self.canvasLayers)
            del cl

            self.onExtentsChanged()
            self.canvas.setRenderFlag(prevFlag)
            self.canvas.repaint()
            self.canvas.refresh()
        except RuntimeError:
            pass

    def _layerId(self, layer):
        if hasattr(layer, 'id'):
            return layer.id()
        return layer.getLayerID()

    def _rendererCrs(self, renderer):
        if hasattr(renderer, 'destinationCrs'):
            return renderer.destinationCrs()
        return renderer.destinationSrs()

    def _setRendererCrs(self, renderer, crs):
        if hasattr(renderer, 'setDestinationCrs'):
            return renderer.setDestinationCrs(crs)
        return renderer.setDestinationSrs(crs)
