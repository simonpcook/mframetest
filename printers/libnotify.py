###### libnotify.py - Prints results via libnotify ############################
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
##  Class for Printing results to a set of popups via libnotify
##  Requires python-notify or equivalent
##
###############################################################################

import math, os, re, subprocess, sys
import pygtk, pynotify

""" Class for printing results to libnotify popups """
class libnotify:
  
  """ Class Constructor. . """
  def __init__(self, config):
    # Set up pygtk and pynotify
    pygtk.require('2.0')
    if not pynotify.init('Basics'):
      sys.stderr.write('Error: Unable to load pynotify\n')
      sys.exit(1)

  """ This printer does not store results, so has nothing to provide """
  def loadLastTest(self):
    return {}

  """ Prints results to output """
  def storeResults(self, results, env):
    for dataset in sorted(results):
      resultset = results[dataset]['results']
      resultset = self.resultFormat(dataset, resultset, env)
      notification = pynotify.Notification('Test Complete: ' + dataset, 
        resultset)
      try:
        if not notification.show():
          sys.stderr.write('Warning: Unable to use libnotify notification.\n')
          return
      except:
        sys.stderr.write('Warning: Unable to send libnotify notification.\n')
        return

  """ Formats one set of summary results. """
  def resultFormat(self, name, dataset, env):
    # Calculate padding size
    retval = 'Results: ' 
    if dataset[0] > 0:
      retval += '%i expected passes. ' % dataset[0]
    if dataset[1] > 0:
      retval += '%i unexpected failures. ' % dataset[1]
    if dataset[2] > 0:
      retval += '%i unexpected successes. ' % dataset[2]
    if dataset[3] > 0:
      retval += '%i expected failures. ' % dataset[3]
    if dataset[4] > 0:
      retval += '%i unresolved testcases.  ' % dataset[4]
    if dataset[5] > 0:
      retval += '%i untested testcases. ' % dataset[5]
    if dataset[6] > 0:
      retval += '%i unsupported tests. ' % dataset[6]
    return retval

  """ Post-execution cleanup (if required). """
  def cleanup(self):
    pass