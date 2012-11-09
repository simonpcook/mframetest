###### dejagnu.py - DejaGnu Test Framework ####################################
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
##  Class for DejaGnu Testing
##
###############################################################################

import os, re, subprocess, sys

""" Class for DejaGnu Testing

Tests are 4-tuples with the following format:
(prefix, directory, command, site.exp) """
class dejagnu:
  _CONFIGKEY = 'test_dejagnu'
  config  = None
  verbose = False

  numtests = 0
  siteexp = None
  tests = []

  """ Function for reading Configuration Information """
  def getConfig(self, name):
    if not self.config:
      sys.stderr.write('Error: Tried to load config with no config loaded')
      sys.exit(1)
    try:
      return self.config.get(self._CONFIGKEY, name)
    except:
      return None

  """ Load module """
  def __init__(self, config):
    # Load config and set variables
    self.config = config
    try:
      if config.get('core', 'verbose') == '1':
        self.verbose = True
    except:
      pass

    # If we don't have a test specific config section, raise error
    if not self._CONFIGKEY in config._sections:
      sys.stderr.write('Error: Config for DejaGnu Tester not found. Is ' + \
        'this the correct tester?\n')
      sys.exit(1)
    
    # Parse dejagnu tester config for all tests
    self.numtests = int(self.getConfig('num_tests'))
    self.siteexp = self.getConfig('siteexp')
    if self.numtests < 1:
      sys.stderr.write('Error: Invalid number of tests.\n')
      sys.exit(1)
    for i in range(1, self.numtests + 1):
      testdir = self.getConfig('test_%i_dir' % i)
      if not testdir:
        testdir = os.getcwd()
      if testdir[0] != '/':
        testdir = os.getcwd() + '/' + testdir
      testcmd = self.getConfig('test_%i_cmd' % i)
      if not testcmd:
        sys.stderr.write('Error: Test %i has no run command.\n' % i)
        sys.exit(1)
      testsite = self.getConfig('test_%i_site' % i)
      if not testsite:
        testsite = self.siteexp
      if testsite[0] != '/' and testsite != 'None':
        testsite = os.getcwd() + '/' + testsite
      testprefix = self.getConfig('test_%i_pre' % i)
      if not testprefix:
        testprefix = ''
      self.tests.append((testprefix, testdir, testcmd, testsite))

    # Print config if verbose
    if self.verbose:
      print 'Global site.exp file:   ', self.siteexp
      print 'Number of DejaGnu tests:', self.numtests
      print 'Tests:'
      for i in xrange(self.numtests):
        print '  Test %i' % (i+1)
        print '    Test Prefix:   ', self.tests[i][0]
        print '    Test Directory:', self.tests[i][1]
        print '    Test Command:  ', self.tests[i][2]
        print '    Test Site:     ', self.tests[i][3]
      print

  """ Execute the tests that were loaded in the configuration """
  def execute(self, results, lasttest, testenv):
    for test in self.tests:
      # Clear output log for error handling
      out = ''
      if self.verbose:
        print 'Executing DejaGnu test \'%s\' with prefix \'%s\'' % \
          (test[2], test[0])
      try:
        # Move to directory and configure build environment
        os.chdir(test[1])
        os.environ['DEJAGNU'] = test[3]
        if test[3] == None or test[3] == 'None':
          # If dejagnu variable should not be set, remove it
          os.environ.pop('DEJAGNU')
        # Run test and log output
        # FIXME: Add a more "shell friendly" split system
        p = subprocess.Popen(test[2].split(' '), stdout=subprocess.PIPE, \
          stderr=subprocess.STDOUT)
        out = p.stdout.read()

        # Parse output log
        out = out.split('\n')
        curtest = None
        # pass, xfail, xpass, fail, unresolved, untested, unsupport
        result = [0, 0, 0, 0, 0, 0, 0]
        # FAIL, XPASS
        testlist = {'FAIL': [], 'XPASS': []}
        for line in out:
          newtest = re.match('\s*=== (.*) tests ===\s*?', line)
          # If we have a new test, save previous result if any
          if newtest:
            if curtest:
              # If we have previous results, create list of changed tests
              # otherwise all tests are new
              if curtest in lasttest:
                # Newly failed tests
                testlist['NEWFAIL'] = []
                for t in testlist['FAIL']:
                  if t not in lasttest[curtest]['FAIL']:
                    testlist['NEWFAIL'].append(t)
                for t in testlist['XPASS']:
                  if t not in lasttest[curtest]['XPASS']:
                    testlist['NEWFAIL'].append(t)
                # Newly fixed tests
                testlist['NOTFAIL'] = []
                for t in lasttest[curtest]['FAIL']:
                  if t not in testlist['FAIL']:
                    testlist['NOTFAIL'].append(t)
                for t in lasttest[curtest]['XPASS']:
                  if t not in testlist['XPASS']:
                    testlist['NOTFAIL'].append(t)
              else:
                testlist['NEWFAIL'] = testlist['FAIL'] + testlist['XPASS']
                testlist['NOTFAIL'] = []
              # Store results
              results[curtest] = {'results': result, 'testlist': testlist}
              if self.verbose:
                print curtest, result
            # Calculate new test name
            if test[0] != None and test[0] != 'None':
              curtest = test[0] + newtest.groups()[0]
            else:
              curtest = newtest.groups()[0]
            result = [0, 0, 0, 0, 0, 0, 0]
            testlist = {'FAIL': [], 'XPASS': []}

          elif 'of expected passes' in line:
            result[0] = int(line.replace('# of expected passes',''))
          elif 'of unexpected failures' in line:
            result[1] = int(line.replace('# of unexpected failures',''))
          elif 'of unexpected successes' in line:
            result[2] = int(line.replace('# of unexpected successes',''))
          elif 'of expected failures' in line:
            result[3] = int(line.replace('# of expected failures',''))
          elif 'of unresolved testcases' in line:
            result[4] = int(line.replace('# of unresolved testcases',''))
          elif 'of untested testcases' in line:
            result[5] = int(line.replace('# of untested testcases',''))
          elif 'of unsupported tests' in line:
            result[6] = int(line.replace('# of unsupported tests',''))
          elif line[:6] == 'FAIL: ':
            testlist['FAIL'].append(line[6:])
          elif line[:7] == 'XPASS: ':
            testlist['XPASS'].append(line[7:])

        # Finished processing file, process last set of results
        if curtest:
          # If we have previous results, create list of changed tests
          # otherwise all tests are new
          if curtest in lasttest:
            # Newly failed tests
            testlist['NEWFAIL'] = []
            for t in testlist['FAIL']:
              if t not in lasttest[curtest]['FAIL']:
                testlist['NEWFAIL'].append(t)
            for t in testlist['XPASS']:
              if t not in lasttest[curtest]['XPASS']:
                testlist['NEWFAIL'].append(t)
            # Newly fixed tests
            testlist['NOTFAIL'] = []
            for t in lasttest[curtest]['FAIL']:
              if t not in testlist['FAIL']:
                testlist['NOTFAIL'].append(t)
            for t in lasttest[curtest]['XPASS']:
              if t not in testlist['XPASS']:
                testlist['NOTFAIL'].append(t)
          else:
            testlist['NEWFAIL'] = testlist['FAIL'] + testlist['XPASS']
            testlist['NOTFAIL'] = []
          # Store results
          results[curtest] = {'results': result, 'testlist': testlist}
          if self.verbose:
            print curtest, result
      except:
        sys.stderr.write('Error: Failed to execute test with prefix \'%s\'\n' \
          % test[0])
        sys.stderr.write('Output was (if any):\n')
        sys.stderr.write(out)
        sys.stderr.write('\n')
        sys.exit(1)
    

  def cleanup(self):
    pass