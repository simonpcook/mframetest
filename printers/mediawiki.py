###### mediawiki.py - MediaWiki Printer #######################################
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
##  Class for Printing results to a MediaWiki wiki
##  (This class is based off the GitHub version)
##  This requires the mwclient python package, but should be easily convertable
##  to alternatives.
##
###############################################################################

import math, re, sys
import mwclient

""" Class for storing results to MediaWiki """
class mediawiki:
  _CONFIGKEY  = 'print_mediawiki'
  config      = None
  verbose     = False
  index       = None
  key         = None
  description = None
  username    = None
  password    = None
  wikiURL     = None
  site        = None

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
      sys.stderr.write('Error: Config for MediaWiki Printer not found. Is ' + \
        'this the correct printer?\n')
      sys.exit(1)

    # Load config
    self.index = self.getConfig('index')
    if self.index == None:
      sys.stderr.write('Error: MediaWiki config is missing index page name.\n')
      sys.exit(1)
    self.key = self.getConfig('key')
    if self.key == None:
      sys.stderr.write('Error: MediaWiki config is missing test key.\n')
      sys.exit(1)
    self.description = self.getConfig('Description')
    if self.description == None:
      self.description = 'Unnamed Test Suite'
    self.username = self.getConfig('username')
    if self.username == None:
      sys.stderr.write('Error: MediaWiki config is missing username.\n')
      sys.exit(1)
    self.password = self.getConfig('password')
    if self.key == None:
      sys.stderr.write('Error: MediaWiki config is missing password.\n')
      sys.exit(1)
    self.wikiURL = self.getConfig('wikiurl')
    if self.wikiURL == None:
      sys.stderr.write('Error: MediaWiki config is missing test key.\n')
      sys.exit(1)
    if not self.wikiURL.startswith('http://'):
      sys.stderr.write('Error: mwclient only supports http://\n')
      sys.exit(1)

    # Try to connect
    url = self.wikiURL.split('/', 3)
    print url
    self.site = mwclient.Site(url[2], path='/'+url[3])
    self.site.login(username=self.username, password=self.password)

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
    # If there is no index (i.e. first test), then return an empty set
    index = self.site.pages[self.index].edit()
    if index == '':
      return {}

    # Find index number of previous test key, if invalid (or not exist),
    # return empty set
    try:
      nextkey = re.search("<!-- ## NEXTKEY ([0-9]*) ## -->", index)
      if nextkey == None:
        return {}
      nextkey = nextkey.groups()[0]
      prevkey = int(nextkey) - 1
      page = self.site.pages[self.key + '-Passes-' + str(prevkey)].edit()
      if page == '':
        return {}
    # Load and return set of previous results, if an exception occurs, just
    # return an empty set
      results = {}
      page = page.split('\n')
      for line in page:
        # New test set
        if line.startswith('== '):
          test = {}
          results[line[3:-3]] = test
        elif line.startswith('=== '):
          testlist = []
          if line == '=== Unexpected Failures ===':
            test['FAIL'] = testlist
          elif line == '=== Unexpected Passes ===':
            test['XPASS'] = testlist
        else:
          testlist.append(line[4:])
    except:
      return {}
    return results

  """ Stores results to wiki. """
  def storeResults(self, results, env):
    # If the index page does not exist, attempt to create a new one
    if self.site.pages[self.index].edit() == '':
      sys.stderr.write('Warning: No index found, creating new.\n')
      index = self._DEFAULT_INDEX % self.description
    else:
      index = self.site.pages[self.index].edit()

    # Find index number of next key, exit if unable to parse
    nextkey = re.search("<!-- ## NEXTKEY ([0-9]*) ## -->", index)
    if nextkey == None:
      sys.stderr.write('Error: Unable to parse index.')
      sys.exit(1)
    nextkey = nextkey.groups()[0]

    # Build testresult row
    testtable = self.genResultTable(results, env, 2)
    testrow = '<!-- ## NEXTROW ## -->\n|-\n ! '
    testrow += '[[%s-Test-%s|Test %s]]<br>\'\'%s\'\' || %s ' % \
      (self.key, nextkey, nextkey, env['Test Date'], testtable)

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
    if self.verbose:
      sys.stderr.write('Updating wiki\n')
    logmessage = 'Updated wiki for test ' + self.key + '-' + nextkey
    self.site.pages[self.index].save(text=index, summary=logmessage)
    self.site.pages[self.key + '-Test-' + nextkey].save(text=testpage, \
      summary=logmessage)
    self.site.pages[self.key + '-Passes-' + nextkey].save(text=passtable, \
      summary=logmessage)
    self.site.pages[self.key + '-Changed-' + nextkey].save(text=difftable, \
      summary=logmessage)

  """ Builds table of newly broken/fixed tests. """
  def genDiffTable(self, results):
    table = ''
    for dataset in sorted(results):
      if 'testlist' in results[dataset].keys():
        resultset = results[dataset]['testlist']
        table += '== ' + dataset + ' ==\n'
        table += '=== Newly Broken ===\n'
        for test in resultset['NEWFAIL']:
          table += '    ' + test + '\n'
        table += '=== Newly Fixed ===\n'
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
        table += '== ' + dataset + ' ==\n'
        table += '=== Unexpected Failures ===\n'
        for test in resultset['FAIL']:
          table += '    ' + test + '\n'
        table += '=== Unexpected Passes ===\n'
        for test in resultset['XPASS']:
          table += '    ' + test + '\n'
        table += '\n'        
    return table

  """ Builds results table. """
  def genResultTable(self, results, env, width):
    colid = 0
    testrow = '\n{|'
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