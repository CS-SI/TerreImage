# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2014-05-12
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

import os
import re
import shutil

from qgis.core import QgsPoint, QgsRaster

from PyQt4.QtGui import QInputDialog

import OTBApplications
import terre_image_run_process

# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_processing')
logger.setLevel(logging.DEBUG)
# log_file = os.path.join(os.path.expanduser("~"), "log_terr_image_qprocess")
# fh = logging.FileHandler(log_file)
# formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)


def ndvi(layer, working_directory, iface):
    # NDVI= (PIR-R)/(PIR+R)
    if not layer:
        logger.debug("Aucune layer selectionnée")
    else:
        if layer.pir and layer.red:
            image_in = layer.source_file
            logger.debug("image_in: " + image_in)
            logger.debug(working_directory)
            output_filename = os.path.join(working_directory,
                                           os.path.basename(os.path.splitext(image_in)[0]) + "_ndvi" + os.path.splitext(image_in)[1])
            logger.debug(output_filename)
            if not os.path.isfile(output_filename):
                layer_pir = "im1b" + str(layer.pir)
                layer_red = "im1b" + str(layer.red)
                expression = "\"if((" + layer_pir + "+" + layer_red + ")!=0,(" + layer_pir + "-" + layer_red + ")/(" + layer_pir + "+" + layer_red + "),0)\""
                logger.debug(expression)
                logger.debug("image_in" + image_in)
                OTBApplications.bandmath_cli([image_in], expression, output_filename)
            return output_filename
    return ""


def ndti(layer, working_directory, iface):
    # SQRT(R+0.5)
    # NDTI= (R-G)/(R+G)
    if not layer:
        logger.debug("Aucune layer selectionnée")
    else:
        if layer.red:
            image_in = layer.source_file
            logger.debug("image_in" + image_in)
            output_filename = os.path.join(working_directory, os.path.basename(os.path.splitext(image_in)[0]) + "_ndti" + os.path.splitext(image_in)[1])
            logger.debug(output_filename)
            if not os.path.isfile(output_filename):
                layer_red = "im1b" + str(layer.red)
                layer_green = "im1b" + str(layer.green)
                # expression = "\"sqrt(" + layer_red + "+0.5)\""
                expression = "\"if((" + layer_red + "+" + layer_green + ")!=0,(" + layer_red + "-" + layer_green + ")/(" + layer_red + "+" + layer_green + "),0)\""
                logger.debug(expression)
                logger.debug("image_in" + image_in)
                OTBApplications.bandmath_cli([image_in], expression, output_filename)
            return output_filename


def brightness(layer, working_directory, iface):
    # IB = sqrt(RxR+PIRxPIR)
    if not layer:
        logger.debug("Aucune layer selectionnée")
    else:
        if layer.pir and layer.red:
            image_in = layer.source_file
            logger.debug("image_in" + image_in)
            logger.debug(working_directory)
            output_filename = os.path.join(working_directory,
                                           os.path.basename(os.path.splitext(image_in)[0]) + "_brillance" + os.path.splitext(image_in)[1])
            logger.debug(output_filename)
            if not os.path.isfile(output_filename):
                layer_pir = "im1b" + str(layer.pir)
                layer_red = "im1b" + str(layer.red)
                expression = "\"sqrt(" + layer_red + "*" + layer_red + "*" + layer_pir + "*" + layer_pir + ")\""
                logger.debug(expression)
                logger.debug("image_in" + image_in)
                OTBApplications.bandmath_cli([image_in], expression, output_filename)
            return output_filename


def threshold(layer, working_directory, forms):
    logger.debug("threshold" + str(forms))
    image_in = layer.get_source()
    temp = []
    i = 1

    if len(forms) == 1:
        output_filename = os.path.join(working_directory,
                                       os.path.basename(os.path.splitext(image_in)[0]) + "_threshold" + os.path.splitext(image_in)[1])
        OTBApplications.bandmath_cli([image_in], forms[0], output_filename)
    else:
        for formula in forms:
            output_filename = os.path.join(working_directory,
                                           os.path.basename(os.path.splitext(image_in)[0]) + "_threshold" + str(i) + os.path.splitext(image_in)[1])
            OTBApplications.bandmath_cli([image_in], formula, output_filename)
            i += 1
            temp.append(output_filename)
        output_filename = os.path.join(working_directory, os.path.basename(os.path.splitext(image_in)[0]) + "_threshold" + os.path.splitext(image_in)[1])

        OTBApplications.concatenateImages_cli(temp, output_filename)

    return output_filename


