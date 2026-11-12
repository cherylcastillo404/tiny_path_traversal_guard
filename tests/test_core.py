import os
import unittest

from tiny_path_traversal_guard import PathTraversalError, resolve_within_base


class ResolveWithinBaseTests(unittest.TestCase):
    def setUp(self):
        self.base = os.path.abspath(os.sep + "srv" + os.sep + "data")

    def test_plain_relative_path_stays_inside(self):
        self.assertEqual(
            resolve_within_base(self.base, "file.txt"),
            os.path.join(self.base, "file.txt"),
        )

    def test_nested_relative_path_stays_inside(self):
        self.assertEqual(
            resolve_within_base(self.base, os.path.join("a", "b", "c.txt")),
            os.path.join(self.base, "a", "b", "c.txt"),
        )

    def test_base_itself_is_allowed(self):
        self.assertEqual(resolve_within_base(self.base, "."), self.base)

    def test_dot_dot_escape_is_blocked(self):
        with self.assertRaises(PathTraversalError):
            resolve_within_base(self.base, os.path.join("..", "secret.txt"))

    def test_deep_dot_dot_escape_is_blocked(self):
        with self.assertRaises(PathTraversalError):
            resolve_within_base(
                self.base, os.path.join("a", "..", "..", "..", "etc", "passwd")
            )

    def test_absolute_path_is_blocked(self):
        with self.assertRaises(PathTraversalError):
            resolve_within_base(self.base, os.path.abspath(os.sep + "etc" + os.sep + "passwd"))

    def test_sibling_directory_with_shared_prefix_is_blocked(self):
        sibling = self.base + "-backup"
        with self.assertRaises(PathTraversalError):
            resolve_within_base(self.base, os.path.join("..", os.path.basename(sibling)))

    def test_empty_untrusted_path_resolves_to_base(self):
        self.assertEqual(resolve_within_base(self.base, ""), self.base)

    def test_redundant_segments_are_normalised(self):
        self.assertEqual(
            resolve_within_base(self.base, os.path.join("a", ".", "b", "..", "c.txt")),
            os.path.join(self.base, "a", "c.txt"),
        )

    def test_relative_base_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_within_base("relative/base", "file.txt")

    def test_error_is_a_value_error(self):
        with self.assertRaises(ValueError):
            resolve_within_base(self.base, os.path.join("..", "outside"))

    def test_error_message_mentions_the_offending_path(self):
        with self.assertRaises(PathTraversalError) as ctx:
            resolve_within_base(self.base, os.path.join("..", "escape.txt"))
        self.assertIn("escape.txt", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
