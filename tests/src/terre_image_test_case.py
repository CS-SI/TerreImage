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
from TerreImage.terre_image_run_process import TerreImageProcess

# import logging for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('terre_image_test_case')
logger.setLevel(logging.DEBUG)


class TerreImageTestCase( unittest.TestCase ):
    def __init__( self, *args, **kwargs ):
        super( TerreImageTestCase, self ).__init__( *args, **kwargs )
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        self.data_dir = os.path.join(parent_dir, "data")
        self.data_dir_input = os.path.join(self.data_dir, "input")
        self.data_dir_baseline = os.path.join(self.data_dir, "baseline")
        self.src_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
        # TBD
        self.working_dir = "/tmp/terre-image-tests"
        if os.path.isdir(self.working_dir):
            os.system("rm -rf {}".format(self.working_dir))
        os.makedirs(self.working_dir)


    def checkResult( self, tested_image, reference_image, input_band=1 ):
        """ Check if testVar and refVar are equal with the given precision and the given type
        @param tested_image: variable computed by the test
        @param reference_image: array variable containing the reference value(s), the precision and the type
            -> reference value(s) to compare with the testVar
            -> numerical precision to use to chekc if variables are equal
            -> type of variables to check

        @return: True is variables are equal, False otherwise
        """
        logger.info("Comparing {} and {}".format(reference_image, tested_image))

        command = "otbcli_CompareImages -ref.in {} -ref.channel {} " \
                  "-meas.in {} -meas.channel {}".format(reference_image,
                                                        input_band,
                                                        tested_image,
                                                        input_band)
        mse = -9999
        mae = -9999
        psnr = -9999
        res = TerreImageProcess().run_process(command)

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

        mse = re.search('mse: (\d*[\.\d]+)$', mse_line).group(1).replace(" ", "")
        mae = re.search('mae: (\d*[\.\d]+)$', mae_line).group(1).replace(" ", "")
        psnr = re.search('psnr: (\d*[\.\d]+)$', psnr_line).group(1).replace(" ", "")

        if mse == mae == psnr == "0":
            return True
        else:
            logging.info("mse: {}, \n mae {}, \n psnr: {}".format(mse, mae, psnr))
            return False

    def checkVector(self, vectorTest, vectorBaseline):
        """

        Args:
            vectorTest:
            vectorBaseline:

        Returns:

        """
        command = "diff {} {}".format(vectorTest, vectorBaseline)
        res = TerreImageProcess().run_process(command)
        lines = str(res).splitlines()

        if len(lines) != 0:
            logging.info( "=====================")
            logging.info( "Result of diff:")
            logging.info( lines)
            logging.info( "=====================")

            command = "ogrinfo -al {} > {}".format(vectorTest, os.path.splitext(vectorTest)[0] + ".ogrinfo")
            os.system(command)
            command = "ogrinfo -al {} > {}".format(vectorBaseline, os.path.splitext(vectorBaseline)[0] + ".ogrinfo")
            os.system(command)
            command = "diff {} {}".format(os.path.splitext(vectorTest)[0] + ".ogrinfo",
                                          os.path.splitext(vectorBaseline)[0] + ".ogrinfo")
            os.system(command)


        return len(lines)


    def checkFiles(self, fileTest, fileBaseline):
        """

        Args:
            fileTest:
            fileBaseline:

        Returns:

        """
        command = "diff {} {}".format(fileTest, fileBaseline)
        res = TerreImageProcess().run_process(command)
        lines = str(res).splitlines()

        if len(lines) != 0:
            logging.info( "=====================")
            logging.info( "Result of diff:")
            logging.info( lines)
            logging.info( "=====================")

            return False
        else:
            return True