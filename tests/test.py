# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

"""
    EaseXML3's unit-tests

"""

## We want to be able to run this both from the test directory and the
## parent directory, beeing sure that we test the development version,
## and not any old installed version of XMLObject.
import sys
sys.path.insert(0,'..')
sys.path.insert(1,'.')

from EaseXML3 import *
import unittest

## For compatibility with older python versions, not having
## False and True.
## (At least I assume so.  -- Tobias, 2004-10-07)
False = 0!=0
True  = 0==0

class Item(XMLObject):
    _entities = [ ('&xml;', 'eXtensible Markup Language')]
    _orderNodes = [ 'dummyData', 'content', 'comment' ]
    _orderAttrs = [  'position', 'record', 'cdataAttr', 'nmTok', 'nmToks' ]
    record = StringAttribute()
    position = IntegerAttribute(optional=False)
    content = TextNode()
    cdataAttr = CDATAttribute(permittedValues=['ok1','ok2'], optional=True)
    nmTok = NMTokenAttribute(optional=True)
    nmToks = NMTokensAttribute(optional=True)
    dummyData = RawNode()
    comment = CommentNode()

    def aMethod(self):
        return 'ok'

class TestEncoding(unittest.TestCase):
    """
    Tests that _encoding works as expected.  Both the xml and the
    python input/output should be encoded as specified.  Tobias thinks
    it could be a good idea to allow for different encodings on the
    XML output and on the python side, though it's not important for
    us right now.  In the future, we would probably want the
    possibility to get out TextNodes and TextAttributes as unicode
    typed strings.

    The Python unicode typed strings are supposedly always safe, those
    are strings that know their own encoding. Ideally we should only
    use such unicode strings in the python code.  However, the
    NordicBet code breaks a lot if we get unicodes instead of strings
    from the XMLObjects, it seems like Python or the Python libraries
    doesn't always accept unicodes when it expects a string.

    utf-8 is a way to encode a unicode string, keeping all ASCII
    characters intact, and using several bytes for the non-ASCII
    characters.  By calling unicode_str.encode('utf-8') we get out an
    ordinary string in utf-8 encoding.  This is an ordinary string
    that is not aware of its own coding.

    To examplify the latter, try running len(text), letting text be a
    string with accents.  In iso-8859-x, every character will be of
    one byte length, and len will thus give the number of characters.
    If the string is of unicode type, it will be aware of its own
    encoding, and it will also count the number of characters
    correctly.  In utf-8 encoding, at the other hand, non-ASCIIs are
    of several bytes length (western european characters are usually
    of two bytes length), and len() will count the number of bytes,
    making the text with accents look longer.
    """

    ## set up some norwegian special characters:
    no_latin1='\xe6\xf8\xe5'
    no_uc=unicode(no_latin1,'iso-8859-1')
    no_utf8=no_uc.encode('utf8')

    ## Sanity tests, not related to XMLObject:
    assert len(no_utf8)==6
    assert no_latin1==no_uc.encode('iso-8859-1')

    class Default(XMLObject):
        _unicodeOutput = False
        ## default encoding is UTF8
        testNode=TextNode()
        testAttr=StringAttribute()

    class Latin1(Default):
        _encoding='iso-8859-1'

    class UnicodeUTF8(Default):
        _unicodeOutput = True

    def runPlainTest(self,input,xmlclass,
                     expected_encoding,expected_py_output=None):
        """
        This test will create an instance of xmlclass, setting
        testNode and testAttr to the input parameter.  It will verify
        that the XML output is marked with the correct encoding.  It
        will verify that the XML is a string.  It will verify that
        when restoring the XMLObject, we get back expected_py_output
        (defaults to input).
        """

        if not expected_py_output:
            expected_py_output=input

        obj=xmlclass(testNode=input, testAttr=input)
        xml=obj.toXml()

        ## This seems to be the first one that breaks.  Since the XML
        ## output is a text string that we eventually may want to pass
        ## to clients not running Python, we should not let it be a
        ## unicode type, that's Python-specific.  Also, since the XML
        ## code explicitly tells about its own coding, it is and
        ## should be treated as a byte string.
        ## @PN: doesn't break anymore.
        self.assertEquals(type(xml),str)
        self.assert_(xml.count('encoding="%s"'%expected_encoding))

        obj2=xmlclass.fromXml(xml)
        self.assertEquals(obj2, obj)
        self.assertEquals(type(obj2.testNode),type(expected_py_output))
        self.assertEquals(obj2.testNode, expected_py_output)

    def testDefaultUTF8In(self):
        """
        We make a default object, and feed it with Norwegian
        characters in utf-8 encoding.  The default encoding is utf-8,
        and we expect utf-8 all over the line.
        """
        self.runPlainTest(input=self.no_utf8,
                          xmlclass=TestEncoding.Default,
                          expected_encoding="utf-8")

    def testDefaultUnicodeIn(self):
        """
        A bit more tricky; we feed the object with a unicode.
        Ideally, the object should discover that it's a unicode, and
        convert it to a utf-8 encoded string.
        """
        self.runPlainTest(input=self.no_uc,
                          xmlclass=TestEncoding.Default,
                          expected_encoding="utf-8",
                          expected_py_output=self.no_utf8)

    def testLatin1(self):
        """
        This is trivial, essentially same test as DefaultUTF8In, just
        that we use iso-8859-1 aka latin1 now
        """
        self.runPlainTest(input=self.no_latin1,
                          xmlclass=TestEncoding.Latin1,
                          expected_encoding="iso-8859-1")

    def testUnicodedObj(self):
        """
        So, we use the class with the Unicode-flag, both input and
        output of the testAttr and testNode is a unicode-typed string.
        """
        self.runPlainTest(input=self.no_uc,
                          xmlclass=TestEncoding.UnicodeUTF8,
                          expected_encoding="utf-8")

    def testUnicodedObj(self):
        """
        As testUnicodeObj, but we give the input as an utf-8-string
        """
        self.runPlainTest(input=self.no_utf8,
                          xmlclass=TestEncoding.UnicodeUTF8,
                          expected_encoding="utf-8",
                          expected_py_output=self.no_uc)


