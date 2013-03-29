###### stdenv.py - Standard Environment Variables #############################
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
##  Class for Setting Standard Environment Variables
##
###############################################################################

import subprocess, time

""" Class for Standard Environment """
class stdenv:
  
  """ Load module, setting test environment variables as required """
  def __init__(self, config, env):
    # Test time
    env['Test Date'] = time.strftime('%b %d, %Y %H:%M')
    # System information
    env['Host Name'] = subprocess.Popen(['uname', '-n'], 
      stdout=subprocess.PIPE).stdout.read()
    env['Host Kernel'] = subprocess.Popen(['uname', '-sr'], 
      stdout=subprocess.PIPE).stdout.read()

  """ Post-execution cleanup (if required). """
  def cleanup(self):
    pass
