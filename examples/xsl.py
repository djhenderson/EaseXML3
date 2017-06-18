import sys
sys.path.insert(0,'..')
from EaseXML import *

class AnotherFoo(XMLObject):
    xslt = ProcessingInstructionNode('xml-stylesheet',
                                     [ (u'type',u'text/css'),
                                       (u'href',u'http://foobar.com/style.css')
                                       ])
    blah = TextNode(optional=True)

af = AnotherFoo()
print af.toXml()

"""
<?xml version="1.0" encoding="utf-8" ?>
<?xml-stylesheet type="text/css" href="http://foobar.com/style.css" ?>
<AnotherFoo/>
"""
