###### devnull.py - /dev/null Printer #########################################
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
##  Class for not printing results (simply a test class)
##
###############################################################################


""" Class for doing nothing well """
class devnull:
  """ Load module """
  def __init__(self, config):
    pass

  """ Return no old results. """
  def loadLastTest(self):
    return {}

  """ Accept results. """
  def storeResults(self, rundesc, results, env):
    pass

  """ Post-execution cleanup (if required). """
  def cleanup(self):
    pass
