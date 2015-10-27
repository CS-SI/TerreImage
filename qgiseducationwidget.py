# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducationDialog
                                 A QGIS plugin
 TerreImage
                             -------------------
        begin                : 2014-04-30
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

from PyQt4 import QtCore, QtGui
from ui_qgiseducation import Ui_QGISEducation

# import GDAL and QGIS libraries
from osgeo import gdal
from qgis.gui import QgsRubberBand, QgsMessageBar
from qgis.core import QGis, QgsMapLayerRegistry

# import project libraries
from terre_image_task import TerreImageProcessing
from terre_image_task import TerreImageDisplay
import terre_image_utils
import terre_image_processing
from terre_image_histogram import TerreImageHistogram_multiband
from terre_image_histogram import TerreImageHistogram_monoband
from terre_image_manager import TerreImageManager
from processing_manager import ProcessingManager

# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_qgiseducationwidget')
logger.setLevel(logging.INFO)


class Terre_Image_Dock_widget(QtGui.QDockWidget):
    """
    Custom widget to catch signal when closed
    """
    __pyqtSignals__ = ("closed(PyQt_PyObject)")

    def __init__(self, title, parent):
        QtGui.QDockWidget.__init__(self, title, parent)

    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL("closed(PyQt_PyObject)"), self)


