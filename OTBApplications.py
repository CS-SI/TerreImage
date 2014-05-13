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

import logging
logger = logging.getLogger("Saterre_OTBApplications")
logger.setLevel(logging.INFO)
 
import otbApplication


def erode( image, radius, outputDirectory ):
    """
    This function applies an erosion via otbcli_BinaryMorphologicalOperation to the given image with the given radius
    
    Keyword arguments:
        image               --    raster layer to process
        expression          --    expression to apply        
        outputDirectory     --    working directory
        keyword             --    keyword for output file name
    """
    if image and radius and outputDirectory :
        app = otbApplication.Registry.CreateApplication("BinaryMorphologicalOperation")
        inputL = str(image)
        #create the output
        filenameWithoutExtension = os.path.basename(os.path.splitext(inputL)[0])
        output = os.path.join( outputDirectory, filenameWithoutExtension + "_erode.tif" ) #+ datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".tif")
        
        #set the arguments of the application
        app.SetParameterString("in", inputL )
        app.SetParameterString("out", output )
        app.SetParameterString("structype.ball.xradius", str(radius))
        app.SetParameterString("filter", "erode")
        #execute the application
        app.ExecuteAndWriteOutput()
        return output
    return None
 
 
def bandmath( image, expression, outputDirectory, keyword="" ):
    """
    This function applies otbcli_BandMath to image with the given expression
    
    Keyword arguments:
        image               --    raster layer to process
        expression          --    expression to apply        
        outputDirectory     --    working directory
        keyword             --    keyword for output file name
    """
    #export ITK_AUTOLOAD_PATH=/usr/lib/otb/applications/:$ITK_AUTOLOAD_PATH
    #export PYTHONPATH=/usr/lib/otb/python/:$PYTHONPATH
    
    sourceInput = str( image )
    
    logger.debug(sourceInput)
    
    filenameWithoutExtension = os.path.basename(os.path.splitext(sourceInput)[0])
    
    if keyword :
        endFilename = "bandmaths_" + keyword + ".tif"
    else :
        endFilename = "bandmaths.tif"
    outputFile = os.path.join( outputDirectory, filenameWithoutExtension +  endFilename )
    logger.debug( outputFile )
    
    app = otbApplication.Registry.CreateApplication("BandMath")
    app.SetParameterStringList("il", [sourceInput] )
    app.SetParameterString("out", outputFile )
    app.SetParameterString("exp", expression)
    logger.debug( "run mask creation" )

    app.ExecuteAndWriteOutput()  
    
    logger.debug( "fin creation mask")
    
    return outputFile


def bandmath_cli( images, expression, output_filename ):
    """
    This function applies otbcli_BandMath to image with the given expression
    
    Keyword arguments:
        image               --    raster layer to process
        expression          --    expression to apply        
        outputDirectory     --    working directory
        keyword             --    keyword for output file name
    """
    
    
    command = "otbcli_BandMath -il "
    
    for image in images :
        command += image + " "
    
    command += " -exp " + str( expression )
    command += " -out " + str( output_filename ) 
    
    print "command", command
    os.system( command )


def bandmathMultipleInput( images, expression, complete_output_filename ):
    """
    This function applies otbcli_BandMath to the given images with the given expression
    
    Keyword arguments:
        images                    --    list of images to process
        expression                --    expression to apply
        completeOutputFilename    --    output file name
    """
    
    print "images in", images
    print "expression", expression
    print "complete output filename", complete_output_filename
    
    app = otbApplication.Registry.CreateApplication("BandMath")
    #app.SetParameterStringList("il", images )
    app.SetParameterStringList("il", ['/home/amondot/OTB-Data/Examples/QB_1_ortho.tif'] )
    app.SetParameterString("out", complete_output_filename )
    app.SetParameterString("exp", expression)
    app.ExecuteAndWriteOutput()
    
    
