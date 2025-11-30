# Contributing to RClone Backup Manager

First off, thank you for considering contributing to RClone Backup Manager! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **Environment details**:
  - OS (Windows/Linux distribution)
  - Python version
  - rclone version
  - Application version

### Suggesting Features

Feature suggestions are welcome! Please:

1. **Check existing issues** to see if it's already suggested
2. **Describe the feature** in detail
3. **Explain the use case** - why is it useful?
4. **Provide examples** if possible

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes** thoroughly
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add feature: description"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots for UI changes

## Development Guidelines

### Code Style

- Follow **PEP 8** for Python code
- Use **type hints** where appropriate
- Keep functions **focused and small**
- Add **docstrings** to functions and classes

### Testing

- Test on both **Windows and Linux** if possible
- Test with **multiple rclone remotes**
- Verify **error handling** works correctly
- Check **UI responsiveness** during long operations

### Documentation

- Update **README.md** for new features
- Add **inline comments** for complex code
- Update **docstrings** when changing function behavior

## Questions?

Feel free to open an issue with the `question` label!

Thank you for contributing! 🙏
