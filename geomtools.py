#!/usr/bin/env python
#-*- coding: utf-8 -*-

from math import pi, atan, atan2, cos, sin, radians, degrees, sqrt

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qgis.core
import qgis.gui

from createnumericaldialog import CreateNumericalDialog

import base

# TODO
# - replace the slope calculation using scipy polyfit with a linear regression

class GeomTools(object):

    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

    def initGui(self):
        icon_tool_bar_name = 'geomtools'
        controls_tool_bar_name = icon_tool_bar_name + ' controls'
        self.icon_tool_bar = self.iface.addToolBar(icon_tool_bar_name)
        self.icon_tool_bar.setObjectName(icon_tool_bar_name)
        self.controls_tool_bar = self.iface.addToolBar(controls_tool_bar_name)
        self.controls_tool_bar.setObjectName(controls_tool_bar_name)
        # add more tools here
        self.create_numerical = CreateNumerical(self.iface, 
                                                self.icon_tool_bar, 
                                                self.controls_tool_bar)

    def unload(self):
        del self.icon_tool_bar


class Tool(object):

    OPERATES_ON = []

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.icon_tool_bar = icon_tool_bar
        self.controls_tool_bar = controls_tool_bar
        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.toggle)
        QObject.connect(self.canvas, SIGNAL("selectionChanged(QgsMapLayer *)"), self.toggle)

    def _selection_correct(self, layer):
        result = False
        if layer is not None and layer.isEditable():
            for operation in self.OPERATES_ON:
                if layer.wkbType() == operation.get('type') and \
                        layer.selectedFeatureCount() == operation.get('features'):
                    result = True
        return result

    def toggle(self, layer=None):
        if layer is None:
            # we could be coming from any of the signals
            layer = self.canvas.currentLayer()
            if layer is None:
                self.action.setEnabled(False)
            else:
                # we came from one of editingStarted() or editingStopped()
                self.toggle_editing()
        else:
            # we are coming from currentLayerChanged or selectionChanged
            self.toggle_editing()

    def toggle_editing(self):
        layer = self.canvas.currentLayer()
        if layer.isEditable() and self._selection_correct(layer):
            self.action.setEnabled(True)
            QObject.connect(layer, SIGNAL('editingStopped()'), 
                            self.toggle_editing)
            QObject.disconnect(layer, SIGNAL('editingStarted()'), 
                               self.toggle_editing)
        else:
            self.action.setEnabled(False)
            QObject.connect(layer, SIGNAL('editingStarted()'), 
                            self.toggle_editing)
            QObject.disconnect(layer, SIGNAL('editingStopped()'), 
                               self.toggle_editing)
            self.action.setChecked(False)

    def toggle_controls(self, active):
        if active:
            self._create_controls()
        else:
            self.controls_tool_bar.clear()

    def _create_controls(self):
        # provide your own _create_controls() method for each tool
        raise NotImplementedError


