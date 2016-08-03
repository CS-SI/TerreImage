# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2014-04-30
        copyright           : (C) 2014 by CNES
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QObject, SIGNAL, Qt
from PyQt4.QtGui import QIcon, QAction, QMessageBox, QColor
from qgis.core import QgsProject, QGis, QgsPoint
from qgis.gui import QgsMessageBar, QgsRubberBand

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from qgiseducationwidget import QGISEducationWidget
from qgiseducationwidget import Terre_Image_Main_Dock_widget

from terre_image_task import TerreImageProcessing
from terre_image_task import TerreImageDisplay
from terre_image_manager import TerreImageManager
import terre_image_utils
import time
from terre_image_constant import TerreImageConstant
from processing_manager import ProcessingManager
# from supervisedclassification import SupervisedClassification
from terre_image_environement import TerreImageParamaters

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()


class QGISEducation:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.constants = TerreImageConstant()
        self.constants.iface = self.iface
        self.constants.canvas = self.iface.mapCanvas()
        self.constants.legendInterface = self.iface.legendInterface()

    def initGui(self):
        """
        Initialisation on the widget interface
        """
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/qgiseducation/img/icon.png"),
            u"Terre Image", self.iface.mainWindow())
        self.action.setWhatsThis("Terre Image")
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        self.aboutAction = QAction(QIcon(":/plugins/DockableMirrorMap/icons/about.png"), "About", self.iface.mainWindow())
        QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&TerreImage", self.action)
        self.iface.addPluginToMenu("TerreImage", self.aboutAction)

        self.qgisedudockwidget = None
        self.dockOpened = False
        self.educationWidget = None

        QObject.connect(self.iface, SIGNAL("projectRead()"), self.onProjectLoaded)
        QObject.connect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.onWriteProject)
        QObject.connect(self.iface, SIGNAL("newProjectCreated()"), self.newProject)


    def do_display_one_band(self, who, qgis_layer, working_directory, mirror_tool):
        logger.debug("who {}".format(who))
        # manage_QGIS.display_one_band(self.qgis_education_manager.layer, who, self.iface)
        if qgis_layer:
            my_process = TerreImageDisplay(self.iface, working_directory, ProcessingManager().working_layer, mirror_tool, who, None, qgis_layer)
        else:
            my_process = TerreImageDisplay(self.iface, working_directory, ProcessingManager().working_layer, mirror_tool, who)
        # ProcessingManager().add_processing(my_process)
        self.educationWidget.set_combobox_histograms()


    def unload(self):
        """
        Defines the unload of the plugin
        """
        self.unload_interface()
            # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&TerreImage", self.action)
        self.iface.removeToolBarIcon(self.action)

    def unload_interface(self):
        if self.qgisedudockwidget is not None and self.educationWidget is not None:
            self.qgisedudockwidget.close()
            self.educationWidget.disconnectP()

    # run method that performs all the real work
    def run(self):
        """
        Defines the behavior of the plugin
        """
        timeBegin = time.time()
        # self.educationWidget.set_working_message(True)

        self.iface.newProject(True)

        # self.qgis_education_manager = TerreImageManager(self.iface)
        # _, bands  = self.qgis_education_manager.set_current_layer( )

        _, bands, working_dir = terre_image_utils.set_current_layer(self.iface)

        timeEnd = time.time()
        timeExec = timeEnd - timeBegin
        logger.info("temps de chargement: {}".format(timeExec))

        self.show_education_widget(bands, working_dir)

        # self.educationWidget.set_working_message(False)

    def show_education_widget(self, bands, working_dir):
        if ProcessingManager().working_layer and bands:

            if not self.dockOpened:
                # create the widget to display information
                self.educationWidget = QGISEducationWidget(self.iface)
                QObject.connect(self.educationWidget, SIGNAL("terminated()"), self.unload_interface)
                # self.educationWidget.qgis_education_manager = self.qgis_education_manager
                self.educationWidget.qgis_education_manager = TerreImageManager(self.iface)
                self.educationWidget.qgis_education_manager.working_directory = working_dir
                self.educationWidget.lineEdit_working_dir.setText(working_dir)

                self.educationWidget.qgis_education_manager.classif_tool.set_layers(ProcessingManager().get_qgis_working_layers(), ProcessingManager().working_layer.get_qgis_layer(), ProcessingManager().working_layer.band_invert)
                self.educationWidget.qgis_education_manager.classif_tool.set_directory(working_dir)
                self.educationWidget.qgis_education_manager.classif_tool.setupUi()

                # create the dockwidget with the correct parent and add the valuewidget
                self.qgisedudockwidget = Terre_Image_Main_Dock_widget("Terre Image", self.iface.mainWindow(), self.iface)
                self.qgisedudockwidget.setObjectName("Terre Image")
                self.qgisedudockwidget.setWidget(self.educationWidget)
                QObject.connect(self.qgisedudockwidget, SIGNAL("closed(PyQt_PyObject)"), self.close_dock)

                # add the dockwidget to iface
                self.iface.addDockWidget(Qt.RightDockWidgetArea, self.qgisedudockwidget)
                self.educationWidget.set_comboBox_sprectral_band_display()

            text = "Plan R <- BS_PIR \nPlan V <- BS_R \nPlan B <- BS_V"

            self.qgisedudockwidget.show()
            self.dockOpened = True

    def about(self):
        from terre_image_about import DlgAbout
        DlgAbout(self.iface.mainWindow()).exec_()

    def close_dock(self, object):
        self.qgisedudockwidget = None
        self.dockOpened = False
        self.educationWidget = None
        if self.iface.legendInterface().layers() != []:
            self.iface.newProject()

    def newProject(self):
        for item in self.iface.mapCanvas().scene().items():
            if isinstance(item, QgsRubberBand):
                item.reset(QGis.Point)
        if self.educationWidget is not None:
            self.educationWidget.disconnect_interface()
            if self.qgisedudockwidget is not None:
                self.qgisedudockwidget.close()
                self.educationWidget.disconnectP()
                self.dockOpened = False

        self.qgisedudockwidget = None
        self.dockOpened = False
        self.educationWidget = None

    def onWriteProject(self, domproject):
        if ProcessingManager().working_layer is None:
            return

