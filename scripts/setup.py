#!/usr/bin/env python3
"""Install the official platform-matched DWS; optionally initialize a PM project."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from dws_runtime import install, platform_key


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path)
    p.add_argument('--with-export',action='store_true',help='Install Playwright and Chromium in the initialized project')
    p.add_argument('--login',action='store_true',help='Start the user-controlled DingTalk login flow')
    a=p.parse_args()
    if sys.version_info<(3,9):p.error('Python 3.9+ required')
    if a.with_export and not a.project:p.error('--with-export requires --project')
    print('Preparing DWS for '+platform_key(),flush=True)
    cli=install()
    print(json.dumps({'cli':cli,'installed':True},ensure_ascii=False),flush=True)
    if a.project:
        root=a.project.resolve()
        subprocess.run([sys.executable,str(Path(__file__).with_name('initialize.py')),'--project',str(root)],check=True)
        if a.with_export:
            subprocess.run([sys.executable,str(root/'scripts/start_service.py'),'--install'],check=True)
    if a.login:
        subprocess.run([cli,'auth','login'],check=True)
    else:
        print('Login when ready: '+json.dumps(cli,ensure_ascii=False)+' auth login')
    print('Setup complete. No background monitor or service was started.')


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as e:raise SystemExit(str(e))
