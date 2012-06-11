#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qgis.core
import qgis.gui

import base

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
            CreateNumericalPoints(self.iface, self.icon_tool_bar, 
                                  self.controls_tool_bar),
            MoveReference(self.iface, self.icon_tool_bar, 
                          self.controls_tool_bar),
            CreateNumericalLine(self.iface, self.icon_tool_bar,
                                self.controls_tool_bar),
        ]
        #self.numerical_points = CreateNumericalPoints(self.iface, 
        #                                              self.icon_tool_bar, 
        #                                              self.controls_tool_bar)
        #self.move_reference = MoveReference(self.iface, self.icon_tool_bar, 
        #                                    self.controls_tool_bar)
        #self.numerical_lines = CreateNumericalLine(self.iface, 
        #                                           self.icon_tool_bar,
        #                                           self.controls_tool_bar)

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
        if layer is not None and layer.isEditable() and \
                self._selection_correct(layer):
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

    def toggle_action(self):
        layer = self.canvas.currentLayer()
        action = False
        for t in self.OPERATES_ON:
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
        self.reference_marker = base.VertexMarker(self.canvas, base.Point())
        self.reference_marker.hide()
        self.reference_map_tool = qgis.gui.QgsMapToolEmitPoint(self.canvas)
        self.ref_action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'select a point in the map window to be used as reference point', 
            self.iface.mainWindow()
        )
        self.ref_action.setCheckable(True)
        QObject.connect(self.ref_action, SIGNAL('toggled(bool)'), 
                        self.toggle_reference_selection)
        QObject.connect(self.reference_map_tool, SIGNAL('canvasClicked(const '\
                        'QgsPoint &, Qt::MouseButton)'), 
                        self.get_reference_point)

    def _create_controls(self):
        self.ref_lab = QLabel(None)
        self.ref_lab.setText('Reference:')
        self.ref_x_lab = QLabel(None)
        self.ref_x_lab.setText('X')
        self.ref_x_le = QLineEdit(None)
        self.ref_y_lab = QLabel(None)
        self.ref_y_lab.setText('Y')
        self.ref_y_le = QLineEdit(None)
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
        self.reference.setX(QVariant(the_text).toFloat()[0])
        self.update_reference_marker_position()

    def change_reference_parameter_y(self, the_text):
        self.reference.setY(QVariant(the_text).toFloat()[0])
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
        self.reference_marker.x = ref_point.x()
        self.reference_marker.y = ref_point.y()
        self._update_controls()
        self.ref_action.toggle()

    def update_reference_marker_position(self):
        self.reference_marker.x = self.reference.x()
        self.reference_marker.y = self.reference.y()


class CreateNumericalPoints(ToolWithReference):
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 0}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        super(CreateNumericalPoints, self).__init__(iface, icon_tool_bar, 
                                              controls_tool_bar)
        self.parameters = {
            'offset_x' : 0.0,
            'offset_y' : 0.0,
            'distance' : 0.0,
            'angle' : 0.0,
        }
        self.target_marker = base.VertexMarker(self.canvas, base.Point())
        self.target_marker.setColor(QColor(0, 0, 255))
        self.target_marker.setIconType(qgis.gui.QgsVertexMarker.ICON_BOX)
        self.target_marker.hide()
        self.action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'create point with numerical input', 
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        icon_tool_bar.addAction(self.action)
        self.tool_bar = controls_tool_bar
        QObject.connect(self.action, SIGNAL("toggled(bool)"), self.run)
        self.toggle()

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


