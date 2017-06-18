#! python
# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

from __future__ import print_function

import sys
sys.path.insert(0, '..')

from EaseXML3 import *

class AnotherFoo(XMLObject):
    xslt = ProcessingInstructionNode('xml-stylesheet',
                                     [ (u'type',u'text/css'),
                                       (u'href',u'http://foobar.com/style.css')
                                       ])
    blah = TextNode(optional=True)

af = AnotherFoo()
print(af.toXml())

"""
<?xml version="1.0" encoding="utf-8" ?>
<?xml-stylesheet type="text/css" href="http://foobar.com/style.css" ?>
<AnotherFoo/>
"""