class GetSetTest(unittest.TestCase):

    klass = Item
    data = {'record':'AB1',
            'position':1,
            'content':'hey this is some content < &xml;',
            'dummyData': 'This is Dummy',
            'comment': 'this should be a comment'}

    def setUp(self):
        self.obj = self.klass(**self.data)

    def testGet(self):
        self.assertEqual(self.obj.content,'hey this is some content < &xml;')
        self.assertEqual(self.obj.position,1)
        self.assertEqual(self.obj.record, 'AB1')
        self.assertEqual(self.obj.dummyData, 'This is Dummy')
        self.assertEqual(self.obj.comment,'this should be a comment')

    def testSet(self):
        self.obj.position = 4
        self.assertEqual(self.obj.position, 4)
        # really dummy :( Could use self.obj.set() instead  of setattr()
        self.assertRaises(TypeError, setattr, self.obj, 'position', 'not a number')
        self.assertRaises(TypeError, setattr, self.obj, 'record', 2)

    def testNewAttrs(self):
        self.obj.cdataAttr = 'ok1'
        self.obj.nmTok = 'some_data:'
        s1 = self.obj.nmToks = """\
        few\t
lines of : text"""
        self.assertRaises(TypeError, setattr, self.obj, 'cdataAttr', '#not > ok')
        self.assertRaises(TypeError, setattr, self.obj, 'nmTok', 'few lines\n')
        self.assertRaises(TypeError, setattr, self.obj, 'nmToks', '#blah ')
        self.assertEqual(self.obj.nmTok,'some_data:')
        self.assertEqual(self.obj.cdataAttr,'ok1')
        self.assertEqual(self.obj.nmToks,s1)


class Playlist(XMLObject):
    name = StringAttribute()
    type = StringAttribute()
    items = ListNode('Item')
    comment = CommentNode()

