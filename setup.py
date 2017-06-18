#!/usr/bin/env python
import sys

try:
    from distutils.core import setup
    from distutils.command.sdist import sdist
except ImportError:
    print "python-dev package is missing."
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
        

setup( name = "EaseXML",
       version = "0.2.0",
       description = "An XML wrapper to Python Objects",
       long_description = """\
EaseXML is an object-xml mapper. It allows to translate XML to Python
objects and vice-versa. Your developer life is made easier :

- design some classes with special attributes
- manipulate the objects in the Python way
- input/output from/to XML data
- input/output from/to Python dictionaries
       """,
       keywords = [ 'xml', 'easy', 'data-binding', 'mapping', 'dtd', 'schema' ],
       url = "http://easexml.base-art.net",
       download_url = "http://easexml.base-art.net/download/",
       classifiers = [ "Development Status :: 3 - Alpha",
                       "Intended Audience :: Developers",
                       "License :: OSI Approved :: Python Software Foundation License",
                       "Programming Language :: Python",
                       "Topic :: Text Processing :: Markup :: XML",
                       "Topic :: Software Development :: Libraries :: Python Modules",
                     ],
       license = "PSF",
       author = "Philippe Normand",
       author_email = "phil@respyre.org",
       maintainer = "Philippe Normand",
       maintainer_email = "phil@respyre.org",
       packages = [ 'EaseXML', 'EaseXML.Validation' ],
       cmdclass = {'sdist': MySdist}
     )
