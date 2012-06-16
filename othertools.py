#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Script's doctring goes here.
"""

from PyQt4 import QtCore, QtGui

import qgis.core
import qgis.gui

import base
import generictools

class MoveReference(generictools.ToolWithReference):
    operates_on = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 'multiple'}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        super(MoveReference, self).__init__(iface, icon_tool_bar, 
                                            controls_tool_bar)
        self.parameters = {
            'target' : base.Point(0, 0),
            'new_points' : [],
            'markers': [],
            'copy' : False,
            'rotate' : 0,
        }
        self.target_marker = base.VertexMarker(self.canvas, base.Point())
        self.target_marker.setColor(QtGui.QColor(0, 0, 255))
        self.target_marker.setIconType(qgis.gui.QgsVertexMarker.ICON_BOX)
        self.target_marker.hide()
        self.action = QtGui.QAction(
            QtGui.QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'Move points according to a reference', 
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        icon_tool_bar.addAction(self.action)
        self.target_action = QtGui.QAction(
            QtGui.QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'select a point in the map window for being the target', 
            self.iface.mainWindow()
        )
        self.target_action.setCheckable(True)
        self.tool_bar = controls_tool_bar
        self.target_map_tool = qgis.gui.QgsMapToolEmitPoint(self.canvas)
        QtCore.QObject.connect(self.action, QtCore.SIGNAL("toggled(bool)"), self.run)
        QtCore.QObject.connect(self.target_action, QtCore.SIGNAL('toggled(bool)'), 
                        self.toggle_target_selection)
        QtCore.QObject.connect(self.target_map_tool, QtCore.SIGNAL('canvasClicked(const '\
                        'QgsPoint &, Qt::MouseButton)'), self.get_target_point)
        self.toggle()

    def run(self, active):
        self.toggle_controls(active)
        self.toggle_markers(active)
        if active:
            self.reference_marker.show()
            self.target_marker.show()
        else:
            self.reference_marker.hide()
            self.target_marker.hide()

    def _create_controls(self):
        super(MoveReference, self)._create_controls()
        self.target_lab = QtGui.QLabel(None)
        self.target_lab.setText('Target:')
        self.target_x_lab = QtGui.QLabel(None)
        self.target_x_lab.setText('X')
        self.target_x_le = QtGui.QLineEdit(None)
        self.target_y_lab = QtGui.QLabel(None)
        self.target_y_lab.setText('Y')
        self.target_y_le = QtGui.QLineEdit(None)

        self.rotate_lab = QtGui.QLabel('Rotate', None)
        self.rotate_sb = QtGui.QDoubleSpinBox(None)
        self.rotate_sb.setMinimum(0)
        self.rotate_sb.setMaximum(360)
        self.rotate_sb.setDecimals(0)
        self.rotate_sb.setSuffix(u'\u00b0')

        self.copy_cb = QtGui.QCheckBox('copy', None)

        self.move_btn = QtGui.QPushButton(None)
        self.move_btn.setText('Move')

        QtCore.QObject.connect(
            self.target_x_le, 
            QtCore.SIGNAL('textChanged(const QString &)'), 
            self.change_target_parameter_x
        )
        QtCore.QObject.connect(
            self.target_y_le, 
            QtCore.SIGNAL('textChanged(const QString &)'), 
            self.change_target_parameter_y
        )
        QtCore.QObject.connect(self.move_btn, QtCore.SIGNAL('released()'), 
                        self.move)
        QtCore.QObject.connect(self.copy_cb, QtCore.SIGNAL('stateChanged(int)'), 
                        self.toggle_copy)
        QtCore.QObject.connect(self.rotate_sb, QtCore.SIGNAL('valueChanged(double)'), 
                        self.change_target_rotation)
        self.copy_cb.setChecked(False)

        self.tool_bar.addWidget(self.target_lab)
        self.tool_bar.addWidget(self.target_x_lab)
        self.tool_bar.addWidget(self.target_x_le)
        self.tool_bar.addWidget(self.target_y_lab)
        self.tool_bar.addWidget(self.target_y_le)
        self.tool_bar.addAction(self.target_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.rotate_lab)
        self.tool_bar.addWidget(self.rotate_sb)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.copy_cb)
        self.tool_bar.addWidget(self.move_btn)
        self._update_controls()

    def _update_controls(self):
        super(MoveReference, self)._update_controls()
        self.target_x_le.setText(str(self.parameters['target'].x()))
        self.target_y_le.setText(str(self.parameters['target'].y()))
        self.rotate_sb.setValue(self.parameters.get('rotate'))

    def toggle_markers(self, active):
        if active:
            for m in self.parameters['markers']:
                m.show()
        else:
            for m in self.parameters['markers']:
                m.hide()

    def toggle_copy(self):
        if self.copy_cb.isChecked():
            self.parameters['copy'] = True
            self.move_btn.setText('Copy')
        else:
            self.parameters['copy'] = False
            self.move_btn.setText('Move')

    def move(self):
        layer = self.canvas.currentLayer()
        feats = layer.selectedFeatures()
        self.calculate_points(feats)
        if self.parameters.get('copy'):
            new_features = []
            for p in self.parameters.get('new_points'):
                geom = qgis.core.QgsGeometry.fromPoint(p)
                feat = qgis.core.QgsFeature()
                feat.setGeometry(geom)
                new_features.append(feat)
            layer.beginEditCommand('Create points')
            layer.addFeatures(new_features, False)
            layer.endEditCommand()
        else:
            layer.beginEditCommand('Move points')
            for index, f in enumerate(feats):
                point = self.parameters.get('new_points')[index]
                geom = qgis.core.QgsGeometry.fromPoint(point)
                layer.changeGeometry(f.id(), geom)
            layer.endEditCommand()
        self.canvas.refresh()

    def calculate_points(self, feature_list):
        self.parameters['new_points'] = []
        offset_x = self.parameters['target'].x() - self.reference.x()
        offset_y = self.parameters['target'].y() - self.reference.y()
        for f in feature_list:
            point = base.Point.from_feature(f)
            point.translate_offsets(offset_x, offset_y)
            point.rotate(self.parameters.get('rotate'), self.parameters['target'])
            self.parameters['new_points'].append(point)

    def draw_markers(self):
        self._delete_markers()
        for p in self.parameters['new_points']:
            v = base.VertexMarker(self.canvas, p)
            v.setColor(QtGui.QColor(0, 0, 255))
            self.parameters['markers'].append(v)

    def _delete_markers(self):
        for m in self.parameters['markers']:
            self.canvas.scene().removeItem(m)
        self.parameters['markers'] = []

    def toggle_target_selection(self, active):
        if active:
            self.canvas.setMapTool(self.target_map_tool)
        else:
            self.canvas.unsetMapTool(self.target_map_tool)

    def change_target_parameter_x(self, the_text):
        self.parameters.get('target').setX(QtCore.QVariant(the_text).toFloat()[0])
        self.update_target_marker_position()

    def change_target_parameter_y(self, the_text):
        self.parameters.get('target').setY(QtCore.QVariant(the_text).toFloat()[0])
        self.update_target_marker_position()

    def change_target_rotation(self):
        self.parameters['rotate'] = self.rotate_sb.value()
        self.update_target_marker_position()

    def update_target_marker_position(self):
        self.target_marker.x = self.parameters.get('target').x()
        self.target_marker.y = self.parameters.get('target').y()
        layer = self.canvas.currentLayer()
        feats = layer.selectedFeatures()
        self.calculate_points(feats)
        self.draw_markers()

    def update_reference_marker_position(self):
        super(MoveReference, self).update_reference_marker_position()
        layer = self.canvas.currentLayer()
        feats = layer.selectedFeatures()
        self.calculate_points(feats)
        self.draw_markers()

    def get_target_point(self, qgs_point, mouse_button):
        target_point = self._get_point(qgs_point, mouse_button, 
                                    self.target_map_tool)
        self.parameters['target'] = target_point
        self.target_marker.x = target_point.x()
        self.target_marker.y = target_point.y()
        self._update_controls()
        self.target_action.toggle()


class ReverseLine(generictools.Tool):

    operates_on = [{'type' : qgis.core.QGis.WKBLineString, 'features' : 'multiple'}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        super(ReverseLine, self).__init__(iface, icon_tool_bar, 
                                          controls_tool_bar)

        self.action = QtGui.QAction(
            QtGui.QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'Reverse line direction', 
            self.iface.mainWindow()
        )
        icon_tool_bar.addAction(self.action)
        QtCore.QObject.connect(self.action, QtCore.SIGNAL("triggered()"), self.run)
        self.toggle()

    def run(self):
        self.reverse_lines()
        self.canvas.refresh()

    def reverse_lines(self):
        layer = self.canvas.currentLayer()
        feats = layer.selectedFeatures()
        layer.beginEditCommand('reverse lines')
        for feat in feats:
            old_geom = feat.geometry()
            old_line = old_geom.asPolyline()
            new_line = []
            for pt in reversed(old_line):
                new_line.append(pt)
            new_geom = qgis.core.QgsGeometry.fromPolyline(new_line)
            layer.changeGeometry(feat.id(), new_geom)
        layer.endEditCommand()