class GetSetTest2(unittest.TestCase):

    klass = Playlist
    data = {'name':'foo',
            'comment': 'blah blah',
            'type':'xml' }

    itemsNb = 10
    defaultPositions = range(itemsNb)

    def setUp(self):
        self.obj = self.klass(**self.data)
        for i in self.defaultPositions:
            self.obj.items.append(Item(position=i, content=str(i)*5))

    def testGetList(self):
        self.assertEqual(len(self.obj.items), self.itemsNb)
        for i in self.defaultPositions:
            self.assertEqual(self.obj.items[i].position,i)

    def testSetList(self):
        class DummyItem(XMLObject): pass
        self.assertRaises(TypeError, self.obj.items.append, DummyItem())
        it = Item(position=0, content='Foo Bar')
        self.obj.items = [ it ]
        self.assertEqual(self.obj.items[0], it)


class ForEachTest(GetSetTest2):

    def findPositions(self, node, xmlObject, **kw):
        if node.getName() == 'position':
            self.positions.append(getattr(xmlObject,node.getName()))

    def testForEach(self):
        self.positions = []
        self.obj.forEach(self.findPositions)
        self.assertEqual(len(self.positions), len(self.obj.items))
        self.assertEqual(self.positions, self.defaultPositions)

class NewNameTest(unittest.TestCase):

    def testCorrectNaming(self):
        class Test(XMLObject):
            _name = 'altTest'
        self.assertEqual(Test().toXml(headers=0), "<altTest/>")

    def testSpaceNaming(self):
        class Test(XMLObject):
            _name = 'alt test'
        self.assertEqual(Test().toXml(headers=0), '<alt_test/>')

    def testTypeName(self):
        class IntTest(XMLObject):
            _name = 2

        class BoolTest(XMLObject):
            _name = True

        self.assertRaises(ValueError, IntTest().toXml)
        self.assertRaises(ValueError, IntTest().toXml)

class ImportExport:
    """ Partial Mixin for import/export tests.

        This class should be used in a mixin with `GetSetTest` class
        to perform tests relating the class-data import/export
        operations.

    """

    def testImport(self):
        obj2 = getattr(self.klass,self.importFunc)(self.xmlData)
        self.assertEqual(obj2, self.obj)

    def testExport(self):
        xml = getattr(self.obj,self.exportFunc)()
        self.assertEqual(xml, self.xmlData)

    def testExportImport(self):
        xml = getattr(self.obj,self.exportFunc)()
        obj2 = getattr(self.klass,self.importFunc)(xml)
        self.assertEqual(obj2, self.obj)

class XMLImportExportTest(GetSetTest, ImportExport):
    importFunc = 'fromXml'
    exportFunc = 'toXml'
    xmlData = """\
<?xml version="1.0" encoding="utf-8" ?>
<Item record="AB1" position="1">
  <!--this should be a comment-->
  <content>
      hey this is some content &lt; eXtensible Markup Language
  </content>
  <![CDATA[This is Dummy]]>
</Item>"""


class DictImportExportTest(GetSetTest,ImportExport):
    importFunc = 'fromDict'
    exportFunc = 'toDict'
    xmlData = {'record':'AB1', 'position':1, 'comment':'this should be a comment',
               'nmTok':None, 'cdataAttr': None, 'nmToks': None,
               'content':'hey this is some content < &xml;',
               'dummyData':'This is Dummy'}

class DeepDictImportExportTest(GetSetTest2, ImportExport):
    importFunc = 'fromDict'
    exportFunc = 'toDict'
    xmlData = {'comment': 'blah blah',
               'items': [{'comment': '', 'content': 5*str(i),
                          'dummyData': None, 'record': None,
                          'nmToks': None, 'position': i,
                          'nmTok': None, 'cdataAttr': None}
                         for i in GetSetTest2.defaultPositions ],
               'type': 'xml', 'name': 'foo'}

