# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


from types import UnicodeType, NoneType
import sys

def lowWord(word):
    " FoObar -> foObar "
    return word[0].lower() + word[1:]

def titleWord(word):
    " foObar -> FoObar "
    return word[0].upper() + word[1:]


def replaceAll(initialString, translationHash):
    """ for each (toReplace, replacement) in `translationHash`
        applying the query-replace operation to `initialString`
    """
    result = ''
    if initialString is not None:
        result = initialString
        for key, value in translationHash:
            result = result.replace(key, value)
    return result

def contains(list1, list2):
    """ Check if some elements of list1 appear in list2

        Return the intersection of the two lists
    """
    return [ it1 for it1 in list1 if it1 in list2 ]

def getDirectChildrenWithName(parent, name):
    """ Fetch *direct* sub-nodes of a `parent` DOM tree. These
        nodes must have a name matching `name`.

        Return a list of DOM Nodes.
    """
    return [ node for node in parent.childNodes
             if node.nodeType == node.ELEMENT_NODE and \
             node.localName == name ]

def customUnicode(data, encoding):
    if type(data) not in (UnicodeType, NoneType):
        if encoding:
            data = unicode(data, encoding)
        else:
            data = unicode(data)
    return data
