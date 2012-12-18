#!/usr/bin/env python
###### mframetest.py - MFrameTest ###########################################
##
##                                  MFrameTest
##
##  Copyright (C) 2012 Embecosm Limited
##
##  This file is part of MFrameTest.
##
##  MFrameTest is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  MFrameTest is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with MFrameTest. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################
##
##  Main MFrameTest Application
##
###############################################################################

import ConfigParser, sys

# Configuration and runtime variables
configname = None
config     = None
tester     = None
printer    = []
loaders    = []
testenv    = {}

VERSION = '1.0'

""" Function for reading Configuration Information """
def getConfig(section, name):
  if not config:
    sys.stderr.write('Error: Tried to load config with no config loaded')
    sys.exit(1)
  try:
    return config.get(section, name)
  except:
    sys.stderr.write('Warning: Config key not found \'%s\'/\'%s\'.\n' % \
      (section, name))
    return None

""" Main Function. This function loads a configuration file, sets up the
required classes and structures and starts tests """
def main():
  global configname
  global config
  # If no config file has been passed, then error
  if len(sys.argv) == 1:
    sys.stderr.write('Error: Config File Required\n')
    sys.exit(1)
  try:
    configname = sys.argv[1]
    config = ConfigParser.SafeConfigParser()
    config.readfp(open(configname))
  except:
    sys.stderr.write('Error: Unable to load config \'%s\'.\n' % (configname))
    sys.exit(1)

  # Print Application name and version if verbose
  if config.get('core', 'verbose') == '1':
    sys.stderr.write('MFrameTest ' + VERSION + '\n')
    sys.stderr.write('Copyright (C) 2012 Embecosm Limited\n\n')

  # Load tester and printer
  global tester
  testname = getConfig('core', 'tester')
  try:
    mod = __import__('testers.' + testname)
    tester = eval('mod.' + testname + '.' + testname + '(config)')
  except:
    sys.stderr.write('Error: Unable to load Tester \'%s\'.\n' % \
      (testname))
    sys.exit(1)
  global printer
  printnames = getConfig('core', 'printer').split(',')
  for printname in printnames:
    printname = printname.replace(' ', '') # Remove spaces from list
    try:
      mod = __import__('printers.' + printname)
      printer.append(eval('mod.' + printname + '.' + printname + '(config)'))
    except:
      sys.stderr.write('Error: Unable to load Printer \'%s\'.\n' % \
        (printname))
      sys.exit(1)
  
  # Load preloaders, setting test variables as required
  global loaders
  global testenv
  loadname = getConfig('core', 'preloaders').split(',')
  for load in loadname:
    load = load.replace(' ', '') # Remove spaces from list
    try:
      mod = __import__('preloaders.' + load)
      loaders.append(eval('mod.' + load + '.' + load + '(config, testenv)'))
    except:
      sys.stderr.write('Error: Unable to load Preloader \'%s\'.\n' % \
        (load))
      sys.exit(1)

  # Print environment if verbose
  if config.get('core', 'verbose') == '1':
    print 'Environment:'
    for param in sorted(testenv):
      print ' ', param + ':', testenv[param]
    print

  # Load previous run's tests for comparisons
  lasttest = printer[0].loadLastTest()

  # Call upon tester to carry out its test
  results = {}
  try:
    tester.execute(results, lasttest, testenv)
  except:
    sys.stderr.write('Error: Test execution failed.\n')
    sys.exit(1)

  # Pass test data to printer
  for p in printer:
    try:
      p.storeResults(results, testenv)
    except:
      sys.stderr.write('Error: Printer Storage failed.\n')
      sys.exit(1)
  
  # Finally tidy everything up
  # (If an exception is thrown, carry on)
  try:
    tester.cleanup()
  except:
    sys.stderr.write('Warning: Tester cleanup failed.\n')
  for p in printer:
    try:
      p.cleanup()
    except:
      sys.stderr.write('Warning: Printer cleanup failed.\n')
  for loader in loaders:
    try:
      loader.cleanup()
    except:
      sys.stderr.write('Warning: Preloader cleanup failed.\n')


if __name__ == '__main__':
  main()
