# Development Guidelines

## Documentation Style
- Keep it minimal - shorter is better
- Focus on core functionality only
- No requirements that can be inferred from code
- Minimal markdown formatting
- No lengthy explanations or tutorials

## README Format
- Title: 1 line description
- Brief overview: 1-2 sentences maximum
- Usage: Only essential commands
- Output: List only what files are produced
- No installation guides or requirements sections

## Package Management
- ONLY use uv, NEVER pip
- Installation: `uv add package`
- Running tools: `uv run tool`
- Upgrading: `uv add --dev package --upgrade-package package`
- FORBIDDEN: `uv pip install`, `@latest` syntax

## Code Quality
- Type hints required for all code
- Public APIs must have docstrings
- Functions must be focused and small
- Line length: 88 chars maximum
- Follow existing patterns exactly

## Code Formatting
- Format: `uv run ruff format .`
- Check: `uv run ruff check .`
- Fix: `uv run ruff check . --fix`
- Critical issues: line length (88 chars), import sorting, unused imports
- Line wrapping: use parentheses for strings, multi-line for function calls

## Type Checking
- Tool: `uv run pyright`
- Requirements: explicit None checks, type narrowing for strings

## Testing
- Framework: `uv run pytest`
- Async testing: use anyio, not asyncio
- New features require tests
- Bug fixes require regression tests

## Pull Requests
- Focus on high-level description of problem and solution
- Don't go into code specifics unless needed for clarity
- NEVER mention tools used to create commit messages or PRs

## Best Practices
- Check git status before commits
- Run formatters before type checks
- Keep changes minimal
- Document public APIs