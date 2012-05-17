#!/usr/bin/env python
#-*- coding: utf-8 -*-

from math import pi, atan, atan2, cos, sin, radians, degrees, sqrt

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qgis.core

from base import Point, Line, VertexMarker

# TODO
# - replace the slope calculation using scipy polyfit with a linear regression

class GeomTools(object):

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        name = 'geomtools'
        self.tool_bar = self.iface.addToolBar(name)
        self.tool_bar.setObjectName(name)
        self.test_tool = TestTool(self.iface, self.tool_bar)
        self.rotate_tool = RotateTool(self.iface, self.tool_bar)
        # add more tools here


    def unload(self):
        del self.tool_bar


class Tool(object):

    OPERATES_ON = []

    def __init__(self, iface, tool_bar):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.tool_bar = tool_bar

    def _selection_correct(self, layer):
        result = False
        if layer is not None:
            for operation in self.OPERATES_ON:
                if layer.wkbType() == operation.get('type') and \
                        layer.selectedFeatureCount() == operation.get('features'):
                    result = True
        return result

    def toggle(self, layer):
        print('layer: %s' % layer)
        if self._selection_correct(layer):
            self.action.setEnabled(True)
        else:
            self.action.setEnabled(False)


class TestTool(Tool):

    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 1}]

    def __init__(self, iface, tool_bar):
        super(TestTool, self).__init__(iface, tool_bar)
        self.action = QAction(QIcon(':plugins/cadtools/icons/pointandline.png'), 'test', self.iface.mainWindow())
        tool_bar.addAction(self.action)
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.toggle)
        QObject.connect(self.canvas, SIGNAL("selectionChanged(QgsMapLayer *)"), self.toggle)

    def run(self):
        current_layer = self.iface.mapCanvas().currentLayer()
        selected_features = current_layer.selectedFeatures()
        feat = selected_features[0]
        p = Point.from_feature(feat)
        v = VertexMarker(self.canvas, p)
        print(v)


class RotateTool(Tool):
    
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBLineString, 'features' : 1}]

    def __init__(self, iface, tool_bar):
        super(RotateTool, self).__init__(iface, tool_bar)
        self.action = QAction(QIcon(':plugins/cadtools/icons/pointandline.png'), 'rotate', self.iface.mainWindow())
        tool_bar.addAction(self.action)
        QObject.connect(self.action, SIGNAL("triggered()"), self.rotate)
        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.toggle)

    def rotate(self):
        current_layer = self.iface.mapCanvas().currentLayer()
        print('current_layer: %s' % current_layer)

