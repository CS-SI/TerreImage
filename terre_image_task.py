# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin                : 2014-05-20
        copyright            : (C) 2014 by CNES
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

import manage_QGIS
from working_layer import WorkingLayer
import terre_image_processing
from processing_manager import ProcessingManager
import OTBApplications

from qgis.core import QGis, QgsMapLayerRegistry
from qgis.gui import QgsRubberBand

from PyQt4.QtGui import QColor
from PyQt4.QtCore import QObject, SIGNAL, Qt

# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_task')
logger.setLevel(logging.INFO)


class TerreImageTask(object):
    def __init__(self, iface, working_dir, layer, mirror_map_tool):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.working_directory = working_dir
        self.layer = layer
        self.mirrormap_tool = mirror_map_tool
        self.histogram = None
        self.output_working_layer = None
        self.mirror = None

    def freezeCanvas(self, setFreeze):
        if setFreeze:
            if not self.iface.mapCanvas().isFrozen():
                self.iface.mapCanvas().freeze(True)
        else:
            if self.iface.mapCanvas().isFrozen():
                self.iface.mapCanvas().freeze(False)
                self.iface.mapCanvas().refresh()

    def end(self):
        if self.mirror:
            if self.mirror in self.mirrormap_tool.dockableMirrors:
                self.mirrormap_tool.dockableMirrors.remove(self.mirror)


class TerreImageProcessing(TerreImageTask, QObject):
    __pyqtSignals__ = ("display_ok()")

    def __init__(self, iface, working_dir, layer, mirror_map_tool, processing, arg=None, rlayer=None):
        """
        processing_type : [processing/display]
        """
        super(TerreImageProcessing, self).__init__(iface, working_dir, layer, mirror_map_tool)
        QObject.__init__(self)

        self.processing_name = processing
        self.mirror = None
        self.rubberband = None
        self.angle_tool = None

        self.r_layer = rlayer

        self.arg = None
        # print "arg", arg
        if arg:
            # print processing, "gave ", arg
            self.arg = arg

        self.run()

    def __str__(self):
        message = self.processing_name
        if self.output_working_layer.source_file:
            message += " : \t status ok \t image resultante :" + self.output_working_layer.source_file
            message += "\t mirror:" + str(self.mirror)

        return message

    def run(self):
        logger.debug("run, processing name" + str(self.processing_name))
        logger.debug("self.arg" + str(self.arg))
        output_filename = ""
        if "NDVI" in self.processing_name:
            output_filename = terre_image_processing.ndvi(self.layer, self.working_directory, self.iface)
        if "NDTI" in self.processing_name:
            output_filename = terre_image_processing.ndti(self.layer, self.working_directory, self.iface)
        if "Indice de brillance" in self.processing_name:
            output_filename = terre_image_processing.brightness(self.layer, self.working_directory, self.iface)
        if "Angle Spectral" in self.processing_name:
            self.rubberband = QgsRubberBand(self.canvas, QGis.Point)
            self.rubberband.setWidth(10)
            self.rubberband.setColor(QColor(Qt.yellow))
            if not self.arg:
                from spectral_angle import SpectralAngle
                self.angle_tool = SpectralAngle(self.iface, self.working_directory, self.layer, self.mirrormap_tool, self.rubberband)
                logger.debug("self.angle_tool" + str(self.angle_tool))
                QObject.connect(self.angle_tool, SIGNAL("anglesComputed(PyQt_PyObject)"), self.display)
                self.angle_tool.get_point_for_angles(self.layer)
                # spectral_angles(self.layer, self.working_directory, self.iface)
            else:
                output_filename = self.arg
        if "KMEANS" in self.processing_name:
            if self.arg:
                output_filename = terre_image_processing.kmeans(self.layer, self.working_directory, self.iface, self.arg)
            else:
                output_filename = terre_image_processing.kmeans(self.layer, self.working_directory, self.iface)
        if "Seuillage" in self.processing_name and self.arg:
            logger.debug("this is thrshold")
            output_filename = terre_image_processing.threshold(self.layer, self.working_directory, self.arg)
        if output_filename:
            OTBApplications.compute_overviews(output_filename)
            logger.debug(output_filename)
            self.display(output_filename)

    def get_filename_result(self):
        return self.output_working_layer.source_file

    def get_output_working_layer(self):
        if not isinstance(self.output_working_layer, WorkingLayer):
            # look for the file in the layers
            logger.debug(self.processing_name)
            raster_layers = manage_QGIS.get_raster_layers()
            for layer in raster_layers:
                if self.processing_name in layer.name:
                    self.output_working_layer.qgis_layer = layer
                    break
        else:
            return self.output_working_layer

    def display(self, output_filename):
        #         if "Angle Spectral" in self.processing_name:
        #             print self.rubberband
        #             print self.rubberband.getPoint(0)
        self.freezeCanvas(True)
        # result_layer = manage_QGIS.get_raster_layer( output_filename,
        # os.path.basename(os.path.splitext(self.layer.source_file)[0]) + "_" + self.processing_name )
        if self.r_layer:
            result_layer = self.r_layer
        else:
            result_layer = manage_QGIS.addRasterLayerToQGIS(output_filename, self.processing_name, self.iface)
            self.r_layer = result_layer
        if self.processing_name == "Seuillage":
            manage_QGIS.histogram_stretching_for_threshold(result_layer, self.iface.mapCanvas())
        else:
            manage_QGIS.histogram_stretching(result_layer, self.iface.mapCanvas())

        logger.debug("defining self.output_working_layer")
        self.output_working_layer = WorkingLayer(output_filename, result_layer)
        # 2 ouvrir une nouvelle vue
        self.mirror = self.mirrormap_tool.runDockableMirror(self.processing_name)
        logger.debug(self.mirror)
        self.mirror.mainWidget.addLayer(result_layer.id())
        self.mirror.mainWidget.onExtentsChanged()
        # 1 mettre image en queue

        iface_legend = self.iface.legendInterface()
        iface_layers = QgsMapLayerRegistry.instance().mapLayers()
        logger.debug("ifacelayers" + str(iface_layers))
        id_layer = result_layer.id()
        logger.debug("id_layer" + str(id_layer))
        logger.debug("result layer" + str(result_layer))
        # QgsMapLayerRegistry.instance().mapLayers()
        # {u'QB_1_ortho20140521141641682': <qgis.core.QgsRasterLayer object at 0x6592b00>,
        # u'QB_1_ortho_bande_bleue20140521141927295': <qgis.core.QgsRasterLayer object at 0x6592950>}
        iface_legend.setLayerVisible(result_layer, False)
        self.iface.mapCanvas().refresh()
        logger.debug(iface_legend.isLayerVisible(result_layer))

        ProcessingManager().add_processing(self)

        self.emit(SIGNAL("display_ok()"))
        logger.debug("signal emitted")
        # thaw the canvas
        self.freezeCanvas(False)


