# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


import sys, re, types, string, copy

if sys.version_info[:2] < (2,2):
    raise RuntimeError('EaseXML3 is not compatible with Python versions prior to 2.2')

# xml.minidom is only used to parse incoming XML
# when building XMLObject from string data
from xml.dom.minidom import parseString

import logging
logging.basicConfig()

import classregistry, utils
from Node import Node, ProcessingInstructionNode
from Attributes import Attribute
from PrettyXMLPrinter import PrettyXMLPrinter
from Namespace import getAllNamespaces

__all__ = [ 'XMLObject', 'ParseError']

XML_PI = 'xmlProcessingInstruction'

class ParseError(Exception):
    """ XML Parse Error.

        Raised when XML data cannot be parsed by `XMLObject.fromXml`.
    """

    def __init__(self, domException, xmlData, encoding=None):
        Exception.__init__(self)
        self._domExcp = domException
        self._xmlData = xmlData
        self._encoding = encoding

    def __str__(self):
        return utils.customUnicode(str(self._domExcp),self._encoding) + \
               u':\n' + utils.customUnicode(str(self._xmlData),self._encoding)

class MetaAttribute(object):
    """ Each XMLObject type deals with MetaAttributes. In the example below,
        ``content`` and ``title`` are MetaAttributes::

          >>> class MyXMLObject(XMLObject):
          ...   content = TextNode('Content') # _XO_content
          ...   title = StringAttribute()     # _XO_title
          ...
          >>>

        MetaAttributes handle value with the XMLObject they're included in.
        Type checking is done in `__set__`.
    """

    def __init__(self, nodeInstance, encoding):
        self._attrName = '_XO_%s' % nodeInstance.getName()
        self._node = nodeInstance
        self._encoding = encoding

    def __get__(self, inst, cls):
        nodeValue = inst.get(self._attrName)
        if not cls._unicodeOutput and type(nodeValue) == type(u''):
            nodeValue = nodeValue.encode(cls._encoding)
        return nodeValue

    def __set__(self, inst, val):
        newVal = self._node.checkType(val)
        if newVal is not False:
            if isinstance(newVal, XMLObject):
                newVal.setParentNode(inst)
            inst.set(self._attrName,newVal)
        else:
            raise TypeError(u'Incorrect type in assignment of '+ \
                            utils.customUnicode(str(self._node.getName()),self._encoding)
                            + u' (%s)' % utils.customUnicode(str(repr(val)),self._encoding))

