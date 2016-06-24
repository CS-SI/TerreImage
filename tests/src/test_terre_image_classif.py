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
from TerreImage.ClassificationSupervisee import classif
from terre_image_test_case import TerreImageTestCase


class TestTerreImageClassif(TerreImageTestCase):

    def setUp(self):
        """
        Defines the test image and the samples for the classifr
        Returns:

        """
        self.image_test = os.path.join(self.data_dir_input, "classif", "taredji_extract_1024.tif")
        self.image_test_ndvi = os.path.join(self.data_dir_input, "classif", "taredji_extract_1024_ndvi.tif")
        self.vector_test = os.path.join(self.data_dir_input, "classif", 'samples', "samples.shp")
        self.working_dir1 = os.path.join(self.working_dir, "1")
        if os.path.isdir(self.working_dir1):
            os.system("rm -rf {}".format(self.working_dir1))
        os.makedirs(self.working_dir1)


    def test_create_vrt_from_filelist(self):
        """
        Test of create_vrt_from_filelist
        Returns:

        """

        outputVRT = os.path.join(self.working_dir1, "createVRT.tif")
        baseline = os.path.join(self.data_dir_baseline, "create_vrt_from_filelist.vrt")
        classif.create_vrt_from_filelist([self.image_test, self.image_test_ndvi], outputVRT)
        self.assertTrue(self.checkResult(outputVRT, baseline))





    def test_full_classification(self):
        """
        Test of full classification chain
        Returns:

        """
        outputclassification = os.path.join(self.working_dir1, "out_classif.tif")
        out_pop = os.path.join(self.working_dir1, "out_classif_pop.xml")
        baseline = os.path.join(self.data_dir_baseline, "classif_new", "out_classif_pop.xml")
        confMat, kappa = classif.full_classification([self.image_test], self.vector_test,
                                                     outputclassification, out_pop, self.working_dir1)
        self.assertEqual(kappa, 1)# 0.999485)
        self.assertTrue(self.checkFiles(out_pop, baseline))




if __name__ == '__main__':
    unittest.main()