class MoveReference(ToolWithReference):
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBPoint, 'features' : 'multiple'}]

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
        self.target_marker.setColor(QColor(0, 0, 255))
        self.target_marker.setIconType(qgis.gui.QgsVertexMarker.ICON_BOX)
        self.target_marker.hide()
        self.action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'Move points according to a reference', 
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        icon_tool_bar.addAction(self.action)
        self.target_action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'select a point in the map window for being the target', 
            self.iface.mainWindow()
        )
        self.target_action.setCheckable(True)
        self.tool_bar = controls_tool_bar
        self.target_map_tool = qgis.gui.QgsMapToolEmitPoint(self.canvas)
        QObject.connect(self.action, SIGNAL("toggled(bool)"), self.run)
        QObject.connect(self.target_action, SIGNAL('toggled(bool)'), 
                        self.toggle_target_selection)
        QObject.connect(self.target_map_tool, SIGNAL('canvasClicked(const '\
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
        self.target_lab = QLabel(None)
        self.target_lab.setText('Target:')
        self.target_x_lab = QLabel(None)
        self.target_x_lab.setText('X')
        self.target_x_le = QLineEdit(None)
        self.target_y_lab = QLabel(None)
        self.target_y_lab.setText('Y')
        self.target_y_le = QLineEdit(None)

        self.rotate_lab = QLabel('Rotate', None)
        self.rotate_sb = QDoubleSpinBox(None)
        self.rotate_sb.setMinimum(0)
        self.rotate_sb.setMaximum(360)
        self.rotate_sb.setDecimals(0)
        self.rotate_sb.setSuffix(u'\u00b0')

        self.copy_cb = QCheckBox('copy', None)

        self.move_btn = QPushButton(None)
        self.move_btn.setText('Move')

        QObject.connect(
            self.target_x_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_parameter_x
        )
        QObject.connect(
            self.target_y_le, 
            SIGNAL('textChanged(const QString &)'), 
            self.change_target_parameter_y
        )
        QObject.connect(self.move_btn, SIGNAL('released()'), 
                        self.move)
        QObject.connect(self.copy_cb, SIGNAL('stateChanged(int)'), 
                        self.toggle_copy)
        QObject.connect(self.rotate_sb, SIGNAL('valueChanged(double)'), 
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
            v.setColor(QColor(0, 0, 255))
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
        self.parameters.get('target').setX(QVariant(the_text).toFloat()[0])
        self.update_target_marker_position()

    def change_target_parameter_y(self, the_text):
        self.parameters.get('target').setY(QVariant(the_text).toFloat()[0])
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


class CreateNumericalLine(ToolWithReference):
    OPERATES_ON = [{'type' : qgis.core.QGis.WKBLineString, 'features' : 0}]

    def __init__(self, iface, icon_tool_bar, controls_tool_bar):
        super(CreateNumericalLine, self).__init__(iface, icon_tool_bar, 
                                                  controls_tool_bar)
        self.parameters = {
            'offset_x' : 0.0,
            'offset_y' : 0.0,
            'distance' : 0.0,
            'angle' : 0.0,
            'use_last_point' : False,
            'line' : [],
            'rubber_markers' : [],
        }

        self.target_marker = base.VertexMarker(self.canvas, base.Point())
        self.target_marker.setColor(QColor(0, 0, 255))
        self.target_marker.setIconType(qgis.gui.QgsVertexMarker.ICON_BOX)
        self.target_marker.hide()

        self.rubber_band = qgis.gui.QgsRubberBand(self.canvas, False)
        self.rubber_band.setColor(QColor(0, 0, 255))
        self.rubber_band.hide()

        self.action = QAction(
            QIcon(':plugins/cadtools/icons/pointandline.png'), 
            'create line with numerical input', 
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        icon_tool_bar.addAction(self.action)
        self.tool_bar = controls_tool_bar
        QObject.connect(self.action, SIGNAL("toggled(bool)"), self.run)
        self.toggle()

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
        self.finish_line_btn = QPushButton(None)
        self.finish_line_btn.setText('Finish line')
        self.clear_line_btn = QPushButton(None)
        self.clear_line_btn.setText('Clear line')

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
        self.tool_bar.addWidget(self.finish_line_btn)
        self.tool_bar.addWidget(self.clear_line_btn)
        self._update_controls()

    def toggle_use_last_point_reference(self):
        if self.last_point_ref_cb.isChecked():
            self.parameters['use_last_point'] = True
        else:
            self.parameters['use_last_point'] = False
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
            self.last_point_ref_cb.setEnabled(False)
        else:
            self.last_point_ref_cb.setEnabled(True)
        if self.last_point_ref_cb.isChecked():
            the_reference = self.parameters['line'][-1]
        else:
            the_reference = self.reference
        self.ref_x_le.setText(str(the_reference.x()))
        self.ref_y_le.setText(str(the_reference.y()))
        self.coor_x_le.setText(str(self.parameters.get('offset_x')))
        self.coor_y_le.setText(str(self.parameters.get('offset_y')))
        self.coor_distance_le.setText(str(self.parameters.get('distance')))
        self.coor_angle_le.setText(str(self.parameters.get('angle')))
        self.update_target_marker_position()

    def create_line(self):
        raise NotImplementedError

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
