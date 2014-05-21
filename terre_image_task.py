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

import os
import OTBApplications
import manage_QGIS
import re

from qgis.core import QGis, QgsPoint, QgsRaster, QgsMapLayerRegistry

from PyQt4.QtGui import QInputDialog
import terre_image_processing
        
        
class TerreImageTask(object):
    def __init__(self, iface, working_dir, layer, mirror_map_tool):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.working_directory = working_dir
        self.layer = layer
        self.mirrormap_tool = mirror_map_tool
        
    def get_mirror_map(self):
        return self.mirrormap
        
        
    def freezeCanvas(self, setFreeze):
        if setFreeze:
            if not self.iface.mapCanvas().isFrozen():
                self.iface.mapCanvas().freeze( True )
        else:
            if self.iface.mapCanvas().isFrozen():
                self.iface.mapCanvas().freeze( False )
                self.iface.mapCanvas().refresh()    
        
        
class TerreImageProcessing(TerreImageTask):
    
    def __init__(self, iface, working_dir, layer, mirror_map_tool, processing, arg=None):
        """
        processing_type : [processing/display]
        """
        super(TerreImageProcessing, self).__init__(iface, working_dir, layer, mirror_map_tool)
        
        self.processing_name = processing
        self.mirror = None
        
        self.result_file_name = ""
        self.arg=None
        if arg:
            self.arg = arg
        
        self.run()
        

        

        
    def run(self):
        output_filename = ""
        if "NDVI" in self.processing_name:
            output_filename = terre_image_processing.ndvi(self.layer, self.working_directory, self.iface)
        if "NDTI" in self.processing_name:
            output_filename = terre_image_processing.ndti(self.layer, self.working_directory, self.iface)
        if "Indice de brillance" in self.processing_name:
            output_filename = terre_image_processing.brightness(self.layer, self.working_directory, self.iface)
        if "Angle Spectral" in self.processing_name:
            from spectral_angle import SpectralAngle
            self.angle_tool = SpectralAngle(self.iface, self.working_directory, self.layer)
            print "self.angle_tool", self.angle_tool
            self.angle_tool.get_point_for_angles(self.layer)
            #spectral_angles(self.layer, self.working_directory, self.iface)
        if "KMEANS" in self.processing_name:
            if self.arg:
                output_filename = terre_image_processing.kmeans(self.layer, self.working_directory, self.iface, self.arg)
            else :
                output_filename = terre_image_processing.kmeans(self.layer, self.working_directory, self.iface)
        if output_filename:
            print output_filename
            self.display(output_filename)
    
    def get_filename_result(self):
        return self.result_file_name
    

    
    
    def display(self, output_filename):
        self.freezeCanvas( True )
        #result_layer = manage_QGIS.get_raster_layer( output_filename, os.path.basename(os.path.splitext(self.layer.source_file)[0]) + "_" + self.processing_name )
        result_layer = manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(self.layer.source_file)[0]) + "_" + self.processing_name, self.iface )
        # 2 ouvrir une nouvelle vue
        self.mirror = self.mirrormap_tool.runDockableMirror(self.processing_name)
        print self.mirror
        self.mirror.mainWidget.addLayer( result_layer.id() )
        # 1 mettre image en queue
        
        
        
        ifaceLegend = self.iface.legendInterface()
        ifaceLayers = QgsMapLayerRegistry.instance().mapLayers()
        print "ifacelayers", ifaceLayers
        id_layer = result_layer.id()
        print "id_layer", id_layer
        print "result layer", result_layer
        #QgsMapLayerRegistry.instance().mapLayers()
        #{u'QB_1_ortho20140521141641682': <qgis.core.QgsRasterLayer object at 0x6592b00>, u'QB_1_ortho_bande_bleue20140521141927295': <qgis.core.QgsRasterLayer object at 0x6592950>}
        ifaceLegend.setLayerVisible( result_layer, False )
        self.iface.mapCanvas().refresh()
        print ifaceLegend.isLayerVisible(result_layer)
        
        # thaw the canvas
        self.freezeCanvas( False )
        
        
class TerreImageDisplay(TerreImageTask):
    
    def __init__(self, iface, working_dir, layer, mirror_map_tool, who, arg=None):
        """
        processing_type : [processing/display]
        """
        super(TerreImageDisplay, self).__init__(iface, working_dir, layer, mirror_map_tool)
        
        self.corres = { 'nat':"Couleurs naturelles", 'red':"Bande rouge", 'green':"Bande verte", 'blue':"Bande bleue", 'pir':"Bande pir", 'mir':"Bande mir" }
        
        self.who = who
        self.processing_name = self.corres[who]
        self.mirror = None
        
        self.result_file_name = ""
        self.arg=None
        if arg:
            self.arg = arg
        
        self.run()
        
        
        
    def run(self):
        self.freezeCanvas( True )
        print "self.who", self.who
        result_layer = manage_QGIS.display_one_band(self.layer, self.who, self.iface)
        if result_layer:
            self.mirror = self.mirrormap_tool.runDockableMirror(self.processing_name)
            print self.mirror
            self.mirror.mainWidget.addLayer( result_layer.id() )
        
        
            ifaceLegend = self.iface.legendInterface()
            ifaceLayers = QgsMapLayerRegistry.instance().mapLayers()
            print "ifacelayers", ifaceLayers
            id_layer = result_layer.id()
            print "id_layer", id_layer
            print "result layer", result_layer
            #QgsMapLayerRegistry.instance().mapLayers()
            #{u'QB_1_ortho20140521141641682': <qgis.core.QgsRasterLayer object at 0x6592b00>, u'QB_1_ortho_bande_bleue20140521141927295': <qgis.core.QgsRasterLayer object at 0x6592950>}
            ifaceLegend.setLayerVisible( result_layer, False )
            self.iface.mapCanvas().refresh()
            print ifaceLegend.isLayerVisible(result_layer)
            
            # thaw the canvas
            self.freezeCanvas( False )
      