class Terre_Image_Main_Dock_widget(QtGui.QDockWidget):
    """
    Custom widget for the main plugin ui. Catches closed signal and ask the user
    """
    __pyqtSignals__ = ("closed(PyQt_PyObject)")

    def __init__(self, title, parent, iface):
        QtGui.QDockWidget.__init__(self, title, parent)
        self.iface = iface

    def closeEvent(self, event):
        if self.iface.legendInterface().layers() != []:
            res = QtGui.QMessageBox.question(self, "TerreImage", "Voulez vous vraiment quitter TerreImage ?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Yes)

            if res != QtGui.QMessageBox.Yes:
                event.ignore()
            else:
                event.accept()
                self.emit(QtCore.SIGNAL("closed(PyQt_PyObject)"), self)


class QGISEducationWidget(QtGui.QWidget, Ui_QGISEducation, QtCore.QObject):
    """
    Main widget
    """
    __pyqtSignals__ = ("valueChanged()")

    def __init__(self, iface):

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        QtGui.QWidget.__init__(self)
        QtCore.QObject.__init__(self)
        self.setupUi(self)
        self.setupUi_extra()

        self.qgis_education_manager = TerreImageManager(self.iface)
        self.lineEdit_working_dir.setText(self.qgis_education_manager.working_directory)

        QtCore.QObject.connect(QgsMapLayerRegistry.instance(), QtCore.SIGNAL("layerWillBeRemoved(QString)"), self.layer_deleted)

        self.dock_histo_opened = False

    def setupUi_extra(self):
        """
        Initialize the interface
        """
        self.toolbar = self.iface.addToolBar(u'TerrImage')
        self.toolbar.setObjectName(u'TerrImage')

        #processings
        itemProcessing = [ "Traitements...", "NDVI", "NDTI", "Indice de brillance", "Angle Spectral" ]
        # toolbar
        self.toolButton_processing = QtGui.QToolButton()
        self.toolButton_processing.setMenu(QtGui.QMenu())
        self.toolButton_processing.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        # self.iface.addToolBarWidget(self.toolButton_processing)
        self.toolbar.addWidget(self.toolButton_processing)
        m = self.toolButton_processing.menu()

        for index, item in enumerate(itemProcessing):
            self.comboBox_processing.insertItem(index, item)
            # toolbar
            #if index > 0:
            action_p = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/mAction.png"),
                                     item,
                                     self.iface.mainWindow())
            action_p.setWhatsThis(item)
            m.addAction(action_p)
            if index == 0:
                self.toolButton_processing.setDefaultAction(action_p)

        self.comboBox_processing.currentIndexChanged[str].connect(self.do_manage_processing)
        self.toolButton_processing.triggered.connect(self.do_manage_actions_for_processing)

        # fill histograms
        self.toolButton_histograms = QtGui.QToolButton()
        self.toolButton_histograms.setMenu(QtGui.QMenu())
        self.toolButton_histograms.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        # self.iface.addToolBarWidget(self.toolButton_histograms) 
        self.toolbar.addWidget(self.toolButton_histograms)
        m2 = self.toolButton_histograms.menu()

        itemHistogrammes = [ "Histogrammes", "Image de travail" ]
        for index, item in enumerate(itemHistogrammes):
            self.comboBox_histogrammes.insertItem(index, item)
            # toolbar
            #if index > 0:
            action_h = QtGui.QAction(
              QtGui.QIcon(":/plugins/qgiseducation/img/mActionFullHistogramStretch.png"),
              item,
              self.iface.mainWindow())
            action_h.setWhatsThis(item)
            m2.addAction(action_h)
            if index == 0:
                self.toolButton_histograms.setDefaultAction(action_h)
        self.comboBox_histogrammes.currentIndexChanged[str].connect(self.do_manage_histograms)
        self.toolButton_histograms.triggered.connect(self.do_manage_actions_for_histogram)

        # widget puttons signal connections
        self.pushButton_kmeans.clicked.connect(self.kmeans)
        self.pushButton_profil_spectral.clicked.connect(self.display_values)
        self.pushButton_working_dir.clicked.connect(self.define_working_dir)
        self.pushButton_status.clicked.connect(self.status)
        self.pushButton_status.hide()
        self.pushButton_histogramme.hide()
        self.pushButton_histogramme.clicked.connect(self.main_histogram)
        self.pushButton_plugin_classification.clicked.connect(self.plugin_classification)
        self.pushButton_kmz.clicked.connect(self.export_kmz)
        QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.display_metadata)

        # hide information labels
        self.label_a_s.hide()
        self.label_a_s_img.hide()
        self.label_a_s_img.setPixmap(QtGui.QPixmap(":/plugins/qgiseducation/img/legende.png"))
        self.label_travail_en_cours.hide()
        self.label_travail_en_cours.setTextFormat(1)
        self.label_travail_en_cours.setText('<html><b><font size="4" color="red">Travail en cours...</font></b></html>')

        # toolbar
        self.toolButton_display_bands = QtGui.QToolButton()
        self.toolButton_display_bands.setMenu(QtGui.QMenu())
        self.toolButton_display_bands.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        # self.iface.addToolBarWidget(self.toolButton_display_bands)
        self.toolbar.addWidget(self.toolButton_display_bands)

        action_ps = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/mIconTableLayer.png"),
                                  "Profil Spectral", self.iface.mainWindow())
        action_ps.setWhatsThis(u"Profil spectral")
        self.toolbar.addAction(action_ps)
        action_ps.triggered.connect(self.display_values)

        # toolbar classif
        self.toolButton_classif = QtGui.QToolButton()
        self.toolButton_classif.setMenu(QtGui.QMenu())
        self.toolButton_classif.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        # self.iface.addToolBarWidget(self.toolButton_histograms)
        self.toolbar.addWidget(self.toolButton_classif)
        m4 = self.toolButton_classif.menu()
        action_classif_ns = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/rendererCategorizedSymbol.png"),
                                          u"Classification non supervisée", self.iface.mainWindow())
        action_classif_ns.setWhatsThis(u"Classification non supervisée")
        m4.addAction(action_classif_ns)
        action_classif_ns.triggered.connect(self.kmeans)
        action_classif_s = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/rendererCategorizedSymbol.png"),
                                         u"Classification supervisée", self.iface.mainWindow())
        action_classif_s.setWhatsThis(u"Classification supervisée")
        m4.addAction(action_classif_s)
        self.toolButton_classif.setDefaultAction(action_classif_ns)
        action_classif_s.triggered.connect(self.plugin_classification)

        action_kmz = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/mMapserverExport.png"),
                                   "Export KMZ", self.iface.mainWindow())
        action_kmz.setWhatsThis(u"Export KMZ")
        self.toolbar.addAction(action_kmz)
        action_kmz.triggered.connect(self.export_kmz)

        action_info = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/mActionContextHelp.png"),
                                    "Information", self.iface.mainWindow())
        action_info.setWhatsThis(u"Information")
        self.toolbar.addAction(action_info)

        action_settings = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/mActionOptions.png"),
                                        "Configuration", self.iface.mainWindow())
        action_settings.setWhatsThis(u"Configuration")
        self.toolbar.addAction(action_settings)

    def status(self):
        """
        Function for debug
        """
        print "############# Status #############"
        print(self.qgis_education_manager)
        print("self.qgis_education_manager.mirror_map_tool.dockableMirrors " + str(self.qgis_education_manager.mirror_map_tool.dockableMirrors)) + "\n"
        print ProcessingManager()
        print ProcessingManager().get_processings_name()
        print "layers value tool "
        print self.qgis_education_manager.value_tool.layers_to_display
        print "##########################"

    def plugin_classification(self):
        """
        Opens the classification plugin
        """
        self.qgis_education_manager.classif_tool.show()
        self.qgis_education_manager.classif_tool.update_layers(ProcessingManager().get_qgis_working_layers())

    def main_histogram(self):
        """
        Display the histogram of the working image
        """
        self.set_working_message(True)
        if not self.dock_histo_opened:
            self.hist = TerreImageHistogram_multiband(ProcessingManager().working_layer, self.canvas)
            self.histodockwidget = Terre_Image_Dock_widget("Histogrammes", self.iface.mainWindow())
            self.histodockwidget.setObjectName("Histogrammes")
            self.histodockwidget.setWidget(self.hist)
            self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.histodockwidget)
            QtCore.QObject.connect(self.hist, QtCore.SIGNAL("threshold(PyQt_PyObject)"), self.histogram_threshold)
            QtCore.QObject.connect(self.histodockwidget, QtCore.SIGNAL("closed(PyQt_PyObject)"), self.histogram_closed)
        self.dock_histo_opened = True
        self.set_working_message(False)

    def histogram_closed(self):
        """
        Called when the dock of the main histogram is closed.
        Set histogram flag to false
        """
        self.dock_histo_opened = False

    def histogram(self, layer_source, processing=None, specific_band=-1, hist=None):
        """
        Display the histogram of the specific processing
        """
        logger.debug("self.histogram")
        self.set_working_message(True)

        if hist is None:
            hist = TerreImageHistogram_monoband(layer_source, self.canvas, processing, specific_band)
        if hist.dock_opened is False:
            histodockwidget = Terre_Image_Dock_widget("Histogrammes", self.iface.mainWindow())
            histodockwidget.setObjectName("Histogrammes")
            histodockwidget.setWidget(hist)
            histodockwidget.setFloating(True)
            histodockwidget.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
            QtCore.QObject.connect(hist, QtCore.SIGNAL("threshold(PyQt_PyObject)"), self.threshold_on_histogram)
            self.iface.addDockWidget(QtCore.Qt.BottomDockWidgetArea, histodockwidget)
            QtCore.QObject.connect(histodockwidget, QtCore.SIGNAL("closed(PyQt_PyObject)"), self.histogram_monoband_closed)
            hist.dock_opened = True
        self.set_working_message(False)
        return hist

    def histogram_monoband_closed(self):
        """
        Called when the dock is closed.
        Set histogram flag to false
        """
        logger.info("QObject.sender() " + str(QtCore.QObject.sender(self)))
        logger.debug(QtCore.QObject.sender(self).widget())
        QtCore.QObject.sender(self).widget().dock_opened = False

    def threshold_on_histogram(self, forms):
        logger.debug("QObject.sender() " + str(QtCore.QObject.sender(self)))
        logger.debug("do processing args " + str(forms))
        who = QtCore.QObject.sender(self)

        if "Seuillage" in ProcessingManager().get_processings_name():
            processings_seuillage = ProcessingManager().processing_from_name("Seuillage")
            if processings_seuillage:
                processings_seuillage[0].mirror.close()
                try :
                    QgsMapLayerRegistry.instance().removeMapLayer(processings_seuillage[0].output_working_layer.qgis_layer.id())
                except RuntimeError:
                    pass

        self.set_working_message(True)
        my_processing = TerreImageProcessing(self.iface, self.qgis_education_manager.working_directory, who.layer, self.qgis_education_manager.mirror_map_tool, "Seuillage", forms)
        self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
        self.set_working_message(False)

    def histogram_threshold(self, forms):
        logger.debug("educationwidget forms: " + str(forms))
        self.do_manage_processing("Seuillage", args=forms)

    def do_manage_actions_for_histogram(self, action):
        """
        Calls do_manage_processing with action name
        """
        histogram_name = action.text()
        self.do_manage_histograms(histogram_name)

    def do_manage_histograms(self, text_changed):
        logger.debug("text changed histogram: " + text_changed)
        if text_changed == "Image de travail":
            self.main_histogram()
        elif text_changed != "Histogrammes" and text_changed != "":
            # find the layer corresponding to the name
            process = ProcessingManager().processing_from_name(text_changed)
            if process :
                process = process[0]
                specific_band = -1

                if text_changed == "Couleurs naturelles":
                    logger.debug("text changed couleurs naturelles")
                    self.set_working_message(True)
                    if not process.histogram:
                        hist = TerreImageHistogram_multiband(ProcessingManager().working_layer, self.canvas, 3, process)
                        process.histogram = hist
                        self.histogram(process.output_working_layer, process, specific_band, hist)
                else:
                    logger.debug("working layer")
                    bs = ["rouge", "verte", "bleue", "pir", "nir"]
                    corres = {"rouge":process.layer.red, "verte":process.layer.green, "bleue":process.layer.blue, "pir":process.layer.pir, "mir":process.layer.mir}
                    logger.debug("corres: " + str(corres))

                    for item in bs:
                        if item in text_changed:
                            logger.debug("bande à afficher : " + str(corres[item]))
                            specific_band = corres[item]

                    logger.debug("specific band: " + str(specific_band))

                    if not process.histogram:
                        # display the histogram of the layer
                        hist = self.histogram(process.output_working_layer, process, specific_band)
                        process.histogram = hist
                    else :
                        hist = self.histogram(process.output_working_layer, process, specific_band, process.histogram)
        self.comboBox_histogrammes.setCurrentIndex(0)

    def define_working_dir(self):
        output_dir = terre_image_utils.getOutputDirectory(self)
        self.qgis_education_manager.working_directory = output_dir

    def do_manage_actions_for_processing(self, action):
        """
        Calls do_manage_processing with action name
        """
        processing_name = action.text()
        self.do_manage_processing(processing_name)

    def do_manage_processing(self, text_changed, args=None):
        if text_changed == "Angle Spectral":
            for item in self.iface.mapCanvas().scene().items():
                if isinstance(item, QgsRubberBand):
                    item.reset(QGis.Point)
            processings_spectral_angle = ProcessingManager().processing_from_name("Angle Spectral")
            if processings_spectral_angle:
                processings_spectral_angle[0].mirror.close()
                ProcessingManager().remove_processing(processings_spectral_angle)
        if text_changed == "Seuillage":
            if "Seuillage" in ProcessingManager().get_processings_name():
                processings_seuillage = ProcessingManager().processing_from_name("Seuillage")
                if processings_seuillage:
                    processings_seuillage[0].mirror.close()
                    ProcessingManager().remove_processing(processings_seuillage)
        do_it = True
        logger.debug("do processing args: " + str(args))
        if text_changed:
            if not text_changed == "Traitements...":
                if text_changed in ["NDVI", "NDTI", "Indice de brillance"]:
                    if text_changed in ProcessingManager().get_processings_name() :
                        do_it = False
                if text_changed in [ "Seuillage", "Angle Spectral" ]:
                    p = [process.processing_name for process in ProcessingManager().processings if process.processing_name == text_changed]
                    if p:
                        process = p[0]
                        try:
                            QgsMapLayerRegistry.instance().removeMapLayer(process.get_output_working_layer().qgis_layer.id())
                        except AttributeError:
                            print 'Failed to delete ', process
                    if text_changed == "Angle Spectral":
                        widget = self.iface.messageBar().createMessage("Terre Image", "Cliquez sur un point de l'image pour en obtenir son angle spectral...")
                        self.iface.messageBar().pushWidget(widget, QgsMessageBar.INFO)
                        self.label_travail_en_cours.show()
                if do_it:
                    if not text_changed == "Angle Spectral":
                        self.set_working_message(True)

                    logger.debug("text changed: " + text_changed)
                    my_processing = TerreImageProcessing(self.iface, self.qgis_education_manager.working_directory, ProcessingManager().working_layer, self.qgis_education_manager.mirror_map_tool, text_changed, args)
                    if text_changed == "Angle Spectral":
                        self.label_a_s.show()
                        self.label_a_s_img.show()
                        QtCore.QObject.connect(my_processing, QtCore.SIGNAL("display_ok()"), lambda who=my_processing: self.processing_end_display(who))
                    if not text_changed == "Angle Spectral":
                        self.set_combobox_histograms()
                        self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
                        self.set_working_message(False)
            self.comboBox_processing.setCurrentIndex(0)

    def processing_end_display(self, my_processing):
        logger.debug("processing_end_display")
        self.set_combobox_histograms()
        self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
        self.set_working_message(False)

    def set_comboBox_sprectral_band_display(self):
        m3 = self.toolButton_display_bands.menu()

        if ProcessingManager().working_layer:
            bands = ProcessingManager().working_layer.bands
            corres = { 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }

            self.comboBox_sprectral_band_display.clear()
            self.comboBox_sprectral_band_display.insertItem(0, "Affichage des bandes spectrales...")

            if ProcessingManager().working_layer.has_natural_colors():
                logger.debug("couleurs naturelles")
                self.comboBox_sprectral_band_display.insertItem(1, "Afficher en couleurs naturelles")

            for i in range(ProcessingManager().working_layer.get_band_number()):
                y = [x for x in bands if bands[x] == i + 1]
                if y:
                    text = corres[y[0]]
                    self.comboBox_sprectral_band_display.insertItem(i + 2, text)
                    action_d = QtGui.QAction(
                      QtGui.QIcon(":/plugins/qgiseducation/img/mActionInOverview.png"),
                      text,
                      self.iface.mainWindow())
                    action_d.setWhatsThis(text)
                    m3.addAction(action_d)
                    if i == 0:
                        self.toolButton_display_bands.setDefaultAction(action_d)
            self.comboBox_sprectral_band_display.currentIndexChanged[str].connect(self.do_manage_sprectral_band_display)
            self.toolButton_display_bands.triggered.connect(self.do_manage_actions_for_display)

    def set_combobox_histograms(self):
        if self.qgis_education_manager:
            if ProcessingManager().working_layer:
                process = ["Histogrammes", "Image de travail"] + [x for x in ProcessingManager().get_processings_name() if x not in ["KMEANS", "Seuillage"]]
                logger.debug("process: " + str(process))

                self.comboBox_histogrammes.clear()
                m2 = self.toolButton_histograms.menu()
                m2.clear()
                for i, item in enumerate(process):
                    self.comboBox_histogrammes.insertItem(i, process[i])
                    action_h = QtGui.QAction(QtGui.QIcon(":/plugins/qgiseducation/img/mActionFullHistogramStretch.png"),
                                             item, self.iface.mainWindow())
                    action_h.setWhatsThis(item)
                    m2.addAction(action_h)
                    if i == 0:
                        self.toolButton_histograms.setDefaultAction(action_h)
                self.comboBox_histogrammes.currentIndexChanged[str].connect(self.do_manage_histograms)

    def do_manage_actions_for_display(self, action):
        """
        Calls do_manage_processing with action name
        """
        band_name = action.text()
        self.do_manage_sprectral_band_display(band_name)

    def do_manage_sprectral_band_display(self, text_changed):
        do_it = True
        if text_changed and text_changed != "Affichage des bandes spectrales...":
            band_to_display = None
            corres = {'nat': "Afficher en couleurs naturelles", 'red': "Afficher la bande rouge", 'green': "Afficher la bande verte", 'blue': "Afficher la bande bleue", 'pir': "Afficher la bande pir", 'mir':"Afficher la bande mir"}
            corres_name_view = {'nat': "Couleurs naturelles", 'red': "Bande rouge", 'green': "Bande verte", 'blue': "Bande bleue", 'pir': "Bande pir", 'mir': "Bande mir"}
            for key in corres:
                if corres[key] == text_changed :
                    who = key
                    logger.debug("do_manage_sprectral_band_display who: " + str(who))
                    if corres_name_view[who] in ProcessingManager().get_processings_name() :
                        do_it = False
                    if do_it:
                        my_processing = TerreImageDisplay(self.iface, self.qgis_education_manager.working_directory, ProcessingManager().working_layer, self.qgis_education_manager.mirror_map_tool, who)
                        self.set_combobox_histograms()
                    break
            self.comboBox_sprectral_band_display.setCurrentIndex(0)

    def display_values(self):
        self.qgis_education_manager.display_values()

    def kmeans(self):
        self.set_working_message(True)
        if ProcessingManager().working_layer == None :
            logger.debug("Aucune layer selectionnée")
        else :
            nb_class = self.spinBox_kmeans.value()
            logger.debug("nb_colass from spinbox: " + str(nb_class))
            my_processing = TerreImageProcessing(self.iface, self.qgis_education_manager.working_directory, ProcessingManager().working_layer, self.qgis_education_manager.mirror_map_tool, "KMEANS", nb_class)
            self.set_combobox_histograms()
            self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
            self.set_working_message(False)

    def export_kmz(self):
        self.set_working_message(True)
        files_to_export = ProcessingManager().get_layers_for_kmz()
        kmz = terre_image_processing.export_kmz(files_to_export, self.qgis_education_manager.working_directory)
        self.set_working_message(False)

    def display_metadata(self):
        # get image size and resolution
        dataset = gdal.Open(ProcessingManager().working_layer.source_file)
        if dataset is not None:
            total_size_x = dataset.RasterXSize
            total_size_y = dataset.RasterYSize
            geotransform = dataset.GetGeoTransform()
            pixel_size_x = geotransform[1]
            pixel_size_y = geotransform[5]

        list_to_display = [(u"Satellite", ProcessingManager().working_layer.type),
                           (u"Lieu", "TO BE DEFINED"),
                           (u"Lignes", str(total_size_x)),
                           (u"Colonnes", str(total_size_y)),
                           (u"Résolution", "TOBEDEFINED" + str(pixel_size_x))]
        # QTreeWidget
        self.treeWidget.clear()
        header = QtGui.QTreeWidgetItem([u"Métadonnée", "Valeur"])
        self.treeWidget.setHeaderItem(header)

        root = QtGui.QTreeWidgetItem(self.treeWidget, ["Image de travail"])
        for key, value in list_to_display:
            A = QtGui.QTreeWidgetItem(root, [key, str(value)])
        self.treeWidget.resizeColumnToContents(0)
        self.treeWidget.resizeColumnToContents(1)

