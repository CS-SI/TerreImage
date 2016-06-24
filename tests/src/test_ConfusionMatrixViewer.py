# -*- coding: utf-8 -*-
"""
/***************************************************************************
TerreImage
                                 A QGIS plugin
                              -------------------
        begin               : 2016-06-23
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
from TerreImage.ClassificationSupervisee import ConfusionMatrixViewer
from terre_image_test_case import TerreImageTestCase


class TestTerreImageClassif(TerreImageTestCase):

    def setUp(self):
        """
        Defines the test image and the samples for the classifr
        Returns:

        """
        self.old_results = os.path.join(self.data_dir_baseline, "classif", "Classification", "classification.resultats.txt")
        self.image_test_ndvi = os.path.join(self.data_dir_input, "classif", "taredji_extract_1024_ndvi.tif")
        self.vector_test = os.path.join(self.data_dir_input, "classif", 'samples', "green.shp")

    def test_read_results_old(self):
        """
        Test on old method to read classification results
        Returns:

        """
        dic_info = ConfusionMatrixViewer.read_results_old(self.old_results)
        self.assertEqual(dic_info["kappa"], 0.957278)
        self.assertEqual(dic_info["percentage"], {0:24.2, 1:12.2, 2:8.2, 3:55.3})
        self.assertEqual(dic_info["confusion"], [["2041", "0", "0", "0"], ["0", "1949", "0", "0"],
                                                 ["0", "20", "1743", "227"], ["0", "3", "6", "2002"]])


    def test_read_results(self):
        """
        Test new old method to read classification results
        Returns:

        """
        confmat = os.path.join(self.data_dir_baseline, "classif_new", "svm.mat")
        kappa = 0.957278
        dic_info = ConfusionMatrixViewer.read_results(confmat, kappa, None)
        self.assertEqual(dic_info["kappa"], 0.957278)
        self.assertEqual(dic_info["percentage"], {0:24.2, 1:12.2, 2:8.2, 3:55.3})
        self.assertEqual(dic_info["confusion"], [["2041", "0", "0", "0"], ["0", "1949", "0", "0"],
                                                 ["0", "20", "1743", "227"], ["0", "3", "6", "2002"]])


if __name__ == '__main__':
    unittest.main()
