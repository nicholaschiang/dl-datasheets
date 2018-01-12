#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def split_val_condition(input_string):
    """
    Split and return a {'value': v, 'condition': c} dict for the value and the condition.
    Condition is empty if no condition was found.

    @param input    A string of the form XXX @ YYYY
    """
    try:
        (value, condition) = [x.strip() for x in input_string.split('@')]
        return {'value': value, 'condition': condition}
    except ValueError:
        # no condition was found
        return {'value': input_string.strip(), 'condition': None}


def transistor_part_normalizer(part):
    # Part number normalization
    return part.replace(' ', '').upper()


def opamp_part_normalizer(part):
    # TODO: Digikey actually has weird formatting on their part numbers,
    #       which will require more normalization than we had to do with
    #       transistors.
    return part.replace(' ', '').upper()


def gain_bandwidth_normalizer(gbp):
    """
    Normalize the gain bandwidth product into kHz.
    """
    parse = split_val_condition(gbp)

    # NOTE: We currently ignore the conditions

    # Process Units
    try:
        (value, unit) = parse['value'].split(" ")
        gain = float(value)
        if unit == "MHz":
            gain = gain * 1000
        elif unit == "kHz":
            # already kHz
            pass
        return str(abs(round(gain, 1)))

    except:
        print("[ERROR]: " + str(parse))
        sys.exit(1)


def supply_current_normalizer(supply_current):
    """
    Normalize input quiescent supply current to uA
    """
    # NOTE: Currently ignoring the conditions.
    parse = split_val_condition(supply_current)

    # Process Units
    try:
        (value, unit) = parse['value'].split(" ")
        value = float(value)
        if unit == "mA":
            value = value * 1000
        elif unit == "nA":
            value = value / 1000
        return str(abs(round(value, 1)))
    except:
        print("[ERROR]: " + str(parse))
        sys.exit(1)


def opamp_voltage_normalizer(supply_voltage):
    """
    Normalize supply voltage into absolute values (remove +/-)
    """
    parse = split_val_condition(supply_voltage)

    try:
        if parse['value'].startswith("± "):
            parse['value'] = parse['value'].replace("± ", "±")
        (value, unit) = parse['value'].split(" ")
    except:
        print("[ERROR]: " + str(parse))
        sys.exit(1)

    if unit != "V":
        import pdb
        pdb.set_trace()

    # Process +/- removal.
    # '±18 V' = '\xc2\xb118 V'
    if value.startswith("±"):
        value = value.replace("±", "")
        value = float(value)
        value = value * 2
    else:
        value = float(value)

    return str(abs(round(value, 1)))


def temperature_normalizer(temperature):
    try:
        (temp, unit) = temperature.rsplit(' ', 1)
        return int(temp)
    except:
        print "Incorrect Temperature Value"


def polarity_normalizer(polarity):
    try:
        if(polarity in ["NPN", "PNP"]):
            return polarity
    except:
        print "Incorrect Polarity Value"


def dissipation_normalizer(dissipation):
    if(dissipation[0] == " "):
        dissipation = dissipation[1:]
    return str(abs(round(float(dissipation.split(" ")[0]), 1)))


def current_normalizer(current):
    if(current[0] == " "):
        current = current[1:]
    return str(abs(round(float(current.split(" ")[0]), 1)))


def voltage_normalizer(voltage):
    voltage = voltage.replace("K", "000")
    voltage = voltage.replace("k", "000")
    return voltage.split(" ")[0].replace("-", "")


def gain_normalizer(gain):
    gain = gain.split('@')[0]
    gain = gain.strip()
    gain = gain.replace(",", "")
    gain = gain.replace("K", "000")
    gain = gain.replace("k", "000")
    return str(abs(round(float(gain.split(" ")[0]), 1)))


def old_dev_gain_normalizer(gain):
    return str(abs(round(float(gain), 1)))
