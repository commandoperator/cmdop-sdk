"""
Syntax highlighting utilities for terminal output.

Provides functions to display code with syntax highlighting
when viewing files through CMDOP SDK.

Uses Rich library (included in SDK dependencies) which internally
uses Pygments for syntax highlighting.

Example:
    >>> from cmdop.helpers import print_code, print_file
    >>>
    >>> # Print code with highlighting
    >>> print_code("print('hello')", language="python")
    >>>
    >>> # Print file content with auto-detected language
    >>> content = await client.files.read("server", "/app/main.py")
    >>> print_file(content, filename="main.py")
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

# Reusable console instance
_console: Console | None = None


def get_console() -> Console:
    """Get or create console instance."""
    global _console
    if _console is None:
        _console = Console()
    return _console


# File extension to language mapping (common cases)
EXTENSION_MAP: dict[str, str] = {
    # Python
    ".py": "python",
    ".pyi": "python",
    ".pyx": "cython",
    # JavaScript/TypeScript
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".mjs": "javascript",
    ".cjs": "javascript",
    # Web
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    # Data formats
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".csv": "text",
    # Config
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "nginx",
    ".env": "dotenv",
    # Shell
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".fish": "fish",
    # Systems
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".kt": "kotlin",
    ".swift": "swift",
    ".m": "objective-c",
    # Ruby
    ".rb": "ruby",
    ".erb": "erb",
    ".rake": "ruby",
    # PHP
    ".php": "php",
    # Perl
    ".pl": "perl",
    ".pm": "perl",
    # Lua
    ".lua": "lua",
    # R
    ".r": "r",
    ".R": "r",
    # SQL
    ".sql": "sql",
    # Docker
    ".dockerfile": "dockerfile",
    # Markdown
    ".md": "markdown",
    ".mdx": "markdown",
    ".rst": "rst",
    # Misc
    ".vim": "vim",
    ".make": "makefile",
    ".cmake": "cmake",
    ".nginx": "nginx",
    ".tf": "terraform",
    ".proto": "protobuf",
    ".graphql": "graphql",
    ".gql": "graphql",
}

# Special filename mappings
FILENAME_MAP: dict[str, str] = {
    "Dockerfile": "dockerfile",
    "docker-compose.yml": "yaml",
    "docker-compose.yaml": "yaml",
    "Makefile": "makefile",
    "CMakeLists.txt": "cmake",
    ".gitignore": "gitignore",
    ".dockerignore": "dockerignore",
    ".editorconfig": "ini",
    "requirements.txt": "text",
    "Pipfile": "toml",
    "Cargo.toml": "toml",
    "go.mod": "go.mod",
    "go.sum": "text",
    "package.json": "json",
    "tsconfig.json": "json",
    "pyproject.toml": "toml",
    "setup.py": "python",
    "setup.cfg": "ini",
    ".bashrc": "bash",
    ".zshrc": "zsh",
    ".bash_profile": "bash",
    ".profile": "bash",
    "nginx.conf": "nginx",
    "httpd.conf": "apacheconf",
}


def detect_language(filename: str) -> str:
    """
    Detect programming language from filename.

    Args:
        filename: File name or path.

    Returns:
        Language identifier for syntax highlighting.
        Returns "text" if language cannot be detected.
    """
    name = Path(filename).name

    # Check exact filename match first
    if name in FILENAME_MAP:
        return FILENAME_MAP[name]

    # Check extension
    suffix = Path(filename).suffix.lower()
    if suffix in EXTENSION_MAP:
        return EXTENSION_MAP[suffix]

    # Default to text
    return "text"


def print_code(
    code: str | bytes,
    language: str = "python",
    *,
    theme: str = "monokai",
    line_numbers: bool = True,
    word_wrap: bool = False,
    start_line: int = 1,
    highlight_lines: set[int] | None = None,
    title: str | None = None,
    background_color: str | None = None,
) -> None:
    """
    Print code with syntax highlighting to terminal.

    Args:
        code: Source code to display (str or bytes).
        language: Programming language for highlighting.
        theme: Pygments theme name. Popular themes:
            - "monokai" (default, dark)
            - "dracula" (dark)
            - "one-dark" (dark)
            - "github-dark" (dark)
            - "native" (dark)
            - "vs" (light)
            - "github-light" (light)
            - "solarized-light" (light)
        line_numbers: Show line numbers.
        word_wrap: Wrap long lines.
        start_line: Starting line number.
        highlight_lines: Set of line numbers to highlight.
        title: Optional title to display above code.
        background_color: Override background color.

    Example:
        >>> print_code('''
        ... def hello():
        ...     print("Hello, World!")
        ... ''', language="python")
    """
    console = get_console()

    # Handle bytes input
    if isinstance(code, bytes):
        try:
            code = code.decode("utf-8")
        except UnicodeDecodeError:
            code = code.decode("latin-1")

    # Strip trailing whitespace but preserve structure
    code = code.rstrip()

    syntax = Syntax(
        code,
        language,
        theme=theme,
        line_numbers=line_numbers,
        word_wrap=word_wrap,
        start_line=start_line,
        highlight_lines=highlight_lines,
        background_color=background_color,
    )

    if title:
        console.print(Panel(syntax, title=title, border_style="dim"))
    else:
        console.print(syntax)


def print_file(
    content: str | bytes,
    filename: str,
    *,
    language: str | None = None,
    theme: str = "monokai",
    line_numbers: bool = True,
    word_wrap: bool = False,
    start_line: int = 1,
    highlight_lines: set[int] | None = None,
    show_title: bool = True,
) -> None:
    """
    Print file content with syntax highlighting.

    Auto-detects language from filename extension.

    Args:
        content: File content (str or bytes).
        filename: Filename for language detection and title.
        language: Override auto-detected language.
        theme: Pygments theme name.
        line_numbers: Show line numbers.
        word_wrap: Wrap long lines.
        start_line: Starting line number.
        highlight_lines: Set of line numbers to highlight.
        show_title: Show filename as title.

    Example:
        >>> content = await client.files.read("server", "/app/main.py")
        >>> print_file(content, "main.py")
    """
    # Auto-detect language if not specified
    if language is None:
        language = detect_language(filename)

    title = filename if show_title else None

    print_code(
        content,
        language=language,
        theme=theme,
        line_numbers=line_numbers,
        word_wrap=word_wrap,
        start_line=start_line,
        highlight_lines=highlight_lines,
        title=title,
    )


def print_diff(
    diff_text: str | bytes,
    *,
    theme: str = "monokai",
    line_numbers: bool = False,
    title: str | None = "Diff",
) -> None:
    """
    Print unified diff with syntax highlighting.

    Args:
        diff_text: Unified diff content.
        theme: Pygments theme name.
        line_numbers: Show line numbers.
        title: Optional title.

    Example:
        >>> diff = '''
        ... --- a/file.py
        ... +++ b/file.py
        ... @@ -1,3 +1,4 @@
        ...  def hello():
        ... -    print("Hello")
        ... +    print("Hello, World!")
        ... +    return True
        ... '''
        >>> print_diff(diff)
    """
    print_code(
        diff_text,
        language="diff",
        theme=theme,
        line_numbers=line_numbers,
        title=title,
    )


def print_json(
    data: str | bytes | dict | list,
    *,
    theme: str = "monokai",
    title: str | None = None,
    indent: int = 2,
) -> None:
    """
    Print JSON with syntax highlighting.

    Args:
        data: JSON string, bytes, or Python dict/list.
        theme: Pygments theme name.
        title: Optional title.
        indent: Indentation level for dict/list input.

    Example:
        >>> print_json({"name": "test", "value": 42})
    """
    import json

    if isinstance(data, (dict, list)):
        content = json.dumps(data, indent=indent, ensure_ascii=False)
    elif isinstance(data, bytes):
        content = data.decode("utf-8")
    else:
        content = data

    print_code(content, language="json", theme=theme, title=title, line_numbers=False)


def print_yaml(
    data: str | bytes,
    *,
    theme: str = "monokai",
    title: str | None = None,
) -> None:
    """
    Print YAML with syntax highlighting.

    Args:
        data: YAML content.
        theme: Pygments theme name.
        title: Optional title.
    """
    print_code(data, language="yaml", theme=theme, title=title, line_numbers=False)


def print_shell_output(
    output: str | bytes,
    command: str | None = None,
    *,
    theme: str = "monokai",
) -> None:
    """
    Print shell command output with optional command display.

    Args:
        output: Command output.
        command: The command that was executed (shown as title).
        theme: Pygments theme name.
    """
    console = get_console()

    if isinstance(output, bytes):
        try:
            output = output.decode("utf-8")
        except UnicodeDecodeError:
            output = output.decode("latin-1")

    if command:
        console.print(f"[bold green]$[/] [cyan]{command}[/]")

    # Try to detect if output looks like code
    lines = output.strip().split("\n")

    # Simple heuristic: if first line looks like a shebang or code
    if lines and (
        lines[0].startswith("#!")
        or lines[0].startswith("def ")
        or lines[0].startswith("class ")
        or lines[0].startswith("import ")
        or lines[0].startswith("from ")
        or lines[0].startswith("function ")
        or lines[0].startswith("const ")
        or lines[0].startswith("let ")
        or lines[0].startswith("var ")
    ):
        # Detect language from shebang
        if lines[0].startswith("#!"):
            if "python" in lines[0]:
                lang = "python"
            elif "bash" in lines[0] or "sh" in lines[0]:
                lang = "bash"
            elif "node" in lines[0]:
                lang = "javascript"
            elif "ruby" in lines[0]:
                lang = "ruby"
            elif "perl" in lines[0]:
                lang = "perl"
            else:
                lang = "bash"
        elif "def " in lines[0] or "import " in lines[0] or "from " in lines[0]:
            lang = "python"
        elif "function " in lines[0] or "const " in lines[0]:
            lang = "javascript"
        else:
            lang = "text"

        print_code(output, language=lang, theme=theme, line_numbers=True)
    else:
        # Plain output
        console.print(output)


# Convenience aliases
cat = print_file  # Like Unix cat but with highlighting
highlight = print_code
