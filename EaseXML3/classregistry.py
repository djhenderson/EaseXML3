# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


"""
classresolver.py
  2 February 2004, Ian Bicking <ianb@colorstudy.com>

Resolves strings to classes, and runs callbacks when referenced
classes are created.

Classes are referred to only by name, not by module.  So that
identically-named classes can coexist, classes are put into individual
registries, which are keyed on strings (names).  These registries are
created on demand.

Use like::

    >>> from __future__ import print_function
    >>> import classregistry
    >>> registry = classregistry.registry('MyModules')
    >>> def afterMyClassExists(cls):
    ...    print('Class finally exists:', cls)
    >>> registry.addClassCallback('MyClass', afterMyClassExists)
    >>> class MyClass(object):
    ...    pass
    >>> registry.addClass(MyClass)
    Class finally exists: MyClass

"""

class ClassRegistry(object):
    """
    We'll be dealing with classes that reference each other, so
    class C1 may reference C2 (in a join), while C2 references
    C1 right back.  Since classes are created in an order, there
    will be a point when C1 exists but C2 doesn't.  So we deal
    with classes by name, and after each class is created we
    try to fix up any references by replacing the names with
    actual classes.

    Here we keep a dictionaries of class names to classes -- note
    that the classes might be spread among different modules, so
    since we pile them together names need to be globally unique,
    to just module unique.
    Like needSet below, the container dictionary is keyed by the
    class registry.
    """

    def __init__(self, name):
        self.name = name
        self.classes = {}
        self.callbacks = {}

    def addClassCallback(self, className, callback, *args, **kw):
        """
        Whenever a name is substituted for the class, you can register
        a callback that will be called when the needed class is
        created.  If it's already been created, the callback will be
        called immediately.
        """
        if className in self.classes:
            callback(self.classes[className], *args, **kw)
        else:
            self.callbacks.setdefault(className, []).append((callback, args, kw))

    def addClass(self, cls):
        """
        Everytime a class is created, we add it to the registry, so
        that other classes can find it by name.  We also call any
        callbacks that are waiting for the class.
        """
        self.classes[cls.__name__] = cls
        if cls.__name__ in self.callbacks:
            for callback, args, kw in self.callbacks[cls.__name__]:
                callback(cls, *args, **kw)
            del self.callbacks[cls.__name__]

    def getClass(self, className):
        return self.classes[className]

    def allClasses(self):
        return self.classes.values()

    def dump(self):
        return self.classes

class _MasterRegistry(object):
    """
    This singleton holds all the class registries.  There can be
    multiple registries to hold different unrelated sets of classes
    that reside in the same process.  These registries are named with
    strings, and are created on demand.  The MasterRegistry module
    global holds the singleton.
    """

    def __init__(self):
        self.registries = {}

    def registry(self, item):
        if not item in self.registries:
            self.registries[item] = ClassRegistry(item)
        return self.registries[item]

MasterRegistry = _MasterRegistry()
registry = MasterRegistry.registry
