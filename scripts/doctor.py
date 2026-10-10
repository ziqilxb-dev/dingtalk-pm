#!/usr/bin/env python3
"""Read-only package check with optional DingTalk or WeCom checks; does not log in or start services."""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
from dws_runtime import resolve_cli, platform_key, verified_binary

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--provider', choices=['package','dingtalk','wecom'], default='package')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
required=['scripts/collect.py','scripts/setup.py','scripts/dws_runtime.py','scripts/initialize.py',
 'bin/checksums-v1.0.63.txt','assets/scripts/prototype_server.py','assets/scripts/start_service.py',
 'assets/scripts/pm_runtime.py','assets/scripts/pm-document.js','assets/templates/prd-shell.html',
 'assets/workflows/edu-pm-prd.md','assets/workflows/edu-pm-demand.md',
 'assets/workflows/edu-pm-acceptance.md','assets/workflows/edu-pm-data-analysis.md',
 'assets/scripts/pm-acceptance.js','references/pm-workflow.md','references/pm-handoff.md',
 'references/workflows.md','references/dingtalk.md','references/minutes.md','references/wecom.md',
 'scripts/wecom.py','SKILL.md','agents/openai.yaml']
missing=[p for p in required if not (root/p).is_file()]
try:key=platform_key()
except ValueError:key=None
cli=resolve_cli() if args.provider=='dingtalk' else None;version=None;error=None
authorization='Not checked; each user logs in independently'
if args.provider=='wecom':
    try:
        from wecom import resolve_cli as resolve_wecom, check
        report=check(resolve_wecom());cli=report['cli'];version=report['version'];authorization=report['authorization']
    except (OSError,RuntimeError,subprocess.SubprocessError) as e:error=str(e)
if cli and args.provider=='dingtalk':
    try:
        r=subprocess.run([cli,'--version'],capture_output=True,text=True,timeout=15)
        version=r.stdout.strip() if r.returncode==0 else None
        if r.returncode:error=r.stderr[:500]
    except (OSError,subprocess.SubprocessError) as e:error=str(e)
result={'packageComplete':not missing,'missing':missing,'platform':key or platform.platform(),
 'provider':args.provider,'cli':cli,'cliVersion':version,'cliError':error,'managedChecksumValid':bool(key and verified_binary(key)) if args.provider=='dingtalk' else None,
 'pythonSupported':sys.version_info>=(3,9),'nextStep':None if args.provider=='package' or (version and authorization!='unauthorized') else ('See references/wecom.md' if args.provider=='wecom' else 'Run python scripts/setup.py'),
 'exportDependencies':'Initialize the PM project, then use its scripts/start_service.py --install / --check',
 'clientFallback':'Requires host computer-use tools and an installed, logged-in DingTalk client. Otherwise use user-provided excerpts/screenshots.',
 'authentication':authorization}
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if not missing and result['pythonSupported'] and (args.provider=='package' or (version and not error and authorization!='unauthorized')) else 1)
