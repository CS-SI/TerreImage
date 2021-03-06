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
import terre_image_exceptions

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()



class TerreImageProcess():

    def __init__(self):
        self.process = QProcess()
        self.process.error[QProcess.ProcessError].connect(self.error_management)
        self.env = QProcessEnvironment().systemEnvironment()
        self.set_otb_process_env_default()
        self.command = ""

    def run_process(self, command):
        logger.info(u"Running {}".format(command))
        self.process.setProcessEnvironment(self.env)

        # logger.debug("..............{}".format(self.process.processEnvironment().value("OTB_APPLICATION_PATH")))
        # logger.debug("..............{}".format(self.process.processEnvironment().value("PATH")))
        # logger.debug("Environ : PATH {}".format(os.environ["PATH"]))
        # logger.debug("Environ : OTB_APPLICATION_PATH {}".format(os.environ.get("OTB_APPLICATION_PATH", "Empty")))
        self.command = command
        self.process.start(command)
        if self.process.waitForStarted():
            self.process.waitForFinished(-1)
            exit_code = self.process.exitCode()
            if exit_code != 0:
                self.error_management(exit_code)
            result = self.process.readAllStandardOutput()
            # logger.debug(" {} {}".format(type(result), result))
            error = self.process.readAllStandardError().data()
            # logger.debug(repr(error))
            if not error in ["\n", ""]:
                logger.error("error : %s"%(error))
            output = result.data()
            logger.info(output)
            return result
        else:
            code_d_erreur = self.process.error()
            self.error_management(code_d_erreur)
        return None

    def error_management(self, errorCode):
        dic_err = { 0:"QProcess::FailedToStart", 1:"QProcess::Crashed",
            2:"QProcess::TimedOut", 3:"QProcess::WriteError",
            4:"QProcess::ReadError", 5:"QProcess::UnknownError",
            127:"Other, The application may not have been found"}
        try:
            type_qt_error = dic_err[errorCode]
            logger.error(u"Error {} {}".format(errorCode, type_qt_error))
        except KeyError:
            type_qt_error = ""
        error = self.process.readAllStandardError().data()
        logger.error(error)
        logger.error( self.process.readAllStandardOutput())
        try:
            raise terre_image_exceptions.TerreImageRunProcessError(u"Error running : {}\n {}{}".format(self.command,
                                                                                  type_qt_error, error
                                                                                  ))
        except UnicodeError:
            raise terre_image_exceptions.TerreImageRunProcessError(u"Error running : {}\n {}".format(self.command,
                                                                                  type_qt_error))

    def set_env_var(self, varname, varval, append = False, pre = False):

        if append == True:
            if pre == False:
                # insert value at the end of the variable
                self.env.insert(varname, self.env.value(varname) + os.pathsep + varval)
            else:
                # insert value in head
                self.env.insert(varname, varval + os.pathsep + self.env.value(varname))
        else:
            # replace value if existing
            self.env.insert(varname, varval)
        # logger.debug("env {} {}".format(varname, self.env.value(varname)))

    def set_otb_process_env(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.set_env_var("OTB_APPLICATION_PATH", os.path.join(dirname, "win32", "plugin"), pre=True)
        self.set_env_var("PATH", os.path.join(dirname, "win32", "bin"), append = False, pre=True)


    def set_otb_process_env_custom(self, otb_app_path="", path=""):
        """
        Add the given values to OTB_APPLICATION_PATH and PATH environement variables
        Args:
            otb_app_path:
            path:

        Returns:

        """
        self.set_env_var("OTB_APPLICATION_PATH", otb_app_path, pre=True)
        self.set_env_var("PATH", path, append = False, pre=True)


    def set_otb_process_env_default(self):
        """
        Add the values from the config file to OTB_APPLICATION_PATH and PATH environement variables
        Args:
            otb_app_path:
            path:

        Returns:

        """
        self.set_env_var("OTB_APPLICATION_PATH",
                         terre_image_configuration.OTB_APPLICATION_PATH, pre=True)
        self.set_env_var("PATH", terre_image_configuration.PATH, append = True, pre=True)
        if terre_image_configuration.LD_LIBRARY_PATH:
            self.set_env_var("LD_LIBRARY_PATH", terre_image_configuration.LD_LIBRARY_PATH, append = True, pre=True)
        # logger.debug(os.listdir(terre_image_configuration.PATH))


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
    command = u"{} {} {}".format(os.path.join(terre_image_configuration.PATH, "otbApplicationLauncherCommandLine"),
                                app_name, arguments)
    return command

def get_osgeo_command(app_name, args=[]):
    """
    Returns a command composed with app_name + 'key "value"' for each key, value in args
    Args:
        command:
        args:

    Returns:

    """
    command_to_return = u'{} "{}"'.format(app_name, '" "'.join(args))
    logger.debug(u"command to return {}".format(command_to_return))
    return command_to_return