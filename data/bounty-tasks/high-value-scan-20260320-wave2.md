# Bounty Scan - 2026-03-20 Wave 2

**Scan Time:** 2026-03-20 08:24 CST
**Sources:** GitHub search (bounty/price/reward labels), devpool-directory, ubiquity-os-marketplace, Algora API (404), polar.sh (404), specific repo checks

---

## 🎯 Best Picks (Realistic for Us: TS/Python/Go/Bash)

### Tier 1: High Priority ⭐

| # | Issue | Repo | Amount | Stack | Comments | Viability |
|---|-------|------|--------|-------|----------|-----------|
| 1 | 🏭 Bounty T1: Search & Filter Engine | SolFoundry/solfoundry | $FNDRY token | Python (FastAPI, PostgreSQL) | 4 | ✅ Open race, good first T1 |
| 2 | 🏭 Bounty T1: Notification System | SolFoundry/solfoundry | $FNDRY token | Python (FastAPI, PostgreSQL) | 4 | ✅ Open race |
| 3 | 🏭 Bounty T1: Payout History & Treasury Stats API | SolFoundry/solfoundry | $FNDRY token | Python (FastAPI, REST API) | 3 | ✅ Open race |
| 4 | 🏭 Bounty T1: Site Navigation & Layout Shell | SolFoundry/solfoundry | $FNDRY token | TypeScript (React, Next.js, Tailwind) | 4 | ✅ Open race, frontend |
| 5 | 🏭 Bounty T1: Leaderboard Page | SolFoundry/solfoundry | $FNDRY token | TypeScript (React, Next.js, Tailwind) | 4 | ✅ Open race |
| 6 | 🏭 Bounty T1: Bounty Detail Page | SolFoundry/solfoundry | $FNDRY token | TypeScript (React, Next.js, Tailwind) | 4 | ✅ Open race |
| 7 | 🏭 Bounty T1: Contributor Profile Page | SolFoundry/solfoundry | $FNDRY token | TypeScript (React, Next.js, Tailwind) | 3 | ✅ Open race |
| 8 | 🏭 Bounty T1: PR Status Tracker Component | SolFoundry/solfoundry | $FNDRY token | TypeScript (React, Next.js, Tailwind) | 3 | ✅ Open race |
| 9 | 🏭 Bounty T1: Tokenomics Page | SolFoundry/solfoundry | $FNDRY token | TypeScript (React, Next.js, Tailwind) | 3 | ✅ Open race |
| 10 | 🏭 Bounty T1: Mobile Responsive Audit & Fixes | SolFoundry/solfoundry | $FNDRY token | TypeScript (React, Next.js, Tailwind) | 3 | ✅ Open race |

**SolFoundry Notes:** All T1 bounties are open race (first quality PR wins). T2 bounties require 4+ merged T1 first. Token-based rewards ($FNDRY). Very active project with clear spec labels.

### Tier 2: Decent Options

| # | Issue | Repo | Amount | Stack | Comments | Viability |
|---|-------|------|--------|-------|----------|-----------|
| 11 | Upgrade to `voyage-4-large` for better performance | devpool-directory/devpool-directory | Time-based | TypeScript | 2 | ✅ Clear scope |
| 12 | Migrate to Bun: runtime, tests, and CI | devpool-directory/devpool-directory | Time-based | TypeScript | 0 | ✅ Clear scope, low comments |
| 13 | Fix Cannot convert undefined or null to object error | devpool-directory/devpool-directory | Time-based | TypeScript | 0 | ✅ Bug fix, quick win |
| 14 | Health Dashboard | devpool-directory/devpool-directory | Time-based | TypeScript | 0 | ✅ Feature, good fit |
| 15 | Plugin health monitor | devpool-directory/devpool-directory | Time-based | TypeScript | 0 | ✅ Feature, good fit |
| 16 | Dynamic Sitemap (Apps & Plugins) | devpool-directory/devpool-directory | Time-based | TypeScript | 0 | ✅ Simple, clear scope |
| 17 | Self Invalidations | devpool-directory/devpool-directory | Time-based | TypeScript | 0 | ✅ Low comments |
| 18 | [BOUNTY: 10 RTC] Add .trashclaw.toml project config | Scottcjn/trashclaw | 10 RTC | Python | 3 | ✅ Feature addition |
| 19 | [BOUNTY: 20 RTC] Add image/screenshot viewing for vision models | Scottcjn/trashclaw | 20 RTC | Python | 2 | ✅ Good scope, useful feature |
| 20 | [BOUNTY: 15 RTC] Add pytest test suite for core tool functions | Scottcjn/trashclaw | 15 RTC | Python | 3 | ✅ Testing, well-defined |
| 21 | [BOUNTY: 10 RTC] Add token-per-second display and generation stats | Scottcjn/trashclaw | 10 RTC | Python | 4 | ✅ Stats feature |
| 22 | [BOUNTY: 5 RTC] Add /pipe command to save last response to file | Scottcjn/trashclaw | 5 RTC | Python | 3 | ✅ Small, quick win |
| 23 | [EASY BOUNTY: 1 RTC] Fix typo or improve documentation | Scottcjn/trashclaw | 1 RTC | Python | 2 | ✅ Easiest entry point |

---

## ❌ Skipped (Not Realistic)

| Reason | Items |
|--------|-------|
| Crypto/Web3 rewards only | SolFoundry token rewards (value uncertain), foremetric/foremetric (crypto), rustchain-bounties (Rust) |
| Not real bounties | IsThereAnyDeal price bugs (user-reported, no $), reward keyword noise |
| Rust/Scala/C++ stack | rustchain-bounties (Rust) |
| Small/unverified repos | yhoungdev/potato-squeezy-bounties-test, AntonSavchuk/koloristika-project |
| Algora API down | 301 → 404 |
| polar.sh explore 404 | Page removed/moved |

---

## 📊 Scan Summary

| Source | Results | Viable |
|--------|---------|--------|
| GitHub label:bounty | 30 | 23 (SolFoundry + trashclaw) |
| GitHub label:price | 30 | 0 (all IsThereAnyDeal user reports) |
| GitHub help wanted + $ | 0 | 0 |
| GitHub reward keyword | 20 | 0 (noise) |
| ubiquity-os-marketplace | 0 | 0 |
| devpool-directory | 20 | 7 |
| Algora API | ❌ 404 | - |
| polar.sh | ❌ 404 | - |
| Specific repos | 0 | 0 |
| topic:bounty repos | 10 | 0 (security/pentest focus) |

**Total viable bounties: 23**
- SolFoundry T1 bounties: 10 (open race, TS + Python)
- devpool-directory: 7 (time-based, TypeScript)
- trashclaw: 6 (RTC tokens, Python)

---

## 🏆 Recommended Action

1. **Start with SolFoundry T1 bounties** - largest batch, clear specs, open race format
2. **Quick wins on trashclaw** - small Python tasks, good for building repo reputation
3. **devpool-directory** - TypeScript tasks, well-documented but may require onboarding
