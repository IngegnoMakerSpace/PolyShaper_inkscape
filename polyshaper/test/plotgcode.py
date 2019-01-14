#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

"""
A script to plot the content of a 2D gcode file

This requires python3 and matplotlib
"""

import argparse
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

def create_cmdline_parser():
    """ Creates and returns the commanline parser
    """

    parser = argparse.ArgumentParser(description="Plots a 2D G-Code file")

    parser.add_argument("filename", metavar="FILENAME", action="store", type=str,
                        help="The G-Code file to plot")
    parser.add_argument("-a", "--animate", action="store_true", help="Animates plot")
    parser.add_argument("-i", "--interval", action="store", type=int, default=100,
                        help="The interval between frames of animation in milliseconds")

    return parser


def update_plot(num, line, data_x, data_y):
    """ The function used by FuncAnimation to animate the plot
    """

    line.set_data(data_x[:num], data_y[:num])

    # This is the same as [line]
    return line,


def main():
    """ The main function of the script
    """
    args = create_cmdline_parser().parse_args()

    gcode_file = open(args.filename, "r")

    x = [0.0] # pylint: disable=invalid-name
    y = [0.0] # pylint: disable=invalid-name
    for line in gcode_file:
        fields = line.split()
        if fields[0] == "G01" and len(fields) > 2:
            x.append(float(fields[1][1:]))
            y.append(float(fields[2][1:]))

    if args.animate:
        figure = pyplot.figure()
        line, = pyplot.plot([], [])
        gcode_ani = animation.FuncAnimation(figure, update_plot, len(x), fargs=(line, x, y), # pylint: disable=unused-variable
                                            interval=args.interval, blit=True)
    else:
        pyplot.plot(x, y)

    pyplot.xlim(min(x) - 1, max(x) + 1)
    pyplot.ylim(min(y) - 1, max(y) + 1)
    pyplot.title(args.filename)
    pyplot.show()


if __name__ == '__main__':
    main()
