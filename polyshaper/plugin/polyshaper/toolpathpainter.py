#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper tool path drawing
"""

import inkex # pylint: disable=import-error

class ToolPathPainter(object):
    """ Draws the path of the tool

    The path is drawn in the svg element provided in the paint function
    """

    def __init__(self, path):
        """ Constructor

        :param path: the path to draw
        :type path: a list of (x, y) coordinates
        """

        self.path = path
        self.factor = None

    def paint(self, parent_element, factor, rgb_color):
        """ Generates the path inside the provided svg element

        :param parent_element: the parent element of the path
        :type parent_element: an svg element
        :param factor: the scaling factor for coordinates
        :type factor: float
        :param rgb_color: the color of the path
        :type rgb_color: a string with format "R,G,B" where all elements are between 0 and 255
        """

        self.factor = factor
        if self.path:
            inkex.etree.SubElement(parent_element, "path", {
                'd': self.transform_path(),
                'style': "stroke:rgb(" + rgb_color + ");fill:none"
            })

    def transform_path(self):
        """ Transforms the path into an SVG path string

        self.path must have at least one element
        :return: an SVG path
        :rtype: string
        """

        def convert_point(point):
            """ Converts a 2D point to working area coordinates and then to string
            """

            svg_x = point[0] * self.factor
            svg_y = point[1] * self.factor

            return "{0},{1}".format(svg_x, svg_y)

        # First point is (0, 0): it is not in the path but the tool is supposed to start from there
        str_path = "M {0} L".format(convert_point((0.0, 0.0)))
        for point in self.path:
            str_path += " {0}".format(convert_point(point))

        return str_path
