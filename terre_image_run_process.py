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
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_RunProcess')
logger.setLevel(logging.DEBUG)


def run_process(fused_command, read_output = False):
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
