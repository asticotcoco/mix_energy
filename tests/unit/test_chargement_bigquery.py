import io
import sys


sys.path.insert(0, "src")

from mix_energy import chargement_bigquery as transfer


class _FakeBlob:
    def __init__(self, name: str, content: str = "colonne\nvaleur\n"):
        self.name = name
        self._content = content

    def open(self, mode="rt", encoding=None):
        assert mode == "rt"
        return io.StringIO(self._content)


def test_blob_contains_data_rows_returns_false_for_header_only_csv():
    blob = _FakeBlob("raw/eco2mix-national-tr.csv", "col_a;col_b\n")

    assert transfer.blob_contains_data_rows(blob) is False


def test_iter_csv_blob_names_skips_header_only_files():
    class _FakeBucket:
        def list_blobs(self, prefix=None):
            assert prefix == "raw/"
            return [
                _FakeBlob("raw/eco2mix-national-tr.csv", "a;b;c\n"),
                _FakeBlob("raw/eco2mix-national-cons-def.csv", "a;b;c\n1;2;3\n"),
            ]

    class _FakeStorageClient:
        def bucket(self, bucket_name):
            assert bucket_name == "bucket-x"
            return _FakeBucket()

    blob_names = transfer.iter_csv_blob_names(
        storage_client=_FakeStorageClient(),
        bucket_name="bucket-x",
        prefix="raw/",
        file_prefix="eco2mix-national",
    )

    assert blob_names == ["raw/eco2mix-national-cons-def.csv"]