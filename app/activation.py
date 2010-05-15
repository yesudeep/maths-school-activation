#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Activation/deinstallation routines.
# Copyright (c) 2009 happychickoo.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# The original source code for some of these routines was written in Pascal
# in 2005 and in 2009 translated to Python by another developer before we touched it.
# We did not receive any source location information from the client or the previous
# developer about where to locate this code in the actual software, but after
# some hunting we nailed it down to the `Source Dec08/m2/Source/ActUnit.pas' file.
# All the source files with the same name in multiple project source directories
# seem to be the same so it appears these projects use the same activation procedure.
#
# Most of the original code is badly written and does not contain any form of 
# commentary.  As a result deciphering the meanings takes more time than usual.

from random import randint
from functools import partial
from datetime import datetime


dec = partial(int, base=10)


# Original code:
# --------------
# The behavior observed is as follows:
# 
# In [8]: Pad('asd', 4, '*')
# Out[8]: '*asd'
#
# In [9]: Pad('asd', 10, '*')
# Out[9]: '*******asd'
#
# In [10]: Pad('asd192387129387123123', 10, '*')
# Out[10]: 'asd192387129387123123'
#
# def Pad(s, width, PadCh):
#    while len(s) < width:
#        s = PadCh + s
#    return s
#
# The original code contains no comments, so we are assuming
# the function left-pads the string `s' with the `PadCh' character until it
# reaches the length `width' and only pads if the string length doesn't
# already exceed `width'.

# Cleaned up.
def left_pad(string, minimum_length, padding_character):
    """
    Left pads the string to stretch it to the required length with the specified 
    padding character only if the string length is shorter than the required length.
    
    Args:
        string  
            String to pad
        minimum_length  
            The required length of the string if padded.  If the length 
            of the string exceeds the required length, it is returned as is.
        padding_character
            The character to pad the string with.
    """
    while len(string) < minimum_length:
        string = padding_character + string
    return string


# Original code:
# --------------
#
# def PadVal(i, width, PadCh):
#    return Pad(unicode(i),width,PadCh)
#
def left_pad_integer(integer, minimum_length, padding_character=u'0'):
    """
    Returns a string representation of the specified integer padded on the left
    with the specified padding character to stretch to `length'.
    
    Args:
        integer     
            Integer number to pad
        minimum_length      
            Minimum length.
        padding_character
            The character to pad the string with. Default is u'0'.
    """
    return left_pad(unicode(integer), minimum_length, padding_character)


def zero_prefix_integer(integer, minimum_length):
    """
    Returns a string representation of the specified integer padded on the left
    with zeros to stretch to the required minimum length.
    
    Args:
        integer
            Integer number to pad
        minimum_length
            Minimum length
    """
    return left_pad_integer(integer, minimum_length, u'0')


# Original code:
# --------------
# def randomNumericString(len):
# # Returns a string of len random digits. }
#     result = u'';
#     while len > 0:
#         result = result + chr(ord(u'0')+randint(0,9))
#         len -=1
#     return result
# Assuming this does return a random numeric string of length `len'

# Cleaned up.
def range_of_digits(length=1):
    """
    Returns a range of start and end numbers that restrict the length to
    `length' digits.

    Args:
        length  
            Optional number of digits required in any number in returned range. 
            Default set to 1 and will return the range (0, 9).
    """
    if length <= 0:
        return (0, 0)
    elif length == 1:
        return (0, 9)  # Special case: include 0 in single digits.
    else:
        return (10**(length-1), 10**length - 1)


def random_numeric_string(length):
    """
    Return a string of random numeric digits of a specified length.
    
    Args:
        length
            Length of the required numeric string.
    """
    random_integer = randint(*range_of_digits(length))
    return unicode(random_integer)

# Original code:
# --------------
#
# Usage:  dcode = deactivationEntryCode(unicode(date.today())
#         *assuming* the server is located in Australia.  
#         This fuckwit doesn't do date time programming.
#
#def deactivationEntryCode(date):
#    # returns a 5 digit string from the date string in
#    # d[0]d[1]/m[0]m[1]/y[0]y[1]y[2]y[3] format
#    # as follows:
#    # y[3]d[0]m[1]d[1]y[0]
#    # e.g. 26/12/2006->62262, 01/01/2007->70112
#    # converted to handle strings in form yyyy-mm-dd on 13/06/09
#    if type(date) != str:
#        exit
#    if len(date) != 10:
#        exit
#    res = date[3]+date[8]+date[6]+date[9]+date[0]
#    return res

