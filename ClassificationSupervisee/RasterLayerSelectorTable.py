# -*- coding: utf-8 -*-
"""
/*=========================================================================

Copyright (c) Centre National d'Etudes Spatiales
All rights reserved.

The "ClassificationSupervisee" Quantum GIS plugin is distributed
under the CeCILL licence version 2.
See Copyright/Licence_CeCILL_V2-en.txt or
http://www.cecill.info/licences/Licence_CeCILL_V2-en.txt for more details.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=========================================================================*/
"""
import os
from PyQt4 import QtCore, QtGui
import xml.etree.ElementTree as ET
# import GDAL and QGIS libraries
from osgeo import gdal
from qgis.core import QgsRasterLayer

# import logging for debug messages
from TerreImage import terre_image_logging
logger = terre_image_logging.configure_logger()


class TreeWidgetItem(QtGui.QTreeWidgetItem):
    def setData(self, column, role, value):
        state = self.checkState(column)
        QtGui.QTreeWidgetItem.setData(self, column, role, value)
        if role == QtCore.Qt.CheckStateRole and state != self.checkState(column):
            treewidget = self.treeWidget()
            if treewidget is not None:
                treewidget.itemChecked.emit(self, column)


class Window(QtGui.QTreeWidget):
    itemChecked = QtCore.pyqtSignal(object, int)

    def __init__(self):
        QtGui.QTreeWidget.__init__(self)


