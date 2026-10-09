#!/usr/bin/env python3
"""Read-only cross-platform package and DWS check; does not log in or start services."""
import json
from pathlib import Path
import platform
import subprocess
import sys
from dws_runtime import resolve_cli, platform_key, verified_binary

root=Path(__file__).resolve().parents[1]
required=['scripts/collect.py','scripts/setup.py','scripts/dws_runtime.py','scripts/initialize.py',
 'bin/checksums-v1.0.63.txt','assets/scripts/prototype_server.py','assets/scripts/start_service.py',
 'assets/scripts/pm_runtime.py','assets/scripts/pm-document.js','assets/templates/prd-shell.html',
 'assets/workflows/edu-pm-prd.md','references/pm-workflow.md']
missing=[p for p in required if not (root/p).is_file()]
try:key=platform_key()
except ValueError:key=None
cli=resolve_cli();version=None;error=None
if cli:
    try:
        r=subprocess.run([cli,'--version'],capture_output=True,text=True,timeout=15)
        version=r.stdout.strip() if r.returncode==0 else None
        if r.returncode:error=r.stderr[:500]
    except (OSError,subprocess.SubprocessError) as e:error=str(e)
result={'packageComplete':not missing,'missing':missing,'platform':key or platform.platform(),
 'cli':cli,'cliVersion':version,'cliError':error,'managedChecksumValid':bool(key and verified_binary(key)),
 'pythonSupported':sys.version_info>=(3,9),'nextStep':None if version else 'Run python scripts/setup.py',
 'exportDependencies':'Install/check Playwright and Chromium per project with setup.py --project PATH --with-export',
 'clientFallback':'Requires host computer-use tools and an installed, logged-in DingTalk client. Otherwise use user-provided excerpts/screenshots.',
 'authentication':'Not checked; each user logs in independently'}
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if not missing and version and result['pythonSupported'] else 1)
