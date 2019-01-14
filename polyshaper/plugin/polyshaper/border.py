#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Border-related classes and functions
"""

from inkex import etree # pylint: disable=import-error


class Border(object):
    """ The class modelling the border of a 2D piece to cut

    This is built adding a margin around the axis-aligned bounding box of the paths to cut. If no
    path is present or if all paths are empty, all values are set to 0. Note that "bottom" is the
    part near to the x axis: in inkscape the upper part (y axis goes from top to bottom)
    """

    def __init__(self, paths, margin):
        """ Constructor

        :param paths: the list of paths
        :type paths: a list of lists of couples of floats (mm)
        :param margin: the internal margin
        :type margin: float (mm)
        """

        def join_aabb(first, second):
            """ Returns the aabb resulting from the union of the two aabbs

            :param first: the first aabb
            :type first: a 4-tuple of floats: (xmin, xmax, ymin, ymax)
            :param second: the second aabb
            :type second: a 4-tuple of floats: (xmin, xmax, ymin, ymax)
            :return: the aabb resulting from the union of first and second
            :rtype: a 4-tuple of floats: (xmin, xmax, ymin, ymax)
            """

            return (min(first[0], second[0]),
                    max(first[1], second[1]),
                    min(first[2], second[2]),
                    max(first[3], second[3]))

        def find_aabb_of_path(path):
            """ Returns the aabb of a path

            :param path: a path
            :type path: a list of couples of floats (mm)
            :return: the aabb of the path
            :rtype: a 4-tuple of floats: (xmin, xmax, ymin, ymax)
            """

            (first_x, first_y) = path[0]
            aabb = (first_x, first_x, first_y, first_y)

            for (x, y) in path[1:]: # pylint: disable=invalid-name
                aabb = join_aabb(aabb, (x, x, y, y))

            return aabb

        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0

        aabb = None

        for path in paths:
            if path:
                if aabb:
                    aabb = join_aabb(aabb, find_aabb_of_path(path))
                else:
                    aabb = find_aabb_of_path(path)

        if aabb:
            self.x_min = aabb[0] - margin
            self.x_max = aabb[1] + margin
            self.y_min = aabb[2] - margin
            self.y_max = aabb[3] + margin

    def width(self):
        """ Returns the width of the border

        :return: the width of the border
        :rtype: float (mm)
        """

        return self.x_max - self.x_min

    def height(self):
        """ Returns the height of the border

        :return: the height of the border
        :rtype: float (mm)
        """

        return self.y_max - self.y_min


    def left(self):
        """ Returns the left side of the border

        :return: the left side of the border
        :rtype: float (mm)
        """

        return self.x_min

    def right(self):
        """ Returns the right side of the border

        :return: the right side of the border
        :rtype: float (mm)
        """

        return self.x_max

    def top(self):
        """ Returns the top side of the border

        :return: the top side of the border
        :rtype: float (mm)
        """

        return self.y_max

    def bottom(self):
        """ Returns the bottom side of the border

        :return: the bottom side of the border
        :rtype: float (mm)
        """

        return self.y_min

    def bottom_left(self):
        """ Returns the bottom left vertex of the border

        :return: the bottom left vertex of the border
        :rtype: couple of floats (mm)
        """

        return (self.x_min, self.y_min)

    def bottom_right(self):
        """ Returns the bottom right vertex of the border

        :return: the bottom right vertex of the border
        :rtype: couple of floats (mm)
        """

        return (self.x_max, self.y_min)

    def top_right(self):
        """ Returns the top right vertex of the border

        :return: the top right verted of the border
        :rtype: couple of float (mm)
        """

        return (self.x_max, self.y_max)

    def top_left(self):
        """ Returns the top left vertex of the border

        :return: the top left vertex of the border
        :rtype: couple of floats (mm)
        """

        return (self.x_min, self.y_max)


class BorderPainter(object):
    """ The class drawing the dorder on the svg
    """

    def __init__(self, border):
        """ Constructor

        :param border: the border to draw
        :type border: an instance of the Border class
        """

        self.border = border
        self.working_area = None

    def paint(self, working_area):
        """ Draws the border in the working area

        :param working_area: the working area where the path is to be drawn
        :type working_area: an instance of the WirkingAreaGenerator
        """

        self.working_area = working_area

        if self.border_is_to_be_drawn():
            border_x = self.working_area.get_factor() * self.border.left()
            border_y = self.working_area.get_factor() * self.border.bottom()
            border_width = self.working_area.get_factor() * self.border.width()
            border_height = self.working_area.get_factor() * self.border.height()
            line_width = self.working_area.get_factor() * 0.25
            etree.SubElement(self.working_area.get_element(), "rect", {
                'x': str(border_x),
                'y': str(border_y),
                'width': str(border_width),
                'height': str(border_height),
                'style': ("stroke-width:{0};stroke-miterlimit:4;stroke-dasharray:0.25,0.25;"
                          "stroke-dashoffset:0;fill:none").format(line_width)})

    def border_is_to_be_drawn(self):
        """ Returns true if border has to be drawn

        :return: true if border has to be drawn
        :rtype: boolean
        """

        return self.border and (
            self.border.left() != 0 or
            self.border.right() != self.working_area.get_dim_x() or
            self.border.top() != self.working_area.get_dim_y() or
            self.border.bottom() != 0
        )