class RasterLayerSelectorTable(QtGui.QWidget):
    itemChecked = QtCore.pyqtSignal(object, int)

    def __init__(self, layers, working_directory, the_layer, bands_order, parent = None):
        logger.debug( "RasterLayerSelectorTable" )
        super(RasterLayerSelectorTable, self).__init__(parent)

        self.layers = layers
        self.the_layer = the_layer
        self.the_layer_bands = bands_order

        self.working_dir = working_directory

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)

        self.label = QtGui.QLabel("Couches images : ")

        self.table = QtGui.QTreeWidget()
        self.table.setHeaderHidden( True )
        logger.debug(  "self.table.isHeaderHidden() {}".format(self.table.isHeaderHidden()) )
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.table = Window()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0, 270)
        self.setTableContent()

        self.selectallbutton = QtGui.QPushButton(u"(Dé)sélectionner tout")
        self.selectallbutton.clicked.connect(self.selectAll)

        self.selectallbuttonlayout = QtGui.QHBoxLayout()
        self.selectallbuttonlayout.addStretch()
        self.selectallbuttonlayout.addWidget(self.selectallbutton)
        self.selectallbuttonlayout.addStretch()

        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.table)
        self.verticalLayout.addLayout(self.selectallbuttonlayout)

        self.setLayout(self.verticalLayout)

        # self.itemChecked.connect(self.manageChild)
        # self.table.itemClicked.connect(self.manageChild1)
        self.table.itemChanged.connect(self.manageChild2)
        # self.table.currentItemChanged.connect(self.manageChild3)

    def selectAll(self):
        checked = QtCore.Qt.Unchecked
        for i in range(len(self.layers)):
            widget = self.table.itemAt(i, 0)
            if not widget.checkState(0) == QtCore.Qt.Checked:
                checked = QtCore.Qt.Checked
                break

        for i in range(self.table.topLevelItemCount()):
            item = self.table.topLevelItem(i)
            item.setCheckState(0, checked)
            for i in range(item.childCount()):
                child_temp = item.child(i)
                child_temp.setCheckState(0, checked)

    def setTableContent(self):
        corres = { 'red': "rouge", 'green': "verte", 'blue': "bleue", 'pir': "pir", 'mir': "mir" }
        # TODO : get the layer[i] if the layer[i] is a multi band layer, add subchild for all bands
        # TODO : connecgt the multiband layer check box to a function which checks/unchecks all children
        n = len(self.layers)
        # self.table.setRowCount(n)
        for i in range(n):
            rename_bands = False
            layer = self.layers[i]
            # item = TreeWidgetItem( self.table )
            item = QtGui.QTreeWidgetItem( self.table )
            item.setFlags(item.flags()|QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(0, QtCore.Qt.Unchecked)
            item.setText( 0, layer.name() )
            item.setExpanded(True)
            if layer == self.the_layer:
                rename_bands = True
            if not layer.rasterType() == 0:
                logger.debug( u"multiband {}".format(layer.bandCount()) )
                for i in range(layer.bandCount()):
                    if rename_bands:
                        logger.debug( self.the_layer_bands[i+1] )
                        child_name = u"{}_band{}".format(layer.name(),corres[self.the_layer_bands[i+1]])
                    else:
                        child_name = u"{}_band{}".format(layer.name(),i+1)
                    #logger.debug(  "child_name" + str(child_name) )
                    item_child = QtGui.QTreeWidgetItem()
                    item_child.setFlags(item_child.flags()|QtCore.Qt.ItemIsUserCheckable)
                    item_child.setCheckState(0, QtCore.Qt.Unchecked)
                    item_child.setText(0, child_name)
                    logger.debug( item_child )
                    item.addChild(item_child)

    def getSelectedOptions(self):
        logger.debug( "get selected options")
        selectedLayers = []
        it = QtGui.QTreeWidgetItemIterator(self.table)
        index_layer = 0
        logger.debug( "nb layers: {}".format(len(self.layers)))
        while it.value() is not None:
            logger.debug( "index_layer {}".format(index_layer) )
            logger.debug( it.value().text(0) )
            logger.debug( it.value() )

            widget = it.value()
            if widget.checkState(0) == QtCore.Qt.Checked:
                logger.debug( "widget checked" )
                selectedLayers.append(self.layers[index_layer])
                it += widget.childCount()
            else:
                logger.debug( "widget unchecked : look children" )
                # uncheked
                # how many children are checked
                all_children = 0
                list_children = []
                logger.debug( "widget.childCount() {}".format(widget.childCount()) )
                if widget.childCount() > 0:
                    for j in range( widget.childCount() ):
                        child_temp = widget.child(j)
                        if child_temp.checkState(0) == QtCore.Qt.Checked:
                            all_children += 1
                            #creating vrt to take only the band j+1
                            vrt_temp_layer = self.rasterToVRT( self.layers[index_layer].source(), j+1)
                            #adding vrt raster layer to the list
                            list_children.append(vrt_temp_layer)
                        it += 1
                        logger.debug( "***index_layer {}".format(index_layer) )
                        logger.debug( it.value().text(0) )
                        logger.debug( it.value() )
                    logger.debug(u"list_children {}".format( list_children ))
                    if all_children == widget.childCount():
                        logger.debug( "all children checked, multiband image added" )
                        #all children checked, multiband image added
                        selectedLayers.append(self.layers[index_layer])
                    else :
                        logger.debug( "add single bands")
                        logger.debug( u"selectedLayers {}".format(selectedLayers) )
                        logger.debug( u"list_children {}".format(list_children) )
                        # else add single bands
                        selectedLayers2 = selectedLayers + list_children
                        selectedLayers = selectedLayers2

            it += 1
            index_layer += 1
            for item in selectedLayers:
                logger.debug( item.name() )

        return selectedLayers

    def manageChild1(self, item, column):
        # void 	itemClicked ( QTreeWidgetItem * item, int column )
        logger.debug( "managechild1" )
        if item.childCount() > 0:
            checked = QtCore.Qt.Unchecked
            if item.checkState(0) == QtCore.Qt.Checked:
                checked = QtCore.Qt.Checked
        for i in range( item.childCount() ):
            child_temp = item.child(i)
            child_temp.setCheckState(0, checked)

    def manageChild2(self, item):
        # void 	itemChanged ( QTreeWidgetItem * item, int column )
        logger.debug(  "managechild2" )
        logger.debug(  "previous {}".format(item) )

        if item.childCount() > 0:
            checked = QtCore.Qt.Unchecked
            if item.checkState(0) == QtCore.Qt.Checked:
                checked = QtCore.Qt.Checked
        for i in range( item.childCount() ):
            child_temp = item.child(i)
            child_temp.setCheckState(0, checked)

    def manageChild3(self, tree, item):
        # void 	currentItemChanged ( QTreeWidgetItem * current, QTreeWidgetItem * previous )
        logger.debug(  "managechild3" )
        logger.debug(  "current {}".format(tree) )
        logger.debug(  "previous {}".format(item) )

        if item.childCount() > 0:
            checked = QtCore.Qt.Unchecked
            if item.checkState(0) == QtCore.Qt.Checked:
                checked = QtCore.Qt.Checked
        for i in range( item.childCount() ):
            child_temp = item.child(i)
            child_temp.setCheckState(0, checked)

    def rasterToVRT( self, filename, band_number ):
        """Convert a raster layer into a single VRT
        It allow to give a SRC to a focal plane product and display it automatically in (0,0)

        Keyword arguments:
                filenames    --    raster layer to load

        Returns a string containing the vrt xml
        """
        logger.debug( "{} {}".format(filename, band_number) )
        ds = gdal.Open(filename)
        if ds is not None :
            band = ds.GetRasterBand(band_number)
            rootNode = ET.Element( 'VRTDataset' )

            #endif
            bandNode = ET.SubElement( rootNode, "VRTRasterBand", {'band': '1'} )

            totalXSize = ds.RasterXSize
            totalYSize = ds.RasterYSize
        #    logger.debug( "totalYSize from rasterToVRT:" + str(totalYSize))

            dataType = gdal.GetDataTypeName(band.DataType)

            # <SourceFilename relativeToVRT="1">nine_band.dat</SourceFilename>
            sourceNode = ET.SubElement(bandNode, 'SimpleSource')
            node = ET.SubElement(sourceNode, 'SourceFilename', {'relativeToVRT': '1'})
            node.text = filename
            # <SourceBand>1</SourceBand>
            node = ET.SubElement(sourceNode, 'SourceBand')
            node.text = str(band_number)

            rootNode.attrib['rasterXSize'] = str(totalXSize)
            rootNode.attrib['rasterYSize'] = str(totalYSize)

            geotransform = ds.GetGeoTransform()
            ftuple = tuple(map(str, geotransform))
            logger.debug(  type(geotransform) )
            geotransform = ET.SubElement( rootNode, "GeoTransform")
            geotransform.text = ", ".join(ftuple)  # "0.0, 1.0, 0.0, 0.0, 0.0, -1.0"
            node = ET.SubElement(rootNode, 'SRS')
            node.text = ds.GetProjection()  # "EPSG:4326"  # projection
            bandNode.attrib['dataType'] = dataType

            logger.debug( "Projection is {}".format(ds.GetProjection()) )
            logger.debug( "geotransform {}".format(ds.GetGeoTransform() ) )

            ds = None
            stringToReturn = ET.tostring(rootNode)

            vrt_name = os.path.join( self.working_dir, os.path.basename(filename) + "_b" + str(band_number) + ".vrt")
            if not os.path.isfile( vrt_name):
                writer = open( vrt_name, 'w')
                writer.write( stringToReturn )
                writer.close()

            layer = QgsRasterLayer( vrt_name, os.path.basename(filename) + "_b" + str(band_number) )

            return layer #stringToReturn

    def set_layers(self, layers):
        self.table.clear()
        self.layers = layers
        self.setTableContent()