class InheritanceTest(unittest.TestCase):

    def checkDataForInstance(self, instance, data):
        for k,v in data.iteritems():
            self.assertEqual(getattr(instance, k), v)

    def testSimpleInherit(self):

        class MyPlaylist(Playlist):
            description = TextNode()

        class QPlaylist(MyPlaylist):
            pass

        data = {'name':'test', 'type':'xml',
                'description': "This is the playlist description"}
        pl = MyPlaylist(**data)

        self.checkDataForInstance(pl, data)
        self.assertEqual(pl.items, [])

        pl2 = MyPlaylist.fromXml(pl.toXml())
        self.assertEqual(pl2.toXml(), pl.toXml())

        qpl = QPlaylist(**data)
        self.checkDataForInstance(qpl, data)
        self.assertEqual(qpl.items, [])
        it = Item(record='foo', content='bar',position=1)
        qpl.items = [ it ]

        pl3 = QPlaylist.fromXml(qpl.toXml())
        self.assertEqual(pl3.toXml(), qpl.toXml())

    def testMultipleInherit(self):
        """
        Do some testing that "simple" multiple inheritation works as
        it should.  Currently (revision 77) XMLObject warns that there
        may be problems with multiple inheriation.  We don't like
        warnings while running the test suite, so we mute the logging
        as of now.
        """
        import logging
        logging.getLogger().setLevel(logging.ERROR)

        class Dummy:
            _name = 'foo bar'

        class MyOtherPlaylist(Playlist, Dummy):
            pass
        self.assertEqual(MyOtherPlaylist.getName(), 'foo_bar')
        logging.getLogger().setLevel(logging.DEBUG)

    def testListNodePolymorphism(self):

        class A1(XMLObject):
            content = TextNode(main=True, default="Fooo")

        class B1(A1):
            version = IntegerAttribute(default=2)

        class ABList(XMLObject):
            objs = ListNode('A1')

        abList = ABList()
        abList.objs.append(A1()) # OK
        abList.objs.append(B1()) # Semantically Ok, but ...
        self.assertEqual(abList.objs[-1], B1())


class Item2(XMLObject):
    _name = "item2"

class DummyItem(XMLObject):
    bl = ItemNode('Blah')

class Blah(XMLObject):
    mix = ChoiceNode(['Item2','Blah'])

class TestChoice(unittest.TestCase):

    def testLeftRecurse(self):
        class Item2(XMLObject):
            bl = ItemNode('Blah')
            txt = TextNode()
        b = Blah()
        it = Item2(txt="glop")
        it2 = DummyItem()
        self.assertRaises(LeftRecursionError, setattr, b, 'mix', it)
        self.assertRaises(LeftRecursionError, setattr, b, 'mix', it2)

    def testLeftRecurse2(self):
        b = Blah()
        b.mix = Item2(txt='glap')
        self.assertEqual(b.mix, Item2(txt='glap'))

        class Blah2(XMLObject):
            mix = ChoiceNode(['Blah2', 'Item2'])

        b = Blah2()
        self.assertRaises(LeftRecursionError, setattr, b, 'mix', Blah2())

    def testMultiples(self):
        class Item(XMLObject):
            content = RawNode()

        class Blah(XMLObject):
            mix = ChoiceNode(['Item', 'Blah'], noLimit=True)

        it1 = Item(content='item1')
        b1 = Blah()
        b1.mix.append(it1)
        b1.mix.append(b1)
        b1.mix.append(Item(content='item2'))
        b1.mix.append(it1)
        b1.mix.append(b1)


    def testOnce(self):
        class Item(XMLObject):
            content = RawNode()

        class Blah(XMLObject):
            mix = ChoiceNode(['Item', 'Blah'], noLimit=False)

        it1 = Item(content='item1')
        b1 = Blah()
        b1.mix = it1

        b2 = Blah.fromXml(b1.toXml())
        self.assertEqual(b1,b2)

class XXX(XMLObject):
    """
    <!ELEMENT XXX (AAA+ , BBB+)>
    <!ELEMENT AAA (BBB | CCC )>
    <!ELEMENT BBB (#PCDATA | CCC )*>
    <!ELEMENT CCC (#PCDATA)>
    """
    _name = 'xxx'
    aaa = ListNode('AAA',optional=False)
    bbb = ListNode('BBB',optional=False)

class AAA(XMLObject):
    _name = 'a_a'
    content = ChoiceNode(['BBB','CCC'],main=True)

