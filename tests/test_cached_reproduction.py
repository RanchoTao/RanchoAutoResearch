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
    def test_restores_original_npz_bytes_from_expanded_public_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            arrays = display.extract_snapshot(
                display.RELEASE / "source-v1.tar.gz", work)
            before = {name: display.digest(work / name) for name in arrays}
            expected = "e4df41b3fc593683fefd67059cabaa199f2ef28ca9426507cca2f5c40fb8ef8f"
            self.assertEqual(display.restore_counts(work, arrays), expected)
            self.assertEqual(len(arrays), 35)
            self.assertEqual(before, {name: display.digest(work / name) for name in arrays})
            target = work / "anc/source/data/broad/window_counts.npz"
            self.assertEqual(display.digest(target), expected)
            target.write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                display.restore_counts(work, arrays)

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

    def test_generated_table_export_is_byte_identical_and_source_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "generated"
            (source / "tables").mkdir(parents=True)
            with tarfile.open(display.RELEASE / "source-v1.tar.gz", "r:gz") as archive:
                tables = {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                          if m.name.startswith("tables/") and m.name.endswith(".tex")}
            self.assertEqual(len(tables), 11)
            windows = {name: content.replace(b"\n", b"\r\n") for name, content in tables.items()}
            for name, content in windows.items():
                (source / name).write_bytes(content)
            asset = source / "unrelated.bin"
            asset.write_bytes(b"binary\r\nbytes")
            target = root / "exported"
            self.assertEqual(len(display.export_generated(source, target)), 11)
            for name, content in tables.items():
                self.assertEqual((target / name).read_bytes(), content)
                self.assertEqual((source / name).read_bytes(), windows[name])
            self.assertEqual((target / asset.name).read_bytes(), asset.read_bytes())
            second = root / "exported-again"
            self.assertEqual(display.export_generated(target, second), [])

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
