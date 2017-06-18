# -*- coding: iso8859-1 -*-
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

## allow rss.py to be executed directly from this directory,
## without installing EaseXML.
import sys
sys.path.insert(0,"../")

from EaseXML import *
import urllib2

## Snippet "RSS-decl"
class Rss(XMLObject):
    _name = 'rss'
    xslt = ProcessingInstructionNode('xml-stylesheet',
                                     [ (u'type',
                                        u'text/css'),
                                       (u'href',
                                        u'http://foo.com/style.css')
                                       ])
    version = StringAttribute(default='2.0')
    channel = ItemNode('Channel')

    def loadFromURL(cls, url):
        data = urllib2.urlopen(url).read()
        return cls.fromXml(data)

    loadFromURL = classmethod( loadFromURL )
## End Snippet

## Snippet "ChannelItem-decl"
class Channel(XMLObject):
    _name = 'channel'
    _nodesOrder = [ 'title','link', 'description',
                    'language', 'items' ]
    title = TextNode(default='Sample Channel Title')
    link  = TextNode(default='http://some/url/rss.xml')
    description = TextNode('Sample Channel Description !!')
    language = TextNode(default='en')
    items = ListNode('Item', optional=True)

class Item(XMLObject):
    _name = 'item'
    _nodesOrder = [ 'title','link', 'date', 'author',
                    'description' ]
    title = TextNode()
    link = TextNode()
    date = TextNode(name='pubDate', optional=True)
    author = TextNode(optional=True)
    description = TextNode()
## End Snippet

## Snippet "RSS-feeding"
channel = Channel(title='EaseXML-powered RSS feed')
rss = Rss(channel=channel)
rss.channel.items = [ Item(title='sample title 1',
                              description='blah',
                              date='2004/11/25 21:12:00',
                              link='http://toto.com') ]
rss.channel.items.append(Item(title='sample title 2',
                              description='blah2',
                              link='http://foobar.fr'))

rss2 = Rss.loadFromURL('http://base-art.net/wk/index.rdf')
## End Snippet

## Snippet "RSS-items"
for item in rss.channel.items:
    print 'title:', item.title

"""
title: sample title 1
title: sample title 2
"""
print len(rss.channel.items)
"""
2
"""
## End Snippet

## Snippet "RSS-forEachItem"
def printNodeName(node, xmlObject, *args, **kw):
    depth = kw['depth']
    print '%s%s (%s)' % ('   ' * depth, xmlObject.getName(),
                         node.getName())

rss.forEach(printNodeName)
"""
rss (version)
   channel (description)
   channel (language)
   channel (title)
      item (description)
      item (author)
      item (title)
      item (link)
      item (pubDate)
      item (description)
      item (author)
      item (title)
      item (link)
      item (pubDate)
   channel (link)
rss (xslt)
"""
## End Snippet

## Snippet "forEachCallback"    
def someCallable(node, xmlObject, *args, **kw):
    """
   - `node`: the current Node instance found by forEach
   - `xmlObject`: the XMLObject instance holding the `node`
   - optional named args (inherited from forEach() call)
   - keyword parameters (also inherited from forEach and
     extended with the "depth" (as integer) from which the
     `node` is reachable to the tree root.
    """
## End Snippet

## Snippet "RSS-dict-output"
import pprint
pprint.pprint(rss.toDict())
"""
{'channel': {'description': 'Sample Channel Description !!',
             'items': [{'author': None,
                        'description': 'blah',
                        'link': 'http://toto.com',
                        'pubDate': '2004/11/25 21:12:00',
                        'title': 'sample title 1'},
                       {'author': None,
                        'description': 'blah2',
                        'link': 'http://foobar.fr',
                        'pubDate': None,
                        'title': 'sample title 2'}],
             'language': 'en',
             'link': 'http://some/url/rss.xml',
             'title': 'EaseXML-powered RSS feed'},
 'version': '2.0',
 'xslt': [(u'type', u'text/css'), (u'href', u'http://foo.com/style.css')] }
"""
## End Snippet

## Snippet "RSS-XML-output"
print rss.toXml()
"""
<?xml version="1.0" encoding="utf-8" ?>
<?xml-stylesheet type="text/css" href="http://foo.com/style.css" ?>
<rss version="2.0">
  <channel>
    <title>
        EaseXML-powered RSS feed
    </title>
    <link>
        http://some/url/rss.xml
    </link>
    <description>
        Sample Channel Description !!
    </description>
    <language>
        en
    </language>
    <item>
      <title>
          sample title 1
      </title>
      <link>
          http://toto.com
      </link>
      <pubDate>
          2004/11/25 21:12:00
      </pubDate>
      <description>
          blah
      </description>
    </item>
    <item>
      <title>
          samplte title 2
      </title>
      <link>
          http://foobar.fr
      </link>
      <description>
          blah2
      </description>
    </item>
  </channel>
</rss>
"""
## End Snippet

## Snippet "RSS-XML-import-export"
rssStr = rss.toXml()
# NB: you can also use str(rss)

# importing XML which structure matches Rss's class
# data description
assert rssStr == Rss.fromXml(rssStr).toXml()

# generic XML import
assert rssStr == XMLObject.instanceFromXml(rssStr).toXml()
## End Snippet