class BBB(XMLObject):
    content = ChoiceNode(['#PCDATA', 'CCC'],optional=True, noLimit=True, main=True)

class CCC(XMLObject):
    _name = 'ccc'
    content = TextNode(main=True)


class TestChoiceListRaw(unittest.TestCase):

    def setUp(self):
        self.xxx = XXX()
        self.xxx.aaa.append(CCC('Precisely one element.'))

        bb = BBB()
        bb.append(CCC())
        bb.append(CCC())
        bb.append(CCC())

        self.xxx.aaa.append(bb)
        self.xxx.bbb.append(BBB())

        bb2 = BBB()
        bb2.append('This is ')
        bb2.append(CCC())
        bb2.append(' a combination ')
        bb2.append(CCC())
        bb2.append(' of ')
        bb2.append(CCC('CCC elements'))
        bb2.append('and text')
        bb2.append(CCC())

        self.xxx.bbb.append(bb2)
        self.xxx.bbb.append(BBB('Text only.'))

    def testExportImport(self):
        xxxStr = self.xxx.toXml()
        xxx2 = XXX.fromXml(xxxStr)
        self.assertEqual(xxx2, self.xxx)

    def testXXX(self):
        xx = XXX()
        self.assertRaises(TypeError, apply, 'append', xx.aaa, 'Some Text')
        self.assertRaises(TypeError, apply, 'toXml',  xx)

    def testAAA(self):
        aa = AAA()
        self.assertRaises(TypeError, apply, 'toXml',  aa)
        self.assertRaises(TypeError, AAA, 'Blah')
        aa = AAA(BBB('Test'))
        self.assertEqual(aa.content, BBB('Test'))
        aa = AAA(CCC('Test2'))
        self.assertEqual(aa.content, CCC('Test2'))

    def testBBB(self):
        bb = BBB()
        self.assertEqual(bb.toXml(headers=0), '<BBB/>')
        bb = BBB()
        bb.append('Toto')
        bb.append(CCC('Foo'))
        self.assertEqual(len(bb.content), 2)

class EntitiesTest(unittest.TestCase):

    def testQuote(self):
        class QuoteTest(XMLObject):
            _entities = [ ('&foo;', 'Bar')]
            title = StringAttribute()

        q = QuoteTest(title='some " quote &foo;')
        expected = '<QuoteTest title="some &quot; quote Bar"/>'
        self.assertEqual(q.toXml(headers=0), expected)
        self.assertEqual(QuoteTest.fromXml(expected).title, 'some " quote Bar')

    def testText(self):
        class Text(XMLObject):
            content = RawNode()

        t = Text("""Some ' and may be "some" quotes and &""")
        expected = """\
<Text>
  <![CDATA[Some ' and may be "some" quotes and &]]>
</Text>"""
        self.assertEqual(t.toXml(headers=0), expected)


class A(XMLObject):
    name = TextNode()
    opt_param = TextNode(optional = True)

class B(XMLObject):
    name = TextNode()
    a_list = ListNode("A")

class TobiasTest(unittest.TestCase):
    def testNameClash(self):
        b = B(name = "BLAH")
        b.a_list.append(A(name="1"))
        b.a_list.append(A(name="2"))

        xml = b.toXml()
        b1 = B.fromXml(xml)

        self.assertEqual(b1.name , "BLAH")
        self.assertEqual(len(b1.a_list) ,2)

    def testNoneAttr(self):
        a1 = A(name = "foo")
        self.assertEqual(a1.opt_param, None)
        a2 = A().fromXml(a1.toXml())
        self.assertEqual(a2.opt_param, None)


class TwoDeep(XMLObject):
    pass

class OneDeep(XMLObject):
    children = ListNode('TwoDeep')

class Root(XMLObject):
    children = ListNode('OneDeep')

