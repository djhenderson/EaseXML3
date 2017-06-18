------------------------
EaseXML Documentation
------------------------

.. contents:: Menu

.. hint::

  If you're reading this file as pure ReST text, use the `buildDoc` script
  provided with the source distribution of EaseXML or read the HTML
  version located at www/doc.html in the source distribution.


Why using EaseXML ?
-------------------

Are you bored fighting with SAX and DOM to deal with your XML data ?
EaseXML combines the best Object Oriented features of Python with XML
management. Declare some classes inheriting from the `XMLObject` type,
you don't have to know the internals, you deal with Objects, you get
XML. That's all.

EaseXML is released under the `Python Licence`_, much known as PSF
(standing for Python Standard Foundation Licence). Since EaseXML
widely uses new-style classes it requires at least Python 2.2.

.. _Python Licence: http://www.python.org/psf/

If you're looking for some kind of persistance system in EaseXML, you
may be desapointed. XMLObjects are basically designed to handle and
store data. More *complex* concepts like circular references - which
seem to be vital for persistance management - lack in EaseXML. There
are **real** Python persistance frameworks like XMLPickle and systems
built around YAML.

EaseXML is at an early stage development. So it currently doesn't
provide support for all XML the features described in the W3C papers. The
effort is made on simplifying XML management. Current planned features
are: 

- xmlns support
- Validation (Schema, DTD, Relax NG?)
- Transitions from/to {Schema,DTD}

EaseXML is not the only XML Python wrapper around. Next section
deals with the most significant differences between EaseXML and the
others object-xml mappers.

Compared to others
------------------

Well there is quite a bunch of XML tools in Python, especially data
bindings. Uche Ogbuji made the `State of Python-XML in 2004`_, a very
interesting paper. Here i mention most (in my opinion) used data
bindings.

Anobind_, ElementTree_ and gnosis.xml.objectify_ can bind arbitrary
XML data, you don't need to use or define XML grammars (Schema, DTD,
Python classes) to make them work. All of them support XPath queries,
namespaces, multiple parsers (scalability) and many other things i
haven't explored yet. Between the 3, my preference goes to
ElementTree. I believe it's the more mature and Pythonic one, it
doesn't depends on many things other than Python itself.

generateDS.py_ is a little different from the three above. You need to
supply an XSchema describing the data format you want to handle with
generateDS. Then, generateDS generates Python classes acting as
bindings to the XML data. Thus classes customization is rather limited. 

EaseXML takes yet another approach. Though validation support and
arbitrary data loading are planned features, i currently prefer
definining custom classes describing the data format i want to deal
with. It's the simplest way, in my opinion and i admit i'm too lazy to
write Schemas or DTDs ;-)

.. _Anobind: http://uche.ogbuji.net/tech/4Suite/anobind/
.. _ElementTree: http://effbot.org/downloads/
.. _generateDS.py: http://www.rexx.com/~dkuhlman/#generateDS
.. _gnosis.xml.objectify: http://gnosis.cx/download/


Now let's go deeply in EaseXML !

Common behavior
---------------

In a wonderful world the developper would have an XML Schema, a DTD
describing an XML grammar or even some XML samples. He would then like
to store data in XML format conforming to that "specifications". And
finally, a program would feed and/or read valid XML data.

Well, the final goal of EaseXML is to handle all of that. Though XML
grammar support is unfinished, the developper can still define some
Python bindings (as new-style classes) describing some implicit XML
grammars. Then, dealing with XML data is as simple as using usual
Python objects. Import and export routines are transparent to the
user. Each XMLObject class instance can be expressed as an XML
fragment.

The next sections cover a little, but significant example used to show
how to use EaseXML when designing an XML-related class
hierarchy. We'll try to read some RSS feeds using EaseXML.

Classes declarations
--------------------

Declaring EaseXML classes can be compared to writing a DTD or a
Schema. But it's far more readable. Though for now EaseXML is less
powerfull than DTD and Schema to handle all XML grammar
possibilities. Here is how the first XMLObject-derived class looks
like:

