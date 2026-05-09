---
name: vuln-scanner
description: Systematic security vulnerability scanner for HackerOne bug bounty hunting. Uses OWASP Top 10 methodology, source code audit, and historical CVE pattern matching to find exploitable vulnerabilities in open-source projects. Use when scanning for security vulnerabilities, performing code audits, hunting bug bounties, or analyzing source code for security flaws.

version: 1.0.0

Triggers on "vuln scan", "security audit", "bug bounty", "find vulnerabilities", "code audit", "H1 scan".
---

# Vulnerability Scanner

Systematic security vulnerability scanner for HackerOne bug bounty hunting.

## Workflow

### Phase 1: Reconnaissance & Attack Surface Mapping

Before scanning, always map the full attack surface:

1. **List all API endpoints** — `ls app/api/server/v1/*.ts`
2. **Identify unauthenticated endpoints** — `grep 'authRequired: false'`
3. **Count DDP methods** (WebSocket) — `find -name "methods.ts" -path "*/server/*"`
4. **Count DDP publications** — `grep 'Meteor.publish'`
5. **Identify file upload/download paths**
6. **Map authentication mechanisms** (OAuth, LDAP, SAML, TOTP)

Output: Attack surface summary with endpoint count, auth requirements, and high-value targets.

### Phase 2: OWASP Top 10 Systematic Scan

Scan each category in order. For each: search → verify → confirm/exclude.

#### A01: Broken Access Control (权限绕过/IDOR)
- Search: `grep -c 'hasPermission\|canAccessRoom'` per endpoint file
- Target: Endpoints with 0 permission checks
- Verify: Check if parent route or middleware provides auth
- Common issues: Missing room membership check, cross-room file access

#### A02: Cryptographic Failures (加密失败)
- Search: `grep -rn 'md5\|sha1\|SHA1\|MD5'` — exclude ETag/cache hashing
- Target: Password hashing, token generation, signature verification
- Verify: Check if weak algo is used for security-critical operations

#### A03: Injection (注入)
- **NoSQL injection**: `grep -rn '$regex.*$options'` without `escapeRegExp`
- **SQL injection**: `grep -rn 'raw\|query\|execute'` in database layers
- **LDAP injection**: Check if user input reaches LDAP filter without `ldapEscape`
- **Command injection**: `grep -rn 'exec(\|spawn(\|execSync('`
- Verify: Compare with secure patterns in the same codebase (defense-in-depth)

#### A04: Insecure Design (不安全设计)
- Check token length: `Random.id(N)` — N < 16 may be brute-forceable
- Check rate limiting: `grep 'rateLimiterOptions'` — missing on sensitive endpoints
- Check password policy defaults

#### A05: Security Misconfiguration
- DOMPurify options: `grep -rn 'ALLOW_UNKNOWN_PROTOCOLS\|ADD_TAGS\|ADD_ATTR'`
- CORS: `grep -rn 'Access-Control-Allow-Origin.*\*'`
- CSP headers: Check for missing or weak policies
- Default credentials/keys

#### A06: Vulnerable Components
- Check `package.json` for outdated dependencies
- Cross-reference with known CVEs

#### A07: Authentication Failures
- Password reset token predictability
- Session management weaknesses
- OAuth state/CSRF validation

#### A08: Data Integrity Failures
- Unsafe deserialization: `grep -rn 'JSON.parse.*param\|ejson.parse.*param'`
- Unsafe eval: `grep -rn 'eval('`

#### A09: Logging Failures
- Check if sensitive operations have audit logging

#### A10: SSRF
- User-controlled URLs in server-side fetch
- Webhook URLs without internal IP filtering
- OEmbed/image preview URL fetching

### Phase 3: CVE/GHSA Pattern Matching

Leverage historical security fixes to find similar unfixed vulnerabilities:

1. Find security fix commits: `grep 'Security Hotfix\|CVE-\|GHSA-' CHANGELOG.md`
2. Identify the fix pattern (e.g., adding `escapeRegExp`)
3. Search for the SAME pattern that was fixed but MISSED in other files
4. **Key technique**: Compare files that HAVE the fix vs files that DON'T

Example workflow:
```bash
# Files WITH escapeRegExp (fixed)
grep -rl 'escapeRegExp' app/api/server/v1/*.ts
# Files WITH $regex (potentially vulnerable)
grep -rl '$regex' app/api/server/v1/*.ts
# Difference = unfixed vulnerabilities
```

### Phase 4: Deep Dive on High-Value Targets

For each confirmed vulnerability:

1. Read the vulnerable code context (±20 lines)
2. Trace input source → sink
3. Verify exploit conditions (auth required? specific role?)
4. Check for mitigating factors (WAF, rate limiting, etc.)
5. Assess impact (data exposure, DoS, RCE, etc.)

## Report Generation

Each confirmed vulnerability must include:
- File path and line number
- Vulnerable code snippet
- Secure alternative (if exists in codebase)
- Steps to reproduce
- Impact assessment
- Suggested fix
- CVSS/severity estimate

## Key Principles

1. **Systematic > Random** — Follow OWASP Top 10 in order, don't jump around
2. **Verify everything** — Every finding must be confirmed or excluded with evidence
3. **Defense-in-depth comparison** — Compare secure vs insecure patterns in the same codebase
4. **Historical CVE leverage** — Past fixes reveal unfixed patterns
5. **Only report Medium+** — Skip Low/Informative findings (missing headers, etc.)
6. **Code-level evidence** — Every finding needs file:line and code snippet

## References

- `references/owasp-checklist.md` — Detailed checklist for each OWASP category
- `references/report-template.md` — HackerOne report template
- `references/common-patterns.md` — Common vulnerability patterns by language/framework

## 📄 许可证

MIT License - Copyright (c) 2026 思捷娅科技