class DeepTest(unittest.TestCase):
    expected = """\
<Root>
  <OneDeep>
    <TwoDeep/>
  </OneDeep>
</Root>"""

    def testOneAfterTwo(self):
        root = Root()
        one = OneDeep()
        two = TwoDeep()
        one.children.append(two)
        root.children.append(one)
        self.assertEqual(str(root), self.expected)
        self.assertEqual(str(Root.fromXml(str(root))),
                         self.expected)

    def testOneBeforeTwo(self):
        root = Root()
        one = OneDeep()
        root.children.append(one)
        two = TwoDeep()
        one.children.append(two)
        self.assertEqual(str(root),self.expected)
        self.assertEqual(str(Root.fromXml(str(root))),
                         self.expected)


    def testFirstChild(self):
        root = Root()
        one = OneDeep()
        root.children.append(one)
        two = TwoDeep()
        one.children.append(two)
        self.assertEqual(root.children[0],one)

class C(XMLObject):
    name = TextNode(optional=True)
    attr = StringAttribute()

class ExoWebTests(unittest.TestCase):
    def testTextNode(self):
        """
        This test tests the TextNode object and ensures that it does
        not turn '' values into None values.
        """
        # correct behavior = None values
        for val in (None, '', 'hello world'):
            c = C(name=val)
            c.getNodeWithName('attr').setOptional(True)
            self.assertEquals(C.fromXml(c.toXml()).name, val)

    def testNotEqualsNone(self):
        """
        When comparing an XMLObject with None, XMLObject used to
        raise an error.  I "fixed" this, though for a long time
        some_xml_object==None would return True.
        """
        C(attr="ffewf")
        self.assertEquals(C==None,False)
        self.assertEquals(C is None,False)
        self.assertEquals(C<None,False)
        self.assertEquals(C==None,False)
        self.assertEquals(C>None,True)
        self.assertEquals(C<>None,True)
        self.assertEquals(C!=None,True)

    def testRequiredAttribute(self):
        """Should bark when loading an XMLObject if required
        attributes are missing"""
        c2 = C()
        xml=c2.toXml()
        self.assertRaises(RequiredNodeError, C.fromXml, xml)

    def testNoneAttributes(self):
        class D(XMLObject):
            attr = StringAttribute(optional=True)
            intattr = IntegerAttribute(optional=True)

        c3 = D()
        self.assertEqual(c3.attr,None)
        self.assertEqual(c3.intattr,None)

    def testSmartFromXML1(self):
        class Sample(XMLObject):
            name = StringAttribute()

        xml = Sample(name = 'jacob').toXml()
        restored_xml_object = XMLObject.instanceFromXml(xml)
        self.assert_(isinstance(restored_xml_object, Sample))
        self.assertEqual('jacob', restored_xml_object.name)

    def testSmartFromXML2(self):
        class Sample2(XMLObject):
            _name = 'fooIsh'
            name = StringAttribute()

        xml = Sample2(name = 'jacob').toXml()
        restored_xml_object = XMLObject.instanceFromXml(xml)
        self.assert_(isinstance(restored_xml_object, Sample2))
        self.assertEqual('jacob', restored_xml_object.name)



class StripTest(unittest.TestCase):

    def testPrettyPrint(self):
        class Unpretty(XMLObject):
            _prettyPrint = False
            node = TextNode()

        class Pretty(Unpretty):
            _prettyPrint = True

        pretty=Pretty(node='test')
        unpretty=Unpretty(node='test')

        ## The pretty and unpretty should be compatible with each other
        self.assertEquals(pretty,Pretty.fromXml(unpretty.toXml()))
        self.assertEquals(unpretty,Unpretty.fromXml(pretty.toXml()))

        ## Unpretty XML should be without whitespace
        self.assert_(unpretty.toXml().count('>test<'))

        ## pretty XML should be with whitespace
        self.assertEquals(pretty.toXml().count('>test<'),0)

    def testStripIt(self):
        class StripTease(XMLObject):
            _stripStrings = False
            content = TextNode()

        data = ' \t       Ouch !   ! !! !!!            \n   '
        st = StripTease(content=data)
        st2 = StripTease.fromXml(st.toXml())

        self.assertEqual(st2, st)
        self.assertEqual(st2.content, st.content)

if __name__ == '__main__':
    unittest.main()