#         QgsProject.instance().writeEntry( "QGISEducation", "/working_layer", self.qgis_education_manager.layer.source_file )
#         # write band orders
#         QgsProject.instance().writeEntry( "QGISEducation", "/working_layer_bands", str(self.qgis_education_manager.layer.bands) )
#         logger.debug( str(self.qgis_education_manager.layer.bands) )
#         QgsProject.instance().writeEntry( "QGISEducation", "/working_layer_type", self.qgis_education_manager.layer.type )
#         QgsProject.instance().writeEntry( "QGISEducation", "/working_directory", self.qgis_education_manager.working_directory )
        QgsProject.instance().writeEntry("QGISEducation", "/working_layer", ProcessingManager().working_layer.source_file)
        # write band orders
        QgsProject.instance().writeEntry("QGISEducation", "/working_layer_bands", str(ProcessingManager().working_layer.bands))
        logger.debug("{}".format(ProcessingManager().working_layer.bands))
        QgsProject.instance().writeEntry("QGISEducation", "/working_layer_type", ProcessingManager().working_layer.type)
        QgsProject.instance().writeEntry("QGISEducation", "/working_directory", self.educationWidget.qgis_education_manager.working_directory)
        p = []
        for process in ProcessingManager().get_processings():
            p.append((process.processing_name, process.output_working_layer.get_source()))
        # print "process", p

        QgsProject.instance().writeEntry("QGISEducation", "/process", str(p))
        QgsProject.instance().writeEntry("QGISEducation", "/index_group", self.constants.index_group)

        if "Angle Spectral" in ProcessingManager().get_processings_name():
            # delete rubberband
            for item in self.iface.mapCanvas().scene().items():
                # item is a rubberband
                if isinstance(item, QgsRubberBand):
                    # get point
                    if item.size() > 0:
                        point = item.getPoint(0)
                        # print point
                        QgsProject.instance().writeEntryDouble("QGISEducation", "/angle_spectral_point_x", point.x())
                        QgsProject.instance().writeEntryDouble("QGISEducation", "/angle_spectral_point_y", point.y())

        p = TerreImageParamaters()
        if p.is_complete():
            QgsProject.instance().writeEntryDouble("QGISEducation", "/red_x_min", p.red_min)
            QgsProject.instance().writeEntryDouble("QGISEducation", "/red_x_max", p.red_max)
            QgsProject.instance().writeEntryDouble("QGISEducation", "/green_x_min", p.green_min)
            QgsProject.instance().writeEntryDouble("QGISEducation", "/green_x_max", p.green_max)
            QgsProject.instance().writeEntryDouble("QGISEducation", "/blue_x_min", p.blue_min)
            QgsProject.instance().writeEntryDouble("QGISEducation", "/blue_x_max", p.blue_max)


    def onProjectLoaded(self):
        # does not work stops the project reading.
        # should desactivate all interface and read the project again
        # self.newProject( True )

        # restore mirrors?
        wl, ok = QgsProject.instance().readEntry("QGISEducation", "/working_layer")
        if not ok or wl == "":
            pass

        if not wl == "":

            bands, ok = QgsProject.instance().readEntry("QGISEducation", "/working_layer_bands")
            logger.debug("is ok" + str(ok))
            logger.debug(bands)

            # working_layer = WorkingLayer(wl, None, bands)

            # TODO interpreter bands
            type, ok = QgsProject.instance().readEntry("QGISEducation", "/working_layer_type")

            working_dir, ok = QgsProject.instance().readEntry("QGISEducation", "/working_directory")

            layer, bands = terre_image_utils.restore_working_layer(wl, eval(bands), type)
            ProcessingManager().working_layer = layer

            self.show_education_widget(bands, working_dir)
    #         self.qgis_education_manager = TerreImageManager( self.iface )
    #         self.qgis_education_manager.restore_processing_manager(wl, eval(bands), type, working_dir)
    #         if self.qgis_education_manager:


            process, ok = QgsProject.instance().readEntry("QGISEducation", "/process")
            logger.debug(eval(process))

            index_group, ok = QgsProject.instance().readDoubleEntry("QGISEducation", "/index_group")
            self.constants.index_group = int(float(index_group))

            process = eval(process)

            for qgis_layer in self.iface.legendInterface().layers():
                # print "layer loading ", qgis_layer.name()
                if qgis_layer.name() in [ "NDVI", "NDTI", "Indice de brillance", "KMEANS" ]:
                    process = TerreImageProcessing(self.iface, working_dir, ProcessingManager().working_layer, self.educationWidget.qgis_education_manager.mirror_map_tool, qgis_layer.name(), None, qgis_layer)
                elif "Angle Spectral" in qgis_layer.name():
                    process = TerreImageProcessing(self.iface, working_dir, ProcessingManager().working_layer, self.educationWidget.qgis_education_manager.mirror_map_tool, qgis_layer.name(), qgis_layer.source(), qgis_layer)
                    # ProcessingManager().add_processing(process)
                elif "couleur_naturelles" in  qgis_layer.name():
                    try:
                        self.do_display_one_band('nat', qgis_layer, working_dir, self.educationWidget.qgis_education_manager.mirror_map_tool)
                    except AttributeError:
                        QMessageBox.warning(None , "Erreur", u'Le projet ne peut être lu. Essayez de créer un projet vierge, puis de réouvrir le projet souhaité.', QMessageBox.Ok)
                        # self.newProject(  )
                        return None
                    # ProcessingManager().add_display( process )

                else:
                    corres = { 'red':"_bande_rouge", 'green':"_bande_verte", 'blue':"_bande_bleue", 'pir':"_bande_pir", 'mir':"_bande_mir", "nat":"_couleurs_naturelles" }
                    result = [x for x in corres if qgis_layer.name().endswith(corres[x])]
                    # print result
                    if result:
                        # print "the couleur", result[0]
                        try:
                            self.do_display_one_band(result[0], qgis_layer, working_dir, self.educationWidget.qgis_education_manager.mirror_map_tool)
                        except AttributeError:
                            QMessageBox.warning(None , "Erreur", u'Le projet ne peut être lu. Essayez de créer un projet vierge, puis de réouvrir le projet souhaité.', QMessageBox.Ok)
                            # self.newProject(  )
                            return None
                    # ProcessingManager().add_display( process )

            angle_spectral_point_x, ok_x = QgsProject.instance().readDoubleEntry("QGISEducation", "/angle_spectral_point_x")
            angle_spectral_point_y, ok_y = QgsProject.instance().readDoubleEntry("QGISEducation", "/angle_spectral_point_y")
            # print "angle_spectral_point_x, angle_spectral_point_y", angle_spectral_point_x, angle_spectral_point_y
            if ok_x and ok_y:
                # print "angle_spectral_point_x, angle_spectral_point_y", angle_spectral_point_x, angle_spectral_point_y
                p = ProcessingManager().processing_from_name("Angle Spectral")
                if p:
                    rubberband = p[0].rubberband
                    rubberband.setWidth(10)
                    rubberband.setColor(QColor(Qt.yellow))
                    rubberband.addPoint(QgsPoint(float(angle_spectral_point_x), float(angle_spectral_point_y)))

            p = TerreImageParamaters()
            p.red_min = QgsProject.instance().readDoubleEntry("QGISEducation", "/red_x_min")[0]
            p.red_max = QgsProject.instance().readDoubleEntry("QGISEducation", "/red_x_max")[0]
            p.green_min = QgsProject.instance().readDoubleEntry("QGISEducation", "/green_x_min")[0]
            p.green_max = QgsProject.instance().readDoubleEntry("QGISEducation", "/green_x_max")[0]
            p.blue_min = QgsProject.instance().readDoubleEntry("QGISEducation", "/blue_x_min")[0]
            p.blue_max = QgsProject.instance().readDoubleEntry("QGISEducation", "/blue_x_max")[0]

            self.educationWidget.set_combobox_histograms()
            self.iface.mapCanvas().refresh()
            self.iface.mapCanvas().repaint()
