###### miscenv.py - Custom Environment Variables ##############################
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
##  Class for Setting Multiple Custom Environment Variables
##
###############################################################################

""" Class for Custom Environment """
class miscenv:
  _CONFIGKEY = 'load_custenv'

  """ Load module, setting test environment variables as required """
  def __init__(self, config, env):
    # If configuration section does not exist, raise error
    if not self._CONFIGKEY in config._sections:
      sys.stderr.write('Error: Config for Custom Environment loader not ' + \
        'found. Is this the correct loader?\n')
      sys.exit(1)
    try:
      envfile = config.get(self._CONFIGKEY, 'file')
      custvars = file(envfile).readlines()
      for line in custvars:
        line = line.split(':', 1)
        env[line[0]] = line[1]
    except:
      sys.stderr.write('Error: Couldn\'t set custom environment\n')
      sys.exit(1)

  """ Post-execution cleanup (if required). """
  def cleanup(self):
    pass
