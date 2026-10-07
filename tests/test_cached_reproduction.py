"""Failure boundaries for the cached-display entry point; no scientific reruns."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("cached_display", Path(__file__).parents[1] / "reproduce.py")
display = importlib.util.module_from_spec(spec)
spec.loader.exec_module(display)


class CachedInputBoundaryTests(unittest.TestCase):
    def test_missing_and_modified_inputs_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "cache.csv"
            path.write_bytes(b"frozen\n")
            manifest = root / "manifest"
            manifest.write_text(display.digest(path) + "  cache.csv\n")
            self.assertEqual(display.verify_manifest(root, manifest), 1)
            path.write_bytes(b"tampered\n")
            with self.assertRaises(ValueError):
                display.verify_manifest(root, manifest)
            path.unlink()
            with self.assertRaises(ValueError):
                display.verify_manifest(root, manifest)

    def test_manifest_traversal_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("../escape", "/absolute", "sub\\escape"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    display.safe_path(root, name)

    def test_archive_links_and_traversal_fail_before_any_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, kind in (("../escape", tarfile.REGTYPE), ("link", tarfile.SYMTYPE)):
                archive = root / "cache.tar.gz"
                target = root / "work"
                target.mkdir(exist_ok=True)
                with tarfile.open(archive, "w:gz") as stream:
                    valid = tarfile.TarInfo("first.txt")
                    valid.size = 4
                    stream.addfile(valid, io.BytesIO(b"data"))
                    bad = tarfile.TarInfo(name)
                    bad.type = kind
                    bad.linkname = "/outside"
                    stream.addfile(bad)
                with self.subTest(name=name), self.assertRaises(ValueError):
                    display.extract_snapshot(archive, target)
                self.assertEqual(list(target.iterdir()), [])

    def test_duplicate_archive_paths_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "cache.tar.gz"
            with tarfile.open(archive, "w:gz") as stream:
                for _ in range(2):
                    stream.addfile(tarfile.TarInfo("duplicate"))
            with self.assertRaises(ValueError):
                display.extract_snapshot(archive, root / "work")


if __name__ == "__main__":
    unittest.main()
