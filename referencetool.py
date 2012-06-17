#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Script's doctring goes here.
"""

import base

_reference = None

def get_reference(canvas):
    if _reference is None:
        reference = Reference(canvas)
        _reference = Reference
    else:
        reference = _reference
    return reference


class Reference(object):
    point = base.Point(0, 0)
    canvas_elements = dict()
    
    def __init__(self, canvas, point=None):
        self.canvas = canvas
        if point is not None:
            self.point = point
        marker = base.VertexMarker(self.canvas, self.point)
        marker.hide()
        self.canvas_elements = {'marker' : marker}

    def update(self, point):
        self.point = point
        self._update_marker()

    def _update_marker(self):
        self.canvas_elements['marker'].x = self.point.x()
        self.canvas_elements['marker'].y = self.point.y()
