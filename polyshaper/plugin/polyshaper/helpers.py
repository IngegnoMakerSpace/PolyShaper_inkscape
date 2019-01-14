#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Helper functions and classes
"""

from itertools import count, izip # pylint: disable=no-name-in-module
import math
import os
import re
from errors import InvalidCuttingPath, PolyshaperIOError # pylint: disable=import-error,no-name-in-module
import inkex # pylint: disable=import-error

def base_filename(basename, path):
    """ Returns the full path and filename of a file to write

    This function appends to basename three digits to make sure files are not
    overwritten. No extension is added.
    :param basename: the base name of the file to generate
    :type basename: string
    :param path: the path where to save the file
    :type path: string
    :return: the name of the file where to write the g-code, WITHOUT THE DIRECTORY
    :rtype: string
    """

    # Filtering files in target dir
    all_files = os.listdir(path)
    reg_expr = re.escape(basename) + "-(\\d{3}).(gcode|psj|svg)"
    filtered = [f for f in all_files if re.match(reg_expr, f)]
    filtered.sort()

    # Getting the highest sequence number
    sequence_number = 0
    if filtered:
        match = re.match(reg_expr, filtered[-1])
        sequence_number = int(match.group(1)) + 1

    return basename + "-{:03}".format(sequence_number)

def write_file(filename, write_func):
    """ Writes the gcode to file

    In case of errors, throws an exception of typePolyshaperIOError
    :param filename: the full path to the file in which gcode is written
    :type filename: string
    :param write_func: a function taking a file in input and that writes data
    :type write_func: a function with one input parameter (a file object)
    """

    try:
        outfile = open(filename, "w")
        try:
            write_func(outfile)
        except IOError:
            raise PolyshaperIOError(filename,
                                    _("Error when trying to write file, it might be corrupted"))
        finally:
            outfile.close()
    except IOError:
        raise PolyshaperIOError(filename, _("Error when trying to open file"))

def squared_length(vector):
    """ Computes the squared length of a 2D vector

    This is more efficient than length in case only length comparisons are needed
    :param vector: the vector whose length is needed
    :type vector: a 2-tuple or a list with 2 elements, both floats
    :return: the length of the vector
    :rtype: float greater or equal to 0
    """

    return vector[0]**2 + vector[1]**2

def length(vector):
    """ Computes the length of a 2D vector

    :param vector: the vector whose length is needed
    :type vector: a 2-tuple or a list with 2 elements, both floats
    :return: the length of the vector
    :rtype: float greater or equal to 0
    """

    return math.sqrt(squared_length(vector))

def squared_distance(point1, point2):
    """ Computes the squared distance between point1 and point2

    This is more efficient than distance in case only length comparisons are needed
    :param point1: The first point
    :type point1: a 2-tuple or a list with 2 elements, both floats
    :param point2: The second point
    :type point2: a 2-tuple or a list with 2 elements, both floats
    :return: the squared distance between the two points
    :rtype: float
    """

    vector = [point1[0] - point2[0], point1[1] - point2[1]]
    return squared_length(vector)

def distance(point1, point2):
    """ Computes the distance between point1 and point2

    :param point1: The first point
    :type point1: a 2-tuple or a list with 2 elements, both floats
    :param point2: The second point
    :type point2: a 2-tuple or a list with 2 elements, both floats
    :return: the distance between the two points
    :rtype: float
    """

    vector = [point1[0] - point2[0], point1[1] - point2[1]]
    return length(vector)

def verify_path_closed(path, close_distance):
    """ Verifies that the given 2D path is closed

    If the path is not closed, an exception is thrown
    :param path: the path to test
    :type path: a list of points (couples of floats)
    :param close_distance: the max allowed distance between the initial and final point
    :type close_distance: float
    """

    if path and (len(path) > 1) and (distance(path[0], path[-1]) > close_distance):
        raise InvalidCuttingPath(_("path is not closed"))

def point_path_squared_distance(point, path):
    """ Computes the distance between a point and a path

    The distance between a point and a path is the distance between the point in the path that
    is nearer to the point. The function returns the squared distance (for efficency) and the
    index of the nearest point in the path
    :param point: a 2D point
    :type point: a couple of floats
    :param path: a 2D path (must not be empty)
    :type path: a list of points (couples of floats)
    :return: the squared distance and the index of the point in the path nearest to point
    :rtype: a couple (squared distance, point index). Squared distance is a float, point index
        is an int
    """

    nearest_index = 0
    nearest_distance = squared_distance(point, path[0])
    for (idx, path_point) in izip(count(1), path[1:]):
        dist = squared_distance(point, path_point)
        if dist < nearest_distance:
            nearest_index = idx
            nearest_distance = dist

    return (nearest_distance, nearest_index)

def rotate_closed_path(path, new_start):
    """ Given a closed path, returns a new path with the starting point at new_start

    This function assumes that the path is closed (i.e. that the first and last point are the same)
    :param path: the 2D path to rotate. This must be closed
    :type path: a list of points (couples of floats)
    :param new_start: the index of the new starting point
    :type new_start: an index (int)
    """

    new_path = []

    if not path:
        return new_path

    # If closest point is the first or the last, we can return the input path as it is
    if (new_start == 0) or (new_start >= len(path) - 1):
        return path

    # From start_point to end
    new_path += path[new_start:]
    # From beginning to start_point (skip the first, re-add start_point to close path)
    new_path += path[1:(new_start + 1)]

    return new_path


def invert_transform(mat):
    """ Returns the inverse of the provided 2D 2x3 transformation matrix

    The code is taken from the simpletransform.invertTransform function in inkscape 0.92 and has
    been coipied here to support inkscape 0.91
    :param mat: the transformation matrixto invert
    :type mat: a 2x3 matrix of floats, i.e. [[a11,a12,a13],[a21,a22,a23]] with aij float
    :return: the inverted matrix
    :rtype: a 2x3 matrix of floats, i.e. [[a11,a12,a13],[a21,a22,a23]] with aij float
    """

    det = mat[0][0]*mat[1][1] - mat[0][1]*mat[1][0]
    result = []
    if det != 0:  # det is 0 only in case of 0 scaling
        # invert the rotation/scaling part
        a11 = mat[1][1]/det
        a12 = -mat[0][1]/det
        a21 = -mat[1][0]/det
        a22 = mat[0][0]/det
        # invert the translational part
        a13 = -(a11*mat[0][2] + a12*mat[1][2])
        a23 = -(a21*mat[0][2] + a22*mat[1][2])
        result = [[a11, a12, a13], [a21, a22, a23]]
    else:
        result = [[0, 0, -mat[0][2]], [0, 0, -mat[1][2]]]

    return result


def generate_path_svg(painter):
    """
    Creates ans svg xml document with the given path

    :param painter: the path painter
    :type painter: an instance of ToolPathPainter
    :return: an SVG document with the path
    :rtype: an xml document
    """

    base_doc = inkex.etree.XML('''\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg">
</svg>''')

    doc = inkex.etree.ElementTree(base_doc)

    painter.paint(doc.getroot(), 1.0, "0,0,0")

    return doc
