#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Script's doctring goes here.
"""

from PyQt4 import QtCore, QtGui

import qgis.core
import qgis.gui

import base

class Tool(object):

    operates_on = []
    canvas_elements = dict()

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.icon_tool_bar = icon_tool_bar
        self.controls_tool_bar = controls_tool_bar
        QtCore.QObject.connect(self.iface, QtCore.SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.toggle)
        QtCore.QObject.connect(self.canvas, QtCore.SIGNAL("selectionChanged(QgsMapLayer *)"), self.toggle)

    def _selection_correct(self, layer):
        result = False
        if layer is not None and layer.isEditable():
            for operation in self.operates_on:
                if layer.wkbType() == operation.get('type'):
                    if layer.selectedFeatureCount() == operation.get('features'):
                        result = True
                    elif layer.selectedFeatureCount() > 0 and \
                            operation.get('features') == 'multiple':
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
            self.toggle_action()
            self.toggle_editing()

    def toggle_editing(self):
        layer = self.canvas.currentLayer()
        if layer is not None:
            if layer.isEditable() and self._selection_correct(layer):
                self.action.setEnabled(True)
                QtCore.QObject.connect(layer, QtCore.SIGNAL('editingStopped()'), 
                                self.toggle_editing)
                QtCore.QObject.disconnect(layer, QtCore.SIGNAL('editingStarted()'), 
                                   self.toggle_editing)
            else:
                self.action.setEnabled(False)
                QtCore.QObject.connect(layer, QtCore.SIGNAL('editingStarted()'), 
                                self.toggle_editing)
                QtCore.QObject.disconnect(layer, QtCore.SIGNAL('editingStopped()'), 
                                   self.toggle_editing)
                self.action.setChecked(False)

    def toggle_action(self):
        layer = self.canvas.currentLayer()
        action = False
        if layer.type() == qgis.core.QgsMapLayer.VectorLayer:
            for t in self.operates_on:
                if layer.wkbType() == t.get('type'):
                    action = True
        if action:
            self.action.setVisible(True)
        else:
            self.action.setVisible(False)
        return action

    def toggle_controls(self, active):
        if active:
            self._create_controls()
        else:
            self.controls_tool_bar.clear()

    def _create_controls(self):
        # provide your own _create_controls() method for each tool
        raise NotImplementedError

    def try_to_snap(self, point, snapping_type=qgis.core.QgsSnapper.SnapToVertex):
        '''
        Try to snap the input point to a layer displayed in the map canvas.

        Inputs:

            point - A QPoint instance

            snapping_type - A QgsSnapper.SnappingType type

        Snapping is done on the current layer first and then, in case of
        failure, in the other layers.
        '''

        snapped_point = None
        snapper = qgis.gui.QgsMapCanvasSnapper(self.canvas)
        retval, result = snapper.snapToCurrentLayer(point, snapping_type)
        if len(result) == 0:
            retval, result = snapper.snapToBackgroundLayers(point)
        if len(result) != 0:
            snapped_point = base.Point(result[0].snappedVertex)
        return snapped_point


class ToolWithReference(Tool):

    reference = base.Point(0, 0)

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        super(ToolWithReference, self).__init__(iface, icon_tool_bar, 
                                                controls_tool_bar)
        
        self.canvas_elements = {
            'reference_marker' : base.VertexMarker(self.canvas, base.Point()),
        }
        self.canvas_elements['reference_marker'].hide()
        self.reference_map_tool = qgis.gui.QgsMapToolEmitPoint(self.canvas)
        self.ref_action = QtGui.QAction(
            QtGui.QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'select a point in the map window to be used as reference point', 
            self.iface.mainWindow()
        )
        self.ref_action.setCheckable(True)
        QtCore.QObject.connect(self.ref_action, QtCore.SIGNAL('toggled(bool)'), 
                        self.toggle_reference_selection)
        QtCore.QObject.connect(self.reference_map_tool, QtCore.SIGNAL('canvasClicked(const '\
                        'QgsPoint &, Qt::MouseButton)'), 
                        self.get_reference_point)

    def _create_controls(self):
        self.ref_lab = QtGui.QLabel(None)
        self.ref_lab.setText('Reference:')
        self.ref_x_lab = QtGui.QLabel(None)
        self.ref_x_lab.setText('X')
        self.ref_x_le = QtGui.QLineEdit(None)
        self.ref_y_lab = QtGui.QLabel(None)
        self.ref_y_lab.setText('Y')
        self.ref_y_le = QtGui.QLineEdit(None)
        QtCore.QObject.connect(
            self.ref_x_le, 
            QtCore.SIGNAL('textChanged(const QString &)'), 
            self.change_reference_parameter_x
        )
        QtCore.QObject.connect(
            self.ref_y_le, 
            QtCore.SIGNAL('textChanged(const QString &)'), 
            self.change_reference_parameter_y
        )
        self.tool_bar.addWidget(self.ref_lab)
        self.tool_bar.addWidget(self.ref_x_lab)
        self.tool_bar.addWidget(self.ref_x_le)
        self.tool_bar.addWidget(self.ref_y_lab)
        self.tool_bar.addWidget(self.ref_y_le)
        self.tool_bar.addAction(self.ref_action)
        self.tool_bar.addSeparator()

    def _update_controls(self):
        self.ref_x_le.setText(str(self.reference.x()))
        self.ref_y_le.setText(str(self.reference.y()))

    def change_reference_parameter_x(self, the_text):
        self.reference.setX(QtCore.QVariant(the_text).toFloat()[0])
        self.update_reference_marker_position()

    def change_reference_parameter_y(self, the_text):
        self.reference.setY(QtCore.QVariant(the_text).toFloat()[0])
        self.update_reference_marker_position()

    def toggle_reference_selection(self, active):
        if active:
            self.canvas.setMapTool(self.reference_map_tool)
        else:
            self.canvas.unsetMapTool(self.reference_map_tool)

    def _get_point(self, qgs_point, mouseButton, map_tool):
        canvas_point = map_tool.toCanvasCoordinates(qgs_point)
        snapped_point = self.try_to_snap(canvas_point)
        if snapped_point is None:
            p = base.Point(qgs_point)
        else:
            p = snapped_point
        return p

    def get_reference_point(self, qgs_point, mouse_button):
        ref_point = self._get_point(qgs_point, mouse_button, 
                                    self.reference_map_tool)
        self.reference = ref_point
        self.canvas_elements['reference_marker'].x = ref_point.x()
        self.canvas_elements['reference_marker'].y = ref_point.y()
        self._update_controls()
        self.ref_action.toggle()

    def update_reference_marker_position(self):
        self.canvas_elements['reference_marker'].x = self.reference.x()
        self.canvas_elements['reference_marker'].y = self.reference.y()
