#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper working area drawing
"""

import inkex # pylint: disable=import-error
import simpletransform # pylint: disable=import-error
from helpers import invert_transform # pylint: disable=import-error,no-name-in-module

class WorkingAreaGenerator(object):
    """ Generates the visual working area, as an svg element

    The element has id eu.polyshaper.inkscape.workarea, so that it can be modified if already
    existing. All dimensions must be in millimeters
    """

    def __init__(self, to_uu, working_area_id):
        """ Constructor

        :param to_uu: the function converting millimiters to user units
        :type to_uu: a function from float to float
        :param working_area_id: the id of the group of the working area
        :type working_area_id: string
        """
        self.area = None
        self.factor = None
        self.view_box_height = None
        self.dim_x = 200.0
        self.dim_y = 200.0
        self.to_uu = to_uu
        self.working_area_id = working_area_id

    def set_size(self, dim_x, dim_y):
        """ Sets the size of the working area

        :param dim_x: the x dimension of the working area
        :type dim_x: float (millimeters)
        :param dim_y: the y dimension of the working area
        :type dim_y: float (millimeters)
        """
        self.dim_x = dim_x
        self.dim_y = dim_y

    def draw(self, transform):
        """ Draws the working area

        :param transform: the transform to apply to points
        :type transform: a 2x3 matrix
        """

        # Using a viewBox so that we can express all measures relative to it. We compute the
        # view box height when the width is 100 to keep the aspect ratio. We also compute the stroke
        # width so that it is 0.5 millimiters
        self.factor = 100.0 / self.dim_x
        self.view_box_height = self.factor * self.dim_y
        line_width = self.factor * 0.5

        # inverting transformation, we know absolute coordinates
        inv_transform = invert_transform(transform)
        # tranforming the position of the box
        box_origin = [0, 0]
        simpletransform.applyTransformToPoint(inv_transform, box_origin)
        # transforming lengths (ignoring translation)
        box_dims = [self.dim_x, self.dim_y]
        length_inv_transform = [
            [inv_transform[0][0], inv_transform[0][1], 0.0],
            [inv_transform[1][0], inv_transform[1][1], 0.0]
        ]
        simpletransform.applyTransformToPoint(length_inv_transform, box_dims)

        self.area = inkex.etree.Element("svg", {
            'id': self.working_area_id,
            'x': str(self.to_uu(box_origin[0])),
            'y': str(self.to_uu(box_origin[1])),
            'width': str(self.to_uu(box_dims[0])),
            'height': str(self.to_uu(box_dims[1])),
            'viewBox': "0 0 100 " + str(self.view_box_height),
            'preserveAspectRatio': "none",
            'style': "fill:none;stroke-width:{0};stroke:rgb(0,0,0)".format(line_width)})

        self.draw_rectangle()
        self.draw_cross()
        self.draw_text()

    def draw_rectangle(self):
        """ Draws the rectangle
        """
        inkex.etree.SubElement(self.area, "rect", {
            'x': "0",
            'y': "0",
            'width': "100",
            'height': str(self.view_box_height)})

    def draw_cross(self):
        """ Draws the cross

        We want the cross to be 20mm x 20mm
        """
        cross_size = self.factor * 20
        cross_half_size = cross_size / 2
        cross_starth = -cross_half_size
        cross_endh = cross_half_size
        cross_startv = -cross_half_size
        cross_endv = cross_half_size
        inkex.etree.SubElement(self.area, "path", {
            'd': "M {starth},0 L {endh},0 M 0,{startv} L 0,{endv}"
                 .format(starth=cross_starth, endh=cross_endh,
                         startv=cross_startv, endv=cross_endv)})

    def draw_text(self):
        """ Draws text

        Text is (0, 0). We need to compute the font size so that it corresponds to 1cm and also the
        text width and height (it is approximately 28mm x 10mm)
        """
        text_size = self.factor * 10
        text_width = self.factor * 28
        text_height = self.factor * 10
        text = inkex.etree.SubElement(self.area, "text", {
            'x': str(-text_width),
            'y': str(-text_height),
            'font-family': "Verdana",
            'font-size': str(text_size)})
        text.text = "(0, 0)"

    def upsert(self, document_root):
        """ Adds the working area in the given layer

        If the layer already contains a working area, updates that one
        :param document_root: the document root, to which the working area is added
        :type document_root: svg element (an lxml.etree.Element object)
        """

        if self.area is None:
            transform = simpletransform.parseTransform(document_root.get("transform"))
            self.draw(transform)

        # If the group already exists, removes it before adding again
        old_working_area_elements = document_root.xpath("*[@id = \"" + self.working_area_id + "\"]")
        for old in old_working_area_elements:
            old.getparent().remove(old)

        document_root.append(self.area)

    def get_element(self):
        """ Returns the element containing the working area

        :return: the element containing the working area or None if upsert hasn't been called yet
        :rtype: and svg element
        """

        return self.area

    def get_dim_x(self):
        """ Returns the x dimension of the working area

        :return: the x dimension of the working area
        :rtype: float (mm)
        """

        return self.dim_x

    def get_dim_y(self):
        """ Returns the y dimension of the working area

        :return: the y dimension of the working area
        :rtype: float (mm)
        """

        return self.dim_y

    def get_factor(self):
        """ Returns the scaling factor for distances inside the viewbox

        :return: the scaling factor for distances inside the viewbox
        :rtype: float
        """

        return self.factor
