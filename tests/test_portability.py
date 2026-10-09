import io
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import dws_runtime as r

class PortabilityTests(unittest.TestCase):
    def test_platform_mapping(self):
        for system,arch,expected in [('Windows','AMD64','windows-amd64'),('Windows','ARM64','windows-arm64'),('Darwin','x86_64','darwin-amd64'),('Darwin','arm64','darwin-arm64'),('Linux','x86_64','linux-amd64'),('Linux','aarch64','linux-arm64')]:
            self.assertEqual(r.platform_key(system,arch),expected)
            self.assertIn(r.asset_name(expected),r.checksums())
        with self.assertRaises(ValueError):r.platform_key('Linux','i686')
    def test_zip_extract_only_executable(self):
        with tempfile.TemporaryDirectory() as t:
            a=Path(t)/'asset.zip'
            with zipfile.ZipFile(a,'w') as z:
                z.writestr('../../escape','bad');z.writestr('sub/dws.exe',b'PE-test')
            self.assertEqual(r.extract_binary(a,t,'windows-amd64').read_bytes(),b'PE-test')
            self.assertEqual(sorted(p.name for p in Path(t).iterdir()),['asset.zip','dws.exe'])
    def test_tar_extract_only_regular_file(self):
        with tempfile.TemporaryDirectory() as t:
            a=Path(t)/'asset.tar.gz'
            with tarfile.open(a,'w:gz') as z:
                i=tarfile.TarInfo('dws');i.type=tarfile.SYMTYPE;i.linkname='/etc/passwd';z.addfile(i)
            with self.assertRaises(ValueError):r.extract_binary(a,t,'linux-amd64')

if __name__=='__main__':unittest.main()
