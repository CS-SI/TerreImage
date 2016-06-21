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
from qgis.core import QgsRasterLayer
from TerreImage.terre_image_run_process import TerreImageProcess, get_otb_command
from terre_image_test_case import TerreImageTestCase


class TestTerreImageProcess(TerreImageTestCase):

    def setUp(self):
        """
        Defines the test image
        Returns:

        """
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")
        self.otb_dir = "/home/amondot/Downloads/OTB-5.2.1-Linux64/"

    def test_getProcessObject(self):
        """
        Test the process creation
        Returns:

        """
        process = TerreImageProcess()
        self.assertIsNotNone(process)


    def test_setOtbProcessEnvCustom(self):
        """
        Test the process environement definition
        Returns:

        """
        process = TerreImageProcess()
        libdir = os.path.join(self.otb_dir, "lib", "otb", "applications")
        bindir = os.path.join(self.otb_dir, "bin")
        process.set_otb_process_env_custom(otb_app_path=libdir,
                                           path=bindir)
        self.assertEqual(process.env.value("OTB_APPLICATION_PATH"), libdir)
        self.assertTrue(str(process.env.value("PATH")).startswith(bindir))


    def test_runWhichLauncher(self):
        """
        Test environement...
        Uncomment to test an other environement than the one defined in the configuration file

        Returns:

        """
        process = TerreImageProcess()
        # libdir = os.path.join(self.otb_dir, "lib", "otb", "applications")
        # bindir = os.path.join(self.otb_dir, "bin")
        # process.set_otb_process_env_custom(otb_app_path=libdir,
        #                                    path=bindir)
        print os.environ.get("PATH")
        command = "which otbApplicationLauncherCommandLine"
        result = process.run_process(command)
        self.assertIsNotNone(result)
        self.assertEqual(result.data().replace("\n", ""),
                         os.path.join(self.otb_dir, "bin", "otbApplicationLauncherCommandLine"))


    def test_runReadImageInfo(self):
        """
        Test of a OTB application and get the output.
        Uncomment to test an other environement than the one defined in the configuration file
        Returns:

        """
        process = TerreImageProcess()
        # libdir = os.path.join(self.otb_dir, "lib", "otb", "applications")
        # bindir = os.path.join(self.otb_dir, "bin")
        # process.set_otb_process_env_custom(otb_app_path=libdir,
        #                                    path=bindir)
        app_name = "ReadImageInfo"
        arguments = "-in {}".format(self.image_test)
        result = process.run_process(get_otb_command(app_name, arguments))
        self.assertIsNotNone(result)
        self.assertIn("Image general information", result.data())


    # def test_runReadImageInfoFail(self):
    #     """
    #     Test of a OTB application this test should fail
    #     Returns:
    #
    #     """
    #     process = TerreImageProcess()
    #     # libdir = os.path.join(self.otb_dir, "lib", "otb", "applications")
    #     # bindir = os.path.join(self.otb_dir, "bin")
    #     # process.set_otb_process_env_custom(otb_app_path=libdir,
    #     #                                    path=bindir)
    #     app_name = "ReadImageInfo"
    #     arguments = ""
    #     result = process.run_process("otbApplicationLauncherCommandLine ReadImageInfo") #(get_otb_command(app_name, arguments))
    #     self.assertIsNotNone(result)
    #     self.assertIn("Image general information", result)



class TestTerreImageRunProcess(TerreImageTestCase):

    def setUp(self):
        """
        Defines the test image
        Returns:

        """
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")
        self.otb_dir = "/home/amondot/Downloads/OTB-5.2.1-Linux64/"


    def test_get_otb_command(self):
        """

        Returns:

        """
        app_name = "ReadImageInfo"
        arguments = "-in {}".format(self.image_test)
        command_otb = get_otb_command(app_name, arguments)
        # command_baseline = "{} ReadImageInfo -in {}".format("otbApplicationLauncherCommandLine",
        #                                                        self.image_test)
        command_baseline = "{} ReadImageInfo -in {}".format(os.path.join(self.otb_dir, "bin",
                                                                         "otbApplicationLauncherCommandLine"),
                                                               self.image_test)
        self.assertEqual(command_otb, command_baseline)


