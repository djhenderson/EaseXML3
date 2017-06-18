# -*- coding: iso8859-1 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)


import re

class NotWellFormedXML(Exception):
    def __init__(self, misMatched, expected):
        self.misMatched = misMatched
        self.expected = expected

    def __str__(self):
        return 'Expected an "%s" closing tag before the "%s" tag.' % (self.expected,
                                                                      self.misMatched)

    __repr__ = __str__

class NoCallbackError(Exception):
    def  __init__(self, xmlData):
        self.xml = xmlData

    def __str__(self):
        return "Don't know how to handle '%s'" % self.xml

    __repr__ = __str__

class PrettyXMLPrinter(object):
    regexps = [ ('processing_instruction', re.compile('<\?([^?]*)\?>')),
                ('cdata', re.compile('<\!\[CDATA\[(.*\s*.*)\]\]>',re.DOTALL)),
                ('comment', re.compile('<\!-- ([^<\-\-]*) -->')),
                ('begin_tag', re.compile('<([-a-zA-Z0-9_]+)((\s+[-a-zA-Z0-9_]+=\\"[^"]*\\")*)(/)?>')),
                ('end_tag', re.compile('</([-a-zA-Z0-9_]*)>') ),
                ('content', re.compile('^[^<]')),
                ]

    def __init__(self):
        self._reset()

    def _reset(self):
        self._tags = []

    def _buildTag(self, tagName, attrs, alone=False):
        tag = '<%s' % tagName
        if attrs:
            tag += attrs
        if alone:
            tag += '/'
        tag += '>'
        return tag

    def prettyPrint(self, stringToProcess, indent=' '):
        result = ''
        stringToProcess = stringToProcess.strip()
        self._indent = indent
        while stringToProcess:
            backup = stringToProcess
            for reName, regexp in self.regexps:
                reResult = regexp.match(stringToProcess)
                if reResult:
                    callback = getattr(self, 'handle_%s' % reName)
                    toAppend, stringToProcess = callback(stringToProcess,
                                                         reResult.groups())
                    result += toAppend
                    break
            if backup == stringToProcess:
                self._reset()
                raise NoCallbackError(stringToProcess)
        self._reset()
        return result[:-1]

    def handle_processing_instruction(self, stringToProcess, reGroups):
        " Processing Instruction "
        content = reGroups[0]
        pi = '<?%s?>' % content
        stringToProcess = stringToProcess[len(pi):]
        return pi + '\n', stringToProcess

    def handle_comment(self, stringToProcess, reGroups):
        " Comment "
        content = '<!--%s-->' % reGroups[0]
        end = stringToProcess.find('-->') + 3
        result = self._indent * len(self._tags) + content + '\n'
        stringToProcess = stringToProcess[end:]
        return result, stringToProcess


    def handle_begin_tag(self, stringToProcess, reGroups):
        " Begin Tag "
        tagName, attrs = reGroups[:2]
        alone = reGroups[-1]
        tag = self._buildTag(tagName, attrs, alone)
        result = self._indent * len(self._tags) + tag + '\n'
        stringToProcess = stringToProcess[len(tag):]
        if not alone:
            self._tags.append(tagName)
        return result, stringToProcess

    def handle_content(self, stringToProcess, reGroups):
        " Element's content "
        nextTagIndex = stringToProcess.find('<')
        content = stringToProcess[:nextTagIndex]
        result = ''
        stringToProcess = stringToProcess[nextTagIndex:]
        content = content.strip()
        if content:
            result = self._indent * (len(self._tags) + 1) + content + '\n'
        return result, stringToProcess

    def handle_cdata(self, stringToProcess, reGroups):
        " CDATA section "
        end = stringToProcess.find(']>') + 2
        result = self._indent * len(self._tags) + stringToProcess[:end] + '\n'
        stringToProcess = stringToProcess[end:]
        return result, stringToProcess

    def handle_end_tag(self, stringToProcess, reGroups):
        " Closing Tag "
        tagName = reGroups[0]
        tag = '</%s>' % tagName
        lastTag = self._tags[-1]
        if lastTag == tagName:
            self._tags = self._tags[:-1]
        else:
            self._reset()
            raise NotWellFormedXML(tagName, lastTag)
        result = self._indent * len(self._tags) + tag + '\n'
        stringToProcess = stringToProcess[len(tag):]
        return result, stringToProcess

if __name__ == '__main__':
    import unittest

    class PrettyPrintTest(unittest.TestCase):

        def setUp(self):
            self.printer = PrettyXMLPrinter()

        def testMultiLevels(self):
            s = """\
<?xml version="1.0" ?><blah><!-- some comments --><!-- another comment --><![CDATA[some cdata é à @ !? <&>]]><item>item1</item><blah><item>item1</item></blah></blah>
"""

            expected = """\
<?xml version="1.0" ?>
<blah>
 <!-- some comments -->
 <!-- another comment -->
 <![CDATA[some cdata é à @ !? <&>]]>
 <item>
   item1
 </item>
 <blah>
  <item>
    item1
  </item>
 </blah>
</blah>"""
            xml = self.printer.prettyPrint(s)
            self.assertEqual(xml,expected)

        def testNotWellFormed(self):
            s2 = """\
<blah><item>item1<blah><item>item1</item></blah></blah>
"""
            self.assertRaises(NotWellFormedXML,self.printer.prettyPrint,s2)

        def testURLs(self):
            s3 = """\
<url blah="/test" boh="http://toto.com?foo=bar"/><url blah="/test"/><url blah="/test"/>"""

            expected = """\
<url blah="/test" boh="http://toto.com?foo=bar"/>
<url blah="/test"/>
<url blah="/test"/>"""
            self.assertEqual(self.printer.prettyPrint(s3), expected)


    unittest.main()
