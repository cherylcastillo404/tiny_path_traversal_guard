# tiny_path_traversal_guard

Validates that a resolved path stays within an allowed base directory, blocking directory traversal escapes.

```python
from tiny_path_traversal_guard import PathTraversalError, resolve_within_base

base = "/srv/data"

# Safe: returns "/srv/data/reports/2024.csv"
resolve_within_base(base, "reports/2024.csv")

# Raises PathTraversalError
try:
    resolve_within_base(base, "../../etc/passwd")
except PathTraversalError as exc:
    print(exc)
```

## Why this exists

Joining an untrusted string to a base directory with `os.path.join` is not safe on its own: a value like `../../etc/passwd` silently escapes the base. This library performs a lexical containment check after normalising the joined path. It is small on purpose and uses only the standard library, so it can be dropped into any project without adding dependencies.

The trade-off is that the check is purely lexical: it does not resolve symlinks. Resolving symlinks can change the meaning of a path after the check, and the process may not have permission to `stat` every component. If you need symlink safety, call `os.path.realpath` on both arguments before passing them in.

## The awkward edge

A sibling directory whose name shares a prefix with the base is easy to miss. If the base is `/srv/data`, then `/srv/data-backup` starts with the string `/srv/data` but is not inside it. The implementation compares against `base + os.sep` (or the base itself) rather than a bare string prefix, so `/srv/data-backup` is correctly rejected. The test suite covers this case explicitly.

## API

- `resolve_within_base(base: str, untrusted: str) -> str`
  - `base` must be an absolute path; otherwise `ValueError` is raised.
  - Returns the absolute, normalised path inside `base`.
  - Raises `PathTraversalError` (a subclass of `ValueError`) if the result escapes `base`.
- `PathTraversalError`
  - Subclass of `ValueError` raised on traversal attempts.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

