# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

from __future__ import print_function

from main import *
from Nodes import *
from CodeGeneratorBackend import CodeGeneratorBackend
from utils import customUnicode, titleWord

from xml.parsers.xmlproc import xmldtd
import sys, types

raise Exception, 'Not ready at all'

def Attribute(dtdAttr):
    declmap = { "#REQUIRED" : "optional=False",
                "#IMPLIED"  : "optional=True",
                "#DEFAULT"  : "default='%s',",
                "#FIXED"    : "default='%s',"
                }

    typs = { 'CDATA': 'CDATAttribute',
             'ID': 'StringAttribute',
             'IDREF': 'StringAttribute',
             'IDREFS': 'StringAttribute',
             'NMTOKEN': 'NMTokenAttribute',
             'NMTOKENS': 'NMTokensAttribute'
             }

    decl = dtdAttr.get_decl()
    default = dtdAttr.get_default()
    name = dtdAttr.get_name()
    typ = dtdAttr.get_type()

    decl = declmap[decl]
    if default:
        default = decl % default
    else:
        default = ''

    permittedValues = "permittedValues=None"
    if type(typ) == type([]):
        permittedValues = "permittedValues=%s" % str([val for val in typ])
        typ = 'StringAttribute'
    else:
        typ = typs[typ]

    return "%s = %s(%s%s)" % (name, typ, default,permittedValues)

class Element2XO:

    def __init__(self, dtd,cog,  dtdElem):
        self.attrs = []
        self.dtd = dtd
        self.elem = dtdElem
        self.name = titleWord(dtdElem.get_name())
        self.processAttrs(dtdElem.get_attr_list())
        self.nodes = self.processModel(dtdElem.get_content_model())
        self.generate(cog)

    def generate(self, cog):
        cog.writeln('class %s(XMLObject):' % titleWord(self.name))
        cog.indent()
        if len(self.attrs) + len(self.nodes) == 0:
            cog.writeln('pass')
        else:
            for a in self.attrs:
                cog.writeln(a)
            for n in self.nodes:
                cog.writeln(n)
        cog.dedent()
        cog.writeln('')

    def processModel(self, model):
        if not model:
            return []
        sep, cps, mod = model
        if sep == '' or sep == ',':
            wrapper = 'ItemNode'
        elif sep == '|':
            wrapper = 'ChoiceNode'

        nodes = []
        for cp in cps:
            d = ''
            if len(cp) == 2:
                name, mod = cp
                if name == "#PCDATA":
                    print('<<<<<<', mod)
                    continue

                modMap = {'?' : ['optional=True','once=True'],
                          '+' : ['optional=False', 'once=False'],
                          '*' : ['optional=True',  'once=False'],
                          ''  : []
                          }
                try:
                    entity = self.dtd.get_general_entities()
                except KeyError:
                    pass
                #else:
                #    print('>>>>>>>>>>>>>>>>>>>>',entity, name)
                print(self.name,wrapper,'<<<<', name, mod, 'ok')
                if wrapper == 'ItemNode':
                    name2 = ["'%s'" % titleWord(name) ]
                else:
                    name2 = []

                nodes.append("%s = %s(%s)" % (name,wrapper,','.join(name2+modMap[mod])))
            elif len(cp) == 3:
                nodes.extend(self.processModel(cp))
            else:
                nodes.append("# %s" % cp)
        return nodes

    def processAttrs(self, attrs):
        self.attrs = []
        for attr in attrs:
            self.attrs.append(Attribute(self.elem.get_attr(attr)))


def processDTD(aDTD, outFile=None):

    print("# Loading DTD %s ... to %s" % (aDTD, outFile))
    print()

    dtd = xmldtd.load_dtd(aDTD)

    c = CodeGeneratorBackend()
    c.begin()

    c.writeln("from EaseXML3 import *")
    c.writeln('')

    elements = []
    for elemname in dtd.get_elements():
        elem = dtd.get_elem(elemname)
        elements.append( Element2XO(dtd,c,elem) )

    if outFile == "stdout":
        print(c.end())
    else:
        c.generate(outFile)

if __name__ == '__main__':
    dtd = sys.argv[1]

    if len(sys.argv) < 3:
        out = "stdout"
    else:
        out = sys.argv[-1]

    processDTD(dtd,out)
