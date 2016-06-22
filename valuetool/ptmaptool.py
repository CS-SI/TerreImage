# -*- coding: utf-8 -*-
#-----------------------------------------------------------
#
# Profile
# Copyright (C) 2008  Borys Jurgiel
# Copyright (C) 2012  Patrice Verchere
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, print to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QCursor
from qgis.gui import QgsMapTool

class ProfiletoolMapTool_ValueTool(QgsMapTool):

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event):
        # print "canvasReleaseEvent_v"
        # print "event", event
        self.emit(SIGNAL("canvas_clicked_v"), {'x': event.pos().x(), 'y': event.pos().y()})
        # print "canvasReleaseEvent_v"

    def activate(self):
        QgsMapTool.activate(self)
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        # print "desactivate 123456789"
        # self.emit( SIGNAL("deactivate") )
        # self.canvas.setCursor( QCursor(Qt.ArrowCursor))
        QgsMapTool.deactivate(self)

    def setCursor(self, cursor):
        self.cursor = QCursor(cursor)
