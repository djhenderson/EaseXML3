#
# a Python code generator backend
#
# fredrik lundh, march 1998
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# $HeadURL: https://svn.base-art.net/full/easexml/trunk/EaseXML/CodeGeneratorBackend.py $
# $Id: CodeGeneratorBackend.py 76 2004-11-11 20:31:59Z phil $


import sys, string

class CodeGeneratorBackend:

    def begin(self, tab="    "):
        self.code = []
        self.tab = tab
        self.level = 0

    def end(self):
        return string.join(self.code, "")

    def write(self, string):
        toWrite = self.tab * self.level + string
        self.code.append(toWrite)

    def writeln(self, string):
        self.write(string + '\n')

    def indent(self):
        self.level = self.level + 1

    def dedent(self):
        if self.level == 0:
            raise SyntaxError, "internal error in code generator"
        self.level = self.level - 1

    def generate(self, filename=None):
        if not filename:
            exec( self.end() )
        else:
            f = open(filename,'w')
            f.write( self.end() )
            f.close()
