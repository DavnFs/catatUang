# Contributing to CatatUang

Terima kasih telah berkontribusi! 🎉

## 🚀 Quick Start

1. **Fork** repository
2. **Clone** fork Anda
3. **Create branch** untuk feature/fix
4. **Make changes** 
5. **Test** perubahan Anda
6. **Submit** Pull Request

## 📋 Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/catatuang.git
cd catatuang

# Install Vercel CLI
npm i -g vercel

# Setup environment
vercel env pull .env.local

# Run locally  
vercel dev

# Test
python examples/test_api.py
```

## 🧪 Testing

Pastikan semua test pass sebelum submit PR:

```bash
# Test
python examples/test_api.py

# Manual testing
curl http://localhost:3000/api/telegram-webhook

# Telegram bot testing (optional)  
python examples/telegram_bot_local.py
```

## 📝 Code Style

### Python
- Follow PEP 8
- Use descriptive variable names
- Add docstrings untuk functions
- Handle exceptions properly

### JavaScript  
- Use ES6+ features
- Consistent indentation (2 spaces)
- Meaningful variable names
- Add JSDoc comments

### Documentation
- Update README.md jika perlu
- Add/update API documentation
- Include examples untuk new features

## 🎯 Pull Request Guidelines

### Title Format
```
[Type] Brief description

Types: feat, fix, docs, style, refactor, test, chore
```

### Examples
- `[feat] Add monthly expense breakdown`
- `[fix] Handle empty message body`
- `[docs] Update setup guide`

### Description Template
```markdown
## Changes
- Brief description of changes

## Testing
- [ ] Tested locally
- [ ] API tests pass
- [ ] Updated documentation

## Related Issues
Fixes #123
```

## 🐛 Bug Reports

Gunakan template ini untuk bug reports:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Bug occurs

## Expected Behavior
What should happen

## Actual Behavior  
What actually happens

## Environment
- Deployment: Vercel/Local
- Telegram Bot: @BotFather token
- Browser/Node version: if applicable

## Additional Context
Screenshots, logs, etc.
```

## 💡 Feature Requests

Template untuk feature requests:

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other ways to solve this problem

## Additional Context
Mockups, examples, etc.
```

## 🔧 Development Guidelines

### Adding New Endpoints

1. **Create handler** di `api/` folder
2. **Follow existing patterns** untuk error handling
3. **Add CORS headers** untuk browser compatibility  
4. **Update documentation** di `docs/api.md`
5. **Add tests** di `examples/test_api.py`

### Environment Variables

1. **Add to vercel.json** jika perlu
2. **Document** di setup guide
3. **Provide examples** di `.env.example`
4. **Never commit** actual values

### Documentation Updates

1. **Update README.md** untuk user-facing changes
2. **Update docs/api.md** untuk API changes
3. **Update docs/setup.md** untuk setup changes
4. **Add examples** jika perlu

## 🏷️ Versioning

Kami menggunakan [Semantic Versioning](https://semver.org/):

- **MAJOR** version untuk breaking changes
- **MINOR** version untuk new features  
- **PATCH** version untuk bug fixes

## 📦 Release Process

1. **Update CHANGELOG.md**
2. **Update version** di package.json
3. **Create release tag**
4. **Deploy to production**
5. **Announce** di discussions

## 🤝 Code of Conduct

- Be respectful dan inclusive
- Provide constructive feedback
- Help others learn dan grow
- Keep discussions on-topic

## 🏆 Recognition

Contributors akan dimasukkan di:
- README.md contributors section
- Release notes  
- Project documentation

## 📞 Getting Help

- 💬 [GitHub Discussions](https://github.com/yourusername/catatuang/discussions)
- 🐛 [Issues](https://github.com/yourusername/catatuang/issues) untuk bugs
- 📖 [Documentation](./docs/) untuk guides

---

**Happy Contributing!** 🚀
