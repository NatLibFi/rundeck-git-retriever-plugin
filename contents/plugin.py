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

import os, sys, stat, re, subprocess, shutil

def checkForErrors(child):
  if child.returncode:
    print('Error:' + child.stderr.read())
    sys.exit(-1)
  else:
    print(child.stderr.read())
    return child

base_directory = os.path.join(os.getenv('RD_PLUGIN_TMPDIR'), os.getenv('RD_JOB_PROJECT'), os.getenv('RD_JOB_NAME'), 'git-retriever', os.getenv('RD_CONFIG_REPOSITORY_URL').split('/')[-1])
clone_directory = os.path.join(base_directory, os.getenv('RD_CONFIG_CHECKOUT_REFERENCE'))
target_directory = os.getenv('RD_CONFIG_TARGET_DIRECTORY')
target_parent_directory = os.path.dirname(target_directory)
git_env = None

if os.getenv('RD_CONFIG_DISABLE_HOSTKEY_VERIFICATION'):

  os.chmod(os.path.join(os.getenv('RD_PLUGIN_BASE'), 'ssh-disable-hostkey.sh'), stat.S_IREAD | stat.S_IEXEC)

  git_env = {
    'GIT_SSH': os.path.join(os.getenv('RD_PLUGIN_BASE'), 'ssh-disable-hostkey.sh')
  }

if not os.path.exists(base_directory):
  os.makedirs(base_directory)

if not os.path.exists(clone_directory):
  child = subprocess.Popen(['git', 'clone', os.getenv('RD_CONFIG_REPOSITORY_URL'), clone_directory], stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=git_env)
  child.wait()
  checkForErrors(child)

  os.chdir(clone_directory)

  child = subprocess.Popen(['git', 'checkout', os.getenv('RD_CONFIG_CHECKOUT_REFERENCE')], stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=git_env)
  child.wait()
  checkForErrors(child)

else:

  print('Repository already cloned')

  os.chdir(clone_directory)

  child = subprocess.Popen(['git', 'status', '-sb'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=git_env)
  child.wait()

  if child.stdout.read().find('(no branch)') < 0:

    checkForErrors(child)

    print('Pulling changes...')

    child = subprocess.Popen(['git', 'pull'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=git_env)
    child.wait()
    checkForErrors(child)
  else:
    checkForErrors(child)

if not os.path.exists(target_parent_directory):
  os.makedirs(target_parent_directory)

if os.getenv('RD_CONFIG_ALLOWED_BRANCH'):

  child = subprocess.Popen(['git', 'branch', '-r', '--contains', os.getenv('RD_CONFIG_CHECKOUT_REFERENCE')], stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=git_env)
  child.wait()
  checkForErrors(child)

  if not re.search('[\s+|/]origin/' + os.getenv('RD_CONFIG_ALLOWED_BRANCH') + '$', child.stdout.read(), re.MULTILINE):
    print("Allowed branch '" + os.getenv('RD_CONFIG_ALLOWED_BRANCH') + "' does not contain reference '" + os.getenv('RD_CONFIG_CHECKOUT_REFERENCE') + ". Aborting.")
    sys.exit(1);

print('Copying files to ' + target_directory)
shutil.copytree(clone_directory, target_directory, ignore=shutil.ignore_patterns('*.git'))
