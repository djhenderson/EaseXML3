# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

from __future__ import print_function

import sys
sys.path.append('..')

from EaseXML3 import *

class HTML(Namespace):
    uri = 'http://www.w3.org/TR/REC-html40'


class Reservation(XMLObject):
    _name = 'RESERVATION'
    name = ItemNode('Name')
    seat = ItemNode('Seat')
    a = ItemNode('A')
    departure = TextNode(name='DEPARTURE')

class Name(XMLObject):
    _name = 'NAME'
    klass = StringAttribute(name='CLASS')
    mainNode = TextNode()

class Seat(XMLObject):
    _name = 'SEAT'
    klass = StringAttribute(name='CLASS')
    mainNode = TextNode()

class A(XMLObject):
    href = StringAttribute(name='HREF')
    mainNode = TextNode()

r = Reservation()

r.name = Name(mainNode='Layman, A',HTML_klass='largeSansSerif')
print(r.name.HTML_klass)
#r.ns.name.klass[HTML] =
#r.name.klass[HTML] =

r.seat = Seat(klass='Y', mainNode='33B')
#r.seat.klass[HTML] = 'largeMonotype'
#r.ns.seat.klass[HTML] = 'largeMonotype'

#r.ns[HTML].append(A(href='/cgi-bin/ResStatus',mainNode="Check Status"))

r.departure = '1997-05-24T07:55:00+1'
print(r)

"""
<RESERVATION xmlns:HTML="http://www.w3.org/TR/REC-html40">
   <NAME HTML:CLASS="largeSansSerif">
     Layman, A
   </NAME>
   <SEAT CLASS="Y" HTML:CLASS="largeMonotype">
     33B
   </SEAT>
   <HTML:A HREF='/cgi-bin/ResStatus'>
     Check Status
   </HTML:A>
   <DEPARTURE>
     1997-05-24T07:55:00+1
   </DEPARTURE>
</RESERVATION>
"""
