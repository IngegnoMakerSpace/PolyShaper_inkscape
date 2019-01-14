#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper plugin for engraving (4 axes machine)
"""

import math
import os.path

import inkex # pylint: disable=import-error
from polyshaper.errors import PolyshaperError # pylint: disable=import-error,no-name-in-module
from polyshaper.gcode import EngravingGCodeGenerator # pylint: disable=import-error,no-name-in-module
from polyshaper.pathsextraction import FlattenBezier, PathsExtractor # pylint: disable=import-error,no-name-in-module
from polyshaper.toolpaths import EngravingToolPathsGenerator # pylint: disable=import-error,no-name-in-module
from polyshaper.workingarea import WorkingAreaGenerator # pylint: disable=import-error,no-name-in-module
from polyshaper.helpers import base_filename, write_file # pylint: disable=import-error,no-name-in-module

####################################################################################################
# List of hardwired parameters
####################################################################################################

# Tool rotation is performed by the E (extrusion) axis of a 3D printer. This is
# the number of degrees for each millimiter of extrusion (needed to compute the
# command to send to the printer)
MM_PER_DEGREE = 18.0

# The id of the working area element in the svg
WORKING_AREA_ID = "eu.polyshaper.inkscape.workarea"

# If two points are less than this value apart, they are considere conincident. This is measured in
# millimeters
MIN_DISTANCE = 0.01

# Safe value for Z (to use when finished working)
SAFE_Z = 10.0

# The distance below which linear movement and tool movement is performed together (see
# GCodeGenerator class description, the value is in millimeters)
SMALL_DISTANCE = 5

# The angular displacement below which linear movement and tool movement is performed together (see
# GCodeGenerator class description, the value is in radiants)
SMALL_ANGLE = math.radians(189.0)

# The discretization step for the path. If not infinite, a tool path will be made up of segments
# that are at most this long. Set to float('inf') (the python for infinity) to disable
# discretization
DISCRETIZATION_STEP = 2

# The maximum length of a segment in discretized beziers and arcs
FLATNESS = 1.0
####################################################################################################

inkex.localize()


class PolyshaperEngraving(inkex.Effect):
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
        # The path where the output file is written
        self.gcode_file_path = os.path.expanduser("~/")

        self.define_command_line_options()

    def define_command_line_options(self):
        """ Defines the commandline options accepted by the script
        """

        self.OptionParser.add_option("-f", "--filename", action="store", type="string",
                                     dest="filename", default="polyshaper",
                                     help=("Basename of the generated G-CODE file (will have .nc "
                                           "extension and will be saved on Desktop"))
        self.OptionParser.add_option("-x", "--dim-x", action="store", type="float", dest="dim_x",
                                     default=200.0, help="Plane X dimension in mm")
        self.OptionParser.add_option("-y", "--dim-y", action="store", type="float", dest="dim_y",
                                     default=200.0, help="Plane Y dimension in mm")
        self.OptionParser.add_option("-z", "--depth-z", action="store", type="float",
                                     dest="depth_z", default=10.0, help="Engraving depth in mm")

        # This is here so we can have tabs - but we do not use it for the moment.
        # Remember to use a legitimate default
        self.OptionParser.add_option("", "--active-tab", action="store", type="string",
                                     dest="active_tab", default='setup', help="Active tab.")

    def effect(self):
        """ Main function
        """

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
            # Using error message even if this it not really an error...
            inkex.debug(_(("No path was seletect, only the working area was generated. Now draw a "
                           "path inside the working area and select it to generate the g-code")))
        else:
            # Extracting paths in machine coordinates
            paths_extractor = PathsExtractor(self.selected.values(), to_mm, WORKING_AREA_ID,
                                             FlattenBezier(FLATNESS))
            paths_extractor.extract()

            # Generate tool positions and orientations
            tool_path_generator = EngravingToolPathsGenerator(paths_extractor.paths(),
                                                              self.options.depth_z, MIN_DISTANCE,
                                                              DISCRETIZATION_STEP)
            tool_path_generator.generate()

            # Generating g-code
            gcode_generator = EngravingGCodeGenerator(tool_path_generator.paths(), MM_PER_DEGREE,
                                                      SAFE_Z, SMALL_DISTANCE, SMALL_ANGLE)
            gcode_generator.generate()

            # Writing to file
            filename = base_filename(self.options.filename, self.gcode_file_path) + ".gcode"
            write_file(filename, lambda f: f.write(gcode_generator.gcode()))

            inkex.debug(_("The generate g-code has been save to ") + filename)


if __name__ == '__main__':
    try:
        e = PolyshaperEngraving() # pylint: disable=invalid-name
        e.affect()
    except PolyshaperError as error:
        inkex.errormsg(error.to_string())
        exit(error.exit_code())
