#! python
# -*- coding: utf-8 -*-
# Copyright © 2017 Doug Henderson <djndnbvg@gmail.com>
# Copyright (C) 2004 Philippe Normand <phil@respyre.org>
#
# This file is part of EaseXML3 (http://easexml.base-art.net)
#
# Under PSF License (see COPYING)

from __future__ import print_function

import sys, os
from epydoc import cli
# from epydoc import objdoc

os.chdir('..')
sys.argv.extend(['-o','www/API','EaseXML3'])

# objdoc.set_default_docformat('restructuredtext')
cli.cli()

print('Done')
