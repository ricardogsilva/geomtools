#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Script's doctring goes here.
"""

from geomtools import Tool, ToolWithReference


class CreateNumerical(ToolWithReference):

    TARGET_MARKER_COLOR = QColor(0, 0, 255)
    TARGET_MARKER_ICON = qgis.gui.QgsVertexMarker.ICON_BOX
    RUBBER_BAND_COLOR = TARGET_COLOR

    def __init__(self, iface, icon_tool_bar, controls_tool_bar, action, 
                 parameters=dict()):
        super(CreateNumerical, self).__init__(iface, icon_tool_bar, 
                                              controls_tool_bar)
        self.parameters = {
            'offset_x' : 0.0,
            'offset_y' : 0.0,
            'distance' : 0.0,
            'angle' : 0.0,
        }
        self.parameters.update(parameters)
        self.target_marker = base.VertexMarker(self.canvas, base.Point())
        self.target_marker.setColor(self.TARGET_MARKER_COLOR)
        self.target_marker.setIconType(self.TARGET_MARKER_ICON)
        self.target_marker.hide()
        self.action = action
        self.action.setCheckable(True)
        icon_tool_bar.addAction(self.action)
        self.tool_bar = controls_tool_bar
        QObject.connect(self.action, SIGNAL("toggled(bool)"), self.run)
        self.toggle()


class CreateNumericalPoints(CreateNumerical):
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 0}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'create point with numerical input', 
            self.iface.mainWindow()
        )
        super(CreateNumericalPoints, self).__init__(iface, icon_tool_bar, 
                                              controls_tool_bar, action)

    def run(self, active):
        self.toggle_controls(active)
        if active:
            self.reference_marker.show()
            self.target_marker.show()
        else:
            self.reference_marker.hide()
            self.target_marker.hide()

    def _create_controls(self):
        super(CreateNumericalPoints, self)._create_controls()
        self.offset_radio = QRadioButton('Offset', None)
        self.angle_dist_radio = QRadioButton('Angle && distance', None)

        self.coor_x_lab = QLabel(None)
        self.coor_x_lab.setText('X')
        self.coor_x_le = QLineEdit(None)
        self.coor_y_lab = QLabel(None)
        self.coor_y_lab.setText('Y')
        self.coor_y_le = QLineEdit(None)

        self.coor_distance_lab = QLabel(None)
        self.coor_distance_lab.setText('Distance')
        self.coor_distance_le = QLineEdit(None)
        self.coor_angle_lab = QLabel(None)
        self.coor_angle_lab.setText('Angle')
        self.coor_angle_le = QLineEdit(None)

        self.create_point_btn = QPushButton(None)
        self.create_point_btn.setText('Create')

        QObject.connect(
            self.coor_x_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_offset_x
        )
        QObject.connect(
            self.coor_y_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_offset_y
        )
        QObject.connect(
            self.coor_distance_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_distance
        )
        QObject.connect(
            self.coor_angle_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_angle
        )
        QObject.connect(self.create_point_btn, SIGNAL('released()'), 
                        self.create_point)

        self.tool_bar.addWidget(self.offset_radio)
        self.tool_bar.addWidget(self.angle_dist_radio)
        # storing QActions in order to be able to hide and show them later
        self.action_coor_x_lab = self.tool_bar.addWidget(self.coor_x_lab)
        self.action_coor_x_le = self.tool_bar.addWidget(self.coor_x_le)
        self.action_coor_y_lab = self.tool_bar.addWidget(self.coor_y_lab)
        self.action_coor_y_le = self.tool_bar.addWidget(self.coor_y_le)
        self.action_coor_distance_lab = self.tool_bar.addWidget(self.coor_distance_lab)
        self.action_coor_distance_le = self.tool_bar.addWidget(self.coor_distance_le)
        self.action_coor_angle_lab = self.tool_bar.addWidget(self.coor_angle_lab)
        self.action_coor_angle_le = self.tool_bar.addWidget(self.coor_angle_le)
        QObject.connect(self.offset_radio, SIGNAL('toggled(bool)'), 
                        self.toggle_mode_controls)
        self.offset_radio.setChecked(True)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.create_point_btn)
        self._update_controls()

    def toggle_mode_controls(self, offsets_active):
        if offsets_active:
            self.action_coor_distance_lab.setVisible(False)
            self.action_coor_distance_le.setVisible(False)
            self.action_coor_angle_lab.setVisible(False)
            self.action_coor_angle_le.setVisible(False)
            self.action_coor_x_lab.setVisible(True)
            self.action_coor_x_le.setVisible(True)
            self.action_coor_y_lab.setVisible(True)
            self.action_coor_y_le.setVisible(True)
        else:
            self.action_coor_x_lab.setVisible(False)
            self.action_coor_x_le.setVisible(False)
            self.action_coor_y_lab.setVisible(False)
            self.action_coor_y_le.setVisible(False)
            self.action_coor_distance_lab.setVisible(True)
            self.action_coor_distance_le.setVisible(True)
            self.action_coor_angle_lab.setVisible(True)
            self.action_coor_angle_le.setVisible(True)
        self.update_target_marker_position()

    def change_target_offset_x(self, the_text):
        self.parameters['offset_x'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def change_target_offset_y(self, the_text):
        self.parameters['offset_y'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def change_target_distance(self, the_text):
        self.parameters['distance'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def change_target_angle(self, the_text):
        self.parameters['angle'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def _update_controls(self):
        super(CreateNumericalPoints, self)._update_controls()
        self.coor_x_le.setText(str(self.parameters.get('offset_x')))
        self.coor_y_le.setText(str(self.parameters.get('offset_y')))
        self.coor_distance_le.setText(str(self.parameters.get('distance')))
        self.coor_angle_le.setText(str(self.parameters.get('angle')))

    def update_reference_marker_position(self):
        super(CreateNumericalPoints, self).update_reference_marker_position()
        self.update_target_marker_position()

    def update_target_marker_position(self):
        new_point = self.calculate_point()
        self.target_marker.x = new_point.x()
        self.target_marker.y = new_point.y()

    def calculate_point(self):
        new_point = base.Point(self.reference.x(), self.reference.y())
        if self.offset_radio.isChecked():
            new_point.translate_offsets(self.parameters.get('offset_x'), 
                                        self.parameters.get('offset_y'))
        else:
            new_point.translate(self.parameters.get('angle'), 
                                self.parameters.get('distance'))
        return new_point

    def create_point(self):
        layer = self.canvas.currentLayer()
        point = self.calculate_point()
        f = qgis.core.QgsFeature()
        geom = qgis.core.QgsGeometry.fromPoint(point)
        f.setGeometry(geom)
        layer.beginEditCommand('Create point')
        layer.addFeatures([f], False)
        layer.endEditCommand()
        self.canvas.refresh()


class CreateNumericalLine(CreateNumerical):
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBLineString, 'features' : 0}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'create line with numerical input', 
            self.iface.mainWindow()
        )
        parameters = {
            'use_last_point' : False,
            'line' : [],
            'rubber_markers' : [],
        }

        self.rubber_band = qgis.gui.QgsRubberBand(self.canvas, False)
        self.rubber_band.setColor(self.RUBBER_BAND_COLOR)
        self.rubber_band.hide()
        super(CreateNumericalLine, self).__init__(iface, icon_tool_bar, 
                                                  controls_tool_bar, action, 
                                                  parameters)

    def run(self, active):
        self.toggle_controls(active)
        if active:
            self.reference_marker.show()
            self.target_marker.show()
            self.rubber_band.show()
            [m.show() for m in self.parameters['rubber_markers']]
        else:
            self.reference_marker.hide()
            self.target_marker.hide()
            self.rubber_band.hide()
            [m.hide() for m in self.parameters['rubber_markers']]

    def _create_controls(self):
        super(CreateNumericalLine, self)._create_controls()

        self.last_point_ref_cb = QCheckBox('Use last point as reference', None)

        self.offset_radio = QRadioButton('Offset', None)
        self.angle_dist_radio = QRadioButton('Angle && distance', None)

        self.coor_x_lab = QLabel(None)
        self.coor_x_lab.setText('X')
        self.coor_x_le = QLineEdit(None)
        self.coor_y_lab = QLabel(None)
        self.coor_y_lab.setText('Y')
        self.coor_y_le = QLineEdit(None)

        self.coor_distance_lab = QLabel(None)
        self.coor_distance_lab.setText('Distance')
        self.coor_distance_le = QLineEdit(None)
        self.coor_angle_lab = QLabel(None)
        self.coor_angle_lab.setText('Angle')
        self.coor_angle_le = QLineEdit(None)

        self.remove_vertex_btn = QPushButton(None)
        self.remove_vertex_btn.setText('Remove vertex')
        self.add_vertex_btn = QPushButton(None)
        self.add_vertex_btn.setText('Add vertex')
        self.clear_line_btn = QPushButton(None)
        self.clear_line_btn.setText('Clear line')
        self.finish_line_btn = QPushButton(None)
        self.finish_line_btn.setText('Finish line')

        QObject.connect(
            self.coor_x_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_offset_x
        )
        QObject.connect(
            self.coor_y_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_offset_y
        )
        QObject.connect(
            self.coor_distance_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_distance
        )
        QObject.connect(
            self.coor_angle_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_angle
        )
        QObject.connect(self.add_vertex_btn, SIGNAL('released()'), 
                        self.add_vertex)
        QObject.connect(self.remove_vertex_btn, SIGNAL('released()'), 
                        self.remove_vertex)
        QObject.connect(self.clear_line_btn, SIGNAL('released()'), 
                        self.clear_line)
        QObject.connect(self.finish_line_btn, SIGNAL('released()'), 
                        self.create_line)

        QObject.connect(self.last_point_ref_cb, SIGNAL('stateChanged(int)'), 
                        self.toggle_use_last_point_reference)
        self.last_point_ref_cb.setChecked(False)

        self.tool_bar.addWidget(self.last_point_ref_cb)
        self.tool_bar.addWidget(self.offset_radio)
        self.tool_bar.addWidget(self.angle_dist_radio)
        # storing QActions in order to be able to hide and show them later
        self.action_coor_x_lab = self.tool_bar.addWidget(self.coor_x_lab)
        self.action_coor_x_le = self.tool_bar.addWidget(self.coor_x_le)
        self.action_coor_y_lab = self.tool_bar.addWidget(self.coor_y_lab)
        self.action_coor_y_le = self.tool_bar.addWidget(self.coor_y_le)
        self.action_coor_distance_lab = self.tool_bar.addWidget(self.coor_distance_lab)
        self.action_coor_distance_le = self.tool_bar.addWidget(self.coor_distance_le)
        self.action_coor_angle_lab = self.tool_bar.addWidget(self.coor_angle_lab)
        self.action_coor_angle_le = self.tool_bar.addWidget(self.coor_angle_le)
        QObject.connect(self.offset_radio, SIGNAL('toggled(bool)'), 
                        self.toggle_mode_controls)
        self.offset_radio.setChecked(True)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.add_vertex_btn)
        self.tool_bar.addWidget(self.remove_vertex_btn)
        self.tool_bar.addWidget(self.clear_line_btn)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.finish_line_btn)
        self._update_controls()

    def toggle_use_last_point_reference(self):
        if self.last_point_ref_cb.isChecked():
            self.parameters['use_last_point'] = True
            self.ref_x_lab.setEnabled(False)
            self.ref_x_le.setEnabled(False)
            self.ref_y_lab.setEnabled(False)
            self.ref_y_le.setEnabled(False)
            self.ref_action.setEnabled(False)
        else:
            self.parameters['use_last_point'] = False
            self.ref_x_lab.setEnabled(True)
            self.ref_x_le.setEnabled(True)
            self.ref_y_lab.setEnabled(True)
            self.ref_y_le.setEnabled(True)
            self.ref_action.setEnabled(True)
        self._update_controls()

    def add_vertex(self):
        new_point = self._get_current_point()
        self.parameters['line'].append(new_point)
        self.update_rubber_band()
        self.update_rubber_markers()
        self.canvas.refresh()
        self._update_controls()

    def update_rubber_markers(self):
        scene = self.canvas.scene()
        [scene.removeItem(m) for m in self.parameters['rubber_markers']]
        self.parameters['rubber_markers'] = []
        for pt in self.parameters['line']:
            rubber_marker = base.VertexMarker(self.canvas, base.Point())
            rubber_marker.setColor(QColor(0, 0, 255))
            rubber_marker.x = pt.x()
            rubber_marker.y = pt.y()
            self.parameters['rubber_markers'].append(rubber_marker)

    def remove_vertex(self):
        removed_point = self.parameters['line'].pop()
        self.update_rubber_markers()
        self.update_rubber_band()
        self._update_controls()
        self.canvas.refresh()

    def update_rubber_band(self):
        line_geom = qgis.core.QgsGeometry.fromPolyline(self.parameters['line'])
        self.rubber_band.setToGeometry(line_geom, None)

    def _get_current_point(self):
        if self.parameters['use_last_point']:
            last_point = self.parameters['line'][-1]
            new_point = base.Point(last_point.x(), last_point.y())
        else:
            new_point = base.Point(self.reference.x(), self.reference.y())
        if self.offset_radio.isChecked():
            new_point.translate_offsets(self.parameters.get('offset_x'), 
                                        self.parameters.get('offset_y'))
        else:
            new_point.translate(self.parameters.get('angle'), 
                                self.parameters.get('distance'))
        return new_point

    def _update_controls(self):
        if len(self.parameters['line']) == 0:
            self.last_point_ref_cb.setChecked(False)
            self.last_point_ref_cb.setEnabled(False)
        else:
            self.last_point_ref_cb.setEnabled(True)
        if self.last_point_ref_cb.isChecked():
            the_reference = self.parameters['line'][-1]
        else:
            the_reference = self.reference
        if len(self.parameters['line']) < 2:
            self.finish_line_btn.setEnabled(False)
        else:
            self.finish_line_btn.setEnabled(True)
        self.ref_x_le.setText(str(the_reference.x()))
        self.ref_y_le.setText(str(the_reference.y()))
        self.coor_x_le.setText(str(self.parameters.get('offset_x')))
        self.coor_y_le.setText(str(self.parameters.get('offset_y')))
        self.coor_distance_le.setText(str(self.parameters.get('distance')))
        self.coor_angle_le.setText(str(self.parameters.get('angle')))
        self.update_target_marker_position()

    def create_line(self):
        layer = self.canvas.currentLayer()
        f = qgis.core.QgsFeature()
        geom = qgis.core.QgsGeometry.fromPolyline(self.parameters['line'])
        f.setGeometry(geom)
        layer.beginEditCommand('Create line')
        layer.addFeatures([f], False)
        layer.endEditCommand()
        self.parameters['line'] = []
        self.update_rubber_band()
        self.update_rubber_markers()
        self._update_controls()
        self.canvas.refresh()

    def clear_line(self):
        self.parameters['line'] = []
        self.update_rubber_markers()
        self.update_rubber_band()
        self._update_controls()
        self.canvas.refresh()

    def change_target_offset_x(self, the_text):
        self.parameters['offset_x'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def change_target_offset_y(self, the_text):
        self.parameters['offset_y'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def change_target_distance(self, the_text):
        self.parameters['distance'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def change_target_angle(self, the_text):
        self.parameters['angle'] = QVariant(the_text).toFloat()[0]
        self.update_target_marker_position()

    def update_target_marker_position(self):
        new_point = self._get_current_point()
        self.target_marker.x = new_point.x()
        self.target_marker.y = new_point.y()

    def toggle_mode_controls(self, offsets_active):
        if offsets_active:
            self.action_coor_distance_lab.setVisible(False)
            self.action_coor_distance_le.setVisible(False)
            self.action_coor_angle_lab.setVisible(False)
            self.action_coor_angle_le.setVisible(False)
            self.action_coor_x_lab.setVisible(True)
            self.action_coor_x_le.setVisible(True)
            self.action_coor_y_lab.setVisible(True)
            self.action_coor_y_le.setVisible(True)
        else:
            self.action_coor_x_lab.setVisible(False)
            self.action_coor_x_le.setVisible(False)
            self.action_coor_y_lab.setVisible(False)
            self.action_coor_y_le.setVisible(False)
            self.action_coor_distance_lab.setVisible(True)
            self.action_coor_distance_le.setVisible(True)
            self.action_coor_angle_lab.setVisible(True)
            self.action_coor_angle_le.setVisible(True)
        self.update_target_marker_position()


class CreateNumericalPolygon(ToolWithReference):

    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPolygon, 'features' : 0}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'create polygon with numerical input', 
            self.iface.mainWindow()
        )
        parameters = {
            'use_last_point' : False,
            'line' : [],
            'rubber_markers' : [],
        }

        self.rubber_band = qgis.gui.QgsRubberBand(self.canvas, True)
        self.rubber_band.setColor(self.RUBBER_BAND_COLOR)
        self.rubber_band.hide()
        super(CreateNumericalPolygon, self).__init__(iface, icon_tool_bar, 
                                                     controls_tool_bar, action, 
                                                     parameters)


