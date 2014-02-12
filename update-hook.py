#!/usr/bin/python3

import os
import sys
import subprocess

from parser import parseFile
from serializer import serializeRecipes

TARGET='/var/www/localhost/htdocs/uhu01/fh/'

def process( file, target):
    r = parseFile(file)
    e = etree.ElementTree(serializeRecipes(r))
    e.write(target,xml_declaration=True,pretty_print=True,encoding='UTF-8')

def changed_files(old,new):
   environ = os.environ.copy()
   proc = subprocess.Popen(['git','diff','--name-status','{}..{}'.format(old,new)], stdout=subprocess.PIPE, env=environ)
   proc.wait(1000)

   if proc.returncode != 0:
      print('git process failed ({})'.format(proc.returncode))
      exit(1)

   return [ l.decode('utf8').strip('\n').split('\t') for l in proc.stdout ]

(ref,old,new) = sys.argv[1:4]

print('starting processing of commit')

cf = changed_files(old,new)

# do a dry run to catch errors
for f in cf:
    if f[0] == 'M' or f[0] == 'A' or f[0] == 'C':
        r = processFile(f[0],'/dev/null')

# do a real run
for c in changed_files(old,new):
   action = c[0]
   file = c[1]
   if action == 'D':
      print('D {}'.format(file))
      try:
         os.remove(TARGET + c[1] + '.xml')
      except FileNotFoundError:
         pass
   elif action == 'M' or action == 'A' or action == 'C':
      print('C {}'.format(file))
      process( file, TARGET + file + '.xml')
   else:
      print('unknown git status {} of <{}>'.format(action,file), file=sys.stderr)
#updateList()

print('finished processing of commit')

exit(1)

