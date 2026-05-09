# SECURITY.md 企业级模板

_适用于大型企业项目_

---

# Security Policy

## Overview

[Project Name] takes security seriously. We appreciate the efforts of security researchers and will respond promptly to legitimate reports.

---

## 🛡️ Security Measures

We implement multiple layers of security:

- **Code Review**: All changes undergo peer review
- **Automated Scanning**: Continuous integration includes security checks
- **Dependency Monitoring**: Automated alerts for vulnerable dependencies
- **Access Controls**: Principle of least privilege for all systems

---

## 📋 Supported Versions

| Version | Supported | Support Level | End of Life |
| ------- | --------- | ------------- | ----------- |
| 3.x     | ✅        | Full support  | TBD         |
| 2.x     | ✅        | Security only | 2026-12-31  |
| 1.x     | ❌        | End of life   | 2025-12-31  |

**Note**: Only the latest minor version of each major version is supported.

---

## 🚨 Reporting a Vulnerability

### Where to Report

**Primary Channel**: [security@example.com](mailto:security@example.com)

**Alternative Channels**:
- 🔐 [HackerOne Program](https://hackerone.com/example) (if applicable)
- 🔑 [PGP Encrypted Email](#pgp-key)

### What to Include

Please provide:

1. **Description**: Clear description of the vulnerability
2. **Impact**: Potential security impact
3. **Reproduction**: Step-by-step reproduction instructions
4. **Proof of Concept**: Code or screenshots (if applicable)
5. **Suggested Fix**: Recommendations (optional but appreciated)

### Response Timeline

| Severity | Acknowledgment | Initial Assessment | Fix Timeline |
|---------- |---------------|--------------------|--------------|
| Critical | 24 hours      | 3 days            | 7 days       |
| High     | 48 hours      | 7 days            | 14 days      |
| Medium   | 72 hours      | 14 days           | 30 days      |
| Low      | 7 days        | 30 days           | 90 days      |

---

## 🔐 PGP Key

For sensitive reports, encrypt your message using our public key:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
[Your public key here]
-----END PGP PUBLIC KEY BLOCK-----
```

**Fingerprint**: `XXXX XXXX XXXX XXXX XXXX  XXXX XXXX XXXX XXXX XXXX`

**Download**: [Link to key server]

---

## 🎁 Rewards

We believe in recognizing security researchers:

### Bounty Program

| Severity | Bounty Range |
|----------|-------------|
| Critical | $5,000 - $10,000 |
| High     | $1,000 - $5,000 |
| Medium   | $500 - $1,000 |
| Low      | $100 - $500 |

**Bonus Opportunities**:
- 🏆 High-quality report: +20%
- 📝 Clear reproduction: +10%
- 🛠️ Working fix included: +15%

### Eligibility

- ✅ First reporter of the vulnerability
- ✅ Follows responsible disclosure
- ✅ No malicious exploitation
- ❌ Public disclosure before fix
- ❌ Attacks on production systems
- ❌ Social engineering

---

## 📜 Disclosure Policy

### Coordinated Disclosure

We follow [Google's disclosure guidelines](https://www.google.com/about/appsecurity/):

1. **Report**: You report the vulnerability privately
2. **Acknowledge**: We acknowledge within 24-72 hours
3. **Investigate**: We investigate and confirm
4. **Fix**: We develop and test a fix
5. **Release**: We release the fix
6. **Announce**: We coordinate public disclosure (typically 90 days)

### Public Disclosure Timeline

- **Target**: 90 days from report
- **Extensions**: Available upon request for complex fixes
- **Early Disclosure**: If we exceed timeline, you may disclose with 14 days notice

---

## 🛠️ Safe Harbor

We support responsible security research:

- ✅ Testing on your own instances
- ✅ Accessing only your own data
- ✅ Reporting vulnerabilities in good faith
- ❌ Accessing other users' data
- ❌ Causing service disruptions
- ❌ Exfiltrating sensitive information

We **will not** pursue legal action against researchers who:
- Make a good faith effort to comply with this policy
- Avoid privacy violations and service disruptions
- Report vulnerabilities promptly
- Do not access data beyond what's necessary

---

## 📞 Contact

### Security Team

- **Email**: [security@example.com](mailto:security@example.com)
- **PGP Key**: [Link]
- **Response Time**: 24-72 hours

### Emergency Contact

For critical vulnerabilities requiring immediate attention:

- 🚨 **Security Hotline**: +1-XXX-XXX-XXXX (24/7)
- 📧 **Priority Email**: [security-urgent@example.com](mailto:security-urgent@example.com)

---

## 🔍 Security Advisories

All security advisories are published at:
- [GitHub Security Advisories](https://github.com/owner/repo/security/advisories)
- [Mailing List](https://example.com/security-list)
- [RSS Feed](https://example.com/security-rss)

---

## 📚 Additional Resources

### For Researchers

- [Bug Bounty Guide](https://github.com/owner/repo/blob/main/docs/bug-bounty-guide.md)
- [Scope of Testing](https://github.com/owner/repo/blob/main/docs/scope.md)
- [Out of Scope](https://github.com/owner/repo/blob/main/docs/out-of-scope.md)

### For Users

- [Security Best Practices](https://github.com/owner/repo/blob/main/docs/security-best-practices.md)
- [Upgrade Guide](https://github.com/owner/repo/blob/main/docs/upgrade-guide.md)
- [Security FAQ](https://github.com/owner/repo/blob/main/docs/security-faq.md)

---

## 📆 Policy Updates

This policy was last updated on **2026-03-29**.

**Change Log**:
- 2026-03-29: Initial version
- [Future updates will be listed here]

---

## 🙏 Acknowledgments

We thank the following security researchers for their responsible disclosures:

| Name | Date | Vulnerability | Bounty |
|------|------|---------------|--------|
| [Researcher 1] | 2026-03-15 | [Issue] | $1,000 |
| [Researcher 2] | 2026-03-10 | [Issue] | $500 |

*[Hall of Fame](https://github.com/owner/repo/blob/main/SECURITY_HALL_OF_FAME.md)*

---

_Thank you for helping keep [Project Name] and our users secure!_

---

## ⚖️ Legal

This security policy is governed by the laws of [Jurisdiction]. By submitting a report, you agree to this policy and our [Terms of Service](https://example.com/terms).

For questions about this policy, contact [legal@example.com](mailto:legal@example.com).
