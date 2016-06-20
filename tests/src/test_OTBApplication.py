# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerreImage
                    -------------------
        begin               : 2016-06-20
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
 ***************************************************************************
"""



import unittest
import os
import shutil
from qgis.core import QgsRasterLayer
from TerreImage import OTBApplications
from terre_image_test_case import TerreImageTestCase


class TestTerreImageOTBApplications(TerreImageTestCase):

    def setUp(self):
        """
        Defines the test image
        Returns:

        """
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")
        self.otb_dir = "/home/amondot/Downloads/OTB-5.2.1-Linux64/"


    def test_BandMath(self):
        """
        Test call of OTBApplication BandMath
        Returns:

        """
        output_image = os.path.join(self.working_dir, "test_band_math.tif")
        OTBApplications.bandmath_cli([self.image_test], "im1b1", output_image)
        self.assertTrue(os.path.exists(output_image))

    def test_Concatenate(self):
        """
        Test call of OTBApplication Concatenate
        Returns:

        """
        output_image = os.path.join(self.working_dir, "test_concatenate.tif")
        OTBApplications.concatenateImages_cli([self.image_test], output_image)
        self.assertTrue(os.path.exists(output_image))

    def test_KMeans(self):
        """
        Test call of OTBApplication KMeans
        Returns:

        """
        output_image = OTBApplications.kmeans_cli(self.image_test, 5, self.working_dir)
        self.assertTrue(os.path.exists(output_image))

    def test_ColorMapping(self):
        """
        Test call of OTBApplication ColorMapping
        Returns:

        """
        output_image = OTBApplications.color_mapping_cli_ref_image(self.image_test, self.image_test, self.working_dir)
        self.assertTrue(os.path.exists(output_image))


    # def test_KmzExport(self):
    #     """
    #     Test call of OTBApplication KmzExport
    #     Returns:
    #
    #     """
    #     output_image = OTBApplications.otbcli_export_kmz(self.image_test, self.working_dir)
    #     self.assertTrue(os.path.exists(output_image))


    def test_ReadImageInfo(self):
        """
        Test call of OTBApplication ReadImageInfo
        Returns:

        """
        result = OTBApplications.read_image_info_cli(self.image_test)
        self.assertIsNotNone(result)
        self.assertIn("Image general information", result.data())

