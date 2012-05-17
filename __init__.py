# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geomtools
                                 A QGIS plugin
 An extra set of tools for editing and digitizing geometries
                             -------------------
        begin                : 2012-05-13
        copyright            : (C) 2012 by Ricardo Garcia Silva
        email                : ricardo.garcia.silva at gmail dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def name():
    return "geomtools"
def description():
    return "An extra set of tools for editing and digitizing geometries"
def version():
    return "Version 0.1"
def icon():
    return "mActionNewVectorLayer.png"
def qgisMinimumVersion():
    return "1.7"
def classFactory(iface):
    from geomtools import GeomTools
    return GeomTools(iface)
