#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

from __future__ import print_function

import sys

try:
    from distutils.core import setup
    from distutils.command.sdist import sdist
except ImportError:
    print("python-dev package is missing.")
    sys.exit()

# patch distutils if it can't cope with the "classifiers" keyword
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None


class MySdist(sdist):
    def prune_file_list (self):
        " exclude .svn versioning infos "
        sdist.prune_file_list(self)
        self.filelist.exclude_pattern(r'/(\.svn)/.*', is_regex=1)


setup( name = "EaseXML3",
       version = "0.3.0",
       description = "An XML wrapper to Python Objects",
       long_description = """\
EaseXML3 is an object-xml mapper. It allows to translate XML to Python
objects and vice-versa. Your developer life is made easier :

- design some classes with special attributes
- manipulate the objects in the Python way
- input/output from/to XML data
- input/output from/to Python dictionaries
       """,
       keywords = [ 'xml', 'easy', 'data-binding', 'mapping', 'dtd', 'schema' ],
       url = "http://www.example.com",
       download_url = "http://www.example.com/download/",
       classifiers = [ "Development Status :: 3 - Alpha",
                       "Intended Audience :: Developers",
                       "License :: OSI Approved :: Python Software Foundation License",
                       "Programming Language :: Python",
                       "Programming Language :: Python :: 2",
                       "Programming Language :: Python :: 2.7",
                       "Programming Language :: Python :: 3",
                       "Programming Language :: Python :: 3.6",
                       "Topic :: Text Processing :: Markup :: XML",
                       "Topic :: Software Development :: Libraries :: Python Modules",
                     ],
       license = "PSF",
       author = "Doug Henderson",
       author_email = "djndnbvg@gmail.com",
       maintainer = "Doug Henderson",
       maintainer_email = "djndnbvg@gmail.com",
       packages = [ 'EaseXML3', 'EaseXML3.Validation' ],
       cmdclass = {'sdist': MySdist}
     )
