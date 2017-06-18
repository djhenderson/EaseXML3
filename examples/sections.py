import sys
sys.path.insert(0,'..')
from EaseXML import *

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
