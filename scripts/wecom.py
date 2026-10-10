#!/usr/bin/env python3
"""Locate and invoke official WeCom CLI without embedding credentials or changing PATH."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


def resolve_cli(explicit=None):
    candidate = explicit or os.environ.get('WECOM_CLI') or shutil.which('wecom-cli')
    if candidate:
        return str(Path(candidate).expanduser())
    systems = {'Darwin': 'darwin', 'Linux': 'linux', 'Windows': 'win32'}
    arches = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64', 'AMD64': 'x64'}
    system, arch = systems.get(platform.system()), arches.get(platform.machine())
    if not system or not arch:
        raise RuntimeError('Unsupported WeCom platform; specify --cli for a verified compatible CLI.')
    package = 'cli-' + system + '-' + arch
    binary = 'wecom-cli.exe' if system == 'win32' else 'wecom-cli'
    root = Path.home() / '.cache/work-assistant/wecom/node_modules'
    candidates = [root / '@wecom' / package / 'bin' / binary]
    candidates += list(root.glob('.pnpm/@wecom+' + package + '@1.3.4/node_modules/@wecom/' + package + '/bin/' + binary))
    for p in candidates:
        if p.is_file():
            return str(p)
    raise RuntimeError('WeCom CLI missing. See references/wecom.md for official installation; or use --cli.')


def check(cli):
    version = subprocess.run([cli, '--version'], capture_output=True, text=True, timeout=30)
    match = re.search(r'wecom-cli\s+(\d+)\.(\d+)\.(\d+)', version.stdout)
    if version.returncode or not match or tuple(map(int, match.groups())) < (1, 2, 1):
        raise RuntimeError('WeCom CLI startup/version check failed; version >= 1.2.1 required.')
    auth = subprocess.run([cli, 'auth', 'show', '--status'], capture_output=True, text=True, timeout=30)
    status = auth.stdout.strip()
    if auth.returncode or status not in ('authorized', 'unauthorized'):
        raise RuntimeError('WeCom authorization check failed; no business call performed.')
    return {'cli': cli, 'version': version.stdout.strip(), 'authorization': status}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    cli = resolve_cli(args.cli)
    if args.check:
        result = check(cli)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['authorization'] == 'authorized' else 2
    command = args.command
    if command[:1] == ['--']:
        command = command[1:]
    if not command:
        parser.error('Use --check or -- <official CLI arguments>')
    # Login remains user controlled. Other commands require a live authorization check.
    if command[:2] != ['auth', 'init'] and command != ['--version']:
        if check(cli)['authorization'] != 'authorized':
            raise RuntimeError('WeCom unauthorized. Complete user-controlled auth init before reading data.')
    return subprocess.run([cli] + command).returncode


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        sys.exit(str(exc))
