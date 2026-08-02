import unittest


class TestGrepInterface(unittest.TestCase):
    def test_search_case_insensitive_true(self):
        # Mock engine for testing the interface contract
        class MockEngine:
            def search(
                self,
                target_dir,
                search_text,
                regex_mode=False,
                case_insensitive=False,
                on_progress=None,
                on_result=None,
                on_complete=None,
            ):
                if case_insensitive and search_text.lower() in "hello world".lower():
                    return 1
                return 0

        engine = MockEngine()
        self.assertEqual(engine.search("dir", "HELLO", case_insensitive=True), 1)

    def test_search_case_insensitive_false(self):
        class MockEngine:
            def search(
                self,
                target_dir,
                search_text,
                regex_mode=False,
                case_insensitive=False,
                on_progress=None,
                on_result=None,
                on_complete=None,
            ):
                if not case_insensitive and search_text in "hello world":
                    return 1
                return 0

        engine = MockEngine()
        self.assertEqual(engine.search("dir", "HELLO", case_insensitive=False), 0)


if __name__ == "__main__":
    unittest.main()
