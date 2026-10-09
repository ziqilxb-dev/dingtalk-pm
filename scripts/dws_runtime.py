"""Cross-platform DWS discovery and verified local installation (standard library)."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import tarfile
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0.63'
BASE = 'https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/releases/download/v' + VERSION


def platform_key(system=None, machine=None):
    system = (system or platform.system()).lower()
    machine = (machine or platform.machine()).lower()
    systems = {'darwin':'darwin', 'windows':'windows', 'linux':'linux'}
    arches = {'arm64':'arm64','aarch64':'arm64','amd64':'amd64','x86_64':'amd64'}
    if system not in systems or machine not in arches:
        raise ValueError('Unsupported system/architecture: ' + system + '/' + machine)
    return systems[system] + '-' + arches[machine]


def asset_name(key):
    if key not in {s+'-'+a for s in ('darwin','linux','windows') for a in ('amd64','arm64')}:
        raise ValueError('Unsupported platform: ' + key)
    return 'dws-' + key + ('.zip' if key.startswith('windows-') else '.tar.gz')


def cache_root():
    return Path(os.environ.get('DINGTALK_PM_CACHE', str(Path.home()/'.cache/dingtalk-pm')))


def executable(directory, key):
    return Path(directory)/('dws.exe' if key.startswith('windows-') else 'dws')


def managed_dir(key):
    return cache_root()/'dws'/VERSION/key


def verified_binary(key):
    dest = managed_dir(key); binary = executable(dest,key); receipt = dest/'receipt.json'
    try:
        r=json.loads(receipt.read_text())
        if r['version']==VERSION and r['platform']==key and hashlib.sha256(binary.read_bytes()).hexdigest()==r['binarySha256']:
            return str(binary)
    except (OSError,ValueError,KeyError):
        pass
    return None


def resolve_cli():
    try:
        cli=verified_binary(platform_key())
    except ValueError:
        cli=None
    return cli or shutil.which('dws')


def checksums():
    return {line.split()[1]:line.split()[0] for line in (ROOT/'bin/checksums-v1.0.63.txt').read_text().splitlines() if line.strip()}


def download(key, directory):
    name=asset_name(key); expected=checksums()[name]; path=Path(directory)/name
    request=urllib.request.Request(BASE+'/'+name,headers={'User-Agent':'dingtalk-pm-setup'})
    digest=hashlib.sha256()
    with urllib.request.urlopen(request,timeout=60) as response, path.open('wb') as out:
        total=0
        while True:
            block=response.read(1024*1024)
            if not block:break
            total+=len(block)
            if total>150*1024*1024:raise ValueError('Unexpected archive size')
            digest.update(block);out.write(block)
    if digest.hexdigest()!=expected:
        raise ValueError('DWS archive checksum mismatch; refusing installation')
    return path


def extract_binary(archive, dest, key):
    """Extract only the expected regular executable; ignore other archive paths."""
    name='dws.exe' if key.startswith('windows-') else 'dws'
    target=Path(dest)/name
    if str(archive).endswith('.zip'):
        with zipfile.ZipFile(archive) as z:
            entries=[i for i in z.infolist() if Path(i.filename).name==name and not i.is_dir()]
            if len(entries)!=1:raise ValueError('Expected exactly one DWS executable')
            entry=entries[0]
            if stat.S_ISLNK(entry.external_attr>>16) or entry.file_size>150*1024*1024:raise ValueError('Invalid executable entry')
            with z.open(entry) as src,target.open('wb') as out:shutil.copyfileobj(src,out)
    else:
        with tarfile.open(archive,'r:gz') as t:
            entries=[i for i in t.getmembers() if Path(i.name).name==name and i.isfile()]
            if len(entries)!=1 or entries[0].size>150*1024*1024:raise ValueError('Expected exactly one DWS executable')
            with t.extractfile(entries[0]) as src,target.open('wb') as out:shutil.copyfileobj(src,out)
    target.chmod(0o755)
    return target


def install():
    key=platform_key()
    current=verified_binary(key)
    if current:return current
    dest=managed_dir(key);dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dws-install-',dir=dest.parent) as temp:
        binary=extract_binary(download(key,temp),temp,key)
        # Verify on the current native platform before publishing. No login.
        import subprocess
        r=subprocess.run([str(binary),'--version'],capture_output=True,text=True,timeout=30)
        if r.returncode or ('v'+VERSION) not in r.stdout:raise RuntimeError('DWS native startup/version check failed: '+r.stderr[:500])
        receipt={'version':VERSION,'platform':key,'asset':asset_name(key),
                 'archiveSha256':checksums()[asset_name(key)],'binarySha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
        dest.mkdir(exist_ok=True)
        os.replace(binary,executable(dest,key))
        staged=Path(temp)/'receipt.json';staged.write_text(json.dumps(receipt,indent=2));os.replace(staged,dest/'receipt.json')
    return str(executable(dest,key))