.. raw:: html
   :file: ../examples/snippets/RSS-decl.html

As you may have guessed, the XML tag associated to that class will
be named "rss". It will have one attribute named "version" and a
sub-node, handled by another XMLObject called `Channel` (cf its code,
later on). The object also includes a processing instruction referring
to an XSL stylesheet. So far so good ? It's a quite simple binding to start
on. But following XMLObjects will be a little more complete.

Nodes
~~~~~

Basically, an XMLObject holds some Nodes (`StringAttribute` and
`ItemNode` in above example) and a set of facultative options (`_name`
for instance). There are two Node families :

- The attributes (e.g `<obj attr="something" />`):

  * CDATAttribute : string data
  * NMTokenAttribute : any string except `:_-.` characters
  * NMTokensAttribute : NMTokenAttribute without space nor tabs nor
    carriage return characters
  * StringAttribute : any string data (just like CDATAttribute but
    with a more friendly name)
  * IntegerAttribute : integer data

- The content (sub-tag) nodes:

  * TextNode : storing 'string' data
  * RawNode  : storing string-with-annoying-characters (<,>,&,...) in
    a CDATA section (example: `<![CDATA[blah < > e]]>`)
  * ItemNode : referring to another XMLObject
  * ListNode : build a list storing XMLObjects of a given type
  * ChoiceNode : like ItemNode, but can refer to itself or any other Type of Node
  * CommentNode : inserting comments in the XML (`<!-- ... -->`)
  * ProcessingInstructionNode : declare an XML processing instruction  (`<?name option1="..." ... ?>`)

Each Node has a set of options declared as keyword parameters to the
Node constructor. Common Node options are:

* `main`: boolean attribute to indicate wether the Node is the only
  one content Node (not Attribute !) handled by the XMLObject
  (`False` by default)
* `default`: setting a default value to use when none is explicitely
  given for that Node (`None` by default)
* `optional`: boolean switch indicating if the user can omit to set
  a value for that Node (`False` by default)
* `title`: the name to give to the corresponding XML tag or
  attribute (defaults to the Python variable name)
* `noLimit`: **ChoiceNode Specific option** indicating if the Node
  can behave as a multi-typed ListNode (see later for a more
  complete explanation on that option). `False` by default
      
XMLObject options
~~~~~~~~~~~~~~~~~

Few XMLObject class attributes may be overriden to customize the
XMLObject behavior:

- `_name` : providing a new string to identify the XMLObject instead
  of the class name. If `_name` contains some space characters, they
  are replaced by underscores.
- `_entities` : a list storing tuple entities
  (e.g, `('&toBeReplaced;', u'this is very very long data')`)
- `_encoding` : a string representing the XML encoding to use during
  XML import/export. Its value defaults to 'utf-8'. The `_encoding` 
  attribute is very important when dealing with accentuated data. 
- `_unicodeOutput`: boolean switch indicating wether the XMLObject
  should output Python Unicode typed strings or not (defaults to
  `True`). This option is important if you're willing to communicate
  XML data with an external non-Python entity.
- `_stripStrings` : a boolean value indicating whether EaseXML
  should strip strings during i/o operations. True by default.
  The `_stripStrings` can be very usefull with XMLObjects dealing
  with large bunches of data. When this attribute is set to False,
  `toXml` method's speed execution will be very improved because
  output data won't be beautified (indentations, etc.)
- `_prettyPrint` : a boolean indicating whether the XML output should
  be human-readable (tags indented, ..) or not.
- Nodes ordering options (when order cares for XML parsers ?) By
  default, EaseXML uses the alphabetical order, you can override this
  behavior: 

  * `_attrsOrder`: usefull if you want to order an XMLObject
    Attributes list, e.g, ``_attrsOrder = [ 'opt1', 'attr2']``

  * `_nodesOrder`: the same, but for content Nodes.

