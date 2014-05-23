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
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui
import os

class QGisLayerType:
    ALL_TYPES = -1
    POINT = 0
    LINE = 1
    POLYGON = 2

class QGisLayers:
    '''This class contains method to communicate with the QGIS interface,
    mostly for retrieving layers and adding new ones to the QGIS canvas'''

    iface = None;

    @staticmethod
    def getRasterLayers():
        layers = QGisLayers.iface.legendInterface().layers()
        raster = list()

        for layer in layers:
            if layer.type() == layer.RasterLayer:
                #if layer.usesProvider() and layer.providerKey() == 'gdal':#only gdal file-based layers
                raster.append(layer)
        return raster

    @staticmethod
    def getVectorLayers(shapetype=QGisLayerType.ALL_TYPES):
        layers = QGisLayers.iface.legendInterface().layers()
        vector = list()
        
        for layer in layers:
            if layer.type() == layer.VectorLayer:
                if shapetype == QGisLayerType.ALL_TYPES or shapetype == layer.geometryType():
                    uri = unicode(layer.source())
                    if not uri.endswith("csv") and not uri.endswith("dbf"):
                        vector.append(layer)
        return vector

    @staticmethod
    def getAllLayers():
        layers = []
        layers += QGisLayers.getRasterLayers();
        layers += QGisLayers.getVectorLayers();
        return layers

    @staticmethod
    def setInterface(iface):
        QGisLayers.iface = iface

    @staticmethod
    def loadList(layers):
        for layer in layers:
            QGisLayers.load(layer)


    @staticmethod
    def loadLabelImage(imagepath, labeldescriptor = None):
        """
        Load a labeled single band raster in the canvas
        
        Keyword arguments:
        imagepath -- the path to the image
        labeldescriptor -- a dictionnary for label (int) to tuple (QColor, QString) conversion
        """
        if imagepath == None:
            return

        name = os.path.splitext( os.path.basename(imagepath) )[0]
        qgslayer = QgsRasterLayer(imagepath, name)
        if not qgslayer.isValid():
             QtGui.QMessageBox.critical( None, \
                                         u"Erreur", \
                                         u"Impossible de charger la couche %s" % unicode(imagepath) )
        
        QgsMapLayerRegistry.instance().addMapLayer(qgslayer)

        qgslayer.setDrawingStyle('SingleBandPseudoColor')    
        
        colorlist = []
        max_label = 0
        for label in sorted(labeldescriptor.keys()):
            color = labeldescriptor[label][0]
            labeltxt = labeldescriptor[label][1]
            colorlist.append(QgsColorRampShader.ColorRampItem(label, color, labeltxt))
            if labeltxt > max_label:
                max_label = labeltxt
          
               
        s = QgsRasterShader()
        c = QgsColorRampShader()
        c.setColorRampType(QgsColorRampShader.INTERPOLATED)
        c.setColorRampItemList(colorlist)
        s.setRasterShaderFunction(c)
        ps = QgsSingleBandPseudoColorRenderer(qgslayer.dataProvider(), 1,  s)
        qgslayer.setRenderer(ps)

        QGisLayers.iface.legendInterface().refreshLayerSymbology(qgslayer)
        if hasattr(qgslayer, "setCacheImage"): qgslayer.setCacheImage(None)
        qgslayer.triggerRepaint()


