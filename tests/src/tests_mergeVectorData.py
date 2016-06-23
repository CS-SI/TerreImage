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
from TerreImage.ClassificationSupervisee import mergeVectorData


class TestMergeVectorData(TerreImageTestCase):

    def setUp(self):
        self.image_test = os.path.join(self.data_dir_input, "classif", "taredji_extract_1024.tif")
        self.vector_test = os.path.join(self.data_dir_input, "classif", 'samples', "green.shp")
        self.working_dir1 = os.path.join(self.working_dir, "1")
        if not os.path.isdir(self.working_dir1):
            os.makedirs(self.working_dir1)

    def testMergeVectorData(self):
        green_files = os.path.join(self.data_dir_input, "classif", 'samples', "green.*")
        os.system("cp {} {}".format(green_files, self.working_dir1))
        green = os.path.join(self.working_dir, "green.shp")
        road_files = os.path.join(self.data_dir_input, "classif", 'samples', "road.*")
        os.system("cp {} {}".format(road_files, self.working_dir1))
        road = os.path.join(self.working_dir, "road.shp")
        union = mergeVectorData.unionPolygonsWithOGR([green, road], self.working_dir1)




if __name__ == '__main__':
    unittest.main()