Well, Ok. There's a little bunch of options to customize your
XMLObjects, but in most cases you should be happy with the
defaults. Below are last two XMLObject declarations, completing the
example class-hierarchy (RSS 1<-->1 Channel 1<-->0..n Item)

.. raw:: html
   :file: ../examples/snippets/ChannelItem-decl.html

After declaring your classes you can use them to store and load data.

Using the classes
-----------------

Data management
~~~~~~~~~~~~~~~

Since XMLObjects behave as data storage structures, there comes a time
where the developer needs to give and/or extract data to/from the
XMLObjects he defines in his code, such as for the RSS example below:

.. raw:: html
   :file: ../examples/snippets/RSS-feeding.html

The code above is trivial to understand, we create one `Rss` instance to
the which we link a `Channel` instance. Then we add two `Item` data
holders to the channel. Thus we have an RSS feed containing two
items. In the example above we use default values for ``link``,
``description`` and ``language`` attributes since they are not
explicitely overriden.

`ListNode` behave just as Python lists, you can explicitely assign
them, extending, inserting, iterating (of course :) on them:

.. raw:: html
   :file: ../examples/snippets/RSS-items.html

Tree parsing
~~~~~~~~~~~~

Basically XML structures are trees, so it's very common to parse XML
trees and perform custom actions on each node of the tree. This kind
of thing can easily be done as shown in the example below:

.. raw:: html
   :file: ../examples/snippets/RSS-forEachItem.html

The ``forEach`` method, applied to an XMLObject instance will perform
a given action, symbolized by a callable object (lambda forms,
functions) to which some parameters will be passed. The callback
signature shall be the same as for `printNodeName` example
function,e.g:

.. raw:: html
   :file: ../examples/snippets/forEachCallback.html

One warning though, the developer might care about `forEach`
performances, especially on deep XMLObjects (e.g, with nested
ItemNodes, ListNodes and ChoiceNodes). Walking over a deep tree can
turn to be painful for your computer's CPU. You've been warned ;-)

Import-Export
-------------

Dealing with XML
~~~~~~~~~~~~~~~~

Well the final goal of EaseXML is to output some XML data. To do so,
use the `toXml` method. If you want to build an XMLObject given its
XML representation, use either the `fromXml` class method or
`XMLObject.instanceFromXml` class method.

.. raw:: html
   :file: ../examples/snippets/RSS-XML-import-export.html

The main advantage of using `instanceFromXml` over `fromXml` is that
you don't need to know the class corresponding to the XML you want to
feed in. Though currently (0.2.0), **EaseXML cannot bind XML data it
doesn't know**, e.g there must exist an XMLObject class in the
namespace either `instanceFromXml` will fail and raise a `ParseError`
exception.

`XMLObject.toXml()` method outputs XML data as a byte string (not Unicode
typed). Since the XML declare its own encoding, we don't need to care
wether the string should be Unicode or not. Here is some XML sample output :

.. raw:: html
   :file: ../examples/snippets/RSS-XML-output.html

Keyword paramaters can be passed to `toXml` method:

- `headers`: boolean switch to tell if you want the <? ?> processing
  instruction(s) placed on XML data head. 
- `tabLength`: integer indicating the tabulation length (2 by default)
- `prettyPrint` : boolean value (True by default) overriding
  `_prettyPrint` class attribute.

That's it for XML import/export API, it remains as simple as
possible. Maybe a more Pythonic behavior : use `str(myXMLObjInstance)`
to get the same result as `myXMLObjInstance.toXml(headers=0)`. 

Python Dictionnaries
~~~~~~~~~~~~~~~~~~~~

Many Python-XML data binders provide dictionary-like access to the XML
bindings (`foo[attr]`). EaseXML can export data it handles as
dictionaries, though `__getitem__` and `__setitem__` behaviors are not
directly supported.

.. raw:: html
   :file: ../examples/snippets/RSS-dict-output.html

