
import sys, os
from epydoc import cli, objdoc

os.chdir('..')
sys.argv.extend(['-o','www/API','EaseXML'])

objdoc.set_default_docformat('restructuredtext')
cli.cli()
print 'Done'
