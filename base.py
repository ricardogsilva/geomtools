#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
A module implementing some base geometry classes with custom methods that
expand on the QGIS classes.
'''

from math import pi, atan, atan2, cos, sin, radians, degrees, sqrt

from qgis.core import QgsPoint, QgsGeometry
from qgis.gui import QgsVertexMarker

class Point(QgsPoint):
    '''
    A class to provide aditional methods to the QgsPoint class.
    '''

    @staticmethod
    def from_feature(feature):
        '''Return a Point object from a QGIS feature.'''

        pnt = feature.geometry().asPoint()
        return Point(pnt.x(), pnt.y())

    def angle(self, other_point):
        '''Return the angle between this point and other_point'''

        offset_x = other_point.x() - self.x()
        offset_y = other_point.y() - self.y()
        angle = atan2(offset_y, offset_x)
        return degrees(angle)

    def translate(self, angle, distance):
        '''Translate this instance using angle and distance.'''

        phi = radians(angle)
        self.setX(self.x() + cos(phi) * distance)
        self.setY(self.y() + sin(phi) * distance)

    def translate_offsets(self, off_x, off_y):
        '''Translate this instance using x and y offsets.'''

        self.setX(self.x() + off_x)
        self.setY(self.y() + off_y)

    def distance(self, other_point):
        '''
        Return the distance between this instance and another Point object.
        '''

        offset_x = other_point.x() - self.x()
        offset_y = other_point.y() - self.y()
        return sqrt(offset_x ** 2 + offset_y ** 2)

    def rotate(self, angle, reference):
        '''Rotate this instance around an input reference Point object.'''

        phi = radians(angle)
        offset_x = self.x() - reference.x()
        offset_y = self.y() - reference.y()
        self.setX(offset_x * cos(phi) - offset_y * sin(phi) + reference.x())
        self.setY(offset_x * sin(phi) + offset_y * cos(phi) + reference.y())


class Line(object):
    '''
    A class to provide methods for working with lists of Point objects.
    '''

    def __init__(self, points):
        self.points = points

    def angle(self, other_line):
        '''
        Calculate the angle between this line and 'other_line'.

        Inputs:

            other_line - A Line instance

        Returns:

            The angle between this line and 'other_line', measured in degrees counter-clockwise from east.
        '''

        sl1 = self.slope()
        sl2 = other_line.slope()
        if sl1 is None or sl2 is None:
            if sl1 is None:
                slope = sl2
            if sl2 is None:
                slope = sl1
            try:
                phi = atan(abs(1 / slope))
            except ZeroDivisionError:
                phi = pi / 2
        elif sl1 == 0 or sl2 == 0:
            if sl1 == 0:
                slope = sl2
            elif sl2 == 0:
                slope = sl1
            phi = atan(abs(slope))
        else:
            if sl1 > sl2:
                slope1 = sl2
                slope2 = sl1
            else:
                slope1 = sl1
                slope2 = sl2
            phi = atan((slope2 - slope1) / (1 + slope1 * slope2))
        return degrees(phi)

    def translate(self, angle, distance):
        '''Translate this instance using angle and distance.'''


        for point in self.points:
            point.translate(angle, distance)

    def translate_offsets(self, off_x, off_y):
        '''Translate this instance using x and y offsets.'''
        for point in self.points:
            point.translate_offsets(off_x, off_y)

    def slope(self):
        '''Return the slope of this line.'''

        first = self.points[0]
        last = self.points[-1]
        delta_x = last.x() - first.x()
        delta_y = last.y() - first.y()
        try:
            slope = delta_y / delta_x
        except ZeroDivisionError:
            slope = None
        return slope

    def length(self):
        '''Return the length of this line.'''

        total_length = 0
        for index in range(len(self.points) - 1):
            first = self.points[index]
            last = self.points[index+1]
            total_length += first.distance(last)
        return total_length

    def center_point(self):
        '''Return a Point in the center of the line.'''

        dist = self.length() / 2
        return self.point_on_line(dist)

    def first_point(self):
        '''Return the first Point of this line.'''

        return self.points[0]

    def last_point(self):
        '''Return the last Point of this line.'''

        return self.points[-1]

    def point_on_line(self, distance):
        '''Return a Point along the line.'''

        if distance > self.length():
            distance = self.length()
        current = 0
        i = 0
        while i < (len(self.points) - 1):
            first = self.points[i]
            last = self.points[i+1]
            if current + first.distance(last) > distance:
                break
            current += first.distance(last)
            i += 1
        remaining_dist = abs(distance - current)
        if remaining_dist > 0:
            angle = first.angle(last)
            the_point = Point(first.x(), first.y())
            the_point.translate(angle, remaining_dist)
        else:
            the_point = Point(last.x(), last.y())
        return the_point


    def rotate(self, angle, reference=None):
        '''Rotate the line around input reference point.'''

        if reference is None:
            reference = self.points[0]
        for point in self.points:
            point.rotate(angle, reference)

    def to_geometry(self):
        '''Return this line as a QgsGeometry instance.'''

        return QgsGeometry.fromPolyline(self.points)

    def __repr__(self):
        return '%s' % [point for point in self.points]
        

class VertexMarker(QgsVertexMarker):
    '''
    A class to provide aditional functionality to the QgsVertexMarker class.
    '''

    point = Point(0, 0)
    _xpos = point.x()
    _ypos = point.y()

    def get_x(self):
        '''Get the current x coordinate.'''

        self._xpos = self.point.x()
        return self._xpos

    def set_x(self, x):
        '''Set the current x coordinate.'''

        self.point.setX(x)
        self._update()

    x = property(get_x, set_x)

    def get_y(self):
        '''Get the current y coordinate.'''

        self._ypos = self.point.y()
        return self._ypos

    def set_y(self, y):
        '''Set the current y coordinate.'''

        self.point.setY(y)
        self._update()

    y = property(get_y, set_y)
        
    def __init__(self, map_canvas, point=None):
        super(VertexMarker, self).__init__(map_canvas)
        self.canvas = map_canvas
        if point is None:
            self.point = Point(0, 0)
        else:
            self.point = point
        self._update()

    def translate(self, angle, distance):
        '''Translate this instance with a given angle and distance.'''

        self.point.translate(angle, distance)
        self._update()

    def rotate(self, angle, reference):
        '''
        Rotate at an angle, according to a reference object.

        Inputs:

            angle - Angle measured in degrees counter-clockwise from east.

            reference - Any object that has x() and y() methods.
        '''

        self.point.rotate(angle, reference)
        self._update()

    def to_point(self):
        '''Return a Point object from this instance.'''

        return self.point

    def _update(self):
        '''Update the instance\'s coordinates.'''

        self.setCenter(self.point)
        #self.canvas.refresh()

    def __repr__(self):
        return '%s %s' % (self.__class__.__name__, self.point)

