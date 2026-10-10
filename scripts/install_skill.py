#!/usr/bin/env python3
"""Install the complete skill into an explicitly selected host directory; never overwrite."""
import argparse
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
INCLUDE=['SKILL.md','README.md','INSTALL_FOR_AI.md','PACKAGE.md','setup.cmd','setup.sh',
         'scripts','assets','references','agents','bin','tests']


def install(dest):
    dest=Path(dest).expanduser().resolve()
    if dest==ROOT or ROOT in dest.parents:
        raise ValueError('Destination must be outside the downloaded source directory')
    if dest.exists():raise FileExistsError('Destination exists; compare before updating: '+str(dest))
    for name in INCLUDE:
        if not (ROOT/name).exists():raise ValueError('Incomplete package: '+name)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.pm-work-assistant-install-',dir=dest.parent) as temp:
        stage=Path(temp)/'pm-work-assistant';stage.mkdir()
        for name in INCLUDE:
            source=ROOT/name;target=stage/name
            if source.is_dir():shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
            else:shutil.copy2(source,target)
        # mkdir gives exclusive reservation; never merge with an existing skill.
        dest.mkdir()
        for p in stage.iterdir():shutil.move(str(p),str(dest/p.name))
    return dest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dest',required=True,type=Path);a=p.parse_args()
    try:print('Installed complete skill: '+str(install(a.dest)))
    except (OSError,ValueError) as e:sys.exit(str(e))
