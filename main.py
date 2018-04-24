import re
import os
import time
import json
import platform
import subprocess

from base import argparse_, subprocess_
from base.assert_ import *

parser = argparse_.p()
parser.add_argument('--ghc_path')
parser.add_argument('--clean', action='store_true')
parser.add_argument('--flavour', choices=['quickest'], default='quickest')
args = parser.parse_args()

username = os.getenv('GITHUB_USERNAME')

assert args.ghc_path, '--ghc_path argument is required'
assert username, 'GITHUB_USERNAME environ is required'

hadrian_path = args.ghc_path + '/hadrian'

# TODO(zhen): validate path here

def get_gcc_version():
    code, stdout, stderr = subprocess_.call_std(['gcc', '-v'])
    assert_eq(code, 0)
    m = re.search('gcc version ([\d\.]+)', stderr)
    return m.group(1)

def get_ghc_version():
    code, stdout, stderr = subprocess_.call_std(['ghc', '--numeric-version'])
    assert_eq(code, 0)
    return stdout.strip()

def get_git_hash(path):
    code, stdout, stderr = subprocess_.call_std(['git', 'rev-parse', 'HEAD'], cwd=path)
    assert_eq(code, 0)
    return stdout.strip()

def get_build_info():
    info = {}
    info['platform'] = platform.platform()
    info['stage0-ghc-version'] = get_ghc_version()
    info['gcc-version'] = get_gcc_version()
    info['ghc-git-hash'] = get_git_hash(args.ghc_path)
    info['hadrian-git-hash'] = get_git_hash(hadrian_path)
    info['timestamp'] = time.ctime()
    return info

def run_build():
    if args.clean:
        subprocess.call(['bash', 'build.sh', 'clean'], cwd=hadrian_path)
    now = time.time()
    code = subprocess.call(['bash', 'build.sh', '-c', '--flavour=' + args.flavour], cwd=hadrian_path)
    duration = time.time() - now
    info = get_build_info()
    info['duration'] = duration
    info['exit-code'] = code
    info['clean'] = args.clean
    info['flavour'] = args.flavour
    print("================= SUMMARY =================")
    print(info)
    f = open('logs/' + username + '.log', 'a+')
    dumped = json.dumps(info)
    assert '\n' not in dumped, 'newline in JSON export'
    f.write(dumped + '\n')
    f.close()

run_build()
