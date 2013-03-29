###### github.py - GitHub Wiki Printer ########################################
##
##                                  MFrameTest
##
##  Copyright (C) 2012-2013 Embecosm Limited
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
##  Class for Printing results to a GitHub Powered Wiki
##  (This uses supported MediaWiki syntax so code can be shared with MW class)
##
###############################################################################

import math, os, re, subprocess, sys

""" Class for storing results to GitHub """
class github:
  _CONFIGKEY  = 'print_github'
  config      = None
  verbose     = False
  remote      = None
  index       = None
  key         = None
  wikidir     = None
  description = None

  """ Default Wiki Index Page """
  _DEFAULT_INDEX = """This page contains the summary of test results for %s
{|
<!-- ## NEXTROW ## -->
|}
<!-- ## NEXTKEY 1 ## --> """

  """ Default Test Page """
  _DEFAULT_TESTPAGE = """
__NOTOC__
[[%s-Test-%i| &laquo; Previous Test]] | [[%s-Test-%i| Next Test &raquo;]]

''Note:'' As pass results may be large and push the limits of the wiki,
they are on a separate page, [[%s-Passes-%s|here]]. Lists of newly broken/fixed
tests can be found [[%s-Changed-%s|here]].
== Test Environment ==
%s
== Test Results ==
%s
"""

  """ Class Constructor. Loads and parses configuration. """
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
      sys.stderr.write('Error: Config for GitHub Printer not found. Is ' + \
        'this the correct printer?\n')
      sys.exit(1)

    # Load config
    self.remote = self.getConfig('remote')
    if self.remote == None:
      sys.stderr.write('Error: GitHub config is missing remote URL.\n')
      sys.exit(1)
    self.wikidir = self.getConfig('wikidir')
    if self.wikidir == None:
      sys.stderr.write('Error: GitHub config is missing wiki directory.\n')
      sys.exit(1)
    # Modify wikidir as cwd may be incorrect when needed
    if self.wikidir[0] != '/':
      self.wikidir = os.getcwd() + '/' + self.wikidir
    self.index = self.getConfig('index')
    if self.index == None:
      sys.stderr.write('Error: GitHub config is missing index page name.\n')
      sys.exit(1)
    self.key = self.getConfig('key')
    if self.key == None:
      sys.stderr.write('Error: GitHub config is missing test key.\n')
      sys.exit(1)
    self.description = self.getConfig('Description')
    if self.description == None:
      self.description = 'Unnamed Test Suite'

    # If the wiki does not yet exist locally, clone it    
    if not os.path.exists(self.wikidir):
      if self.verbose:
        sys.stderr.write('Info: Wiki Directory does not exist, cloning...\n')
      p = subprocess.Popen(['git', 'clone', self.remote, self.wikidir],
        stdout=file('/dev/null','wb'), stderr=subprocess.STDOUT)
      if p.wait() != 0:
        sys.stderr.write('Error: Unable to clone wiki\n')
        sys.exit(1)
    # Update wiki
    else:
      olddir = os.getcwd()
      os.chdir(self.wikidir)
      p = subprocess.Popen(['git', 'pull'], stdout=file('/dev/null','wb'),
        stderr=subprocess.STDOUT)
      if p.wait() != 0:
        sys.stderr.write('Error: Unable to upate wiki\n')
        sys.exit(1)
      os.chdir(olddir)

  """ Helper function to pull class-specific configuration variables """
  def getConfig(self, name):
    if not self.config:
      sys.stderr.write('Error: Tried to load config with no config loaded')
      sys.exit(1)
    try:
      return self.config.get(self._CONFIGKEY, name)
    except:
      return None

  """ If possible, returns the previous set of test results from the wiki. """
  def loadLastTest(self):
    os.chdir(self.wikidir)
    # If there is no index (i.e. first test), then return an empty set
    if not os.path.exists(self.index + '.mediawiki'):
      return {}

    # Find index number of previous test key, if invalid (or not exist),
    # return empty set
    try:
      index = file(self.index + '.mediawiki').read()
      nextkey = re.search("<!-- ## NEXTKEY ([0-9]*) ## -->", index)
      if nextkey == None:
        return {}
      nextkey = nextkey.groups()[0]
      prevkey = int(nextkey) - 1
      if prevkey < 1 or not os.path.exists(self.key + '/' + self.key +
        '-Passes-' + str(prevkey) + '.md'):
        return {}
    except:
      return {}
    # Load and return set of previous results, if an exception occurs, just
    # return an empty set
    try:
      results = {}
      page = file(self.key + '/' + self.key + '-Passes-' + str(prevkey) + '.md')
      page = page.read().split('\n')
      for line in page:
        # New test set
        if line.startswith('## '):
          test = {}
          results[line[3:]] = test
        elif line.startswith('### '):
          testlist = []
          if line == '### Unexpected Failures':
            test['FAIL'] = testlist
          elif line == '### Unexpected Passes':
            test['XPASS'] = testlist
        else:
          testlist.append(line[4:])
    except:
      return {}
    return results

  """ Stores results to wiki. """
  def storeResults(self, rundesc, results, env):
    os.chdir(self.wikidir)
    # If the index page does not exist, attempt to create a new one
    if not os.path.exists(self.index + '.mediawiki'):
      sys.stderr.write('Warning: No index found, creating new.\n')
      index = self._DEFAULT_INDEX % self.description
    else:
      index = file(self.index + '.mediawiki').read()

    # Find index number of next key, exit if unable to parse
    nextkey = re.search("<!-- ## NEXTKEY ([0-9]*) ## -->", index)
    if nextkey == None:
      sys.stderr.write('Error: Unable to parse index.')
      sys.exit(1)
    nextkey = nextkey.groups()[0]

    # Build testresult row
    testtable = self.genResultTable(results, env, 2)
    testrow = '<!-- ## NEXTROW ## -->\n|-\n !! '
    testrow += '[[%s-Test-%s|Test %s]]<br>\'\'%s\'\'<br>\'\'%s\'\' || %s ' % \
      (self.key, nextkey, nextkey, env['Test Date'], rundesc, testtable)

    # Update index and next row key
    index = index.replace('<!-- ## NEXTROW ## -->', testrow)
    index = index.replace('<!-- ## NEXTKEY ' + nextkey + ' ## -->', \
    '<!-- ## NEXTKEY ' + str(int(nextkey) + 1) + ' ## -->')

    # Build results pages
    envtable  = self.genEnvTable(env)
    testtable = self.genResultTable(results, env, 3)
    passtable = self.genPassTable(results)
    difftable = self.genDiffTable(results)
    testpage = self._DEFAULT_TESTPAGE % (self.key, int(nextkey)-1, self.key,
      int(nextkey)+1, self.key, nextkey, self.key, nextkey,
      envtable, testtable)

    # Write, commit and push new pages, using the key as a directory
    if not os.path.exists(self.key):
      os.mkdir(self.key)
    if self.verbose:
      sys.stderr.write('Updating wiki\n')
    file(self.index + '.mediawiki', 'w').write(index)
    file(self.key + '/' + self.key + '-Test-' + nextkey + '.mediawiki', \
      'w').write(testpage)
    file(self.key + '/' + self.key + '-Passes-' + nextkey + '.md', \
      'w').write(passtable)
    file(self.key + '/' + self.key + '-Changed-' + nextkey + '.md', \
      'w').write(difftable)
    p = subprocess.Popen(['git', 'add', self.index + '.mediawiki', \
      self.key + '/' + self.key + '-Test-' + nextkey + '.mediawiki',
      self.key + '/' + self.key + '-Passes-' + nextkey + '.md',
      self.key + '/' + self.key + '-Changed-' + nextkey + '.md'],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p = p.stdout.read()
    if self.verbose:
      print p,
    p = subprocess.Popen(['git', 'commit', '-m', 'Updated wiki for test ' + \
      self.key + '-' + nextkey],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p = p.stdout.read()
    if self.verbose:
      print p,
    p = subprocess.Popen(['git', 'push'],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p = p.stdout.read()
    if self.verbose:
      print p,

  """ Builds table of newly broken/fixed tests. """
  def genDiffTable(self, results):
    table = ''
    for dataset in sorted(results):
      if 'testlist' in results[dataset].keys():
        resultset = results[dataset]['testlist']
        table += '## ' + dataset + '\n'
        table += '### Newly Broken\n'
        for test in resultset['NEWFAIL']:
          table += '    ' + test + '\n'
        table += '### Newly Fixed\n'
        for test in resultset['NOTFAIL']:
          table += '    ' + test + '\n'
        table += '\n'        
    return table    

  """ Builds table of environment variables. """
  def genEnvTable(self, env):
    result = '{|'
    for key in sorted(env):
      result += '\n|-\n! ' + key + ' || ' + str(env[key])
    result += '\n|}'
    return result

  """ Builds list of unexpected failures. """
  def genPassTable(self, results):
    table = ''
    for dataset in sorted(results):
      if 'testlist' in results[dataset].keys():
        resultset = results[dataset]['testlist']
        table += '## ' + dataset + '\n'
        table += '### Unexpected Failures\n'
        for test in resultset['FAIL']:
          table += '    ' + test + '\n'
        table += '### Unexpected Passes\n'
        for test in resultset['XPASS']:
          table += '    ' + test + '\n'
        table += '\n'        
    return table

  """ Builds results table. """
  def genResultTable(self, results, env, width):
    colid = 0
    testrow = '{|'
    for dataset in sorted(results):
      if colid == 0:
        testrow += '\n|-'
      resultset = results[dataset]['results']
      testrow += self.resultFormat(dataset, resultset, env)
      colid = (colid + 1) % width
    testrow += '\n|}\n'
    return testrow

  """ Formats one set of summary results. """
  def resultFormat(self, name, dataset, env):
    # Calculate padding size
    pad = int(math.ceil(math.log10(max(dataset))))
    retval = '\n|| \'\'\'%s\'\'\'<pre>' % name
    if dataset[0] > 0:
      retval += '\n%s expected passes ' % str(dataset[0]).rjust(pad)
    if dataset[1] > 0:
      retval += '\n%s unexpected failures ' % str(dataset[1]).rjust(pad)
    if dataset[2] > 0:
      retval += '\n%s unexpected successes ' % str(dataset[2]).rjust(pad)
    if dataset[3] > 0:
      retval += '\n%s expected failures ' % str(dataset[3]).rjust(pad)
    if dataset[4] > 0:
      retval += '\n%s unresolved testcases  ' % str(dataset[4]).rjust(pad)
    if dataset[5] > 0:
      retval += '\n%s untested testcases ' % str(dataset[5]).rjust(pad)
    if dataset[6] > 0:
      retval += '\n%s unsupported tests ' % str(dataset[6]).rjust(pad)
    retval += '</pre>'
    return retval

  """ Post-execution cleanup (if required). """
  def cleanup(self):
    pass
