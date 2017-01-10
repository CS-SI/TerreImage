# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin                : 2016-06-29
        copyright            : (C) 2016 by CNES
        email                : alexia.mondot@c-s.fr
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

import sys, os
import logging
import logging.config
import terre_image_configuration

def configure_logger(name="", log_path=""):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'verbose': {'format' : '%(asctime)s - %(filename)s - line %(lineno)d - %(module)s:%(funcName)s - %(levelname)s - %(message)s'},
            'console': {'format': '%(asctime)s - %(levelname)s - %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'console',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': terre_image_configuration.log_file,
                'maxBytes': 1048576,
                'backupCount': 3
            },
            'file2': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'console',
                'filename': terre_image_configuration.log_file,
                'maxBytes': 1048576,
                'backupCount': 3
            }
        },
        'loggers': {
            'default': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            },
            'debug': {
                'level': 'DEBUG',
                'handlers': ['file2']
            }
        },
        'disable_existing_loggers': False
    })
    if name:
        return logging.getLogger(name)
    else:
        return logging.getLogger('default')


def display_parameters(dictParameters, functionName, logger):
    """
    Display parameters of the functionName.
    Used as follows :
        display_parameters(locals(), "color_mapping_cli_ref_image")
    """
    # logger.debug(""dictParameters {}".format(dictParameters))
    logger.debug("--------------------------------")
    logger.debug( u"\t {}".format(functionName))
    for argument, value in dictParameters.iteritems():
        logger.debug( u"\t\t {}: {}".format(argument,value))
    logger.debug( "--------------------------------")


logger = configure_logger("debug")
def decorate_debug(func):
    """
    Decorator to trace entering and exiting a function
    Args:
        func:

    Returns:

    """
    def wrapper(*arg,**kwargs):
        sys.stdout.flush()
        try :
            frame = sys._getframe(1)
        except ValueError:
            frame = sys._getframe(0)

        logger.debug("Launching {} from {}, {}:{}".format(func.__name__, frame.f_code.co_name,
                                                         os.path.basename(frame.f_code.co_filename), frame.f_lineno))
        response=func(*arg,**kwargs)
        logger.debug("Exiting {} from {}, {}:{}".format(func.__name__, frame.f_code.co_name,
                                                         os.path.basename(frame.f_code.co_filename), frame.f_lineno))
        return response
    return wrapper

def trace(frame, event, arg):
    """
    Trace all functions called by python.
    To be used like this :
    from terre_image_logging import trace
    import sys

    #add the break point
    sys.settrace(trace)
    Args:
        frame:
        event:
        arg:

    Returns:

    """
    if event == "call":
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        # Here I'm printing the file and line number,
        # but you can examine the frame, locals, etc too.
        logger.debug("%s @ %s" % (filename, lineno))