def get_now_for_timezone(timezone='UTC'):
    """
    Returns the current datetime for the given timezone.
    
    Args:
        timezone
            Timezone as from the list of 
            `from pytz import all_timezones'
             
    """
    from pytz.gae import pytz
    tz = pytz.timezone(timezone)
    date = tz.fromutc(datetime.utcnow())
    return date


def generate_deactivation_entry_code(date=None, timezone='UTC'):
    """
    The deactivation entry code is generated according to the following format.
    
        year[last-digit] day[first-digit] month[second-digit] day[second-digit] year[first-digit]

    where the
        year has 4 digits (e.g., 1992)
        month has 2 digits (01-12)
        day has 2 digits (01-31)
    
    Or in programming terms:
    
        year[3] day[0] month[1] day[1] year[0]
    
    This means that for a year ending in 0, e.g. 2010, all codes during that year
    will start with 0.  Therefore, the entry code cannot be an integer.  This function,
    therefore, returns a string.
    
    Args:
        date
            Optional date which will be used to generate the code.
            If not specified and the timezone is also not specified,
            the current UTC date is used.  Otherwise, the current date
            in the specified timezone is used.
        timezone
            Timezone as from the list of 
            `from pytz import all_timezones'
            
    """
    if date is None:
        if timezone == 'UTC':
            date = datetime.utcnow()
        else:
            date = get_now_for_timezone(timezone)
    year = unicode(date.year)
    month = '%02d' % date.month
    day = '%02d' % date.day
    string_code = year[3] + day[0] + month[1] + day[1] + year[0]
    return string_code


# Original code:
# --------------
# def sisACode(compId, serialNum, useGivenABase, givenABase):
#    n1 = int(compId[2:5])
#    n2 = int(serialNum[4:7])
#    n3 = (n1 +n2) % 1000
#    if useGivenABase:          # -- Doesn't Python have optional arguments? A wtf moment.
#        aBase = givenABase
#    else:
#        aBase = randint(0,999)
#    a = PadVal(aBase,3,u'0')
#    s = PadVal(aBase + n3,4,u'0')
#    m1 = int(compId[0:2])      
#    m2 = int(compId[5:7])      # -- int guesses at the base if not specified. 
#    m3 = int(serialNum[0:3])   # -- I'm pretty sure this guy wanted decimal.
#    m4 = int(serialNum[3:7])
#    ms = PadVal((m1*m2 + m3 + m4) % 1000,3,u'0')
#    return ms + s[2] + a[0] + a[1] + s[3] + a[2] + s[1] + s[0]

# Cleaned up.
def calculate_activation_code(machine_id, serial_number, a_base=None):
    """
    Calculates and returns an activation code for the given machine ID and
    serial number combination.
    
    Warning:
        The routine assumes the machine_id and serial_number are 7 digit 
        integers.  It will bomb if they aren't.
    
    Args:
        machine_id
            String representing the machine ID.  Original code calls it
            compId or CompId.  We're just sticking to terms we have used
            in our data models to avoid any further confusion.
        serial_number
            String representing the serial number.
        a_base
            Optional integer used to test the routine.
        
    Notes:
        The machine ID is a 7 digit number divided into three parts as in the 
        following figure:
        
            mm mmm mm
            B  A   C

        The serial number is another 7 digit number divided and regrouped as follows:
                
            nnn n nnn
            B     A
            
            nnn nnnn
            B   C
        
        in order of appearance.
        
        So let
        
        machine_id_a = dec(machine_id[2:5])
        machine_id_b = dec(machine_id[0:2])
        machine_id_c = dec(machine_id[5:7])
        
        and
        
        serial_number_a = dec(serial_number[4:7])
        serial_number_b = dec(serial_number[0:3])
        serial_number_c = dec(serial_number[3:7])
        
    """
    n1 = dec(machine_id[2:5])
    n2 = dec(serial_number[4:7])

    n3 = (n1 + n2) % 1000

    if a_base is None:
        a_base = randint(0, 999)

    a = zero_prefix_integer(a_base, minimum_length = 3)
    s = zero_prefix_integer(a_base + n3, minimum_length = 4)

    m1 = dec(machine_id[0:2])
    m2 = dec(machine_id[5:7])

    m3 = dec(serial_number[0:3])
    m4 = dec(serial_number[3:7])

    ms = zero_prefix_integer(((m1 * m2) + m3 + m4) % 1000, minimum_length = 3)

    return ms + s[2] + a[0] + a[1] + s[3] + a[2] + s[1] + s[0]
