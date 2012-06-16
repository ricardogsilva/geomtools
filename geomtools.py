#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

import qgis.core
import qgis.gui

import createnumerical
import othertools

# TODO
# - At maximum only one tool must be active at a time, so there has to be a 
#   way to toggle them
# - Implement more tools:
#       - Create a point in the center of the bounding box of the selected 
#         points
# - Add custom icons

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
        self.tools = [
            createnumerical.CreateNumericalPoints(self.iface, 
                                                  self.icon_tool_bar, 
                                                  self.controls_tool_bar),
            othertools.MoveReference(self.iface, self.icon_tool_bar, 
                          self.controls_tool_bar),
            createnumerical.CreateNumericalLine(self.iface, 
                                                self.icon_tool_bar,
                                                self.controls_tool_bar),
            othertools.ReverseLine(self.iface, self.icon_tool_bar, 
                        self.controls_tool_bar),
        ]

    def unload(self):
        del self.icon_tool_bar

#
#class CreateNumericalPoints(ToolWithReference):
#    operates_on = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 0}]
#
#    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
#        super(CreateNumericalPoints, self).__init__(iface, icon_tool_bar, 
#                                              controls_tool_bar)
#        self.parameters = {
#            'offset_x' : 0.0,
#            'offset_y' : 0.0,
#            'distance' : 0.0,
#            'angle' : 0.0,
#        }
#        target_marker = base.VertexMarker(self.canvas, base.Point())
#        target_marker.setColor(QtGui.QColor(0, 0, 255))
#        target_marker.setIconType(qgis.gui.QgsVertexMarker.ICON_BOX)
#        target_marker.hide()
#        self.canvas_elements['target_marker'] = target_marker
#        self.action = QtGui.QAction(
#            QtGui.QIcon(':plugins/cadtools/icons/pointandline.png'), 
#            'create point with numerical input', 
#            self.iface.mainWindow()
#        )
#        self.action.setCheckable(True)
#        icon_tool_bar.addAction(self.action)
#        self.tool_bar = controls_tool_bar
#        QtCore.QObject.connect(self.action, QtCore.SIGNAL("toggled(bool)"), self.run)
#        self.toggle()
#
#    def run(self, active):
#        self.toggle_controls(active)
#        for id, element in self.canvas_elements.iteritems():
#            if active:
#                element.show()
#            else:
#                element.hide()
#
#    def _create_controls(self):
#        super(CreateNumericalPoints, self)._create_controls()
#        self.offset_radio = QtGui.QRadioButton('Offset', None)
#        self.angle_dist_radio = QtGui.QRadioButton('Angle && distance', None)
#
#        self.coor_x_lab = QtGui.QLabel(None)
#        self.coor_x_lab.setText('X')
#        self.coor_x_le = QtGui.QLineEdit(None)
#        self.coor_y_lab = QtGui.QLabel(None)
#        self.coor_y_lab.setText('Y')
#        self.coor_y_le = QtGui.QLineEdit(None)
#
#        self.coor_distance_lab = QtGui.QLabel(None)
#        self.coor_distance_lab.setText('Distance')
#        self.coor_distance_le = QtGui.QLineEdit(None)
#        self.coor_angle_lab = QtGui.QLabel(None)
#        self.coor_angle_lab.setText('Angle')
#        self.coor_angle_le = QtGui.QLineEdit(None)
#
#        self.create_point_btn = QtGui.QPushButton(None)
#        self.create_point_btn.setText('Create')
#
#        QtCore.QObject.connect(
#            self.coor_x_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_offset_x
#        )
#        QtCore.QObject.connect(
#            self.coor_y_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_offset_y
#        )
#        QtCore.QObject.connect(
#            self.coor_distance_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_distance
#        )
#        QtCore.QObject.connect(
#            self.coor_angle_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_angle
#        )
#        QtCore.QObject.connect(self.create_point_btn, QtCore.SIGNAL('released()'), 
#                        self.create_point)
#
#        self.tool_bar.addWidget(self.offset_radio)
#        self.tool_bar.addWidget(self.angle_dist_radio)
#        # storing QActions in order to be able to hide and show them later
#        self.action_coor_x_lab = self.tool_bar.addWidget(self.coor_x_lab)
#        self.action_coor_x_le = self.tool_bar.addWidget(self.coor_x_le)
#        self.action_coor_y_lab = self.tool_bar.addWidget(self.coor_y_lab)
#        self.action_coor_y_le = self.tool_bar.addWidget(self.coor_y_le)
#        self.action_coor_distance_lab = self.tool_bar.addWidget(self.coor_distance_lab)
#        self.action_coor_distance_le = self.tool_bar.addWidget(self.coor_distance_le)
#        self.action_coor_angle_lab = self.tool_bar.addWidget(self.coor_angle_lab)
#        self.action_coor_angle_le = self.tool_bar.addWidget(self.coor_angle_le)
#        QtCore.QObject.connect(self.offset_radio, QtCore.SIGNAL('toggled(bool)'), 
#                        self.toggle_mode_controls)
#        self.offset_radio.setChecked(True)
#        self.tool_bar.addSeparator()
#        self.tool_bar.addWidget(self.create_point_btn)
#        self._update_controls()
#
#    def toggle_mode_controls(self, offsets_active):
#        if offsets_active:
#            self.action_coor_distance_lab.setVisible(False)
#            self.action_coor_distance_le.setVisible(False)
#            self.action_coor_angle_lab.setVisible(False)
#            self.action_coor_angle_le.setVisible(False)
#            self.action_coor_x_lab.setVisible(True)
#            self.action_coor_x_le.setVisible(True)
#            self.action_coor_y_lab.setVisible(True)
#            self.action_coor_y_le.setVisible(True)
#        else:
#            self.action_coor_x_lab.setVisible(False)
#            self.action_coor_x_le.setVisible(False)
#            self.action_coor_y_lab.setVisible(False)
#            self.action_coor_y_le.setVisible(False)
#            self.action_coor_distance_lab.setVisible(True)
#            self.action_coor_distance_le.setVisible(True)
#            self.action_coor_angle_lab.setVisible(True)
#            self.action_coor_angle_le.setVisible(True)
#        self.update_target_marker_position()
#
#    def change_target_offset_x(self, the_text):
#        self.parameters['offset_x'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def change_target_offset_y(self, the_text):
#        self.parameters['offset_y'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def change_target_distance(self, the_text):
#        self.parameters['distance'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def change_target_angle(self, the_text):
#        self.parameters['angle'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def _update_controls(self):
#        super(CreateNumericalPoints, self)._update_controls()
#        self.coor_x_le.setText(str(self.parameters.get('offset_x')))
#        self.coor_y_le.setText(str(self.parameters.get('offset_y')))
#        self.coor_distance_le.setText(str(self.parameters.get('distance')))
#        self.coor_angle_le.setText(str(self.parameters.get('angle')))
#
#    def update_reference_marker_position(self):
#        super(CreateNumericalPoints, self).update_reference_marker_position()
#        self.update_target_marker_position()
#
#    def update_target_marker_position(self):
#        new_point = self.calculate_point()
#        self.canvas_elements['target_marker'].x = new_point.x()
#        self.canvas_elements['target_marker'].y = new_point.y()
#
#    def calculate_point(self):
#        new_point = base.Point(self.reference.x(), self.reference.y())
#        if self.offset_radio.isChecked():
#            new_point.translate_offsets(self.parameters.get('offset_x'), 
#                                        self.parameters.get('offset_y'))
#        else:
#            new_point.translate(self.parameters.get('angle'), 
#                                self.parameters.get('distance'))
#        return new_point
#
#    def create_point(self):
#        layer = self.canvas.currentLayer()
#        point = self.calculate_point()
#        f = qgis.core.QgsFeature()
#        geom = qgis.core.QgsGeometry.fromPoint(point)
#        f.setGeometry(geom)
#        layer.beginEditCommand('Create point')
#        layer.addFeatures([f], False)
#        layer.endEditCommand()
#        self.canvas.refresh()
#
#
#class CreateNumericalLine(ToolWithReference):
#    operates_on = [{'type' : qgis.core.QGis.WKBLineString, 'features' : 0}]
#
#    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
#        super(CreateNumericalLine, self).__init__(iface, icon_tool_bar, 
#                                                  controls_tool_bar)
#        self.parameters = {
#            'offset_x' : 0.0,
#            'offset_y' : 0.0,
#            'distance' : 0.0,
#            'angle' : 0.0,
#            'use_last_point' : False,
#            'line' : [],
#            'rubber_markers' : [],
#        }
#
#        self.target_marker = base.VertexMarker(self.canvas, base.Point())
#        self.target_marker.setColor(QtGui.QColor(0, 0, 255))
#        self.target_marker.setIconType(qgis.gui.QgsVertexMarker.ICON_BOX)
#        self.target_marker.hide()
#
#        self.rubber_band = qgis.gui.QgsRubberBand(self.canvas, False)
#        self.rubber_band.setColor(QtGui.QColor(0, 0, 255))
#        self.rubber_band.hide()
#
#        self.action = QtGui.QAction(
#            QtGui.QIcon(':plugins/cadtools/icons/pointandline.png'), 
#            'create line with numerical input', 
#            self.iface.mainWindow()
#        )
#        self.action.setCheckable(True)
#        icon_tool_bar.addAction(self.action)
#        self.tool_bar = controls_tool_bar
#        QtCore.QObject.connect(self.action, QtCore.SIGNAL("toggled(bool)"), self.run)
#        self.toggle()
#
#    def run(self, active):
#        self.toggle_controls(active)
#        if active:
#            self.reference_marker.show()
#            self.target_marker.show()
#            self.rubber_band.show()
#            [m.show() for m in self.parameters['rubber_markers']]
#        else:
#            self.reference_marker.hide()
#            self.target_marker.hide()
#            self.rubber_band.hide()
#            [m.hide() for m in self.parameters['rubber_markers']]
#
#    def _create_controls(self):
#        super(CreateNumericalLine, self)._create_controls()
#
#        self.last_point_ref_cb = QtGui.QCheckBox('Use last point as reference', None)
#
#        self.offset_radio = QtGui.QRadioButton('Offset', None)
#        self.angle_dist_radio = QtGui.QRadioButton('Angle && distance', None)
#
#        self.coor_x_lab = QtGui.QLabel(None)
#        self.coor_x_lab.setText('X')
#        self.coor_x_le = QtGui.QLineEdit(None)
#        self.coor_y_lab = QtGui.QLabel(None)
#        self.coor_y_lab.setText('Y')
#        self.coor_y_le = QtGui.QLineEdit(None)
#
#        self.coor_distance_lab = QtGui.QLabel(None)
#        self.coor_distance_lab.setText('Distance')
#        self.coor_distance_le = QtGui.QLineEdit(None)
#        self.coor_angle_lab = QtGui.QLabel(None)
#        self.coor_angle_lab.setText('Angle')
#        self.coor_angle_le = QtGui.QLineEdit(None)
#
#        self.remove_vertex_btn = QtGui.QPushButton(None)
#        self.remove_vertex_btn.setText('Remove vertex')
#        self.add_vertex_btn = QtGui.QPushButton(None)
#        self.add_vertex_btn.setText('Add vertex')
#        self.clear_line_btn = QtGui.QPushButton(None)
#        self.clear_line_btn.setText('Clear line')
#        self.finish_line_btn = QtGui.QPushButton(None)
#        self.finish_line_btn.setText('Finish line')
#
#        QtCore.QObject.connect(
#            self.coor_x_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_offset_x
#        )
#        QtCore.QObject.connect(
#            self.coor_y_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_offset_y
#        )
#        QtCore.QObject.connect(
#            self.coor_distance_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_distance
#        )
#        QtCore.QObject.connect(
#            self.coor_angle_le, 
#            QtCore.SIGNAL('textChanged(const QString &)'), 
#            self.change_target_angle
#        )
#        QtCore.QObject.connect(self.add_vertex_btn, QtCore.SIGNAL('released()'), 
#                        self.add_vertex)
#        QtCore.QObject.connect(self.remove_vertex_btn, QtCore.SIGNAL('released()'), 
#                        self.remove_vertex)
#        QtCore.QObject.connect(self.clear_line_btn, QtCore.SIGNAL('released()'), 
#                        self.clear_line)
#        QtCore.QObject.connect(self.finish_line_btn, QtCore.SIGNAL('released()'), 
#                        self.create_line)
#
#        QtCore.QObject.connect(self.last_point_ref_cb, QtCore.SIGNAL('stateChanged(int)'), 
#                        self.toggle_use_last_point_reference)
#        self.last_point_ref_cb.setChecked(False)
#
#        self.tool_bar.addWidget(self.last_point_ref_cb)
#        self.tool_bar.addWidget(self.offset_radio)
#        self.tool_bar.addWidget(self.angle_dist_radio)
#        # storing QActions in order to be able to hide and show them later
#        self.action_coor_x_lab = self.tool_bar.addWidget(self.coor_x_lab)
#        self.action_coor_x_le = self.tool_bar.addWidget(self.coor_x_le)
#        self.action_coor_y_lab = self.tool_bar.addWidget(self.coor_y_lab)
#        self.action_coor_y_le = self.tool_bar.addWidget(self.coor_y_le)
#        self.action_coor_distance_lab = self.tool_bar.addWidget(self.coor_distance_lab)
#        self.action_coor_distance_le = self.tool_bar.addWidget(self.coor_distance_le)
#        self.action_coor_angle_lab = self.tool_bar.addWidget(self.coor_angle_lab)
#        self.action_coor_angle_le = self.tool_bar.addWidget(self.coor_angle_le)
#        QtCore.QObject.connect(self.offset_radio, QtCore.SIGNAL('toggled(bool)'), 
#                        self.toggle_mode_controls)
#        self.offset_radio.setChecked(True)
#        self.tool_bar.addSeparator()
#        self.tool_bar.addWidget(self.add_vertex_btn)
#        self.tool_bar.addWidget(self.remove_vertex_btn)
#        self.tool_bar.addWidget(self.clear_line_btn)
#        self.tool_bar.addSeparator()
#        self.tool_bar.addWidget(self.finish_line_btn)
#        self._update_controls()
#
#    def toggle_use_last_point_reference(self):
#        if self.last_point_ref_cb.isChecked():
#            self.parameters['use_last_point'] = True
#            self.ref_x_lab.setEnabled(False)
#            self.ref_x_le.setEnabled(False)
#            self.ref_y_lab.setEnabled(False)
#            self.ref_y_le.setEnabled(False)
#            self.ref_action.setEnabled(False)
#        else:
#            self.parameters['use_last_point'] = False
#            self.ref_x_lab.setEnabled(True)
#            self.ref_x_le.setEnabled(True)
#            self.ref_y_lab.setEnabled(True)
#            self.ref_y_le.setEnabled(True)
#            self.ref_action.setEnabled(True)
#        self._update_controls()
#
#    def add_vertex(self):
#        new_point = self._get_current_point()
#        self.parameters['line'].append(new_point)
#        self.update_rubber_band()
#        self.update_rubber_markers()
#        self.canvas.refresh()
#        self._update_controls()
#
#    def update_rubber_markers(self):
#        scene = self.canvas.scene()
#        [scene.removeItem(m) for m in self.parameters['rubber_markers']]
#        self.parameters['rubber_markers'] = []
#        for pt in self.parameters['line']:
#            rubber_marker = base.VertexMarker(self.canvas, base.Point())
#            rubber_marker.setColor(QtGui.QColor(0, 0, 255))
#            rubber_marker.x = pt.x()
#            rubber_marker.y = pt.y()
#            self.parameters['rubber_markers'].append(rubber_marker)
#
#    def remove_vertex(self):
#        removed_point = self.parameters['line'].pop()
#        self.update_rubber_markers()
#        self.update_rubber_band()
#        self._update_controls()
#        self.canvas.refresh()
#
#    def update_rubber_band(self):
#        line_geom = qgis.core.QgsGeometry.fromPolyline(self.parameters['line'])
#        self.rubber_band.setToGeometry(line_geom, None)
#
#    def _get_current_point(self):
#        if self.parameters['use_last_point']:
#            last_point = self.parameters['line'][-1]
#            new_point = base.Point(last_point.x(), last_point.y())
#        else:
#            new_point = base.Point(self.reference.x(), self.reference.y())
#        if self.offset_radio.isChecked():
#            new_point.translate_offsets(self.parameters.get('offset_x'), 
#                                        self.parameters.get('offset_y'))
#        else:
#            new_point.translate(self.parameters.get('angle'), 
#                                self.parameters.get('distance'))
#        return new_point
#
#    def _update_controls(self):
#        if len(self.parameters['line']) == 0:
#            self.last_point_ref_cb.setChecked(False)
#            self.last_point_ref_cb.setEnabled(False)
#        else:
#            self.last_point_ref_cb.setEnabled(True)
#        if self.last_point_ref_cb.isChecked():
#            the_reference = self.parameters['line'][-1]
#        else:
#            the_reference = self.reference
#        if len(self.parameters['line']) < 2:
#            self.finish_line_btn.setEnabled(False)
#        else:
#            self.finish_line_btn.setEnabled(True)
#        self.ref_x_le.setText(str(the_reference.x()))
#        self.ref_y_le.setText(str(the_reference.y()))
#        self.coor_x_le.setText(str(self.parameters.get('offset_x')))
#        self.coor_y_le.setText(str(self.parameters.get('offset_y')))
#        self.coor_distance_le.setText(str(self.parameters.get('distance')))
#        self.coor_angle_le.setText(str(self.parameters.get('angle')))
#        self.update_target_marker_position()
#
#    def create_line(self):
#        layer = self.canvas.currentLayer()
#        f = qgis.core.QgsFeature()
#        geom = qgis.core.QgsGeometry.fromPolyline(self.parameters['line'])
#        f.setGeometry(geom)
#        layer.beginEditCommand('Create line')
#        layer.addFeatures([f], False)
#        layer.endEditCommand()
#        self.parameters['line'] = []
#        self.update_rubber_band()
#        self.update_rubber_markers()
#        self._update_controls()
#        self.canvas.refresh()
#
#    def clear_line(self):
#        self.parameters['line'] = []
#        self.update_rubber_markers()
#        self.update_rubber_band()
#        self._update_controls()
#        self.canvas.refresh()
#
#    def change_target_offset_x(self, the_text):
#        self.parameters['offset_x'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def change_target_offset_y(self, the_text):
#        self.parameters['offset_y'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def change_target_distance(self, the_text):
#        self.parameters['distance'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def change_target_angle(self, the_text):
#        self.parameters['angle'] = QtCore.QVariant(the_text).toFloat()[0]
#        self.update_target_marker_position()
#
#    def update_target_marker_position(self):
#        new_point = self._get_current_point()
#        self.target_marker.x = new_point.x()
#        self.target_marker.y = new_point.y()
#
#    def toggle_mode_controls(self, offsets_active):
#        if offsets_active:
#            self.action_coor_distance_lab.setVisible(False)
#            self.action_coor_distance_le.setVisible(False)
#            self.action_coor_angle_lab.setVisible(False)
#            self.action_coor_angle_le.setVisible(False)
#            self.action_coor_x_lab.setVisible(True)
#            self.action_coor_x_le.setVisible(True)
#            self.action_coor_y_lab.setVisible(True)
#            self.action_coor_y_le.setVisible(True)
#        else:
#            self.action_coor_x_lab.setVisible(False)
#            self.action_coor_x_le.setVisible(False)
#            self.action_coor_y_lab.setVisible(False)
#            self.action_coor_y_le.setVisible(False)
#            self.action_coor_distance_lab.setVisible(True)
#            self.action_coor_distance_le.setVisible(True)
#            self.action_coor_angle_lab.setVisible(True)
#            self.action_coor_angle_le.setVisible(True)
#        self.update_target_marker_position()
#