#         A = QtGui.QTreeWidgetItem(root, ["A"])
#
#         barA = QtGui.QTreeWidgetItem(A, ["bar", "i", "ii"])
#         bazA = QtGui.QTreeWidgetItem(A, ["baz", "a", "b"])
        root.setExpanded(True)

    def layer_deleted(self, layer_id):

        # logger.debug( str(layer_id) + " deleted")
        # print str(layer_id) + " deleted"
        layer_id = layer_id.encode('utf-8')

        if "Angle_Spectral" in str(layer_id):
            # delete rubberband
            for item in self.iface.mapCanvas().scene().items():
                if isinstance(item, QgsRubberBand):
                    item.reset(QGis.Point)
            # hide legend
            self.label_a_s.hide()
            self.label_a_s_img.hide()

        if self.qgis_education_manager:
            # logger.debug( "ProcessingManager().working_layer.get_qgis_layer().id(): " +  str(ProcessingManager().working_layer.get_qgis_layer().id()))
            if ProcessingManager().working_layer.get_qgis_layer().id() == layer_id:
                self.disconnect_interface()

        ProcessingManager().remove_process_from_layer_id(layer_id)
        ProcessingManager().remove_displays_from_layer_id(layer_id)

        try:
            self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
        except AttributeError:
            pass

        self.set_combobox_histograms()

    def disconnect_interface(self):
        if self.qgis_education_manager:
            self.qgis_education_manager.disconnect()
        # histograms
        try:
            self.hist.close()
            self.hist = None
        except AttributeError:
            pass
        # rubberband
        if self.dock_histo_opened:
            # remove the dockwidget from iface
            self.iface.removeDockWidget(self.histodockwidget)
        # disable working layer
        self.qgis_education_manager = None
        self.emit(QtCore.SIGNAL("terminated()"))

    def set_working_message(self, set=True):
        if set:
            widget = self.iface.messageBar().createMessage("Terre Image", "Travail en cours...")
            self.iface.messageBar().pushWidget(widget, QgsMessageBar.INFO)
            self.iface.mainWindow().statusBar().showMessage("Terre Image : Travail en cours...")
            self.label_travail_en_cours.show()
        else:
            self.iface.messageBar().popWidget()
            self.iface.messageBar().clearWidgets()
            self.iface.mainWindow().statusBar().clearMessage()
            self.label_travail_en_cours.hide()

    def disconnectP(self):
        """
        Disconnection of signals, go back to the main interface
        """
        self.iface.mainWindow().statusBar().showMessage("")