def angles(layer, working_directory, iface, x, y):
    ident = layer.get_qgis_layer().dataProvider().identify(QgsPoint(x, y), QgsRaster.IdentifyFormatValue)
    logger.debug(ident)
    if ident is not None:
        attr = ident.results()
        logger.debug(attr)
        if len(attr) == layer.get_qgis_layer().bandCount():
            image_in = layer.get_qgis_layer().source()
            output_filename = os.path.join(working_directory, os.path.basename(os.path.splitext(image_in)[0]) + "_angles" + str(x).replace(".", "dot") + "_" + str(y).replace(".", "dot") + os.path.splitext(image_in)[1])

            if not os.path.isfile(output_filename):
                num = []
                denom = []
                fact = []
                # acos((im1b1*1269+im1b2*1060+im1b3*974+im1b4*1576)/
                # (sqrt((1269*1269+1060*1060+974*974+1576*1576)*
                # (im1b1*im1b1+im1b2*im1b2+im1b3*im1b3+im1b4*im1b4))))
                for index in range(1, layer.get_qgis_layer().bandCount() + 1):
                    current_band = "im1b" + str(index)
                    band_value = attr[index]
                    num.append(current_band + "*" + str(band_value))
                    denom.append(str(band_value) + "*" + str(band_value))
                    fact.append(current_band + "*" + current_band)

                formula = "if(((" + "+".join(fact) + ") != 0),"

                formula += "acos("
                formula += "(" + "+".join(num) + ")/"
                formula += "(sqrt("
                formula += "(" + "+".join(denom) + ")*"
                formula += "(" + "+".join(fact) + ")"
                formula += "))"
                formula += "), 0)"

                formule_ = "\"if( " + formula + ">0.0001, 1/" + formula + ", 0)\""

                logger.debug("num" + str(num))
                logger.debug("denom" + str(denom))
                logger.debug("fact" + str(fact))
                logger.debug("formula" + str(formula))

                OTBApplications.bandmath_cli([image_in], formule_, output_filename)
                # rlayer = manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_angles" + str(x) + "_" + str(y), iface )
                # manage_QGIS.histogram_stretching( rlayer, iface.mapCanvas())
            return output_filename


def kmeans(layer, working_directory, iface, nb_class=None):
    """
    WARNING: nb_valid_pixels à calculer ?
    """
    internal_working_directory = os.path.join(working_directory, "Internal")
    if not os.path.exists(internal_working_directory):
        os.makedirs(internal_working_directory)

    logger.debug("enntree dans le kmeans")
    bands = []
    if nb_class is None:
        testqt, ok = QInputDialog.getInt(None, "Kmeans", "Nombre de classes", 5)
        if ok:
            nb_class = testqt
    # mask = OTBApplications.bandmath([layer.get_source()], "if(im1b1>0,1,0)", working_directory, "mask")
    output = OTBApplications.kmeans_cli(layer.get_source(), nb_class, internal_working_directory)
    image_ref = recompose_image(layer, internal_working_directory)
    # if not os.path.isfile(output_colored):
    output_colored = OTBApplications.color_mapping_cli_ref_image(output, image_ref, working_directory)
    return output_colored


def recompose_image(layer, working_directory):
    bands = layer.bands
    image_in = layer.get_source()
    num_band_pir = bands['pir']
    num_band_red = bands['red']
    num_band_green = bands['green']
    band_pir = gdal_translate_get_one_band(image_in, num_band_pir, working_directory)
    band_red = gdal_translate_get_one_band(image_in, num_band_red, working_directory)
    band_green = gdal_translate_get_one_band(image_in, num_band_green, working_directory)

    logger.debug("pir" + band_pir)
    logger.debug("red" + band_red)
    logger.debug("green" + band_green)

    output_filename = os.path.join(working_directory, os.path.splitext(os.path.basename(image_in))[0] + "pir_red_green" + os.path.splitext(os.path.basename(image_in))[1])
    logger.debug("recomposed image" + output_filename)
    if not os.path.isfile(output_filename):
        OTBApplications.concatenateImages_cli([band_pir, band_red, band_green], output_filename, "uint16")
    return output_filename


def gdal_translate_get_one_band(image_in, band_number, working_dir):
    """
    Runs gdal translate to get the band_number of the image_in
    TODO: working dir
    """
    output_image_one_band = os.path.join(working_dir, os.path.splitext(os.path.basename(image_in))[0] + "-b" + str(band_number) + os.path.splitext(image_in)[1])
    if not os.path.isfile(output_image_one_band):
        command_gdal = "gdal_translate -b " + str(band_number) + " " + "\"" + image_in + "\"" + " " + "\"" + output_image_one_band + "\""
        logger.info("command_gdal" + command_gdal)
        # os.system( command_gdal )
        terre_image_run_process.run_process(command_gdal)
    return output_image_one_band


def get_sensor_id(image):
    currentOs = os.name

#     if currentOs == "posix":
    command = "otbcli ReadImageInfo "  # -in " + image  # + " | grep \"sensor:\""
#     else:
#         command = "otbcli ReadImageInfo -in " + image #+ " | findstr \"sensor:\""
    args = " -in " + image

    if currentOs == "posix":
        command += args
        result_sensor = terre_image_run_process.run_process(command)
    else:
        result_sensor = terre_image_run_process.run_otb_app("ReadImageInfo", args)
    if result_sensor:
        # type(result_sensor) = PyQt4.QtCore.QByteArray
        for line in str(result_sensor).splitlines():
            if "sensor" in line:
                # sensor_line = result_sensor[0]
                sensor = re.search('sensor: ([a-zA-Z \d]+)$', line)

                if sensor:
                    # group 1 parce qu'on a demande qqchose de particulier a la regexpr a cause des ()
                    sensor = sensor.group(1)
                return sensor


def export_kmz(filenames, working_directory):
    """
    """
    internal_working_directory = os.path.join(working_directory, "Internal")
    if not os.path.exists(internal_working_directory):
        os.makedirs(internal_working_directory)

    kmzs = []
    for image in filenames:
        kmz_tmp = OTBApplications.otbcli_export_kmz(image, internal_working_directory)
        kmzs.append(kmz_tmp)

    # attention rustine
    # kmzs = glob.glob( os.path.join(internal_working_directory, "*.kmz"))
    kmz_to_return = []
    for kmz in kmzs:
        new_path = os.path.join(working_directory, os.path.basename(kmz))
        shutil.copy(kmz, new_path)
        kmz_to_return.append(new_path)

    return kmz_to_return


