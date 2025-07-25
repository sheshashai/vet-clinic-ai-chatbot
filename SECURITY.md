# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please report it to us privately.

### How to Report

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email us at: [your-email@example.com] with details
3. Include steps to reproduce the vulnerability
4. Allow us time to assess and fix the issue before public disclosure

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### Response Timeline

- We will acknowledge receipt within 48 hours
- We will provide an initial assessment within 7 days
- We will work to resolve critical issues within 30 days

## Security Best Practices

### For Users

1. **Never commit real API keys** to version control
2. Use strong passwords for user accounts
3. Keep dependencies updated
4. Use HTTPS in production
5. Regularly backup your database

### For Developers

1. Follow secure coding practices
2. Validate all user inputs
3. Use parameterized queries
4. Implement proper authentication
5. Regular security audits

## Known Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Database**: SQLite suitable for development, consider PostgreSQL for production
3. **Sessions**: Use strong secret keys
4. **Password Hashing**: bcrypt is used for secure password storage

## Dependencies

We regularly update dependencies to patch security vulnerabilities. Run:

```bash
pip install --upgrade -r requirements.txt
```

## Contact

For security-related inquiries: [your-email@example.com]
