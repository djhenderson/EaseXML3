#! python
# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

from __future__ import print_function

import sys
sys.path.insert(, '..')

from EaseXML3 import *

## Snippet "playlist-decl"
class Song(XMLObject):
    _orderNodes = [ 'title', 'comment' ]
    _orderAttrs = [ 'artist', 'file', 'length' ]
    _stripStrings = False
    file = StringAttribute()
    length = IntegerAttribute()
    artist = StringAttribute(optional=True)
    title = TextNode(default='Track Name')
    comment = CommentNode(default='Blah blah')

class Playlist(XMLObject):
    _entities = [ ('&xml;','eXtensible Markup Language')]
    name = StringAttribute()
    songs = ListNode('Song')
## End Snippet

## Snippet "playlist-creation"
s1 = Song(file='foobar.ogg', length=300, artist='foo', title='Bar')

pList = Playlist(songs=[s1])
pList.name = 'My Favorites in &xml;'
## End Snippet

## Snippet "playlist-newSong"
s2 = Song(file='opensource.ogg', comment='hey man it rocks')
s2.length = 250
pList.songs.append(s2)
## End Snippet

## Snippet "playlist-save"
xmlPlaylist = pList.toXml()
xmlPlaylist2 = XMLObject.instanceFromXml(pList.toXml())

pList2 = Playlist.fromXml(xmlPlaylist)
print(pList2.toXml())
print(type(pList2.toXml()))
## <type 'str'>
assert xmlPlaylist == pList2.toXml(), 'Pb during import/export'
assert xmlPlaylist2.toXml() == pList2.toXml(), 'Pb during import/export'
## End Snippet

"""
## Snippet "playlist-display"
<?xml version="1.0" encoding="utf-8" ?>
<Playlist name="My Favorites in eXtensible Markup Language">
  <Song artist="foo" length="300" file="foobar.ogg">
    <!--Blah blah-->
    <title>
        Bar
    </title>
  </Song>
  <Song length="250" file="opensource.ogg">
    <!--hey man it rocks-->
    <title>
        Track Name
    </title>
  </Song>
</Playlist>
## End Snippet
"""
