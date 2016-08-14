#!/usr/bin/env python
#
# Copyright 2016 University Of Helsinki (The National Library Of Finland)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os, sys, subprocess, shutil

def checkForErrors(child):
  if child.returncode:
    print('Error:' + child.stderr.read())
    sys.exit(-1)
  else:
    print(child.stderr.read())
    return child

base_directory = os.path.join(os.getenv('RD_PLUGIN_TMPDIR'), os.getenv('RD_RUNDECK_PROJECT'), os.getenv('RD_JOB_NAME'), 'git-retriever')
clone_directory = os.path.join(base_directory, os.getenv('RD_CONFIG_CHECKOUT_REFERENCE'))
target_directory = os.path.join(base_directory, os.getenv('RD_JOB_EXECID'))
symlink_path = os.path.join(target_directory, os.getenv('RD_CONFIG_DIRECTORY_NAME'))

os.makedirs(target_directory)

if not os.path.exists(clone_directory):
  child = subprocess.Popen(['git', 'clone', os.getenv('RD_CONFIG_REPOSITORY_URL'), clone_directory], stderr=subprocess.PIPE)
  child.wait()
  checkForErrors(child)

  os.chdir(clone_directory)

  child = subprocess.Popen(['git', 'checkout', os.getenv('RD_CONFIG_CHECKOUT_REFERENCE')], stderr=subprocess.PIPE)
  child.wait()
  checkForErrors(child)

  if os.getenv('RD_CONFIG_EXCLUDE_GIT_DIRECTORY'):
    shutil.rmtree(os.path.join(clone_directory, '.git'))

  os.chdir('..')
else:
  os.chdir(clone_directory)

  child = subprocess.Popen(['git', 'pull'], stderr=subprocess.PIPE)
  child.wait()
  checkForErrors(child)

  os.chdir('..')

print('Creating symlink ' + symlink_path + ' -> ' + clone_directory)
os.symlink(clone_directory, symlink_path)