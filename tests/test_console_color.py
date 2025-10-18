def _reload_console(monkeypatch, *, env_color="1", has_colorama=True, is_tty=True, under_pytest=False):
    import types, importlib, sys

    if "app.console" in sys.modules:
        del sys.modules["app.console"]

    monkeypatch.setenv("CALCULATOR_COLOR", env_color)
    if under_pytest:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "x")
    else:
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    # <-- CHANGE HERE
    if has_colorama:
        fake = types.SimpleNamespace(
            init=lambda autoreset=True: None,
            Fore=types.SimpleNamespace(CYAN="CYN", GREEN="GRN", YELLOW="YLW", RED="RED", MAGENTA="MAG"),
            Style=types.SimpleNamespace(BRIGHT="<B>", RESET_ALL="</B>"),
        )
        monkeypatch.setitem(sys.modules, "colorama", fake)
    else:
        # Inject a dummy module with no attributes so "from colorama import ..." fails
        class _DummyColoramaModule:
            pass
        monkeypatch.setitem(sys.modules, "colorama", _DummyColoramaModule())
    # --^

    class _StdOut:
        def isatty(self): return is_tty
    monkeypatch.setattr("sys.stdout", _StdOut(), raising=False)

    import app.console as console
    importlib.reload(console)
    return console
