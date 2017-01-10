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
 With changes in mu parser, formula changes from
 if(cond, value_if_true, value_if_false)
 to
 (cond?value_if_true:value_if_false)
"""

import os
import re
import shutil

from qgis.core import QgsPoint, QgsRaster

from PyQt4.QtGui import QInputDialog

import OTBApplications
from terre_image_run_process import TerreImageProcess
from terre_image_gdal_api import get_image_size_with_gdal

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()


def ndvi(layer, working_directory):
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
                layer_pir = "im1b{}".format(layer.pir)
                layer_red = "im1b{}".format(layer.red)
                expression = "\"((" + layer_pir + "+" + layer_red + ")!=0?(" + layer_pir + "-" + layer_red + ")/(" + layer_pir + "+" + layer_red + "):0)\""
                logger.debug(expression)
                logger.debug("image_in" + image_in)
                OTBApplications.bandmath_cli([image_in], expression, output_filename)
            return output_filename
    return ""


def ndti(layer, working_directory):
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
                layer_red = "im1b{}".format(layer.red)
                layer_green = "im1b{}".format(layer.green)
                # expression = "\"sqrt(" + layer_red + "+0.5)\""
                expression = "\"((" + layer_red + "+" + layer_green + ")!=0?(" + layer_red + "-" + layer_green + ")/(" + layer_red + "+" + layer_green + "):0)\""
                logger.debug(expression)
                logger.debug("image_in" + image_in)
                OTBApplications.bandmath_cli([image_in], expression, output_filename)
            return output_filename


def brightness(layer, working_directory):
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
                layer_pir = "im1b{}".format(layer.pir)
                layer_red = "im1b{}".format(layer.red)
                expression = "\"sqrt(" + layer_red + "*" + layer_red + "+" + layer_pir + "*" + layer_pir + ")\""
                logger.debug(expression)
                logger.debug("image_in" + image_in)
                OTBApplications.bandmath_cli([image_in], expression, output_filename)
            return output_filename


def threshold(layer, working_directory, forms):
    logger.debug("threshold {}".format(forms))
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


def angles(layer, working_directory, x, y):
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
                    current_band = "im1b{}".format(index)
                    band_value = attr[index]
                    num.append(current_band + "*" + str(band_value))
                    denom.append(str(band_value) + "*" + str(band_value))
                    fact.append(current_band + "*" + current_band)

                #compute denom for testing != 0
                mult_denom = "({})*({})".format("+".join(denom),
                                                "+".join(fact))
                #raw formula
                formula = "acos(({})/(sqrt({})))".format("+".join(num),
                                                        mult_denom)
                #add threshold
                formule_ = '"({}>0.0001?1/{}:0)"'.format(formula, formula)
                #add test on denom
                formula_with_test_denom_diff_0 = "({}!=0?{}:0)".format(mult_denom, formule_)

                logger.debug("num {}".format(num))
                logger.debug("denom {}".format(denom))
                logger.debug("fact {}".format(fact))
                logger.debug("formula {}".format(formula_with_test_denom_diff_0))

                OTBApplications.bandmath_cli([image_in], formula_with_test_denom_diff_0, output_filename)
                # rlayer = manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_angles" + str(x) + "_" + str(y), iface )
                # manage_QGIS.histogram_stretching( rlayer, iface.mapCanvas())
            return output_filename


def kmeans(layer, working_directory, nb_class=None):
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
        command_gdal = u'gdal_translate -b {} "{}" "{}"'.format(band_number, image_in, output_image_one_band)
        logger.info(u"command_gdal {}".format(command_gdal))
        TerreImageProcess().run_process(command_gdal)
    return output_image_one_band


def get_sensor_id(image):
    """
    Returns the sensor of the given image if found by ReadImageInfo
    Args:
        image:

    Returns:

    """
    result_sensor = OTBApplications.read_image_info_cli(image)
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
        size = get_image_size_with_gdal(image)
        warning_size = 0
        # by default, tile size of kmz export is 512
        # if the image size is smaller than 512, the application does not work properly
        if size[0] < 512 or size[1] < 512:
            warning_size = size[0] if (size[0]<size[1]) else size[1]
        kmz_tmp = OTBApplications.otbcli_export_kmz(image, internal_working_directory, warning_size)
        kmzs.append(kmz_tmp)

    # attention rustine
    # kmzs = glob.glob( os.path.join(internal_working_directory, "*.kmz"))
    kmz_to_return = []
    for kmz in kmzs:
        new_path = os.path.join(working_directory, os.path.basename(kmz))
        shutil.copy(kmz, new_path)
        kmz_to_return.append(new_path)

    return kmz_to_return


