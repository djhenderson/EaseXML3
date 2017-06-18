# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

import sys
sys.path.insert(0,'..')

from EaseXML3 import *

## Snippet "section-decl"
class Section(XMLObject):
    _nodesOrder = [ 'title', 'mix' ]
    title = TextNode()
    mix = ChoiceNode(['Paragraph', 'Section'])

class Paragraph(XMLObject):
    content = TextNode(main=True)
## End Snippet


## Snippet "section-usage"

section = Section()
section.title = 'Level 1'
section.mix = Section(title='Level 2',
                      mix=Paragraph('Foo bar'))

print section.toXml()
"""
<?xml version="1.0" encoding="utf-8" ?>
<Section>
  <title>
      Level 1
  </title>
  <Section>
    <title>
        Level 2
    </title>
    <Paragraph>
        Foo bar
    </Paragraph>
  </Section>
</Section>
"""
## End Snippet
