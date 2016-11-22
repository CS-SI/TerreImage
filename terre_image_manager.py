# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2014-05-06
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
import os

from PyQt4 import QtCore, QtGui
import terre_image_utils
from qgis.core import QgsMapLayerRegistry
from processing_manager import ProcessingManager

from valuetool.valuewidget import ValueWidget
from DockableMirrorMap.dockableMirrorMapPlugin import DockableMirrorMapPlugin
from ClassificationSupervisee.supervisedclassificationdialog import SupervisedClassificationDialog

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()


class TerreImageManager(QtCore.QObject):

    essai = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)
    tapped = QtCore.Signal()

    def __init__(self, iface):
        QtCore.QObject.__init__(self)
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.working_directory = None  # , _ = terre_image_utils.fill_default_directory()
        self.layer = None
        # settrace()
        self.value_tool = ValueWidget(self.iface)  # , self )
        self.valuedockwidget = None

        self.mirror_map_tool = DockableMirrorMapPlugin(self.iface)
        self.mirror_map_tool.initGui()
        QtCore.QObject.connect(self.mirror_map_tool, QtCore.SIGNAL("mirrorClosed(PyQt_PyObject)"), self.view_closed)

        # self.angle_tool = SpectralAngle(self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool)

        self.classif_tool = SupervisedClassificationDialog(self.iface)
        self.updated.emit(1)
        # self.classif_tool.setupUi()

    def set_value_tool_dock_widget(self):
        # creating a dock widget
        # create the dockwidget with the correct parent and add the valuewidget
        self.valuedockwidget = QtGui.QDockWidget("Valeurs spectrales", self.iface.mainWindow())
        self.valuedockwidget.setObjectName("Valeurs spectrales")
        self.valuedockwidget.setWidget(self.value_tool)
        self.iface.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.valuedockwidget)
        self.valuedockwidget.hide()
        logger.info(self.value_tool)


    def set_current_layer(self):
        self.layer, bands = terre_image_utils.get_workinglayer_on_opening(self.iface)
        if self.layer:
            self.working_directory = os.path.join(os.path.dirname(self.layer.source_file), "working_directory")
            terre_image_utils.update_subdirectories(self.working_directory)
            if not os.path.exists(self.working_directory):
                os.makedirs(self.working_directory)
            ProcessingManager().working_layer = self.layer
            self.classif_tool.set_layers(ProcessingManager().get_qgis_working_layers(), self.layer.get_qgis_layer(), self.layer.band_invert)
            self.classif_tool.set_directory(self.working_directory)
            self.classif_tool.setupUi()
        # self.layers_for_value_tool.append(self.layer ) #.get_qgis_layer())
        logger.debug("working directory")

        return self.layer, bands

    def __str__(self):
        sortie = "working_dir : " + self.working_directory
        return sortie

    def restore_processing_manager(self, filename, bands, layer_type, working_dir):
        self.layer, bands = terre_image_utils.restore_working_layer(filename, bands, layer_type)
        ProcessingManager().working_layer = self.layer
        # self.layers_for_value_tool.append(self.layer )
        self.working_directory = working_dir
        return self.layer, bands

    def display_values(self):
        if self.valuedockwidget is None :
            self.set_value_tool_dock_widget()
        logger.debug("dispkay values 123456789")
        self.valuedockwidget.show()
        self.value_tool.changeActive(QtCore.Qt.Checked)
        self.value_tool.cbxActive.setCheckState(QtCore.Qt.Checked)
        self.value_tool.set_layers(ProcessingManager().get_working_layers())

    def view_closed(self, name_of_the_closed_view):
        # logger.debug("{} has been closed".format(str(name_of_the_closed_view)))
        self.essai.emit()
        self.tapped.emit()
        logger.debug("Trying to emit something")
        logger.debug("{} has been closed".format(name_of_the_closed_view))
        process = ProcessingManager().processing_from_name(name_of_the_closed_view)
        logger.debug("{}".format(process))
        if process:
            loaded_layers_id = [x.id() for x in self.iface.legendInterface().layers()]
            logger.debug(loaded_layers_id)
            if process[0] and process[0].output_working_layer and process[0].output_working_layer.qgis_layer and \
                process[0].output_working_layer.qgis_layer.id():
                if process[0].output_working_layer.qgis_layer.id() in loaded_layers_id:
                    QgsMapLayerRegistry.instance().removeMapLayer(process[0].output_working_layer.qgis_layer.id())

            try:
                ProcessingManager().remove_processing(process[0])
                ProcessingManager().remove_display(process[0])
            except KeyError:
                pass
            else:
                logger.debug("ProcessingChanged signal emitted")

    def removing_layer(self, layer_id):
        ProcessingManager().remove_process_from_layer_id(layer_id)

    def disconnect(self):
        logger.debug("Disconnect")
        # disconnect value tool
        self.iface.mainWindow().statusBar().clearMessage()
        logger.debug("Statusbar cleared")
        try:
            self.value_tool.changeActive(QtCore.Qt.Unchecked)
            self.value_tool.set_layers([])
            self.value_tool.close()
            self.value_tool.disconnect()
            self.value_tool = None
        except AttributeError:
            pass
        logger.debug("ValueTool cleared")

        # disconnect dockable mirror map
        self.mirror_map_tool.unload()
        logger.debug("Mirror map tool unloaded")

        # remove the dockwidget from iface
        if self.valuedockwidget:
            self.iface.removeDockWidget(self.valuedockwidget)
            logger.debug("Remove dock widget")
