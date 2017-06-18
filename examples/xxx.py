# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

import sys
sys.path.insert(0, '..')

from EaseXML3 import *

## Snippet "xxx-decl1"
class XXX(XMLObject):
    """
    <!ELEMENT XXX (AAA+ , BBB+)>
    """
    aaa = ListNode('AAA',optional=False)
    bbb = ListNode('BBB',optional=False)

class AAA(XMLObject):
    """
    <!ELEMENT AAA (BBB | CCC )>
    """
    content = ChoiceNode(['BBB','CCC'], main=True)
## End Snippet

## Snippet "xxx-decl2"
class BBB(XMLObject):
    """
    <!ELEMENT BBB (#PCDATA | CCC )*>
    """
    content = ChoiceNode(['#PCDATA', 'CCC'],optional=True,
                         main=True, noLimit=True)

class CCC(XMLObject):
    """
    <!ELEMENT CCC (#PCDATA)>
    """
    content = TextNode(main=True)
## End Snippet

## Snippet "xxx-mainNode"
cc = CCC('Some Text')
print(cc.toXml(headers=False))
"""
<CCC>
    Some Text
</CCC>
"""
print(cc.content)
"""
Some Text
"""
## End Snippet

## Snippet "xxx-invalid"
xx = XXX()
try:
    print(xx.toXml())
except TypeError:
    pass
"""
Traceback (most recent call last):
 ...
TypeError: Expected some node in 'XXX.aaa' as it is not optional
"""
## End Snippet

## Snippet "xxx-fill-in1"
xxx = XXX()
xxx.aaa.append(CCC('Precisely one element.'))

bb = BBB()
bb.append(CCC())
bb.append(CCC())
bb.append(CCC())
xxx.aaa.append(bb)

xxx.bbb.append(BBB())
## End Snippet
## Snippet "xxx-fill-in2"
bb2 = BBB()
bb2.append('This is')
bb2.append(CCC())
bb2.append('a combination')
bb2.append(CCC())
bb2.append('of')
bb2.append(CCC('CCC elements'))
bb2.append('and text')
bb2.append(CCC())
xxx.bbb.append(bb2)

xxx.bbb.append(BBB('Text only.'))
## End Snippet


xxxStr = xxx.toXml()
xxx2 = XXX.fromXml(xxxStr)
assert xxx2 == xxx, "Pb during import/export"

print(xxxStr)

"""
## Snippet "xxx-display"
<?xml version="1.0" encoding="utf-8" ?>
<XXX>
  <AAA>
    <CCC>
        Precisely one element.
    </CCC>
  </AAA>
  <AAA>
    <BBB>
      <CCC/>
      <CCC/>
      <CCC/>
    </BBB>
  </AAA>
  <BBB/>
  <BBB>
      This is
    <CCC/>
      a combination
    <CCC/>
      of
    <CCC>
        CCC elements
    </CCC>
      and text
    <CCC/>
  </BBB>
  <BBB>
      Text only.
  </BBB>
</XXX>
## End Snippet
"""

"""
## Snippet "xxx-display2"
<BBB>
    This is
  <CCC/>
    a combination
  <CCC/>
    of
  <CCC>
      CCC elements
  </CCC>
    and text
  <CCC/>
</BBB>
<BBB>
    Text only.
</BBB>
## End Snippet
"""