def ccSegmentation(image, outputDirectory, shapeMask, expression, neighbor = False, minSize = None ):
    """
    Runs the Segmentation OTB application.
    
    Keyword arguments:
        theLayer            --    raster layer to segment
        outputDirectory     --    working directory
        shapeMask           --    mask for the segmentation
    
    """
    logger.debug( "debut segmentation connected components" )
    output = ""
    
    if image and outputDirectory :
        #create the Segmentation application
        app = otbApplication.Registry.CreateApplication("Segmentation")
        
        #create the output
        filenameWithoutExtension =  os.path.basename(os.path.splitext(image)[0])
        output = os.path.join( outputDirectory , filenameWithoutExtension + "extraction_regions" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".sqlite" )  # + temp[index:]
        
        #set the arguments of the application
        app.SetParameterString("in", str(image))
        app.SetParameterString("filter", "cc")
        app.SetParameterString("mode", "vector")
        app.SetParameterString("mode.vector.out", output)
        app.SetParameterString("mode.vector.inmask", shapeMask)
        app.SetParameterString("filter.cc.expr", expression )
        if not neighbor == False :
            app.SetParameterString("mode.vector.neighbor", "1")
        if not minSize == None :
            app.SetParameterInt("mode.vector.minsize", minSize)
        
        #execute the application
        app.ExecuteAndWriteOutput() 
        logger.debug( "fin segmentation _ connected components" )
   
    return output


def rasterizationWithSupportImage( vectorIn, supportImage, outputDirectory, field = None ):
    """
    Runs the Rasterization OTB application.
    
    Keyword arguments:
        vectorIn         --    vector to rasterize
        supportImage     --    support image
        outputDirectory  --    working directory
        field            --    specific field to rasterize
    """

    if vectorIn and supportImage and outputDirectory :
        #create the Segmentation application
        app = otbApplication.Registry.CreateApplication("Rasterization")
        
        #create the output
        if not field :
            field = ""
        filenameWithoutExtension = os.path.basename(os.path.splitext(vectorIn)[0])
        output = os.path.join( outputDirectory, filenameWithoutExtension + "_" + field + "_raster.tif" ) # + temp[index:]
        
        #set the arguments of the application
        app.SetParameterString("in", str(vectorIn))
        app.SetParameterString("out", output)
        app.SetParameterString("im", str(supportImage) )
        app.SetParameterFloat("background", 0)
        if field :
            app.SetParameterString("mode", "attribute")
            app.SetParameterString("mode.attribute.field", field)
        else :
            app.SetParameterString("mode", "binary")
            app.SetParameterFloat("mode.binary.foreground", 1)
        
        
        #execute the application
        app.ExecuteAndWriteOutput() 
        logger.debug( "fin rasterization" )
   
    return output


def concatenateImages( listImagesIn, outputname ):
    """
    Runs the ConcatenateImages OTB application.
    
    Keyword arguments:
        listImagesIn     --    list of images to concatenates
        outputname     --    output image
    """

    if listImagesIn and outputname :
        #create the Segmentation application
        app = otbApplication.Registry.CreateApplication("ConcatenateImages")
        
       
        #set the arguments of the application
        app.SetParameterStringList("il", listImagesIn)
        app.SetParameterString("out", outputname)

        #execute the application
        app.ExecuteAndWriteOutput() 
   


def kmeans( image, nbClass, outputDirectory, mask=None, nbvalidPixels=None ):
    """
    pass
    """
    print "nb pixels valides : ", nbvalidPixels
    output = None
    if image and nbClass and outputDirectory :
        #create the Segmentation application
        app = otbApplication.Registry.CreateApplication("KMeansClassification")
        
        filenameWithoutExtension = os.path.basename(os.path.splitext(image)[0]) 
        output = os.path.join( outputDirectory, filenameWithoutExtension + "_kmeans.tif" ) # + temp[index:]
        
       
        #set the arguments of the application
        app.SetParameterString("in", image)
        app.SetParameterString("out", output)
        app.SetParameterInt("nc", nbClass)
        if mask :
            app.SetParameterString( "vm", mask)
        app.SetParameterInt("rand", 42)
        if nbvalidPixels :
            app.SetParameterInt("ts", nbvalidPixels)

        #execute the application
        app.ExecuteAndWriteOutput()
        
    return output



