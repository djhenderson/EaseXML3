# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

from __future__ import print_function

import string, copy

# ProcessingInstructionNode is defined in Node to prevent recursive import between
# main and this module.
from Node import Node, ProcessingInstructionNode, RequiredNodeError
from main import XMLObject
from TypedList import TypedList
from MixedList import MixedList
import classregistry, utils
from types import StringType, UnicodeType

__all__ = [ 'RawNode', 'TextNode', 'ItemNode', 'ChoiceNode',
            'ProcessingInstructionNode',
            'ListNode', 'CommentNode', 'LeftRecursionError' ]

class LeftRecursionError(Exception):

    def __init__(self, msg):
        Exception.__init__(self)
        self._msg = msg

    def __str__(self):
        return self._msg

    __repr__ = __str__


class CommentNode(Node):
    """ Insert comments in the XML object

        CommentNodes are optional by default. May I change this in
        near future :)

        Example:

        ::

          class CommentTator(XMLObject):
              myComment = CommentNode()

          print(CommentTator(myComment='Blah lbah').toXml(headers=0))

          <CommentTator>
             <!-- Blah lbah -->
          </CommentTator>

    """

    def __init__(self, default='', optional=True,main=False):
        Node.__init__(self, optional=optional, main=main,
                      default=default, noLimit=False)

    def xmlrepr(self, parentInstance=None):
        value = self.getValue()
        if value and parentInstance:
            value = utils.replaceAll(value, parentInstance.getEntities())
            if not self.isMain():
                value = "<!-- %s -->" % value
        else:
            value = ''
        value = utils.customUnicode(value, parentInstance._encoding)
        return value

    def getValueFromDom(self, dom, attrName, **kw):
        value = ''
        for node in dom.childNodes:
            if node.nodeType == node.COMMENT_NODE:
                value += node.data
        if kw['stripStrings']:
            value = value.strip()
        if value == '':
            value = None
        return value

class TextNode(Node):
    """ Example class:

        ::

          class Foo(XMLObject):
              text = TextNode()

          f = Foo(text = 'Kind of fun')
          print(f.toXml(headers=False))

        Example XML output:

        ::

          <Foo>
            <text>
               Kind of fun
            </text>
          </Foo>
    """

    def __init__(self, default = None, optional=False,name='',main=False):
        Node.__init__(self, optional=optional, name=name, main=main,
                      default = default, noLimit=False)

    def xmlrepr(self, parentInstance=None):
        value = self.getValue()
        if value is not None and parentInstance:
            value = utils.replaceAll(value, parentInstance.getEntities())
            if not self.isMain():
                value = "<%s>%s</%s>" % (self.getName(), value, self.getName())
        else:
            value = ''
        value = utils.customUnicode(value, parentInstance._encoding)
        return value

    def getValueFromDom(self, dom, attrName, **kw):
        value = None
        candidates = utils.getDirectChildrenWithName(dom,self.getName())
        if len(candidates) == 0:
            candidates = utils.getDirectChildrenWithName(dom,self.getName())
            if len(candidates) == 0:
                if self.isMain():
                    candidates = [dom]
                elif not self.isOptional():
                    raise RequiredNodeError(self.getName(),dom.toxml())
        for candidate in candidates:
            for node in candidate.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    if value is None: value = ''
                    value += node.data
        if value != None and kw['stripStrings']:
            value = value.strip()
        return value

class RawNode(Node):
    """ Example class:

        ::

          class Foo(XMLObject):
              text = RawNode()

          f = Foo(text = 'Kind of fun')
          print(f.toXml(headers=False))

        Example XML output:

        ::

          <Foo>
             <![CDATA[Kind of fun]]>
          </Foo>
    """

    def __init__(self, default = None, optional=False,main=False):
        Node.__init__(self, optional=optional, main=main,
                      default = default, noLimit=False)

    def xmlrepr(self, parentInstance=None):
        value = self.getValue()
        if value is None:
            value = ''
        if value != '':
            value = "<![CDATA[%s]]>" % value
        value = utils.customUnicode(value, parentInstance._encoding)
        return value

    def getValueFromDom(self, dom, attrName, **kw):
        value = ''
        for node in dom.childNodes:
            if node.nodeType == node.CDATA_SECTION_NODE:
                value += node.data
        if kw['stripStrings']:
            value = value.strip()
        if value == '':
            value = None
        return value


