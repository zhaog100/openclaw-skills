# OWASP Top 10 Detailed Checklist

## A01: Broken Access Control
- [ ] List all endpoints with 0 permission checks
- [ ] Check IDOR: Can user A access user B's resources by changing ID?
- [ ] Check horizontal privilege escalation (same role, different user)
- [ ] Check vertical privilege escalation (regular user → admin)
- [ ] Check API key/token exposure in responses
- [ ] Verify file access controls (can user download files from other rooms?)
- [ ] Check for missing authentication on sensitive operations
- [ ] Test forceful browsing (direct URL access without proper auth)

## A02: Cryptographic Failures
- [ ] Search for MD5/SHA1 in security-critical paths
- [ ] Check password hashing algorithm (bcrypt rounds, argon2)
- [ ] Check token generation entropy (Random.id length)
- [ ] Verify HTTPS enforcement
- [ ] Check sensitive data in logs/responses
- [ ] Verify encryption at rest for sensitive fields

## A03: Injection
- [ ] NoSQL: $regex without escapeRegExp
- [ ] NoSQL: $where with user input
- [ ] NoSQL: $expr with user input
- [ ] SQL: Raw queries with string concatenation
- [ ] LDAP: User input in search filters without ldapEscape
- [ ] Command: exec/spawn with user input
- [ ] Template: User input in template rendering
- [ ] Compare secure vs insecure patterns in same codebase

## A04: Insecure Design
- [ ] Token entropy (Random.id(N) — N < 16 risky)
- [ ] Rate limiting on sensitive endpoints
- [ ] Password policy strength
- [ ] Account lockout after failed attempts
- [ ] Invite/share link predictability

## A05: Security Misconfiguration
- [ ] DOMPurify config (ALLOW_UNKNOWN_PROTOCOLS, ADD_TAGS)
- [ ] CORS wildcard origin
- [ ] Missing security headers (CSP, X-Frame-Options)
- [ ] Default credentials
- [ ] Debug mode enabled in production
- [ ] Verbose error messages

## A06: Vulnerable Components
- [ ] Check package.json versions against known CVEs
- [ ] Check for abandoned/deprecated packages

## A07: Authentication Failures
- [ ] Password reset token in URL (leaked via Referer)
- [ ] OAuth state parameter validation
- [ ] Session fixation
- [ ] 2FA bypass possibilities
- [ ] Brute force protection

## A08: Data Integrity Failures
- [ ] Unsafe JSON.parse on user input
- [ ] Unsafe eval()
- [ ] Deserialization of untrusted data
- [ ] Insecure direct object references in serialization

## A09: Logging Failures
- [ ] Sensitive operations logged (login, password change, admin actions)
- [ ] Sensitive data not in logs (passwords, tokens)

## A10: SSRF
- [ ] User-controlled URLs in server-side fetch
- [ ] Webhook URLs without IP validation
- [ ] Image/URL preview fetching
- [ ] OEmbed provider fetching
- [ ] Check for internal IP filtering (127.0.0.1, 10.x, 192.168.x, 169.254.x)