def kmeans_cli( image, nbClass, outputDirectory ):
    """
    pass
    """
    filenameWithoutExtension = os.path.basename(os.path.splitext(image)[0]) 
    output = os.path.join( outputDirectory, filenameWithoutExtension + "_kmeans.tif" ) # + temp[index:]
      
    if image and nbClass and outputDirectory :
        command = "otbcli_KMeansClassification "
        command += " -in " + image
        command += " -out " + output
        command += " -nc " + str(nbClass)
        command += " -rand " + str(42)
        
        os.system(command)
        
    return output


    
    

# def jetColorMapping( image, outputDirectory ):
#     """
#     app.SetParameterOutputImagePixelType( std::string parameter, ImagePixelType pixelType )
#     pixelType :
#     enum otb::Wrapper::ImagePixelType
#     Enumerator
#     ImagePixelType_uint8     
#     ImagePixelType_int16     
#     ImagePixelType_uint16     
#     ImagePixelType_int32     
#     ImagePixelType_uint32     
#     ImagePixelType_float     
#     ImagePixelType_double     
#     """
#     output = None
#     if image and outputDirectory :
#         #create the Segmentation application
#         app = otbApplication.Registry.CreateApplication("ColorMapping")
#         
#         filenameWithoutExtension = os.path.basename(os.path.splitext(image)[0])
#         output = os.path.join( outputDirectory, filenameWithoutExtension + "_colored.tif" ) # + temp[index:]
#         
#         #set the arguments of the application
#         app.SetParameterString("in", image)
#         app.SetParameterString("out", output)
#         app.SetParameterOutputImagePixelType("out", 0 )
#         app.SetParameterString("method", "continuous" )
#         app.SetParameterString("method.continuous.lut", "jet")
# 
#         stats = Saterre_gdalFunctions.computeStatistics(image, 0)
#         min = max = None
#         min, max, _, _ = stats
#         # print "min max : ", min, max
#         if not (min == None and max == None):
#             app.SetParameterFloat( "method.continuous.min", min )
#             app.SetParameterFloat( "method.continuous.max", max )
#         else :
#             print "Warning : Attention, pas de min max trouvé, l'image en sortie rique d'être faussée."
# 
#         #execute the application
#         app.ExecuteAndWriteOutput()
#         
#     return output


def imageEnvelope( image, outputDirectory ):
    """
    Runs OTB Application Image enveloppe for the given image.
    Returns the output shapefile
    """

    output = None
    if image and outputDirectory :
        #create the Segmentation application
        app = otbApplication.Registry.CreateApplication("ImageEnvelope")
        
        filenameWithoutExtension = os.path.basename(os.path.splitext(image)[0]) 
        output = os.path.join( outputDirectory, filenameWithoutExtension + "_extent.shp" )
        
       
        #set the arguments of the application
        app.SetParameterString("in", image)
        app.SetParameterString("out", output)

        #execute the application
        app.ExecuteAndWriteOutput()
        
    return output


def meanshiftSegmentation(theLayer, shapeMask, spatialRadius, spectralValue, convergenceTh, maxIteration, minimunRegionSize, outputDirectory):
    """
    Runs the Segmentation OTB application with the given layer and shapemask.
    
    Keyword arguments:
        theLayer            --    raster layer
        outputDirectory     --    working directory
        shapeMask           --    mask
    
    Returns the processed image
    """
    output = ""
    if theLayer and outputDirectory :
        app = otbApplication.Registry.CreateApplication("Segmentation")
        
        input = str( theLayer )
        temp = os.path.basename( str( input ) )
        
        try :
            index = temp.index(".")
        # case of a file without extension opened (.hdr)
        except ValueError:
            index = len(temp)
        
        output = outputDirectory + "/" + temp[0:index] + "_segmentation_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".sqlite"# + temp[index:]
        
        app.SetParameterString("in", input)
        app.SetParameterString("mode.vector.out", output)
        app.SetParameterString("mode.vector.inmask", shapeMask)
        app.SetParameterInt("filter.meanshift.spatialr", spatialRadius )
        app.SetParameterFloat("filter.meanshift.ranger", spectralValue )
        app.SetParameterFloat("filter.meanshift.thres", convergenceTh )
        app.SetParameterInt("filter.meanshift.maxiter", maxIteration )
        app.SetParameterInt("filter.meanshift.minsize", minimunRegionSize )

        app.ExecuteAndWriteOutput()
        
    return output


