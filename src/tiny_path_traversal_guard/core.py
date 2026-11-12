import os


class PathTraversalError(ValueError):
    """Raised when a path resolves outside the allowed base directory."""


def resolve_within_base(base: str, untrusted: str) -> str:
    """Resolve *untrusted* relative to *base* and ensure it stays inside *base*.

    The base directory is resolved to an absolute path first. The untrusted
    path is then joined to the base and normalised. If the result is not the
    base itself or a descendant of the base, :class:`PathTraversalError` is
    raised.

    This is a lexical check: it does not follow symlinks. That trade-off is
    deliberate, because resolving symlinks can change the meaning of a path
    after the check and because the caller may not have permission to stat
    every component. Callers that need symlink safety should call
    :func:`os.path.realpath` on both arguments before passing them in.

    Args:
        base: The directory that must contain the result.
        untrusted: A path fragment supplied by an untrusted source.

    Returns:
        The absolute, normalised path inside *base*.

    Raises:
        PathTraversalError: If the resolved path escapes *base*.
        ValueError: If *base* is not an absolute path.
    """
    if not os.path.isabs(base):
        raise ValueError("base must be an absolute path")

    base_abs = os.path.normpath(base)
    candidate = os.path.normpath(os.path.join(base_abs, untrusted))

    if candidate == base_abs:
        return candidate

    prefix = base_abs if base_abs.endswith(os.sep) else base_abs + os.sep
    if candidate.startswith(prefix):
        return candidate

    raise PathTraversalError(
        f"path {untrusted!r} escapes base directory {base!r}"
    )