About ChoiceNode
----------------

ChoiceNode is a little more complicated that other Node types and thus
requires a dedicated paragraph. 

Mixed content
~~~~~~~~~~~~~

It's very common that a tag (say `body` in XHTML) stores many kinds of
sub-tags (`h1`, `h2, `pre`, `a`, ...) So you want to store mixed
content in XML, ChoiceNode is what you need. Let's consider the
following specification:

.. raw:: html
   :file: ../examples/snippets/xxx-decl2.html


The `BBB` class which can store either strings (`#PCDATA`) either
`CCC` objects zero or many times (`*`). `#PCDATA` is a special
alternative handled by `ChoiceNode`. It means that strings without
enclosing tag can be inserted in `ChoiceNode`. The following snippet
shows how to use `BBB`:

.. raw:: html
   :file: ../examples/snippets/xxx-fill-in2.html

Because BBB can store many objects (`noLimit=True`), it behaves as a
list, just like `ListNode` but it can store more than one XMLObject
type. The XML output looks like this:

.. raw:: html
   :file: ../examples/snippets/xxx-display2.html

Recursive structures
~~~~~~~~~~~~~~~~~~~~

Sometimes it's interesting to provide recursive structures. For
instance a `Section` can store a `title`, and a `Paragraph` or another
`Section`:

.. raw:: html
   :file: ../examples/snippets/section-decl.html

But, to avoid left recursion, 'Section' reference cannot be the first
in the alternatives list, or a `LeftRecursionError` will be
raised. Using such structures is trivial:

.. raw:: html
   :file: ../examples/snippets/section-usage.html

We're done with ChoiceNode. Its usage remains simple when you know how
to use it correctly :-)

Limitations
-----------

As mentionned in the beginning of this document, EaseXML lacks few
nice features, mainly validation support. Second point, EaseXML can't
bind arbitrary XML data, e.g the developer has to define XMLObjects
according to the XML data structures he wants to handle.

Another interesting point is scalability. EaseXML has not really been
tested with wide data sets. Internally it uses `xml.minidom` to parse
incoming (`fromXml`) data. This parser (and more generally DOM) store
entire data trees on dynamic memory, thus potentially eat **lots** of
memory. Other parsers like *PyRXP* or *expat* may be more suitable in
these cases and i'm considering bringing support for them in next
EaseXML versions, though help/patches are always very welcome :-)


Exported Symbols
----------------

Simply doing `from EaseXML import *` won't pollute much your
namespace. Though here are exported symbols detailled per module:

From EaseXML.main:

* `XMLObject`
* `ParseError`

From EaseXML.Node:

* `Node`
* `RequiredNodeError`

From EaseXML.Nodes:

* `ItemNode`
* `ListNode`
* `TextNode`
* `ChoiceNode`
* `RawNode`
* `CommentNode`
* `ProcessingInstructionNode`
* `LeftRecursionError` (raised by `ChoiceNode`)

From EaseXML.Attributes:

* `CDATAttribute`
* `NMTokenAttribute`
* `NMTokensAttribute`
* `StringAttribute`
* `IntegerAttribute`

For a more complete reference about EaseXML internals and API, the
interested developer shall consult the `online API documentation`_.

.. _online API documentation: http://easexml.base-art.net/API/

Thanks
------

I'd like to thank Ian Bicking for :

- his `classregistry` module coming from SQLObject. This module is
  used to remember classes given their name.
- the `examplesstripper.py` script helping to produce code snippets in
  XHTML, very useful when writting this documentation sheet.
- SQLObject globally which is a good source of inspiration for
  EaseXML.

ExoWeb_ people are active users, debuggers of EaseXML and i thank them
for the many enhancements and feedback they provide to this software
in general. 

.. _ExoWeb: http://exoweb.net

Back
----
Go back to index

.. _`State of Python-XML in 2004`: http://www.xml.com/pub/a/2004/10/13/py-xml.html