class MetaXMLObject(type):
    """ The place where all magic happens:

        - remember the name of the new type (class)
        - store attribute instances (used in XMLObject.{to,from}Xml methods)
        - create MetaAttributes
        - handle inheritance

        Special variables are:

        - `XMLObject.__name__` : the class name
        - `XMLObject.__nodes__` : the hash of class members keyed by name.
          Each node has to be an instance of the Node class.

    """

    __methods__ = [ 'set','get', 'getEntities', 'orderNodes', 'setParentNode',
                    'getClassName', 'toDict', 'fromDict', 'getNodes',
                    'getNodeWithName', 'setName', 'orderAttrs', 'getParentNode',
                    'toXml', 'fromXml', '_fromDom','getName', 'getChildren']

    def __new__(cls, className, bases, dictionnary):

        # check if user defined class doesn't override esssential stuff
        intersection = utils.contains(dictionnary.keys(), cls.__methods__)
        if len(intersection) > 0 and className != 'XMLObject':
            logging.warn('Methods redefined (%s) in %s ... At your own risks' %
                         (unicode(className), unicode(str(intersection))))

        dictionnary['__name__'] = className
        dictionnary['__nodes__'] = {}
        dictionnary['__ns_nodes__'] = {}

        nodes = filter(lambda x: x is not None,
                       map(lambda y,z: cls.isXONode(y,z),
                           dictionnary.keys(), dictionnary.values()))

        try:
            encoding = dictionnary['_encoding']
        except KeyError:
            encoding = XMLObject._encoding

        foundAMain = False
        # build the MetaAttributes corresponding to the nodes of the class
        for name, instance in nodes:
            if instance.isMain():
                if not foundAMain:
                    foundAMain = True
                else:
                    logging.error("Defining multiple main Nodes is non-sense")

            # store the attribute name somewhere
            if instance.getName() == '':
                instance.setName(name)
            instance.setParentType(className)
            dictionnary['__nodes__'][name] = instance
            dictionnary[name] = MetaAttribute(instance,encoding)

        newClass = type.__new__(cls, className, bases, dictionnary)

        # mutiple inheritance
        if cls.mro(newClass)[-1] != object:
            logging.warn('Multiple inheritance is not correctly handled by XMLObject')

        # simple inheritance handling
        for superClass in cls.mro(newClass)[1:-2]:
            for nodeName,node in superClass.__nodes__.iteritems():
                # we need to make a copy of the node to keep the "super-node" safe
                # from parentType modification
                nodeCopy = copy.copy(node)
                nodeCopy.setParentType(className)
                newClass.__nodes__[nodeName] = nodeCopy
                setattr(newClass, nodeName, MetaAttribute(nodeCopy,encoding))


        # add the xmlProcessingInstruction
        if XML_PI in newClass.__nodes__:
            del newClass.__nodes__[XML_PI]
        xmlPI = ProcessingInstructionNode('xml',[(u'version',u'1.0'),
                                                 (u'encoding', newClass._encoding)
                                                 ],
                                          optional=True)
        xmlPI.setName(XML_PI)
        xmlPI.setParentType(newClass.getClassName())
        newClass.__nodes__[XML_PI] = xmlPI

        # finally register the new class type so that it can be found
        # using its name
        classregistry.registry(newClass._registry).addClass(newClass)

        # propagate the registry id in each node
        for nodeName,node in newClass.__nodes__.iteritems():
            node.setRegistry(newClass._registry)

        return newClass

    def isXONode(cls, name, instance):
        """ Checks if an instance variable is an XMLObject Node

        """
        result = None
        if isinstance(instance,Node) and u'_' not in name[:1] \
           and name not in cls.__methods__ and type(instance) != types.FunctionType:
            result = (name,instance)
        return result
    isXONode = classmethod( isXONode )

    def instanceFromXml(cls, xmlData, registryID=None):
        """
            Builds a new XMLObject instance given its XML representation. This method
            differs from `XMLObject.fromXml` in the fact that you don't need to care
            about the XMLObject type to use because it's taken from the class registry.

            Though, XMLObjects you defined need to be in the namespace where you use
            this method.
        """
        if not registryID:
            registryID = XMLObject._registry
        registry = classregistry.registry(registryID)
        for klass in registry.allClasses():
            try:
                data = xmlData.encode(klass._encoding)
            except:
                data = xmlData

            try:
                dom = parseString(data)
            except Exception as ex:
                raise ParseError(ex, data)
            else:
                root_node_name = dom.documentElement.localName
                if klass.getName() == root_node_name:
                    val = klass()
                    val._fromDom(dom.documentElement)
                    dom.unlink()
                    return val
        raise ParseError(u'No XMLObject found for',xmlData)

    instanceFromXml = classmethod( instanceFromXml )



