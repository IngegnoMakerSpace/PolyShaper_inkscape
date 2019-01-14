#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper machines definitions
"""

def machine_factory(name):
    """ Returns an instance of the Machine class given a machine name

    :param name: the name of the machine to return
    :type name: string
    :return: the object modelling the machine or None if no machine with the given name exists
    :type: instance of Machine
    """

    if name == "P400":
        return P400()
    elif name == "PolyShaperAzul":
        return PolyShaperAzul()
    elif name == "PolyShaperAzul+":
        return PolyShaperAzulPlus()
    elif name == "PolyShaperGrænt":
        return PolyShaperGraent()
    elif name == "PolyShaperOranje":
        return PolyShaperOranje()
    elif name == "MakerWelt":
        return MakerWelt()

    return None


class Machine(object):
    """ The class modelling a Polyshaper machine

    This is "abstract" a blueprint to model actual classes below
    """

    def __init__(self):
        """ Constructor

        This is here to prevent instantiation
        """
        raise NotImplementedError("Cannot instantiate Machine, use one of the children classes")

    def name(self):
        """ Returns the name of the machine

        This is abstract
        """
        raise NotImplementedError("Method 'name' not implemented!")

    def working_area_width(self):
        """ Returns the width of the working area

        This is abstract
        """
        raise NotImplementedError("Method 'working_area_width' not implemented!")

    def working_area_height(self):
        """ Returns the height of the working area

        This is abstract
        """
        raise NotImplementedError("Method 'working_area_height' not implemented!")

    def piece_dimensions_allowed(self, width, height):
        """ Returns true if the piece fits in the machine

        :param width: the width of the piece
        :type width: float (mm)
        :param height: the height of the piece
        :type height: float (mm)
        :return: true if the piece fits the machine, false otherwise
        :rtype: boolean
        """

        return width <= self.working_area_width() and height <= self.working_area_height()

class MakerWelt(Machine):
    """ The class modelling the P400
    """

    def __init__(self): # pylint: disable=super-init-not-called
        """ Constructor
        """
        pass

    def name(self):
        """ Returns the name of the machine

        :return: the name of the machine
        :rtype: string
        """
        return "MakerWelt"

    def working_area_width(self):
        """ Returns the width of the working area

        :return: the width of the working area
        :rtype: float (mm)
        """
        return 1200

    def working_area_height(self):
        """ Returns the height of the working area

        :return: the height of the working area
        :rtype: float (mm)
        """
        return 800

class P400(Machine):
    """ The class modelling the P400
    """

    def __init__(self): # pylint: disable=super-init-not-called
        """ Constructor
        """
        pass

    def name(self):
        """ Returns the name of the machine

        :return: the name of the machine
        :rtype: string
        """
        return "P400"

    def working_area_width(self):
        """ Returns the width of the working area

        :return: the width of the working area
        :rtype: float (mm)
        """
        return 400

    def working_area_height(self):
        """ Returns the height of the working area

        :return: the height of the working area
        :rtype: float (mm)
        """
        return 400


class PolyShaperAzul(Machine):
    """ The class modelling the PolyShaper Azul
    """

    def __init__(self): # pylint: disable=super-init-not-called
        """ Constructor
        """
        pass

    def name(self):
        """ Returns the name of the machine

        :return: the name of the machine
        :rtype: string
        """
        return "PolyShaper Azul"

    def working_area_width(self):
        """ Returns the width of the working area

        :return: the width of the working area
        :rtype: float (mm)
        """
        return 1000

    def working_area_height(self):
        """ Returns the height of the working area

        :return: the height of the working area
        :rtype: float (mm)
        """
        return 500


class PolyShaperAzulPlus(Machine):
    """ The class modelling the PolyShaper Azul+
    """

    def __init__(self): # pylint: disable=super-init-not-called
        """ Constructor
        """
        pass

    def name(self):
        """ Returns the name of the machine

        :return: the name of the machine
        :rtype: string
        """
        return "PolyShaper Azul+"

    def working_area_width(self):
        """ Returns the width of the working area

        :return: the width of the working area
        :rtype: float (mm)
        """
        return 1200

    def working_area_height(self):
        """ Returns the height of the working area

        :return: the height of the working area
        :rtype: float (mm)
        """
        return 600


class PolyShaperGraent(Machine):
    """ The class modelling the PolyShaper Graent
    """

    def __init__(self): # pylint: disable=super-init-not-called
        """ Constructor
        """

    def name(self):
        """ Returns the name of the machine

        :return: the name of the machine
        :rtype: string
        """
        return "PolyShaper Grænt"

    def working_area_width(self):
        """ Returns the width of the working area

        :return: the width of the working area
        :rtype: float (mm)
        """
        return 1100

    def working_area_height(self):
        """ Returns the height of the working area

        :return: the height of the working area
        :rtype: float (mm)
        """
        return 1100


class PolyShaperOranje(Machine):
    """ The class modelling the PolyShaper Oranje
    """

    def __init__(self): # pylint: disable=super-init-not-called
        """ Constructor
        """

    def name(self):
        """ Returns the name of the machine

        :return: the name of the machine
        :rtype: string
        """
        return "PolyShaper Oranje"

    def working_area_width(self):
        """ Returns the width of the working area

        :return: the width of the working area
        :rtype: float (mm)
        """
        return 500

    def working_area_height(self):
        """ Returns the height of the working area

        :return: the height of the working area
        :rtype: float (mm)
        """
        return 500
