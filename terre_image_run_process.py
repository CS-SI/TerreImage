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

        print "..............", self.process.processEnvironment().value("PATH")

        self.process.start(command)
        if self.process.waitForStarted():
            self.process.waitForFinished(-1)
            exit_code = self.process.exitCode()
            logger.info("Code de sortie : " + str(exit_code))
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
            self.env.insert(varname, varval)
        print "env {} {}".format(varname, self.env.value(varname))

    def set_otb_process_env(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.set_env_var("OTB_APPLICATION_PATH", os.path.join(dirname, "win32", "plugin"), pre=False)
        self.set_env_var("PATH", os.path.join(dirname, "win32", "bin"), append = True, pre=False)


    def set_otb_process_env_custom(self, otb_app_path="", path=""):
        """
        Add the given values to OTB_APPLICATION_PATH and PATH environement variables
        Args:
            otb_app_path:
            path:

        Returns:

        """
        self.set_env_var("OTB_APPLICATION_PATH", otb_app_path, pre=False)
        self.set_env_var("PATH", path, append = True, pre=False)


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
        self.set_env_var("PATH", terre_image_configuration.PATH, append = True, pre=False)





def get_otb_command(app_name, arguments):
    """
    Returns the command to launch.
    WARNING : OTB_APPLICATION_PATH has to be set.
    Args:
        app_name:
        arguments:

    Returns:

    """
    command = "otbApplicationLauncherCommandLine {} {}".format(app_name, arguments)
    return command


def run_process(fused_command, read_output = False):
    #     print "run process", fused_command
    #     qprocess = QProcess()
    #     set_process_env(qprocess)
    #     code_de_retour = qprocess.execute(fused_command)
    #     print "code de retour", code_de_retour
    #     logger.info("command: ")
    #     logger.info(fused_command)
    #     logger.info("code de retour" + str(code_de_retour))
    #
    # #     if not qprocess.waitForStarted():
    # #         # handle a failed command here
    # #         print "qprocess.waitForStarted()"
    # #         return
    # #
    # #     if not qprocess.waitForReadyRead():
    # #         # handle a timeout or error here
    # #         print "qprocess.waitForReadyRead()"
    # #         return
    # #     #if not qprocess.waitForFinished(1):
    # #     #    qprocess.kill()
    # #     #    qprocess.waitForFinished(1)
    #
    # #     if read_output:
    #
    #     # logger.info("Erreur")
    #     code_d_erreur = qprocess.error()
    #     dic_err = { 0:"QProcess::FailedToStart", 1:"QProcess::Crashed", 2:"QProcess::TimedOut", 3:"QProcess::WriteError", 4:"QProcess::ReadError", 5:"QProcess::UnknownError" }
    #     logger.info("Code de retour: " + str(code_d_erreur))
    #     logger.info(dic_err[code_d_erreur])
    #
    #     print "get output"
    #     output = str(qprocess.readAllStandardOutput())
    #     # print "output", output
    #     print 'end output'
    process = QProcess()
    process.start(fused_command)
    if process.waitForStarted():
        process.waitForFinished(-1)
        exit_code = process.exitCode()
        logger.info("Code de sortie : " + str(exit_code))
        if exit_code < 0:
            code_d_erreur = process.error().data
            dic_err = { 0:"QProcess::FailedToStart", 1:"QProcess::Crashed", 2:"QProcess::TimedOut", 3:"QProcess::WriteError", 4:"QProcess::ReadError", 5:"QProcess::UnknownError" }
            logger.info("Code erreur : " + str(code_d_erreur))
            logger.info(dic_err[code_d_erreur])

        result = process.readAllStandardOutput()
        # print type(result), result
        error = process.readAllStandardError().data()
        # print repr(error)
        if not error == "\n":
            logger.info("error : " + "\'" + str(error) + "\'")
        logger.info("output : " + result.data() + "fin output")
        return result
    else:
        code_d_erreur = process.error()
        dic_err = { 0:"QProcess::FailedToStart", 1:"QProcess::Crashed", 2:"QProcess::TimedOut", 3:"QProcess::WriteError", 4:"QProcess::ReadError", 5:"QProcess::UnknownError" }
        logger.info("Code erreur : " + str(code_d_erreur))
        logger.info(dic_err[code_d_erreur])
    return None


def run_otb_app(app_name, arguments):
    dirname = os.path.dirname(os.path.abspath(__file__))
    launcher = os.path.join(dirname, "win32", "bin", "otbApplicationLauncherCommandLine.exe") + " " + app_name + " " + os.path.join(dirname, "win32", "plugin")
    command = launcher + " " + arguments
    output = run_process(command)
    return output


def set_OTB_PATH():
    dirname = os.path.dirname(os.path.abspath(__file__))
    if not os.name == "posix":
        if "PATH" in os.environ.keys():
            os.environ["PATH"] = os.path.join(dirname, "win32", "bin") + ";" + os.environ["PATH"]
        else:
            os.environ["PATH"] = os.path.join(dirname, "win32", "bin")
        if "ITK_AUTOLOAD_PATH" in os.environ.keys():
            os.environ["ITK_AUTOLOAD_PATH"] = os.path.join(dirname, "win32", "plugin") + ";" + os.environ["ITK_AUTOLOAD_PATH"]
        else:
            os.environ["ITK_AUTOLOAD_PATH"] = os.path.join(dirname, "win32", "plugin")
    # print os.environ["PATH"]
    # print os.environ["ITK_AUTOLOAD_PATH"]

