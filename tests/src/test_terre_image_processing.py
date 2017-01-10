# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2016-05-24
        copyright           : (C) 2016 by CNES
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


import unittest
import os
from qgis.core import QgsRasterLayer
from TerreImage import terre_image_processing
from TerreImage.working_layer import WorkingLayer
from terre_image_test_case import TerreImageTestCase


class TestTerreImageProcessingMethods(TerreImageTestCase):

    def setUp(self):
        """
        Defines the test image and create a Terre Image working layer
        Returns:

        """
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")
        self.raster_layer = QgsRasterLayer(self.image_test, "taredji_extract")
        self.terre_image_layer = WorkingLayer(self.image_test, self.raster_layer, {'red':1, 'green':2, 'blue':3, 'pir':4, 'mir':None})

    def test_ndvi(self):
        """
        Test the ndvi function
        Returns:

        """
        generated_image = terre_image_processing.ndvi(self.terre_image_layer, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_ndvi.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))

    def test_ndti(self):
        """
        Test the ndti function
        Returns:

        """
        generated_image = terre_image_processing.ndti(self.terre_image_layer, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_ndti.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))

    def test_brightness(self):
        """
        Test the brightness function
        Returns:

        """
        generated_image = terre_image_processing.brightness(self.terre_image_layer, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_brightness.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))

    def test_threshold(self):
        """
        Test the threshold function
        Returns:

        """
        generated_image = terre_image_processing.brightness(self.terre_image_layer, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_brightness.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))


    # #TODO uses QGIS API to get the value of the image at the given coordinate
    # #TODO create baseline
    # def test_angles(self):
    #     """
    #     Test the spectral angle function
    #     Returns:
    #
    #     """
    #     pass
    #     #generated_image = terre_image_processing.angles(self.terre_image_layer, self.working_dir, 0, 0)
    #     # baseline = os.path.join(self.data_dir_baseline, "taredji_extract_brightness.tif")
    #     # self.assertTrue(self.checkResult(generated_image, baseline))

    def test_kmeans(self):
        """
        Test the kmeans function
        Returns:

        """
        generated_image = terre_image_processing.kmeans(self.terre_image_layer, self.working_dir, 5)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_5classes_colored.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))
        self.assertTrue(self.checkResult(generated_image, baseline), 2)
        self.assertTrue(self.checkResult(generated_image, baseline), 3)

    def test_get_sensor_id(self):
        """
        Test the function to get a sensor
        Returns:

        """
        generated_sensor = terre_image_processing.get_sensor_id(self.terre_image_layer.source_file)
        self.assertEqual(generated_sensor, None)
        qb_1_extract = os.path.join(self.data_dir_input, "qb_1_ortho_extract.tif")
        generated_sensor = terre_image_processing.get_sensor_id(qb_1_extract)
        self.assertEqual(generated_sensor, "QB02")

    def test_gdal_translate_get_one_band(self):
        """
        Test the gdal function to get a specific band
        Returns:

        """
        generated_image = terre_image_processing.gdal_translate_get_one_band(self.terre_image_layer.source_file,
                                                                             1, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_b1.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))


if __name__ == '__main__':
    unittest.main()

