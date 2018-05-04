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
parser.add_argument('--flavour',
                    choices=['quickest', 'default', 'quick', 'quickest-cross'],
                    default='quickest')
parser.add_argument('--integer', choices=['simple', 'gmp'], default='gmp')
args = parser.parse_args()

username = os.getenv('GITHUB_USERNAME')

assert args.ghc_path, '--ghc_path argument is required'
assert username, 'GITHUB_USERNAME environ is required'

hadrian_path = args.ghc_path + '/hadrian'

assert os.path.isdir(args.ghc_path), "%s is not directory" % arg.ghc_path
assert os.path.isdir(hadrian_path), "%s is not directory" % hadrian_path

words = args.flavour.split('-')
if len(words) > 1 and words[1] == 'cross':
    flavour = words[0]
    cross_compiling = True
else:
    flavour = args.flavour
    cross_compiling = False

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
        subprocess.call(['./boot'], cwd=args.ghc_path)
        if cross_compiling:
            subprocess.call(['./configure', '--target=arm-linux-gnueabihf'], cwd=args.ghc_path)
        else:
            subprocess.call(['./configure'], cwd=args.ghc_path)
    with open(hadrian_path + '/src/UserSettings.hs', 'r') as f:
        user_settings = f.read()
    with open(hadrian_path + '/src/UserSettings.hs', 'w') as f:
        f.write(user_settings.replace('stage1Only = False', 'stage1Only = True'))
    now = time.time()
    build_args = ['bash', 'build.sh', '--flavour=' + flavour]
    if args.integer == 'simple':
        build_args.append('--integer-simple')
    code = subprocess.call(build_args, cwd=hadrian_path)
    duration = time.time() - now
    with open(hadrian_path + '/src/UserSettings.hs', 'w') as f:
        f.write(user_settings)
    info = get_build_info()
    info['duration'] = duration
    info['exit-code'] = code
    info['clean'] = args.clean
    info['flavour'] = args.flavour
    info['integer'] = args.integer
    print("================= SUMMARY =================")
    print(info)
    print("======= reported by hadrian's brick =======")
    f = open('logs/' + username + '.log', 'a+')
    dumped = json.dumps(info)
    assert '\n' not in dumped, 'newline in JSON export'
    f.write(dumped + '\n')
    f.close()

run_build()
