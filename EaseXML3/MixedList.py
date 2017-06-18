# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

import copy

from . TypedList import TypedList
from . main import XMLObject
from . import classregistry

class MixedList(TypedList):
    """ Multiple Type storage List

        This kind of list can store every XMLObject type declared
        in its parent `ChoiceNode`. Plus Strings.

        Example:

        ::

          class Foo(XMLObject):
              pass

          class Bar(XMLObject):
              mix = ChoiceNode(['#PCDATA','Foo'], noLimit=True)

        In ``mix`` node, a backend MixedList will be created. It will
        ensure items stored are either strings ('#PCDATA') or ``Foo``
        instances.

    """

    def walkOnXMLObject(self, typeList, registry, callback, *args, **kw):
        if '#PCDATA' in typeList and callback('#PCDATA',*args, **kw):
            return True
        for className in typeList:
            theClass = classregistry.registry(registry).getClass(className)
            for nodeName, nodeInstance in theClass.__nodes__.iteritems():
                if nodeInstance.getType()  == 'ChoiceNode':
                    for classRef in nodeInstance.getItemType():
                        if callback(classRef, *args, **kw):
                            return True
                elif nodeInstance.getType() in ['ListNode','ItemNode']:
                    if callback(nodeInstance.getType(), *args, **kw):
                        return True
        return False


    def checkItem(self, it):
        typeMismatch = False
        alternatives = self._xmlList.getItemType()
        if isinstance(it, (type(b''), type(u''))):
            if not self.walkOnXMLObject(alternatives,
                                        self._xmlList.getRegistry(),
                                        self._compareTypes, it):
                typeMismatch = True

        elif not isinstance(it, XMLObject):
            typeMismatch = True
        elif it.getClassName() not in alternatives:
            if not self.walkOnXMLObject(alternatives,
                                        self._xmlList.getRegistry(),
                                        self._compareTypes, it):
                typeMismatch = True

        if typeMismatch:
            raise TypeError("""\
%s type required for %s. Got %s instead""" % (repr(alternatives),
                                              repr(self._xmlList.getName()),
                                              repr(type(it))))

        if isinstance(it,XMLObject):
            if it.getClassName() == self._xmlList.getParentType():
                it = copy.deepcopy(it)
            it.setParentNode(self._xmlList)
        return it
