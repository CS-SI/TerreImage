# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2013-11-21
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
#import system libraries
import os
import datetime


#import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger( 'TerreImage_OTBApplications' )
logger.setLevel(logging.INFO)


currentOs = os.name
if currentOs == "posix" :
    prefix = ""
else:
    prefix = os.path.join( os.path.dirname(__file__),  "win32", "bin" )



def bandmath_cli( images, expression, output_filename ):
    """
    This function applies otbcli_BandMath to image with the given expression
    
    Keyword arguments:
        image               --    raster layer to process
        expression          --    expression to apply        
        outputDirectory     --    working directory
        keyword             --    keyword for output file name
    """
    
    
    command = os.path.join(prefix, "otbcli ")
    command += " BandMath -il "
    
    for image in images :
        command += "\"" + image + "\"" + " "
    
    command += " -exp " + str( expression )
    command += " -out " + str( output_filename ) 
    
    logger.info( "command: "+ str(command) ) 
    os.system( command )



def concatenateImages_cli( listImagesIn, outputname, options=None ):
    """
    Runs the ConcatenateImages OTB application.
    
    Keyword arguments:
        listImagesIn     --    list of images to concatenates
        outputname     --    output image
    """
    
    if listImagesIn and outputname :
        command = os.path.join(prefix, "otbcli ")
        command += " ConcatenateImages "
        command += " -il " + " ".join(listImagesIn)
        command += " -out " + "\"" + outputname + "\""
        if options:
            command += " uint16 " 
        
        logger.info( "command: " + str(command))
        
        os.system(command)



def kmeans_cli( image, nbClass, outputDirectory ):
    """
    pass
    """
    filenameWithoutExtension = os.path.basename(os.path.splitext(image)[0]) 
    output = os.path.join( outputDirectory, filenameWithoutExtension + "_kmeans_" + str(nbClass) + ".tif" ) # + temp[index:]
    if not os.path.isfile(output):
        if image and nbClass and outputDirectory :
            command = os.path.join(prefix, "otbcli")
            command += " KMeansClassification "
            command += " -in " + "\"" + image + "\""
            command += " -out " + "\"" + output + "\""
            command += " -nc " + str(nbClass)
            command += " -rand " + str(42)
            
            logger.info( "command: " + str(command))
            
            os.system(command)
        
    return output


def color_mapping_cli_ref_image( image_to_color, reference_image, working_dir):
    output_filename = os.path.join( working_dir, os.path.splitext(os.path.basename(image_to_color))[0]) + "colored.tif"# + os.path.splitext(image_to_color)[0]
    
    if not os.path.isfile(output_filename):
        logger.info( output_filename )
        command = os.path.join(prefix, "otbcli")
        command += " ColorMapping "
        command += " -in " + "\"" + image_to_color + "\""
        command += " -out " + "\"" + output_filename + "\" uint8"
        command += " -method \"image\""
        command += " -method.image.in " + "\"" + reference_image + "\""
        logger.info( "command: " + str(command))
        os.system(command)
    return output_filename



def otbcli_export_kmz( filename, working_directory):
    output_kmz = os.path.join(working_directory, os.path.basename(os.path.splitext(filename)[0]) + ".kmz" )
    if not os.path.isfile(output_kmz):
        command = os.path.join(prefix, "otbcli ")
        command += "KmzExport "
        command += " -in " + "\"" + filename + "\""
        command += " -out " + "\"" + output_kmz + "\""
        logger.info( "command: " + str(command))
        os.system( command )
    return output_kmz
    