# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


import UserList, copy
from main import XMLObject
import classregistry
from types import StringType, UnicodeType

class TypedList(UserList.UserList):
    """ A *special* list implementation

        It stores XMLObjects all of the same type OR strings.
        Mainly used by `Nodes.ListNode`.

        Example:

        ::

          class Bar(XMLObject):
              pass

          class Foo(XMLObject):
              liste = ListNode('Bar')

        ``liste`` node will create a TypedList in background. This list
        will ensure all items it stores are ``Bar`` instances.
    """

    def __init__(self, xmlList, data=[]):
        UserList.UserList.__init__(self, data)
        self._xmlList = xmlList

    def walkOnXMLObject(self,xoName, registry, callback, *args, **kw):
        theClass = classregistry.registry(registry).getClass(xoName)
        for nodeName, nodeInstance in theClass.__nodes__.iteritems():
            if nodeInstance.getType()  == 'ChoiceNode':
                for classRef in nodeInstance.getItemType():
                    if callback(classRef, *args, **kw):
                        return True
            elif nodeInstance.getType() in ['ListNode','ItemNode']:
                if callback(nodeInstance.getType(), *args, **kw):
                    return True
        return False

    def _compareTypes(self, itemType1, *args, **kw):
        """ Callback used to compare two type names.

            Used by `TypedList.walkOnXMLObject`
        """
        itemType2 = getattr(args[0],'__name__',args[0])
        if itemType1 == '#PCDATA' and type(itemType2) in [StringType, UnicodeType]:
            itemType1 = itemType2
        return itemType1 == itemType2


    def checkItem(self, it):
        parentType = self._xmlList.getItemType()
        registry = self._xmlList.getRegistry()
        paClass = classregistry.registry(registry).getClass(parentType)
        typeMismatch = False
        if type(it) in [StringType, UnicodeType]:
            if not self.walkOnXMLObject(parentType,
                                        self._xmlList.getRegistry(),
                                        self._compareTypes, it):
                typeMismatch = True

        elif not isinstance(it, XMLObject):
            typeMismatch = True
        #elif it.getClassName() != parentType and \
        elif not isinstance(it, paClass) and \
                 not self.walkOnXMLObject(parentType,
                                          self._xmlList.getRegistry(),
                                          self._compareTypes, it):
            #print('humm')

            #itClass = classregistry.registry(registry).getClass(it.getClassName())
            #import pdb; pdb.set_trace()
            typeMismatch = True

        if typeMismatch:
            #
            raise TypeError("""\
%s type required for %s. Got %s instead""" % (repr(parentType),
                                              repr(self._xmlList.getName()`,
                                              repr(type(it))))
        if isinstance(it,XMLObject):
            if it.getClassName() == self._xmlList.getParentType():
                it = copy.deepcopy(it)
            it.setParentNode(self._xmlList)
        return it

    def checkList(self, other):
        other2 = self.__class__(self._xmlList)
        for it in other:
            other2.append(it)
        return other2

    def append(self, item):
        item = self.checkItem(item)
        UserList.UserList.append(self, item)

    def insert(self, index, item):
        item = self.checkItem(item)
        UserList.UserList.insert(self,index, item)

    def extend(self, other):
        other2 = self.checkList(other)
        UserList.UserList.extend(self, other2)

    def __add__(self, other):
        other2 = self.checkList(other)
        if isinstance(other2, self.__class__):
            return self.__class__(self._xmlList, self.data + other2.data)
        elif isinstance(other2, type(self.data)):
            return self.__class__(self._xmlList, self.data + other2)
        else:
            return self.__class__(self._xmlList, self.data + list(other2))

    def __iadd__(self, other):
        other2 = self.checkList(other)
        return UserList.UserList.__iadd__(self, other2)

    def __radd__(self, other):
        other2 = self.checkList(other)
        if isinstance(other2, self.__class__):
            return self.__class__(self._xmlList, other2.data + self.data)
        elif isinstance(other2, type(self.data)):
            return self.__class__(self._xmlList, other2 + self.data)
        else:
            return self.__class__(self._xmlList, list(other2) + self.data)

    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        return self.__class__(self._xmlList,self.data[i:j])
