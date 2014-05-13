# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin                : 2014-05-12
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

from qgis.core import QGis, QgsPoint, QgsRaster

from PyQt4.QtGui import QInputDialog
        
        
def ndvi(layer, working_directory, iface):
    #NDVI= (PIR-R)/(PIR+R)
    if not layer :
        print "Aucune layer selectionnée"
    else :
        if layer.pir and layer.red :
            image_in = layer.source_file
            print "image_in", image_in
            print working_directory
            output_filename = os.path.join( working_directory, 
                                            os.path.basename(os.path.splitext(image_in)[0]) + "_ndvi" + os.path.splitext(image_in)[1]
                                          )
            print output_filename
            layer_pir = "im1b" + str(layer.pir)
            layer_red = "im1b" + str(layer.red)
            expression = "\"(" + layer_pir + "-" + layer_red + ")/(" + layer_pir + "+" + layer_red + ")\""
            print expression
            print "image_in", image_in
            OTBApplications.bandmath_cli( [image_in], expression, output_filename )
            manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_ndvi", iface )    
    
    
def ndti(layer, working_directory, iface):
    #SQRT(R+0.5)
    if not layer :
        print "Aucune layer selectionnée"
    else :
        if layer.red :
            image_in = layer.source_file
            print "image_in", image_in
            output_filename = os.path.join( working_directory, os.path.basename(os.path.splitext(image_in)[0]) + "_ndti" + os.path.splitext(image_in)[1])
            print output_filename
            layer_red = "im1b" + str(layer.red)
            expression = "\"sqrt(" + layer_red + "+0.5)\""
            print expression
            print "image_in", image_in
            OTBApplications.bandmath_cli( [image_in], expression, output_filename )
            manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_ndti", iface )
                

def brightness( layer, working_directory, iface ):
    #IB = sqrt(RxR+PIRxPIR)
    if not layer :
        print "Aucune layer selectionnée"
    else :
        if layer.pir and layer.red :
            image_in = layer.source_file
            print "image_in", image_in
            print working_directory
            output_filename = os.path.join( working_directory, 
                                            os.path.basename(os.path.splitext(image_in)[0]) + "_brillance" + os.path.splitext(image_in)[1]
                                          )
            print output_filename
            layer_pir = "im1b" + str(layer.pir)
            layer_red = "im1b" + str(layer.red)
            expression = "\"sqrt(" + layer_red + "*" + layer_red + "*" + layer_pir + "*" + layer_pir + ")\""
            print expression
            print "image_in", image_in
            OTBApplications.bandmath_cli( [image_in], expression, output_filename )
            manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_brillance", iface )    
    
    
    
    
   
def angles(layer, working_directory, iface, x, y):
    ident = layer.get_qgis_layer().dataProvider().identify(QgsPoint(x, y), QgsRaster.IdentifyFormatValue )
    print ident
    if ident is not None :
        attr = ident.results()
        print attr
        if len(attr) == layer.get_qgis_layer().bandCount():
            formula = "\"acos("
            num = []
            denom = []
            fact = []
            #acos((im1b1*1269+im1b2*1060+im1b3*974+im1b4*1576)/
            #(sqrt((1269*1269+1060*1060+974*974+1576*1576)*
            #(im1b1*im1b1+im1b2*im1b2+im1b3*im1b3+im1b4*im1b4))))
            for index in range( 1,layer.get_qgis_layer().bandCount()+1 ):
                current_band = "im1b" + str(index)
                band_value = attr[index]
                num.append( current_band + "*" + str(band_value)  )
                denom.append(str(band_value) + "*" + str(band_value) )
                fact.append(current_band + "*" + current_band)
            
            formula += "(" + "+".join(num) + ")/"
            formula += "(sqrt("
            formula += "(" + "+".join(denom) + ")*"
            formula += "(" + "+".join(fact) + ")"
            formula += "))"
            formula += ")\""
            
            print "num", num
            print "denom", denom
            print "fact", fact
            print "formula", formula
            
            
            image_in = layer.get_qgis_layer().source()
            output_filename = os.path.join( working_directory, os.path.basename(os.path.splitext(image_in)[0]) + "_angles" + str(x) + "_" + str(y) + os.path.splitext(image_in)[1])
            OTBApplications.bandmath_cli( [image_in], formula, output_filename )
            rlayer = manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_angles" + str(x) + "_" + str(y), iface )
            manage_QGIS.contrastForRasters( rlayer, 0, 0.5)
                
                
                
def kmeans( layer, working_directory, iface ):
    """
    WARNING: nb_valid_pixels à calculer ?
    """
    bands = []

    for band_number in range(layer.get_qgis_layer().bandCount()):

        bands.append("band " + str(band_number +1))
        testqt, ok = QInputDialog.getInt(None, "Kmeans", "Nombre de classes")
        if ok:
            nb_class = testqt
            #mask = OTBApplications.bandmath([layer.get_source()], "if(im1b1>0,1,0)", working_directory, "mask")
            OTBApplications.kmeans(layer.get_source(), nb_class, working_directory)



    
    
    
    
    
    
                