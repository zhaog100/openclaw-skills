<!--
Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
-->
# HackerOne Report Template

## Title Format
`[Vulnerability Type] via [Parameter/Component] in [Endpoint/Feature]`

## Structure

### Summary
One paragraph: what's the vulnerability, where, and what's the impact.

### Vulnerable Component
- File path and line number
- Code snippet showing the vulnerability

### Steps to Reproduce
Numbered list of exact steps to trigger the vulnerability.

### Proof of Concept
Actual payload/request that demonstrates the vulnerability.

### Impact
- Specific attack scenarios
- Who is affected (all users? admin only?)
- CVSS estimate with justification

### Suggested Fix
Code-level fix recommendation. Ideally reference existing secure patterns in the same codebase.

### Environment
- Source branch/commit
- Component type (API, client, server)

### References
- Relevant CVEs, security advisories
- OWASP references

## Severity Guidelines
- **Critical**: RCE, auth bypass without conditions, mass data exfiltration
- **High**: Stored XSS, significant data exposure, SSRF to internal services
- **Medium**: Reflected XSS, limited data exposure, DoS, injection with conditions
- **Low**: Information disclosure, open redirect
- **Informative**: Missing headers, best practice recommendations

## Tips for Higher Bounties
1. Show real impact, not theoretical
2. Include working PoC when possible
3. Reference existing secure code as proof it's a bug (not by design)
4. Demonstrate attack chain (how to escalate)
5. Provide a clear, simple fix
