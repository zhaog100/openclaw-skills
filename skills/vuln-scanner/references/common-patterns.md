# Common Vulnerability Patterns by Type

## NoSQL Injection (MongoDB)
**Vulnerable:**
```javascript
{ name: { $regex: userInput, $options: 'i' } }
```
**Secure:**
```javascript
import { escapeRegExp } from '@rocket.chat/string-helpers';
{ name: { $regex: escapeRegExp(userInput), $options: 'i' } }
```

## XSS (React)
**Vulnerable:**
```jsx
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```
**Secure:**
```jsx
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
// Without ALLOW_UNKNOWN_PROTOCOLS!
```

## LDAP Injection
**Vulnerable:**
```javascript
filter: `(uid=${username})`
```
**Secure:**
```javascript
import ldapEscape from 'ldap-escape';
const escapedUsername = ldapEscape.filter`${username}`;
filter: `(uid=${escapedUsername})`
```

## SSRF
**Vulnerable:**
```javascript
await fetch(userControlledUrl)
```
**Secure:**
```javascript
// Block internal IPs before fetching
const blockedRanges = ['127.0.0.0/8', '10.0.0.0/8', '192.168.0.0/16', '169.254.0.0/16'];
```

## IDOR (File Access)
**Vulnerable:**
```javascript
const file = await Files.findOneById(userProvidedId);
// No ownership check
```
**Secure:**
```javascript
const file = await Files.findOneById(userProvidedId);
if (file.userId !== currentUser._id) throw new Error('Forbidden');
```

## Mass Assignment
**Vulnerable:**
```javascript
const user = { ...req.body }; // All fields accepted
await Users.update(id, user);
```
**Secure:**
```javascript
const { name, email } = req.body; // Only allowed fields
await Users.update(id, { name, email });
```

## Token Predictability
**Vulnerable:**
```javascript
const token = Random.id(6); // Too short, brute-forceable
```
**Secure:**
```javascript
const token = Random.id(32); // Sufficient entropy
```

## Pattern Matching Strategy
For each codebase:
1. Find one instance of the secure pattern
2. Search for the same pattern WITHOUT the security measure
3. The difference = potential vulnerability
4. Verify each finding against mitigating factors
