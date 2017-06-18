# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

import sys,os
sys.path.append('..')

from XMLObject import *

class title(XMLObject):
    mainNode = TextNode()

class desc(title): pass
class info(title): pass
class separator(XMLObject): pass
class icon(XMLObject): pass

class alias(XMLObject):
    ref = IntegerAttribute()
    
class bookmark(XMLObject):
    href = StringAttribute()
    added = IntegerAttribute(optional=True)
    visited = IntegerAttribute(optional=True)
    title = ItemNode('title')

class folder(XMLObject):
    id = StringAttribute()
    added = IntegerAttribute(optional=True)
    folded = StringAttribute(default='yes',optional=True)
    toolbar = StringAttribute(default='no',optional=True)
    title = ItemNode('title', optional=True)
    info = ItemNode('info', optional=True)
    desc = ItemNode('desc', optional=True)
    icon = ItemNode('icon', optional=True)
    bookmarks = ListNode('bookmark')
    
class xbel(XMLObject):
    title = ItemNode('title')
    desc = ItemNode('desc',optional=True)
    folders = ListNode('folder')
    bookmarks = ListNode('bookmark')

if len(sys.argv) == 2:
    xbelFile = sys.argv[-1]
else:
    xbelFile = os.path.join(os.getenv('HOME'), 'bookmarks.xml')

f = open(xbelFile)
xb = xbel.fromXml(f.read())
f.close()

st =  xb.toXml()
st = st.encode('iso-8859-1')
f = open('out.xml','w')
f.write(st)
f.close()
