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
import re
from TerreImage.terre_image_run_process import run_process

class TerreImageTestCase( unittest.TestCase ):
    def __init__( self, *args, **kwargs ):
        super( TerreImageTestCase, self ).__init__( *args, **kwargs )
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        self.data_dir = os.path.join(parent_dir, "data")
        self.data_dir_input = os.path.join(self.data_dir, "input")
        self.data_dir_baseline = os.path.join(self.data_dir, "baseline")
        # TBD
        self.working_dir = "/tmp"


    def checkResult( self, tested_image, reference_image ):
        """ Check if testVar and refVar are equal with the given precision and the given type
        @param tested_image: variable computed by the test
        @param reference_image: array variable containing the reference value(s), the precision and the type
            -> reference value(s) to compare with the testVar
            -> numerical precision to use to chekc if variables are equal
            -> type of variables to check

        @return: True is variables are equal, False otherwise
        """
        print "Comparing {} and {}".format(reference_image, tested_image)

        command = "otbcli_CompareImages -ref.in {} -meas.in {}".format(reference_image,
                                                                       tested_image)
        mse = -9999
        mae = -9999
        psnr = -9999
        res = run_process(command)
        lines = str(res).splitlines()
        # for line in lines:
        #     # sensor_line = result_sensor[0]
        #     mse = re.search('mse: (\d*)$', line)
        #     if mse:
        #         # group 1 parce qu'on a demande qqchose de particulier a la regexpr a cause des ()
        #         mse = mse.group(1)
        #         continue
        # print "suite", lines
        # for line in lines:
        #     mae = re.search('mae: (\d*)$', line)
        #     if mae:
        #         # group 1 parce qu'on a demande qqchose de particulier a la regexpr a cause des ()
        #         mae = mae.group(1)
        #         print "MAE", mae
        #         continue
        # for line in lines:
        #     psnr = re.search('mse: (\d*)$', line)
        #     if psnr:
        #         # group 1 parce qu'on a demande qqchose de particulier a la regexpr a cause des ()
        #         mse = psnr.group(1)
        #         continue
        mse_line = lines[-4]
        mae_line = lines[-3]
        psnr_line = lines[-2]

        mse = re.search('mse: (\d*)$', mse_line).group(1).replace(" ", "")
        mae = re.search('mae: (\d*)$', mae_line).group(1).replace(" ", "")
        psnr = re.search('psnr: (\d*)$', psnr_line).group(1).replace(" ", "")

        if mse == mae == psnr == "0":
            return True
        else:
            print '"{}"'.format(mse)
            print "mse: {}, \n mae {}, \n psnr: {}".format(mse, mae, psnr)
            return False