class XMLObject(object):
    """
        Class attributes of interest:

        - ``_name`` : overrides `__name__`
        - ``_entities`` : user-defined entities stored in a tuples-list,
        - ``_stripStrings`` : does xml import should strip strings ? (remove tabs,
          extra spaces)
        - ``_prettyPrint`` : should XML output be pretty printed ?
        - Nodes ordering:

          * ``_nodesOrder`` : a list of Node (TextNode, ListNode, RawNode, CommentNode, ...) names
          * ``_attrsOrder`` : a list of Attributes (StringAttribute, IntegerAttribute, ...) names

        - ``_encoding`` : document encoding (default: 'utf-8')

        If you pass the keyword ``main=True`` to one of your Nodes, it will be hooked so that
        calling Node methods ('append' for instance) from the XMLObject instance will
        be applied to that main Node:

        ::

          class Other(XMLObject):
              boo = StringAttribute(default='titi')

          class Single(XMLObject):
              content = ChoiceNode(['Other','Single'], noLimit=True, main=True)
              title = StringAttribute()

          single = Single()
          single.title = 'Foo'
          single.append(Other())
          single.append(Other())
          single.append(single)

          <Single title="Foo">
            <Other boo="titi"/>
            <Other boo="titi"/>
            <Single title="Foo">
              <Other boo="titi"/>
              <Other boo="titi"/>
            </Single>
          </Single>
    """

    __metaclass__ = MetaXMLObject

    _registry = 'registryID'
    _encoding = 'utf-8'
    _unicodeOutput = True

    _stripStrings = True
    _prettyPrint = True

    _defaultEntities = [ ('&', '&amp;'),
                         ('<', '&lt;'),
                         ('>', '&gt;'),
                         ('"', '&quot;'),
                         ("'", '&apos;'),
                       ]

    _entities = [ ]
    _nodesOrder = [ ]
    _attrsOrder = [ ]

    _dtd = None

    def __init__(self, *args, **kw):
        self._attributes = {}

        self._prettyPrinter = PrettyXMLPrinter()

        # set default values for the new class instance
        for attrName, instance in self.getNodes().iteritems():
            instance.resetValue()
            if instance.getValue() is not None:
                setattr(self, attrName, instance.getValue())

        # if we have only one Node, it can directly be initialized
        # by unnamed constructor argument (in `args` tuple)
        if len(args) == 1 and len(self.getChildren()) == 2:
            nodeNames = self.getChildren()
            nodeNames.remove(XML_PI)
            setattr(self, nodeNames[0],args[0])

        # set user values for the class instance
        # Some may override defaults
        for k,v in kw.iteritems():
            if self.getNodeWithName(k) is not None:
                setattr(self, k, v)

        # i have a dummy parent, overriden when i'm encapsulated in a
        # ChoiceNode or ListNode
        self.setParentNode(Node())

        # execute user-defined initialization code
        self._init()

    #####################################################################
    ### Private
    #####################################################################

    def _fromDom(self, dom):
        """ Building an XMLObject given its pendant DOM tree.

        """
        for attrName, node in self.getNodes().iteritems():
            try:
                value = node.getValueFromDom(dom, attrName,
                                             registry=self._registry,
                                             stripStrings=self._stripStrings)
            except Exception as e:
                raise
            else:
                setattr(self, attrName, value)
        return self

    #####################################################################
    ### Nodes Access (Reserved to MetaAttribute class)
    #####################################################################

    def get(self, nodeName):
        """ Fetch a node value given its name.
            using directly (or implicitely) `getattr` is smarter.
            This method is used by the MetaAttribute instances
        """
        return self._attributes.get(nodeName,None)

    def set(self, nodeName, val):
        """ Modify a node value given its name.
            Same external behaviour as `setattr`
            This method is used by the MetaAttribute instances
        """
        self._attributes[nodeName] = val

    #####################################################################
    ### Hooks
    #####################################################################

    def _init(self):
        """ Method executed after instance initialization (__init__).

            End-user can override this as he would for __init__.
        """
        pass

    def __ne__(self, other):
        if not isinstance(other,XMLObject):
            raise TypeError("Comparing an XMLObject with non-XMLObject is forbiden")
        o1 = self.toXml(headers=0)
        o2 = other.toXml(headers=0)
        return o1 != o2

    def __eq__(self, other):
        if not isinstance(other,XMLObject):
            raise TypeError("Comparing an XMLObject with non-XMLObject is forbiden")
        o1 = self.toXml(headers=0)
        o2 = other.toXml(headers=0)
        return o1 == o2

    def __cmp__(self, other):
        """ Two XMLObjects are equal if they have the same XML representation
        """
        ## Tobias did wrong here.  cmp should return -1,0,1, not False or True.
        ## To do this Right we should maybe implement __eq__ and __ne__ and
        ## rather raise an exception here if other is not an XMLObject.
        ## (Bug discovered and investigated by Ken Wong, Exoweb)
        ## @PN: solved now ?
        if not isinstance(other,XMLObject):
            raise TypeError("Comparing an XMLObject with non-XMLObject is forbiden")

        o1 = self.toXml(headers=0, prettyPrint=False)
        o2 = other.toXml(headers=0, prettyPrint=False)
        return cmp(o1, o2)

    def __getattr__(self, attrName):
        if '_' not in attrName[:1]:
            for node in self.getNodes().values():
                if node.isMain():
                    attr = MetaAttribute(node, self._encoding)
                    return getattr(attr.__get__(self, self.__class__), attrName)
                elif node.getName() == attrName:
                    attr = MetaAttribute(node, self._encoding)
                    return attr.__get__(self, self.__class__)
        raise AttributeError(attrName)

    __getitem__ = __getattr__

    def __str__(self):
        return self.toXml(headers=0)

    #####################################################################
    ###
    #####################################################################

    def setParentNode(self, node):
        """ Setting the parent Node instance.

            When XMLObjects are stored in ChoiceNodes or in ListNodes,
            we need to keep track of their parent. This method is
            mainly used by back-storage {Mixed,Typed}List instances
            used respectively by ChoiceNodes and ListNodes.
        """
        self._parentNode = node

    def getParentNode(self):
        """ Accessing the parent Node instance.

            Return a dummy Node() by default (see `__init__`).
        """
        return self._parentNode

    def forEach(self, callableFunc, *args, **kw):
        """ Execute an action for *each* Node handled by an XMLObject.

            The head XML processing instruction is ignored. The
            `callableFunc` may have the following prototype:

            ::

              def myCallable(node, xmlObject, *args, **kw):
                  # do some things with the node ?
                  pass

            ``node`` is the Node instance to apply user-defined
            action. ``xmlObject`` is the XMLObject instance handling
            this ``node``. ``args`` and ``kw`` store the content of their
            homonyms in the ``forEach`` method prototype.

            Warning: This method can be very CPU-expensive if the
            XMLObject is deep (nested ListNodes and/or ChoiceNodes)
            because it make use of a recursion mechanism.
        """
        if not 'depth' in kw:
            kw['depth'] = 0
        depth = kw['depth']
        for nodeName,node in self.getNodes().iteritems():
            if nodeName == XML_PI:
                # we silently ignore the head XML processing-instruction
                continue
            if node.getType() == 'ListNode':
                kw.update({'depth': depth + 1})
                for item in getattr(self, node.getName()):
                    item.forEach(callableFunc, *args, **kw)
                kw['depth'] -= 1
            elif node.getType() == 'ChoiceNode' and node.isNoLimit():
                kw.update({'depth': depth + 1})
                for item in getattr(self, node.getName()):
                    item.forEach(callableFunc, *args, **kw)
                kw['depth'] -= 1
            elif node.getType() == 'ItemNode':
                kw.update({'depth': depth + 1})
                getattr(self, nodeName).forEach(callableFunc, *args, **kw)
                kw['depth'] -= 1
            else:
                callableFunc(node, xmlObject=self, *args, **kw)

    def getEntities(self):
        """ Get all entities specified in the xmlobject:

        - `_defaultEntities` stores the most common entities (<, >, ...)
        - `_entities` stores user-defined entities

        This method merges the two entities lists.
        """
        return self._entities + self._defaultEntities

    def getClassName(cls):
        return unicode(cls.__name__)

    getClassName = classmethod(getClassName)

    def setName(self, newName):
        self._name = newName

    def getName(cls):
        """ Fetch XMLObject's instance name
            which can be redefined by ``_name`` class attribute.
            Space (' ') characters are replaced by underscores ('_') in returned
            result.
        """
        name = cls.__name__
        if hasattr(cls, '_name'):
            if type(cls._name) not in [types.StringType, types.UnicodeType]:
                raise ValueError("Incorrect '_name' for %s: '%s'" % (name,cls._name))
            name = cls._name
        name = name.replace(' ','_')
        return name

    getName = classmethod(getName)

    def getChildren(self):
        """ Basic Introspection

            Fetch XMLObject node names.
        """
        return self.getNodes().keys()

    def getNodes(self):
        """ Sub-Nodes accessor

            Fetch XMLObject nodes. Return a hash. This method differs
            from `toDict` in the way that the hash stores Node class
            instances. So it'd be more useful if the developer wants
            to inspect an XMLObject instance.
        """
        return self.__nodes__

    def getNodeWithName(self, nodeName):
        """ Specific-Node accessor

            Return a `Node` instance given its name.
            Return None if Node doesn't exist under ``nodeName``.
        """
        return self.getNodes().get(nodeName, None)

    def orderNodes(self, nodesList=None):
        """
            XMLObject remembers its children by a hash storage. Since hash
            sorting is not really friendly, this method returns two lists
            (nodeNames & nodes).
        """
        if not nodesList:
            nodesList = self.getChildren()
        nodes = []
        for nodeName in nodesList:
            nodes.append(self.getNodeWithName(nodeName))
        return (nodesList, nodes)

    def orderAttrs(self):
        return self.orderNodes(nodesList=self._attrsOrder)

    #####################################################################
    ### XML input/output
    #####################################################################

    def toXml(self, headers = 1, tabLength=2, prettyPrint=True):
        """ Exporting an XMLObject instance to XML.

            Optionnal keyword parameters are:

            - `headers` : boolean to figure out if XML data has to be headed by
              the processing instruction(s) (like <?xml ..?>)
            - `tabLength`: XML indentation length

            Return a string representing the XMLObject instance
        """
        result = u''
        if headers:
            # I need to make this more smart
            for nodeName, node in self.getNodes().iteritems():
                if isinstance(node, ProcessingInstructionNode ):
                    result += node.xmlrepr()

        attrs, others = u'', u''
        name = self.getName()
        result += u'<%s' % name

        mainNode = None
        mainNodeName = ''

        # XMLObject sub-tags
        nodeNames, nodes = self.orderNodes(self._nodesOrder)
        for index in range(len(nodes)):
            attrName, node = nodeNames[index], nodes[index]
            if isinstance(node, Attribute) or isinstance(node,ProcessingInstructionNode):
                continue
            # 0. backup default node value
            default = node.getValue()
            # 1. set node value temporary
            node.setValue(getattr(self, attrName))
            nodeRepr = node.xmlrepr(parentInstance=self)
            try:
                others += nodeRepr
            except:
                raise
            if node.isMain():
                mainNode = nodeRepr
                mainNodeName = attrName
            # 2. reset value to default
            node.setValue(default)

        # XMLObject tag attributes
        attrNames, nodes = self.orderAttrs()
        for index in range(len(nodes)):
            attrName, node = attrNames[index], nodes[index]
            if not isinstance(node, Attribute):
                continue
            # 0. backup default node value
            default = node.getValue()
            # 1. set node value temporary
            node.setValue(getattr(self, attrName))
            nodeRepr = node.xmlrepr(parentInstance=self)
            if nodeRepr:
                attrs += u' ' + nodeRepr
            # 2. reset value to default
            node.setValue(default)

        if attrs:
            result += attrs
        if others != u'':
            if mainNode:
                try:
                    others = re.match('<%(main)s>(.*)</%(main)s>' % {'main':mainNodeName},
                                      mainNode).groups()[0]
                except:
                    others = mainNode
            result = u"%s>%s</%s>" % (result, others, name)
        else:
            result = u'%s/>' % result

        if self._stripStrings and self._prettyPrint and prettyPrint:
            result = self._prettyPrinter.prettyPrint(result, indent=' '*tabLength)

        result = result.encode(self._encoding)
        return result

    def fromXml(cls, xmlData):
        """ Feeding an XMLObject instance with XML string data.

            `xmlData` is parsed by `xml.dom.minidom.parseString`.
            The resulting DOM tree is then used to build Nodes
            recursively.
        """
        xo = cls()
        if type(xmlData) == type(u''):
            xmlData = xmlData.encode(xo._encoding)
        try:
            dom = parseString(xmlData)
        except Exception as ex:
            raise ParseError(ex, xmlData, encoding=xo._encoding)
        else:
            xo._fromDom(dom.documentElement)
        dom.unlink()
        return xo

    fromXml = classmethod(fromXml)

    #####################################################################
    ### Python dictionnary input/output
    #####################################################################

    def toDict(self):
        """ Fetch an XMLObject instance's data in a hash mapped by Node name

            This method provides instant access to all data stored by an
            XMLObject instance.
        """
        result = {}
        parsedObjects = []

        def getXOData(node, xmlObject, **kw):
            if xmlObject == self:
                result.update({ node.getName(): getattr(xmlObject, node.getName()) })
            elif xmlObject not in parsedObjects:
                parent = xmlObject.getParentNode()
                subDict = xmlObject.toDict()
                if parent.getName() == self.getName():
                    result.update({xmlObject.getName(): subDict})
                elif self.getNodeWithName(parent.getName()):
                    # XXX: add more checking here (ChoiceNode.noLimit for instance)
                    try:
                        result[parent.getName()].append(subDict)
                    except KeyError:
                        result[parent.getName()] = [ subDict ]
                parsedObjects.append(xmlObject)

        self.forEach(getXOData)
        return result

    def fromDict(cls, aDict):
        """ Build an XMLObject given its dict representation.

        """
        xo = cls()
        for key, value in aDict.iteritems():
            if type(value) == type([]):
                klassName = xo.getNodeWithName(key).getItemType()
                klass = classregistry.registry(xo._registry).getClass(klassName)
                objs = []
                for value2 in value:
                    objs.append( klass.fromDict(value2) )
                setattr(xo, key, objs)
            elif value is not None:
                setattr(xo, key, value)
        return xo

    fromDict = classmethod(fromDict)
