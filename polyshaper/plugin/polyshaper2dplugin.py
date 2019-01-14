#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper plugin for cutting machine (2 axes)
"""

import json
import os.path

import inkex # pylint: disable=import-error
from polyshaper.errors import InvalidWorkpieceDimensions, PolyshaperError # pylint: disable=import-error,no-name-in-module
from polyshaper.gcode import CuttingGCodeGenerator # pylint: disable=import-error,no-name-in-module
from polyshaper.machine import machine_factory # pylint: disable=import-error,no-name-in-module
from polyshaper.pathsextraction import FlattenBezier, PathsExtractor # pylint: disable=import-error,no-name-in-module
from polyshaper.pathinfo import PathInfo # pylint: disable=import-error,no-name-in-module
from polyshaper.pathsunion import PathsJoiner # pylint: disable=import-error,no-name-in-module
from polyshaper.toolpathpainter import ToolPathPainter # pylint: disable=import-error,no-name-in-module
from polyshaper.toolpaths import CuttingToolPathsGenerator # pylint: disable=import-error,no-name-in-module
from polyshaper.workingarea import WorkingAreaGenerator # pylint: disable=import-error,no-name-in-module
from polyshaper.helpers import base_filename, write_file, generate_path_svg # pylint: disable=import-error,no-name-in-module
from polyshaper.border import Border, BorderPainter # pylint: disable=import-error,no-name-in-module

####################################################################################################
# List of hardwired parameters
####################################################################################################

# The id of the working area element in the svg
WORKING_AREA_ID = "eu.polyshaper.inkscape.workarea"

# If two points are less than this value apart, they are considered conincident. This is measured in
# millimeters (used to check if a path is closed)
CLOSE_DISTANCE = 0.5

####################################################################################################

inkex.localize()


class Polyshaper2D(inkex.Effect):
    """ The main class of the plugin
    """

    def __init__(self):
        """ Constructor
        """

        # Initializing the superclass
        inkex.Effect.__init__(self)

        # More initializations
        # This is the height of the document in millimeters
        self.doc_height = 0
        # The path where the output file is written, created if not existing
        self.gcode_file_path = os.path.join(os.path.expanduser("~"), "PolyShaper")
        if not os.path.isdir(self.gcode_file_path):
            os.mkdir(self.gcode_file_path, 0755)

        self.define_command_line_options()

    def define_command_line_options(self):
        """ Defines the commandline options accepted by the script
        """

        self.OptionParser.add_option("-n", "--shapename", action="store", type="string",
                                     dest="shapename", default="my shape",
                                     help=("Shape name and basename of the generated files (will "
                                           "be saved on ~/PolyShaper"))
        self.OptionParser.add_option("-x", "--dim-x", action="store", type="float", dest="dim_x",
                                     default=200.0, help="Workpiece X dimension in mm")
        self.OptionParser.add_option("-y", "--dim-y", action="store", type="float", dest="dim_y",
                                     default=200.0, help="Workpiece Y dimension in mm")
        self.OptionParser.add_option("-s", "--speed", action="store", type="float",
                                     dest="speed", default=500.0, help="Cutting speed in mm/min")
        self.OptionParser.add_option("-b", "--flatness", action="store", type="float",
                                     dest="flatness", default=0.1,
                                     help="Flatness (for bezier curves)")
        self.OptionParser.add_option("-c", "--square", action="store", type="inkbool",
                                     dest="square", default=False,
                                     help="Cut along margin at the end")
        self.OptionParser.add_option("-m", "--margin", action="store", type="float",
                                     dest="margin", default="0.0", help=("Margin around path in"
                                                                         "mm"))
        self.OptionParser.add_option("-t", "--type", action="store", type="string",
                                     dest="machine_type", default="P400", help=("The machine type"))
        self.OptionParser.add_option("-p", "--draw-toolpath", action="store", type="inkbool",
                                     dest="draw_toolpath", default=True,
                                     help="Draws the path of the tool")
        self.OptionParser.add_option("-a", "--auto-close-path", action="store", type="inkbool",
                                     dest="auto_close_path", default=True,
                                     help=("Automatically close open paths by joining start with "
                                           "end"))

        # This is here so we can have tabs - but we do not use it for the moment.
        # Remember to use a legitimate default
        self.OptionParser.add_option("", "--active-tab", action="store", type="string",
                                     dest="active_tab", default='setup', help="Active tab.")

    def effect(self):
        """ Main function
        """

        # First of all generating the machine instance and checking piece dimensions fit
        machine = machine_factory(self.options.machine_type)
        if machine:
            valid_dimensions = machine.piece_dimensions_allowed(self.options.dim_x,
                                                                self.options.dim_y)
            if not valid_dimensions:
                raise InvalidWorkpieceDimensions(machine.working_area_width(),
                                                 machine.working_area_height())

        # A function to convert to millimiters
        to_mm = lambda value: self.uutounit(value, 'mm')
        # A function to convert to user units. This must be used to write units in the svg
        to_uu = lambda value: self.unittouu(str(value) + "mm")

        # Draw the working area
        working_area_generator = WorkingAreaGenerator(to_uu, WORKING_AREA_ID)
        working_area_generator.set_size(self.options.dim_x, self.options.dim_y)
        working_area_generator.upsert(self.document.getroot())

        if not self.options.ids:
            # print info and exit
            inkex.debug(_(("No path was seletect, only the working area was generated. Now draw a "
                           "path inside the working area and select it to generate the g-code")))
        else:
            # Extracting paths in machine coordinates
            paths_extractor = PathsExtractor(self.selected.values(), to_mm, WORKING_AREA_ID,
                                             FlattenBezier(self.options.flatness),
                                             self.options.auto_close_path)
            paths_extractor.extract()

            # The border to use. This is None if no border is requested. If border is present, also
            # draws it
            border = None
            if self.options.square:
                border = Border(paths_extractor.paths(), self.options.margin)
                painter = BorderPainter(border)
                painter.paint(working_area_generator)

            # Joining paths. This will also check that all paths are closed
            paths_joiner = PathsJoiner(paths_extractor.paths(), CLOSE_DISTANCE)
            paths_joiner.unite()

            # Generate tool positions
            tool_path_generator = CuttingToolPathsGenerator(paths_joiner.union_path(),
                                                            CLOSE_DISTANCE, border)
            tool_path_generator.generate()

            # The object drawing the tool path
            painter = ToolPathPainter(tool_path_generator.path())

            # Draw tool path on original svg if requested
            if self.options.draw_toolpath:
                painter.paint(working_area_generator.get_element(),
                              working_area_generator.get_factor(), "255,0,0")

            # Generating g-code
            gcode_generator = CuttingGCodeGenerator(tool_path_generator.path(), self.options.speed)
            gcode_generator.generate()

            # Computing information about path
            generic_filename = base_filename(self.options.shapename, self.gcode_file_path)
            info = PathInfo(tool_path_generator.path(), self.options, generic_filename)

            # Writing gcode to file
            write_file(os.path.join(self.gcode_file_path, info.gcode_filename()),
                       lambda f: f.write(gcode_generator.gcode()))

            # Writing svg to file
            doc = generate_path_svg(painter)
            write_file(os.path.join(self.gcode_file_path, info.svg_filename()),
                       lambda f: doc.write(f))

            # Writing metainfo to file
            write_file(os.path.join(self.gcode_file_path, info.metainfo_filename()),
                       lambda f: f.write(json.dumps(info.metainfo(), indent=2)))

            message = (_("The generate g-code has been saved to ") + info.gcode_filename() +
                       _(". Estimated working time: ") + str(info.working_time_min()) +
                       _(" minutes"))
            if not info.is_path_inside_workpiece():
                message += _(". WARNING: some points are outside the workpiece")

            inkex.debug(message)


if __name__ == '__main__':
    try:
        e = Polyshaper2D() # pylint: disable=invalid-name
        e.affect()
    except PolyshaperError as error:
        inkex.errormsg(error.to_string())
        exit(error.exit_code())
