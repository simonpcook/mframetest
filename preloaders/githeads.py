###### githeads.py - Git Branch Heads Environment Vars ########################
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
##  Class for Storing Git Version information
##
###############################################################################

import os, subprocess, time, sys

""" Class for Git Information """
class githeads:
  _CONFIGKEY = 'load_githeads'

  """ Load module, setting test environment variables as required """
  def __init__(self, config, env):
    startdir = os.getcwd()
    # If we don't have a loader specific config section, raise error
    if not self._CONFIGKEY in config._sections:
      sys.stderr.write('Error: Config for GitHeads Loader not found. Is ' + \
        'this the correct loader?\n')
      sys.exit(1)
    # Get directory list for evaluation
    try:
      dirs = config.get(self._CONFIGKEY, 'dirs')
      dirs = dirs.split(',')
    except:
      sys.stderr.write('Error: Invalid config for GitHeads Loader\n')
      sys.exit(1)
    # Check that we have git in our path
    try:
      subprocess.Popen(['git', '--version'], stdout=subprocess.PIPE, \
        stderr=subprocess.STDOUT)
    except:
      sys.stderr.write('Error: git not found in PATH.')
      sys.exit(1)
    
    # For each directory, attempt to find head commit
    for d in dirs:
      # If we start with a space, remove it
      while d[0] == ' ':
        d = d[1:]
      try:
        # Change relative to fixed path and move to it
        if d[0] != '/':
          d = startdir + '/' + d
        os.chdir(d)
        p = subprocess.Popen(['git', 'log', '-1', '--pretty=format:%H'], \
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        commit = p.stdout.read()
        # If return code is not 0, raise exception to skip directory
        if p.wait() != 0:
          sys.stderr.write('Warning: Unable to process git in directory \'' \
            + d + '\'. Error was:')
          sys.stderr.write(commit)
          raise ValueError
        p = subprocess.Popen(['git', 'status', '--porcelain'], \
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        status = p.stdout.read()
        # If return code is not 0, raise exception to skip directory
        if p.wait() != 0:
          sys.stderr.write('Warning: Unable to process git in directory \'' \
            + d + '\'. Error was:')
          sys.stderr.write(status)
          raise ValueError
        # If status is non-blank (i.e. not clean commit, add an asterisk to
        # the commit)
        if status != '':
          commit = commit + '*'
        # Finally, store what we have learnt in the environment
        # The following line may need removing in the future (or a new var)
        d = d.split('/')[-1]
        env['git_' + d] = commit
      except:
        # If we raise an exception, just move on. This case could be triggered 
        # by asking for git information in a non-git directory
        pass
    os.chdir(startdir)

  """ Post-execution cleanup (if required). """
  def cleanup(self):
    pass