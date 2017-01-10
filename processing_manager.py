# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2014-05-06
        copyright            : (C) 2014 by CNES
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
# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()


class ProcessingManager(object):
    instance = None

    def __new__(cls, *args, **kwargs):  # __new__ always a classmethod
        if not cls.instance:
            cls.instance = super(ProcessingManager, cls).__new__(cls, *args, **kwargs)
            cls.instance.__private_init__()
        return cls.instance

    def __private_init__(self):
        """
        Init to have constant values
        """
        self.working_layer = None
        self.processings = []
        self.displays = []

    def get_processings_name(self):
        return [x.processing_name for x in self.processings] + [x.processing_name for x in self.displays]

    def get_layers(self):
        return [self.working_layer] + [x.output_working_layer for x in self.processings] + [x.output_working_layer for x in self.displays]

    def get_working_layers(self):
        return [self.working_layer] + [x.output_working_layer for x in self.processings if not x.processing_name == 'KMEANS']  # if isinstance(x, TerreImageProcessing)]

    def get_layers_for_kmz(self):
        return [self.working_layer.get_source()] + [x.output_working_layer.get_source() for x in self.processings]

    def get_qgis_working_layers(self):
        # return [self.working_layer.get_qgis_layer()] +
        return [self.working_layer.get_qgis_layer()] + [x.output_working_layer.get_qgis_layer() for x in self.processings if not x.processing_name == 'KMEANS']  # if isinstance(x, TerreImageProcessing)]

    def get_processings(self):
        return self.processings

    def add_processing(self, processing):
        self.processings.append(processing)

    def get_displays(self):
        return self.displays

    def add_display(self, processing):
        self.displays.append(processing)

    def remove_processing(self, process):
        if process in self.processings:
            self.processings.remove(process)
            process.end()

    def remove_process_from_layer_id(self, layer_id):
        process = [ p for p in self.processings if p.output_working_layer.qgis_layer.id() == layer_id ]
        logger.debug("process {}".format(process))
        if process:
            try:
                process[0].mirror.close()
            except RuntimeError:
                pass
            self.remove_processing(process[0])

    def remove_display(self, process):
        if process in self.displays :
            self.displays.remove(process)
            process.end()

    def remove_displays_from_layer_id(self, layer_id):
        # for p in self.displays:
        #    logger.debug(p.output_working_layer.qgis_layer.id())
        process = [ p for p in self.displays if p.output_working_layer.qgis_layer.id() == layer_id ]
        logger.debug("process {}".format(process))
        if process :
            # logger.debug("process trouvé")
            process[0].mirror.close()
            self.remove_display(process[0])

    def remove_all(self):
        pass

    def has_spectral_angle(self):
        return "Angle Spectral" in [x.processing_name for x in self.processings]

    def has_seuillage(self):
        return "Seuillage" in [x.processing_name for x in self.processings]

    def processing_from_name(self, name):
        return [x for x in self.processings if x.processing_name == name] + [x for x in self.displays if x.processing_name == name]

#     def get_process_to_display(self):
#         for x in self.processings:
#             logger.debug( x )
#             logger.debug( x.output_working_layer.qgis_layer )
#
#         temp = [x.output_working_layer.qgis_layer for x in self.processings if isinstance(x, TerreImageProcessing) and x.output_working_layer.qgis_layer is not None]
#         logger.debug( temp )
#         return temp

    def __str__(self):
        sortie = "processings : ["
        for pro in self.processings:
            sortie += str(pro) + "\n"
        for pro in self.displays:
            sortie += str(pro) + "\n"
        sortie += "]\n"
        sortie += "layers" + "\n"
        for l in self.get_layers():
            sortie += str(l) + "\n"
        sortie += "working_layers" + "\n"
        for l in self.get_working_layers():
            sortie += str(l) + "\n"

        return sortie

#
#
#     def view_closed(self, name_of_the_closed_view):
#         logger.debug( str(name_of_the_closed_view) + " has been closed")
#         try:
#             process = self.name_to_processing[name_of_the_closed_view]
#             QgsMapLayerRegistry.instance().removeMapLayer( process.output_working_layer.qgis_layer.id())
#             self.remove_processing(process)
#         except KeyError:
#             pass
#
#
#
#
#     def removing_layer(self, layer_id):
#         process = [ p for p in self.processings if p.output_working_layer.qgis_layer.id() == layer_id ]
#         logger.debug( "process" + str( process))
#         if process :
#             process[0].mirror.close()
#             self.remove_processing(process[0])
