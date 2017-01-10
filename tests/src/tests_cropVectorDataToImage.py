# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2016-06-02
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
from terre_image_test_case import TerreImageTestCase
from TerreImage.ClassificationSupervisee import cropVectorDataToImage
from TerreImage.terre_image_gdal_api import get_image_epsg_code_with_gdal


class TestCropVectorDataToImage(TerreImageTestCase):

    def setUp(self):
        self.image_test = os.path.join(self.data_dir_input, "classif", "taredji_extract_1024.tif")
        self.vector_test = os.path.join(self.data_dir_input, "classif", 'samples', "green.shp")
        self.working_dir1 = os.path.join(self.working_dir, "1")
        if not os.path.isdir(self.working_dir1):
            os.makedirs(self.working_dir1)


    def testGenerateEnvelope_ok(self):
        """
        Test on Terre Image Generate envelope
        Returns:

        """
        epsg_code = get_image_epsg_code_with_gdal(self.image_test)
        generated_vector = cropVectorDataToImage.GenerateEnvelope(self.image_test, epsg_code, self.working_dir1)
        baseline = os.path.join(self.data_dir_baseline, "classif", "Classification", "class0", "imageenveloppe.shp")
        self.assertEqual(self.checkVector(generated_vector, baseline),0)


    #
    # def testReprojectVector_ok(self):
    #     """
    #     Test on Terre Image ReprojectVector
    #     Returns:
    #
    #     """
    #     generated_vector = cropVectorDataToImage.ReprojectVector(self.vector_test, self.image_test, self.working_dir1)
    #     baseline = os.path.join(self.data_dir_baseline, "classif", "Classification", "class0", "tmp_reprojected.shp")
    #     self.assertEqual(self.checkVector(generated_vector, baseline),0)


    def testIntersectLayers_ok(self):
        """
        Test on Terre Image IntersectLayers
        Returns:

        """
        inputVector = os.path.join(self.data_dir_baseline, "classif", "Classification", "class0", "tmp_reprojected.shp")
        inputEnvelope = os.path.join(self.data_dir_baseline, "classif", "Classification", "class0", "imageenveloppe.shp")
        generated_vector = cropVectorDataToImage.IntersectLayers(inputVector, inputEnvelope, self.working_dir1)
        baseline = os.path.join(self.data_dir_baseline, "classif", "Classification", "class0", "preprocessed.shp")
        self.assertEqual(self.checkVector(generated_vector, baseline),0)

    #
    # def testCropVectorDataToImage_ok(self):
    #     """
    #     Test on Terre Image CropVectorDataToImage
    #     Returns:
    #
    #     """
    #     generated_vector = cropVectorDataToImage.cropVectorDataToImage(self.image_test, self.vector_test, self.working_dir)
    #     baseline = os.path.join(self.data_dir_baseline, "classif", "Classification", "class0", "preprocessed.shp")
    #     self.assertEqual(self.checkVector(generated_vector, baseline),0)


if __name__ == '__main__':
    unittest.main()