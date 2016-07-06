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

import os
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
                'maxBytes': 4096,
                'backupCount': 3
            }
        },
        'loggers': {
            'default': {
                'level': 'INFO',
                'handlers': ['console', 'file']
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
    # print "dictParameters", dictParameters
    logger.debug("--------------------------------")
    logger.debug( "\t {}".format(functionName))
    for argument, value in dictParameters.iteritems():
        logger.debug( "\t\t {}: {}".format(argument,value))
    logger.debug( "--------------------------------")