class ItemNode(Node):
    """ Class used to refer to an existing XMLObject type.
        Suppose you have an XMLObject type like this one:

        ::

          class FooBar(XMLObject):
              glop = StringAttribute()

        You can then use it in other XMLObjects:

        ::

          class Blah(XMLObject):
              fb = ItemNode('FooBar')

          blah = Blah( fb = FooBar(glop = 'HelloWorld') )

        blah.toXml() would output:

        ::

            <Blah>
                 <FooBar glop="HelloWorld" />
            </Blah>

        ``optional`` keyword specifies wether the Item is mandatory or not.
    """

    def __init__(self, itemType, default=None, optional=False,main=False):
        Node.__init__(self, itemType=itemType, noLimit=False, main=main,
                      optional=optional, default=default)

    def xmlrepr(self, parentInstance=None):
        value = self.getValue()
        if value is not None:
            value = value.toXml(headers=0, prettyPrint=False)
        else:
            value = ''
        value = utils.customUnicode(value, parentInstance._encoding)
        return value

    def getValueFromDom(self, dom, attrName, **kw):
        itemTypeName = self.getItemType()
        parentTypeName = self.getParentType()
        xmlObject = classregistry.registry(kw['registry']).getClass(itemTypeName)()
        parentType = classregistry.registry(kw['registry']).getClass(parentTypeName)
        candidates = utils.getDirectChildrenWithName(dom,xmlObject.getName())
        if len(candidates) == 0 and not self.isOptional():
            raise RequiredNodeError(self.getName())
        value = None
        for candidate in candidates:
            if candidate.parentNode.nodeName == parentType.getName():
                value = xmlObject._fromDom(candidate)
                break
        return value

class ChoiceNode(Node):
    """ Alternative Nodes

        Right recursivity is permitted, but left recursions are (I hope so)
        prohibited. In the following example, ``mix`` can be an ``Item`` or
        a ``Blah`` object:

        ::

          class Item(XMLObject):
              pass

          class Blah(XMLObject):
              mix = ChoiceNode(['Item','Blah'])

        One can also use the special '#PCDATA' alternative:

        ::

          class Blah(XMLObject):
              mix = ChoiceNode(['#PCDATA', 'Item'])

        So ``mix`` can be either a string or an Item instance.
        ``noLimit`` keyword can be set to True when the node has to
        bahave as a List.
        Setting ``optional`` to True, XMLObject won't complain if it's empty.
    """

    def __init__(self, choiceAlternatives, optional=False, noLimit=False,main=False):
        self.alternatives = choiceAlternatives
        default = None
        if noLimit:
            default = MixedList(self)
        Node.__init__(self, itemType=choiceAlternatives,main=main,
                      optional=optional, default=default, noLimit=noLimit)

    def checkForLeftRecursivity(self, xmlObject, nodeName):
        if self.getParentType() == nodeName:
            raise LeftRecursionError('Left recursivity detected in "%s"' % self.getName())
        elif isinstance(xmlObject, XMLObject):
            for child, instance in xmlObject.getNodes().iteritems():
                exc = LeftRecursionError("""\
Left recursivity detected in "%s" through "%s" attribute of "%s" """ %
                                 (self.getName(), child, xmlObject.getName()))
                if instance.getItemType() == self.getParentType():
                    raise exc
                elif instance.getType() == self.getType():
                    if instance.getItemType()[0] == self.getParentType():
                        raise exc

    def resetValue(self):
        if self.isNoLimit():
            self.setValue(MixedList(self))
        else:
            self.setValue(None)

    def setValue(self, value):
        if isinstance(value, ChoiceNode):
            value = copy.deepcopy(value)
        Node.setValue(self, value)

    def checkType(self, val):
        if len(self.alternatives) > 0:
            self.checkForLeftRecursivity(val,self.alternatives[0])
        result = val
        if isinstance(val, MixedList) or type(val) == type([]):
            try:
                result = MixedList(self).checkList(val)
            except:
                result = False
        elif isinstance(val, XMLObject) and val.getClassName() not in self.alternatives:
            result = False
        elif '#PCDATA' not in self.alternatives and type(val) in [StringType, UnicodeType]:
            result = False
        return result

    def xmlrepr(self, parentInstance=None):
        val = self.getValue()
        result = ''
        if val is not None:
            if isinstance(val, MixedList) or type(val) == type([]):
                for node in val:
                    result += str(node)
            elif isinstance(val, parentInstance.__class__):
                result += val.toXml(headers=0, prettyPrint=False)
            else:
                result += str(val)
        result = utils.customUnicode(result, parentInstance._encoding)
        return result

    def getValueFromDom(self, dom, attrName, **kw):
        result = None
        if self.isNoLimit():
            result = MixedList(self)

        for childNode in dom.childNodes:
            for alt in self.alternatives:
                value = None
                if alt == '#PCDATA':
                    if childNode.nodeType == childNode.TEXT_NODE:
                        value = childNode.data
                        if kw['stripStrings']:
                            value = value.strip()
                try:
                    xmlObject = classregistry.registry(kw['registry']).getClass(alt)()
                    if childNode.nodeName == xmlObject.getName():
                        value = xmlObject._fromDom(childNode)
                except KeyError:
                    pass
                if not value:
                    continue
                elif not self.isNoLimit():
                    return value
                else:
                    result.append(value)
        return result


