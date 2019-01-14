#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper path statistics
"""

from datetime import datetime
import math
from polyshaper.helpers import distance # pylint: disable=import-error,no-name-in-module

class PathInfo(object):
    """ The class to generate various path statisics

    It checks whether the path is inside the workpiece or not and estimates the working time
    """

    def __init__(self, path, options, base_filename):
        """ Constructor

        :param path: the tool path
        :type path: a list of couples of floats
        :param options: the options, as received by the script on the commandline
        :type options: an object with options
        :param base_filename: the name files to generate without any extension
        :type base_filename: string
        """

        self.path = path
        self.options = options
        self.base_filename = base_filename

        self.path_inside_workpiece = None
        self.working_time = None # in seconds, float number

    def is_path_inside_workpiece(self):
        """ Returns true if the path is inside the workpiece

        :return: true if the path is inside the workpiece
        :rtype: boolean
        """

        if self.path_inside_workpiece is None:
            self.path_inside_workpiece = True

            for (point_x, point_y) in self.path:
                if point_y > self.options.dim_y or point_y < 0 or\
                   point_x > self.options.dim_x or point_x < 0:
                    self.path_inside_workpiece = False

        return self.path_inside_workpiece

    def working_time_min(self):
        """ Returns the estimated working time in integer minutes

        :return: the estimated working time in minutes
        :rtype: int (minutes)
        """

        return int(math.ceil(self._working_time_sec() / 60.0))

    def gcode_filename(self):
        """ Returns the gcode filename

        :return: the gcode filename
        :rtype: string
        """

        return self.base_filename + ".gcode"

    def svg_filename(self):
        """ Returns the svg filename

        :return: the svg filename
        :rtype: string
        """

        return self.base_filename + ".svg"

    def metainfo_filename(self):
        """ Returns the metainfo filename

        :return: the metainfo filename
        :rtype: string
        """

        return self.base_filename + ".psj"

    def _working_time_sec(self):
        if self.working_time is None:
            self.working_time = 0

            if self.options.speed != 0:
                length = 0
                if self.path:
                    prev_point = self.path[0]
                    for point in self.path[1:]:
                        length += distance(prev_point, point)
                        prev_point = point

                self.working_time = length / self.options.speed * 60.0

        return self.working_time

    def metainfo(self):
        """ Returns meta-information about the path as a dict

        :return: meta-information about the path
        :rtype: a dict with string keys
        """

        return {
            "version": 1,
            "name": self.options.shapename,
            "generatedBy": "2DPlugin",
            "gcodeFilename": self.gcode_filename(),
            "svgFilename": self.svg_filename(),
            "duration": int(math.ceil(self._working_time_sec())),
            "creationTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "pointsInsideWorkpiece": self.is_path_inside_workpiece(),
            "workpieceDimX": self.options.dim_x,
            "workpieceDimY": self.options.dim_y,
            "speed": self.options.speed,
            "flatness": self.options.flatness,
            "square": self.options.square,
            "margin": self.options.margin,
            "machineType": self.options.machine_type,
            "drawToolpath": self.options.draw_toolpath,
            "autoClosePath": self.options.auto_close_path
        }
