# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerreImage
                    -------------------
        begin               : 2015-10-28
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
"""

import os
from PyQt4.QtCore import QProcessEnvironment, QProcess

import terre_image_configuration

import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_RunProcess')
logger.setLevel(logging.DEBUG)




class TerreImageProcess():

    def __init__(self):
        self.process = QProcess()
        self.env = QProcessEnvironment.systemEnvironment()
        self.set_otb_process_env_default()

    def run_process(self, command):
        print "Running {}".format(command)
        self.process.setProcessEnvironment(self.env)

        print "..............", self.process.processEnvironment().value("OTB_APPLICATION_PATH")
        print "..............", self.process.processEnvironment().value("PATH")
        # print "Environ : PATH {}".format(os.environ["PATH"])
        # print "Environ : OTB_APPLICATION_PATH {}".format(os.environ.get("OTB_APPLICATION_PATH", "Empty"))

        self.process.start(command)
        if self.process.waitForStarted():
            self.process.waitForFinished(-1)
            exit_code = self.process.exitCode()
            logger.info("Code de sortie : " + str(exit_code))
            print "exit code", exit_code
            if exit_code < 0:
                code_d_erreur = self.process.error().data
                dic_err = { 0:"QProcess::FailedToStart", 1:"QProcess::Crashed",
                            2:"QProcess::TimedOut", 3:"QProcess::WriteError",
                            4:"QProcess::ReadError", 5:"QProcess::UnknownError" }
                logger.info("Code erreur : " + str(code_d_erreur))
                logger.info(dic_err[code_d_erreur])

            result = self.process.readAllStandardOutput()
            # print type(result), result
            error = self.process.readAllStandardError().data()
            # print repr(error)
            if not error == "\n":
                logger.info("error : " + "\'" + str(error) + "\'")
                print "************", error
            logger.info("output : " + result.data() + "fin output")
            return result
        else:
            code_d_erreur = self.process.error()
            dic_err = { 0:"QProcess::FailedToStart", 1:"QProcess::Crashed",
                        2:"QProcess::TimedOut", 3:"QProcess::WriteError",
                        4:"QProcess::ReadError", 5:"QProcess::UnknownError" }
            logger.info("Code erreur : " + str(code_d_erreur))
            logger.info(dic_err[code_d_erreur])
        return None

    def set_env_var(self, varname, varval, append = False, pre = False):

        if append == True:
            if pre == True:
                # insert value at the end of the variable
                self.env.insert(varname, self.env.value(varname) + os.pathsep + varval)
            else:
                # insert value in head
                self.env.insert(varname, varval + os.pathsep + self.env.value(varname))
        else:
            # replace value if existing
            self.env.remove(varname)
            self.env.insert(varname, varval)
        print "env {} {}".format(varname, self.env.value(varname))

    def set_otb_process_env(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.set_env_var("OTB_APPLICATION_PATH", os.path.join(dirname, "win32", "plugin"), pre=False)
        self.set_env_var("PATH", os.path.join(dirname, "win32", "bin"), append = False, pre=False)


    def set_otb_process_env_custom(self, otb_app_path="", path=""):
        """
        Add the given values to OTB_APPLICATION_PATH and PATH environement variables
        Args:
            otb_app_path:
            path:

        Returns:

        """
        self.set_env_var("OTB_APPLICATION_PATH", otb_app_path, pre=False)
        self.set_env_var("PATH", path, append = False, pre=False)


    def set_otb_process_env_default(self):
        """
        Add the values from the config file to OTB_APPLICATION_PATH and PATH environement variables
        Args:
            otb_app_path:
            path:

        Returns:

        """

        self.set_env_var("OTB_APPLICATION_PATH",
                         terre_image_configuration.OTB_APPLICATION_PATH, pre=False)
        self.set_env_var("PATH", terre_image_configuration.PATH, append = False, pre=True)
        # print os.listdir(terre_image_configuration.PATH)


def get_otb_command(app_name, arguments):
    """
    Returns the command to launch.
    WARNING : OTB_APPLICATION_PATH has to be set.
    Args:
        app_name:
        arguments:

    Returns:

    """
    # command = "otbApplicationLauncherCommandLine {} {}".format(app_name, arguments)
    command = "{} {} {}".format(os.path.join(terre_image_configuration.PATH, "otbApplicationLauncherCommandLine"),
                                app_name, arguments)
    return command


