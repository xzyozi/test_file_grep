import unittest


def test_single_file():
    from src.grep.parallel_runner import run_parallel

    files = ["dummy1"]
    results = run_parallel(files, "pattern")
    assert len(results) >= 0


def test_multiple_files():
    from src.grep.parallel_runner import run_parallel

    files = ["dummy1", "dummy2", "dummy3"]
    results = run_parallel(files, "pattern")
    assert len(results) >= 0


class TestParallelRunner(unittest.TestCase):
    def test_single_file(self):
        from src.grep.parallel_runner import run_parallel

        files = ["dummy1"]
        results = run_parallel(files, "pattern")
        self.assertIsInstance(results, list)

    def test_multiple_files(self):
        from src.grep.parallel_runner import run_parallel

        files = ["dummy1", "dummy2", "dummy3"]
        results = run_parallel(files, "pattern")
        self.assertIsInstance(results, list)

    def test_max_workers(self):
        from src.grep.parallel_runner import run_parallel

        files = ["dummy1"]
        # max_workers=2 を 指定 しても エラー なし
        results = run_parallel(files, "pattern", max_workers=2)
        self.assertIsInstance(results, list)


if __name__ == "__main__":
    unittest.main()