class TerreImageDisplay(TerreImageTask):

    def __init__(self, iface, working_dir, layer, mirror_map_tool, who, arg=None, rlayer=None):
        """
        processing_type : [processing/display]
        """
        super(TerreImageDisplay, self).__init__(iface, working_dir, layer, mirror_map_tool)

        self.corres = {'nat': "Couleurs naturelles", 'red': "Bande rouge", 'green': "Bande verte",
                       'blue': "Bande bleue", 'pir': "Bande pir", 'mir': "Bande mir"}

        self.who = who
        self.processing_name = self.corres[who]
        self.mirror = None

        self.arg = None
        if arg:
            self.arg = arg
        self.r_layer = rlayer
        self.run()

    def run(self):
        self.freezeCanvas(True)
        logger.debug("self.who" + str(self.who))
        if not self.r_layer:
            result_layer = manage_QGIS.display_one_band(self.layer, self.who, self.iface)
        else:
            result_layer = self.r_layer
        if result_layer:
            self.output_working_layer = WorkingLayer(self.layer.source_file, result_layer)
            self.mirror = self.mirrormap_tool.runDockableMirror(self.processing_name)
            logger.debug(self.mirror)
            self.mirror.mainWidget.addLayer(result_layer.id())
            self.mirror.mainWidget.onExtentsChanged()

            iface_legend = self.iface.legendInterface()
            iface_layers = QgsMapLayerRegistry.instance().mapLayers()
            logger.debug("ifacelayers" + str(iface_layers))
            # id_layer = result_layer.id()
            # logger.debug( "id_layer" + str( id_layer ))
            # logger.debug( "result layer" + str( result_layer ))
            # QgsMapLayerRegistry.instance().mapLayers()
            # {u'QB_1_ortho20140521141641682': <qgis.core.QgsRasterLayer object at 0x6592b00>,
            # u'QB_1_ortho_bande_bleue20140521141927295': <qgis.core.QgsRasterLayer object at 0x6592950>}
            iface_legend.setLayerVisible(result_layer, False)
            self.iface.mapCanvas().refresh()
            logger.debug(iface_legend.isLayerVisible(result_layer))

            ProcessingManager().add_display(self)
            # thaw the canvas
            self.freezeCanvas(False)

    def __str__(self):
        """
        Implements str method for debbuging
        """
        message = self.processing_name
        if self.output_working_layer.source_file:
            message += "\t mirror:" + str(self.mirror)
        return message