class CreateNumerical(Tool):
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 0}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        super(CreateNumerical, self).__init__(iface, icon_tool_bar, 
                                              controls_tool_bar)
        self.parameters = {
            'reference' : base.Point(0, 0),
            'offset_x' : 0.0,
            'offset_y' : 0.0,
            'distance' : 0.0,
            'angle' : 0.0,
        }
        self.reference_marker = base.VertexMarker(self.canvas, base.Point())
        self.reference_marker.hide()
        self.target_marker = base.VertexMarker(self.canvas, base.Point())
        self.target_marker.hide()
        self.action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'create point with numerical input', 
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        icon_tool_bar.addAction(self.action)
        self.ref_action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'select a point in the map window', 
            self.iface.mainWindow()
        )
        self.ref_action.setCheckable(True)
        self.tool_bar = controls_tool_bar
        self.map_tool = qgis.gui.QgsMapToolEmitPoint(self.canvas)
        QObject.connect(self.action, SIGNAL("toggled(bool)"), self.run)
        QObject.connect(self.map_tool, SIGNAL('canvasClicked(const '\
                        'QgsPoint &, Qt::MouseButton)'), self.get_point)
        QObject.connect(self.ref_action, SIGNAL('toggled(bool)'), 
                        self.toggle_reference_selection)
        self.toggle()

    def run(self, active):
        #self.dlg = CreateNumericalDialog()
        #QObject.connect(self.dlg, SIGNAL('point_selected'), self.create_vertex)
        #self.dlg.show()
        self.toggle_controls(active)
        if active:
            self.reference_marker.show()
        else:
            self.reference_marker.hide()

    def _create_controls(self):
        self.ref_lab = QLabel(None)
        self.ref_lab.setText('Reference:')
        self.ref_x_lab = QLabel(None)
        self.ref_x_lab.setText('X')
        self.ref_x_le = QLineEdit(None)
        self.ref_y_lab = QLabel(None)
        self.ref_y_lab.setText('Y')
        self.ref_y_le = QLineEdit(None)

        self.offset_radio = QRadioButton('Offset', None)
        self.angle_dist_radio = QRadioButton('Angle && distance', None)
        QObject.connect(self.offset_radio, SIGNAL('toggled(bool)'), self.toggle_mode_controls)
        self.offset_radio.setChecked(True)

        self.coor_x_lab = QLabel(None)
        self.coor_x_lab.setText('X')
        self.coor_x_le = QLineEdit(None)
        self.coor_y_lab = QLabel(None)
        self.coor_y_lab.setText('Y')
        self.coor_y_le = QLineEdit(None)

        self.coor_distance_lab = QLabel(None)
        self.coor_distance_lab.setText('Distance')
        self.coor_angle_lab = QLabel(None)
        self.coor_angle_lab.setText('Angle')

        self.create_point_btn = QPushButton(None)
        self.create_point_btn.setText('Create')
        QObject.connect(
            self.ref_x_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_reference_parameter_x
        )
        QObject.connect(
            self.ref_y_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_reference_parameter_y
        )
        QObject.connect(self.create_point_btn, SIGNAL('released()'), 
                        self.create_point)

        self.tool_bar.addWidget(self.ref_lab)
        self.tool_bar.addWidget(self.ref_x_lab)
        self.tool_bar.addWidget(self.ref_x_le)
        self.tool_bar.addWidget(self.ref_y_lab)
        self.tool_bar.addWidget(self.ref_y_le)
        self.tool_bar.addAction(self.ref_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.offset_radio)
        self.tool_bar.addWidget(self.angle_dist_radio)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.coor_x_lab)
        self.tool_bar.addWidget(self.coor_x_le)
        self.tool_bar.addWidget(self.coor_y_lab)
        self.tool_bar.addWidget(self.coor_y_le)
        self.tool_bar.addWidget(self.create_point_btn)
        self._update_controls()

    def change_reference_parameter_x(self, the_text):
        self.parameters.get('reference').setX(QVariant(the_text).toFloat()[0])
        self.update_reference_marker_position()

    def change_reference_parameter_y(self, the_text):
        self.parameters.get('reference').setY(QVariant(the_text).toFloat()[0])
        self.update_reference_marker_position()

    def toggle_reference_selection(self, active):
        if active:
            self.canvas.setMapTool(self.map_tool)
        else:
            self.canvas.unsetMapTool(self.map_tool)

    def get_point(self, qgs_point, mouseButton):
        p = base.Point(qgs_point)
        self.parameters['reference'] = p
        self._update_controls()
        self.reference_marker.x = p.x()
        self.reference_marker.y = p.y()
        self.ref_action.toggle()

    def _update_controls(self):
        self.ref_x_le.setText(str(self.parameters.get('reference').x()))
        self.ref_y_le.setText(str(self.parameters.get('reference').y()))
        self.coor_x_le.setText(str(self.parameters.get('offset_x')))
        self.coor_y_le.setText(str(self.parameters.get('offset_y')))

    def update_reference_marker_position(self):
        self.reference_marker.x = self.parameters.get('reference').x()
        self.reference_marker.y = self.parameters.get('reference').y()

    #def update_target_marker_position(self):
    #    self.target_marker.x = self.parameters.get('reference').x()
    #    self.target_marker.y = self.parameters.get('reference').y()

    def create_point(self):
        v = base.VertexMarker(self.canvas, point)
        v.setColor = QColor(0, 0, 255)



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
        p = base.Point.from_feature(feat)
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

