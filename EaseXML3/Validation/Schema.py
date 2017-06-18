# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


from EaseXML3 import *

__all__ = [ 'Schema', 'AttributeGroup', 'Attribute', 'Element', 'ComplexType',
            'SimpleType', 'Group', 'Sequence', 'Choice', 'Enumeration' ]

class Schema(XMLObject):
    # _namespace = "http://www.w3.org/1999/XMLSchema"
    elements = ListNode('Element')
    attributeGroups = ListNode('AttributeGroup', optional=True)

class AttributeGroup(XMLObject):
    name = StringAttribute(optional=True)
    ref = StringAttribute(optional=True)
    attributes = ListNode('Attribute')

class Attribute(XMLObject):
    name = StringAttribute()
    type = StringAttribute(optional=True)
    use = StringAttribute()
    value = StringAttribute(optional=True)
    simpleType = ItemNode('SimpleType',optional=True)

class Element(XMLObject):
    name = StringAttribute(optional=True)
    type = StringAttribute(optional=True)
    ref = StringAttribute(optional = True)
    minOccurs = IntegerAttribute(optional=True)
    maxOccurs = StringAttribute(optional=True)
    complexType = ItemNode('ComplexType',optional=True)
    simpleType = ItemNode('SimpleType',optional=True)

class ComplexType(XMLObject):
    content = StringAttribute(optional=True)
    group = ItemNode('Group',optional=True)
    choice = ItemNode('Choice',optional=True)
    attributes = ListNode('Attribute',optional=True)
    attributeGroups = ListNode('AttributeGroup', optional=True)

class SimpleType(XMLObject):
    ref = StringAttribute(optional=True)
    base = StringAttribute(optional=True)
    enumerations = ListNode('Enumeration',optional=True)

class Group(XMLObject):
    sequence = ItemNode('Sequence', optional=True)
    choice = ItemNode('Choice', optional=True)

class Sequence(XMLObject):
    elements = ListNode('Element')
    group = ItemNode('Group',optional=True)
    choice = ItemNode('Choice',optional=True)

class Choice(XMLObject):
    elements = ListNode('Element')

class Enumeration(XMLObject):
    value = StringAttribute()

if __name__ == '__main__':
    import sys

    fname = sys.argv[-1]
    f = open(fname)
    lines = f.read()
    f.close()

    schema = Schema.fromXml(lines)
    result = schema.toXml(tabLength=4)

    f = open('result.xml','w')
    f.write(result)
    f.close()