class ListNode(Node):
    """ Single Typed List node

        ListNode is used to represent a variable number of XMLObjects,
        all of the same type. Example:

        ::

          class Apple(XMLObject):
              type =  StringAttribute()
              color = StringAttribute()

          class AppleBag(XMLObject):
              apples = ListNode('Apple')

          bag = AppleBag()
          bag.apples.append(Apple(type='Blah',color='green'))
          print(bag.toXml(headers=0))

          <AppleBag>
            <Apple type="Blah" color="green" />
            <!-- other apples can fit here :) -->
          </AppleBag>

        If ``optional`` flag set to False, the bag has to carry at least
        one apple.
    """

    def __init__(self, itemType, optional=True, main=False):
        Node.__init__(self, itemType=itemType, main=main,
                      optional=optional, noLimit=True,
                      default = TypedList(self))

    def checkType(self, aList):
        result = True
        itemsNb = len(aList)
        if itemsNb > 1 and not self.isNoLimit():
            result = False
        if result:
            try:
                result = TypedList(self).checkList(aList)
            except Exception as ex:
                print(ex)
                result = False
        return result

    def xmlrepr(self, parentInstance=None):
        result = ''
        itemsNb = len(self.getValue())
        registry = classregistry.registry(parentInstance._registry)
        parentClass = registry.getClass(self.getItemType())
        itemTypeName = parentClass.getName()
        if itemsNb < 1 and not self.isOptional():
            raise TypeError("Expected some node in '%s.%s' as it is not optional" %
                            (parentInstance.getName(),self.getName()))
        for node in self.getValue():
            nodeRepr = node.toXml(headers=0, prettyPrint=False)
            if not isinstance(node, parentClass):
                result += "<%s>%s</%s>" % (itemTypeName,nodeRepr,itemTypeName)
            else:
                result += nodeRepr
        result = utils.customUnicode(result, parentInstance._encoding)
        return result

    def resetValue(self):
        self.setValue(TypedList(self))

    def getValueFromDom(self, dom, attrName, **kw):
        xmlList = TypedList(self)
        itemTypeName = self.getItemType()
        parentTypeName = self.getParentType()
        klass = classregistry.registry(kw['registry']).getClass(itemTypeName)
        parentType = classregistry.registry(kw['registry']).getClass(parentTypeName)
        candidates = utils.getDirectChildrenWithName(dom,klass.getName())
        if len(candidates) == 0:
            candidates = utils.getDirectChildrenWithName(dom,klass.getClassName())
        if len(candidates) == 0 and (not self.isOptional()):
            raise RequiredNodeError(self.getName(),dom.toxml())
        for xmlNode in candidates:
            if xmlNode.parentNode.nodeName == parentType.getName():
                xmlObject = klass()
                xmlList.append( xmlObject._fromDom(xmlNode) )
        return xmlList
