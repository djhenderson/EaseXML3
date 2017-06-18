# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


import classregistry, utils
from Node import Node, RequiredNodeError
from types import StringType, UnicodeType

__all__ = [ 'CDATAttribute', 'NMTokenAttribute', 'NMTokensAttribute',
            'IntegerAttribute', 'StringAttribute' ]

class Attribute(Node):
    """ Base Class for Attributes

        This should not be directly used. It's only a general class
        used by the 'real' attribute implementations.
    """

    def __init__(self, default=None, permittedValues=None, optional=False, name=''):
        if optional:
            default = None
        # set noLimit to False for all attributes.
        # This isn't negociable :) Why would you want multiple
        # attributes of the same name in one XML element ?
        Node.__init__(self, noLimit = False, default=default, optional=optional, name=name)
        self.permittedValues = permittedValues

    def checkType(self, val):
        result = val
        if self.permittedValues is not None and val not in self.permittedValues:
            result = False
        return result

    def xmlrepr(self, parentInstance=None):
        val = self.getValue()
        if self.isOptional() and val == self.getDefaultValue():
            result = ''
        elif val is not None:
            result = '%s="%s"' % (self.getName(),val)
        else:
            result = ''
        result = utils.customUnicode(result, parentInstance._encoding)
        return result

class CDATAttribute(Attribute):

    def checkType(self, val):
        result = False
        if self.isOptional() and val in (None,self.getDefaultValue()):
            result = val
        elif type(val) in [StringType, UnicodeType] and Attribute.checkType(self, val):
            result = val
        return result


    def getValueFromDom(self, dom, attrName, **kw):
        xmlAttrNode = dom.getAttributeNode(attrName)
        try:
            value = xmlAttrNode.value
        except AttributeError:
            if not self.isOptional():
                raise RequiredNodeError(self.getName())
            else:
                value = self.getDefaultValue()
        if value is not None and kw['stripStrings']:
            value = value.strip()
        return value

class NMTokenAttribute(CDATAttribute):

    _valids = [':','_','-','.']

    def checkType(self, val):
        result = CDATAttribute.checkType(self,val)
        if result is not False and val not in (None,self.getDefaultValue()):
            tmpVal = val or ''
            for car in self._valids:
                tmpVal = tmpVal.replace(car,'')
            if not tmpVal.isalnum():
                result = False
        return result


class NMTokensAttribute(NMTokenAttribute):

    _valids = NMTokenAttribute._valids + [' ', '\t', '\r\n', '\n']

class StringAttribute(CDATAttribute):
    """
        Suppose you have an XMLObject type like this one:

        ::

          class FooBar(XMLObject):
              glop = StringAttribute()

        FooBar(glop="Hey Yah").toXml() would output:

        ::

          <fooBar glop="Hey Yah" />

    """

    def xmlrepr(self, parentInstance=None):
        val = self.getValue()
        if self.isOptional() and val == self.getDefaultValue():
            result = ''
        elif val is not None:
            val = utils.replaceAll(val, parentInstance.getEntities())
            result = '%s="%s"' % (self.getName(),val)
        else:
            result = ''
        result = utils.customUnicode(result, parentInstance._encoding)
        return result

class IntegerAttribute(CDATAttribute):
    """

    """

    def __init__(self, default=None, permittedValues=None, optional=False):
        CDATAttribute.__init__(self, permittedValues=permittedValues,
                               default=default, optional=optional)

    def getValueFromDom(self, dom, attrName, **kw):
        val = CDATAttribute.getValueFromDom(self, dom,attrName, **kw)
        if val:
            val = int(val)
        return val

    def checkType(self, val):
        result = False
        if self.isOptional() and val is None:
            result = val
        elif type(val) == type(0):
            result = Attribute.checkType(self, val)
            if result is not False:
                result = val
        return result
##         result = False
##         if self.isOptional() and val is None:
##             result = val
##         elif type(val) == type(0) and Attribute.checkType(self, val):
##             result = val
##         return result
