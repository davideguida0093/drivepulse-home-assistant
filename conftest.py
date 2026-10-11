"""Root conftest.

On Windows two things in the Home Assistant test plugin (written for Linux CI)
get in the way of running the tests locally: it blocks the socket pair an
asyncio loop needs, and aiodns refuses a non-selector event loop. Both are
lifted here, on Windows only. CI runs on Linux and keeps the plugin as it is.
"""

import sys

if sys.platform == "win32":
    import asyncio

    import aiodns
    import pytest_socket

    pytest_socket.disable_socket = lambda *args, **kwargs: None

    class _AsyncioShim:
        """asyncio, but any loop counts as a 'SelectorEventLoop' for aiodns."""

        SelectorEventLoop = asyncio.AbstractEventLoop

        def __getattr__(self, name):
            return getattr(asyncio, name)

    aiodns.asyncio = _AsyncioShim()

    import pytest

    @pytest.fixture(autouse=True)
    def verify_cleanup():
        """The plugin's thread check trips on Windows' shutdown helper thread."""
        yield
