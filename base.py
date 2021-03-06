#!/usr/bin/env python
#-*- coding: utf-8 -*-

from math import pi, atan, atan2, cos, sin, radians, degrees, sqrt

from qgis.core import QgsPoint, QgsGeometry
from qgis.gui import QgsVertexMarker

class Point(QgsPoint):

    @staticmethod
    def from_feature(feature):
        pt = feature.geometry().asPoint()
        p = Point(pt.x(), pt.y())
        return p

    def angle(self, other_point):
        '''Return the angle between this point and other_point'''

        dx = other_point.x() - self.x()
        dy = other_point.y() - self.y()
        angle = atan2(dy, dx)
        return degrees(angle)

    def translate(self, angle, distance):
        phi = radians(angle)
        self.setX(self.x() + cos(phi) * distance)
        self.setY(self.y() + sin(phi) * distance)

    def translate_offsets(self, off_x, off_y):
        self.setX(self.x() + off_x)
        self.setY(self.y() + off_y)

    def distance(self, other_point):
        dx = other_point.x() - self.x()
        dy = other_point.y() - self.y()
        return sqrt(dx ** 2 + dy ** 2)

    def rotate(self, angle, reference):
        phi = radians(angle)
        dx = self.x() - reference.x()
        dy = self.y() - reference.y()
        self.setX(dx * cos(phi) - dy * sin(phi) + reference.x())
        self.setY(dx * sin(phi) + dy * cos(phi) + reference.y())


class Line(object):

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

        s1 = self.slope()
        s2 = other_line.slope()
        if s1 is None or s2 is None:
            if s1 is None:
                m = s2
            if s2 is None:
                m = s1
            try:
                phi = atan(abs(1 / m))
            except ZeroDivisionError:
                phi = pi / 2
        elif s1 == 0 or s2 == 0:
            if s1 == 0:
                m = s2
            elif s2 == 0:
                m = s1
            phi = atan(abs(m))
        else:
            if s1 > s2:
                m1 = s2
                m2 = s1
            else:
                m1 = s1
                m2 = s2
            phi = atan((m2 - m1) / (1 + m1 * m2))
        return degrees(phi)

    def translate(self, angle, distance):
        phi = radians(angle)
        for p in self.points:
            p.translate(angle, distance)

    def translate_offsets(self, off_x, off_y):
        for p in self.points:
            p.translate_offsets(off_x, off_y)

    def slope(self):
        '''Return the slope of this line.'''
        first = self.points[0]
        last = self.points[-1]
        x = last.x() - first.x()
        y = last.y() - first.y()
        try:
            slope = y / x
        except ZeroDivisionError:
            slope = None
        return slope

    def length(self):
        '''Return the length of this line.'''
        total_length = 0
        for p in range(len(self.points) - 1):
            first = self.points[p]
            last = self.points[p+1]
            total_length += first.distance(last)
        return total_length

    def center_point(self):
        '''Return a Point in the center of the line.'''

        dist = self.length() / 2
        return self.point_on_line(dist)

    def first_point(self):
        return self.points[0]

    def last_point(self):
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
        for p in self.points:
            p.rotate(angle, reference)

    def to_geometry(self):
        '''Return this line as a QgsGeometry instance.'''
        g = QgsGeometry.fromPolyline(self.points)
        return g

    def __repr__(self):
        return '%s' % [p for p in self.points]
        

class VertexMarker(QgsVertexMarker):
    point = Point(0, 0)

    @property
    def x(self):
        return self.point.x()

    @x.setter
    def x(self, x):
        self.point.setX(x)
        self._update()

    @property
    def y(self):
        return self.point.y()

    @y.setter
    def y(self, y):
        self.point.setY(y)
        self._update()
        
    def __init__(self, map_canvas, point=None):
        super(VertexMarker, self).__init__(map_canvas)
        self.canvas = map_canvas
        if point is None:
            self.point = Point(0, 0)
        else:
            self.point = point
        self._update()

    def translate(self, angle, distance):
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
        return self.point

    def _update(self):
        self.setCenter(self.point)
        #self.canvas.refresh()

    def __repr__(self):
        return '%s %s' % (self.__class__.__name__, self.point)

