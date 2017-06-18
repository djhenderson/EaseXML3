# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)
# $HeadURL$
# $Id$

import sys
import classregistry

class MetaNamespace(type):

    def __new__(cls, className, bases, dictionnary):

        if not dictionnary.has_key('__name__'):
            dictionnary['__name__'] = className
        newClass = type.__new__(cls, className, bases, dictionnary)
        classregistry.registry('namespaces').addClass(newClass)

        return newClass

class Namespace(object):

    __metaclass__ = MetaNamespace

    uri = ''

def getAllNamespaces():
    return classregistry.registry('namespaces').allClasses()
