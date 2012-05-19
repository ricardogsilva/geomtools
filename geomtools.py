#!/usr/bin/env python
#-*- coding: utf-8 -*-

from math import pi, atan, atan2, cos, sin, radians, degrees, sqrt

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qgis.core
import qgis.gui

from createnumericaldialog import CreateNumericalDialog

from base import Point, Line, VertexMarker

# TODO
# - replace the slope calculation using scipy polyfit with a linear regression

class GeomTools(object):

    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

    def initGui(self):
        name = 'geomtools'
        self.tool_bar = self.iface.addToolBar(name)
        self.tool_bar.setObjectName(name)
        # add more tools here
        self.create_numerical = CreateNumerical(self.iface, self.tool_bar)

    def unload(self):
        del self.tool_bar


class Tool(object):

    OPERATES_ON = []

    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.map_layer_registry = qgis.core.QgsMapLayerRegistry.instance()
        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.toggle)
        QObject.connect(self.canvas, SIGNAL("selectionChanged(QgsMapLayer *)"), self.toggle)
        #QObject.connect(self.canvas, SIGNAL("editingStarted()"), self.toggle)

    def _selection_correct(self, layer):
        result = False
        if layer is not None and layer.isEditable():
            for operation in self.OPERATES_ON:
                if layer.wkbType() == operation.get('type') and \
                        layer.selectedFeatureCount() == operation.get('features'):
                    result = True
        return result

    def toggle(self, layer=None):
        if layer is not None:
            # current layer changed or selection changed
            if layer.isEditable():
                QObject.connect(layer, SIGNAL('editingStopped()'), self.toggle)
                QObject.disconnect(layer, SIGNAL('editingStarted()'), self.toggle)
                if self._selection_correct(layer):
                    self.action.setEnabled(True)
            else:
                QObject.connect(layer, SIGNAL('editingStarted()'), self.toggle)
                QObject.disconnect(layer, SIGNAL('editingStopped()'), self.toggle)
                self.action.setEnabled(False)
        else:
            # editing started or editing stopped
            layer = self.canvas.currentLayer()
            if layer is not None:
                if layer.isEditable():
                    if self._selection_correct(layer):
                        self.action.setEnabled(True)
                else:
                    self.action.setEnabled(False)


class CreateNumerical(Tool):
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 0}]

    def __init__(self, iface, tool_bar):
        super(CreateNumerical, self).__init__(iface)
        self.action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'create point with numerical input', 
            self.iface.mainWindow()
        )
        tool_bar.addAction(self.action)
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        self.toggle()

    def run(self):
        self.dlg = CreateNumericalDialog()
        QObject.connect(self.dlg, SIGNAL('point_created'), self.create_vertex)
        self.dlg.show()

    def create_vertex(self, point):
        #name = 'numerical create'
        #tb = self.iface.addToolBar(name)
        #tb.setObjectName(name)
        #le = QLineEdit()
        #tb.addWidget(le)
        v = VertexMarker(self.canvas, point)



class TestTool(Tool):

    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 1}]

    def __init__(self, iface, tool_bar):
        super(TestTool, self).__init__(iface, tool_bar)
        self.rotation_marker = VertexMarker(self.canvas)
        self.rotation_marker.hide()
        self.action = QAction(QIcon(':plugins/cadtools/icons/pointandline.png'), 'test', self.iface.mainWindow())
        tool_bar.addAction(self.action)
        self.map_tool = qgis.gui.QgsMapToolEmitPoint(self.canvas)
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        #QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.toggle)
        #QObject.connect(self.canvas, SIGNAL("selectionChanged(QgsMapLayer *)"), self.toggle)
        QObject.connect(self.canvas, SIGNAL('xyCoordinates(const QgsPoint &)'), self.mouse_position)

    def run(self):
        QObject.connect(self.map_tool, SIGNAL("canvasClicked(const ' \
                        'QgsPoint &, Qt::MouseButton)"), self.canvas_clicked)
        current_layer = self.iface.mapCanvas().currentLayer()
        selected_features = current_layer.selectedFeatures()
        feat = selected_features[0]
        p = Point.from_feature(feat)
        self.rotation_marker.x = p.x()
        self.rotation_marker.y = p.y()
        self.rotation_marker.show()
        self.canvas.setMapTool(self.map_tool)

    def canvas_clicked(self, qgs_point):
        print('canvas x: %s' % qgs_point.x())
        print('canvas y: %s' % qgs_point.y())
        self.rotation_marker.x = qgs_point.x()
        self.rotation_marker.y = qgs_point.y()

    def mouse_position(self, qgs_point):
        print('mouse x: %s y: %s' % (qgs_point.x(), qgs_point.y()))



class RotateTool(Tool):
    
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBLineString, 'features' : 1}]

    def __init__(self, iface, tool_bar):
        super(RotateTool, self).__init__(iface, tool_bar)
        self.action = QAction(QIcon(':plugins/cadtools/icons/pointandline.png'), 'rotate', self.iface.mainWindow())
        tool_bar.addAction(self.action)
        #QObject.connect(self.action, SIGNAL("triggered()"), self.rotate)
        #QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.toggle)

    def rotate(self):
        current_layer = self.iface.mapCanvas().currentLayer()
        print('current_layer: %s' % current_layer)

