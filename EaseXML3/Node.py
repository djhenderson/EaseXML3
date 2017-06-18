# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


import copy

class RequiredNodeError(Exception):
    """ A node is required.

        Exception raised when EaseXML3 could not find a non-optional
        Node in XML data.
    """

    def __init__(self, name,xmlData=''):
        Exception.__init__(self)
        self._xml = xmlData
        self._msg = "'%s' node is not optional" % name
        if self._xml:
            self._msg += " in \n%s" % self._xml

    def __str__(self):
        return self._msg

class Node(object):
    """ This is the base class for XMLObject's content. Each node has:

        - a ``type`` (string)
        - an ``itemType`` (string) : used by ListNode so that it remembers
          what kind of items it has to store.
        - a ``default`` value
        - a ``optional`` boolean switch
        - a ``noLimit`` boolean switch
        - a ``main`` boolean switch indicating wether the Node is main One of the XMLObject

        For each of these properties, there are getters and setters.

        * `xmlrepr` is the method responsible of giving a string representing
          the node. User defined nodes should override it.
        * `getValueFromDom` is used to build a Node given its DOM tree.
        * `checkType` is responsible for node type checking during assignment.
          It returns True when assignment is legitim, False either.
    """

    def __init__(self, main=False, itemType='', default=None, optional=False,
                 noLimit=False, name=''):
        self.setType(self.__class__.__name__)
        self.setItemType(itemType)
        self.setDefaultValue(default)
        self.setValue(default)
        self.setName(name)
        self.setOptional(optional)
        self.setNoLimit(noLimit)
        self.setMain(main)

    def setNoLimit(self, val):
        self._noLimit = val

    def isNoLimit(self):
        return self._noLimit

    def setMain(self, m):
        self._main = m

    def isMain(self):
        return self._main

    def setOptional(self, val):
        self._optional = val

    def isOptional(self):
        return self._optional

    def setItemType(self, type):
        self._itemType = type

    def getItemType(self):
        return self._itemType

    def setName(self, name):
        self._nodeName = name

    def getName(self):
        return self._nodeName

    def setValue(self, value):
        self._value = value

    def getValue(self):
        return self._value

    def setDefaultValue(self, default):
        self._defaultValue = default

    def getDefaultValue(self):
        return self._defaultValue

    def setType(self, type):
        self._type = type

    def getType(self):
        return self._type

    def getParentType(self):
        return self._parentType

    def setParentType(self, parentType):
        self._parentType = parentType

    def xmlrepr(self, parentInstance=None):
        """ XML representation of the Node

            Returns a string representing the Node as XML data.
        """
        return ''

    def getValueFromDom(self, dom, attrName, **kw):
        return None

    def checkType(self, val):
        """ Type checking.

            `val` is object to check. If `checkType` returns False, a
            TypeError is raised to claim that Node value assignment is
            not valid. Either, `checkType` should return an optionally
            modified version of `val` (usefull when dealing with lists
            assignements where items should be XMLObject instances).
        """
        return val

    def resetValue(self):
        self.setValue(self.getDefaultValue())

    def setRegistry(self, reg):
        self._registry = reg

    def getRegistry(self):
        return self._registry

class ProcessingInstructionNode(Node):
    """ Processing Instruction.

        Example:

        ::

           class AnotherFoo(XMLObject):
               _orderNodes = ['xslt', 'blah']
               xslt = ProcessingInstructionNode('style-sheet',
                                                [('url','http://foobar.com/style.xsl'),
                                                 ])
               blah = TextNode(optional=True)

           af = AnotherFoo()

        NB: This Node is not defined in Nodes module to prevent from
            recursive import between main and Nodes modules.
    """

    def __init__(self, name, data, **kw):
        kw['default'] = data
        Node.__init__(self, **kw)
        self.name = name

    def xmlrepr(self, parentInstance=None):
        result = u'<?%s' % self.name
        values = u''
        for key, val in self.getValue():
            values += u'%s="%s" ' % (key,val)
        if len(values):
            result += u' ' + values
        result += u'?>'
        return result
