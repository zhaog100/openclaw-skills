# Changelog - GitHub Bounty Hunter

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [7.5.6] - 2026-07-13

### Changed
- **Version alignment**: Unified version across all files (SKILL.md, package.json, scripts, archive)
- **Copyright cleanup**: Fixed duplicate copyright headers in `payment_checker.py`; fixed LICENSE bottom attribution (miliger → SJYKJ)
- **Code structure**: Fixed `full-auto-pipeline.py` docstring placement per PEP 8 (moved after shebang)
- **Code structure**: Removed duplicate `if __name__` block and duplicate function definition in `gitcoin_monitor.py`
- **Hardcoded defaults**: Removed placeholder values from `PAYMENT_ADDRESS` and `WALLET_ADDRESS` checks
- **Environment variables**: RTC gateway IP in SKILL.md now uses `${RTC_GATEWAY_URL:-}` fallback pattern
- **DEPRECATED markers**: Added deprecation notices to root-level script copies (`monitor.py`, `algora_monitor.py`, `gitcoin_monitor.py`, `replit_monitor.py`, `superteam_monitor.py`, `bountysource_monitor.py`) — they are duplicates of `scripts/monitors/` versions; will be removed in v8.0
- **Shell scripts**: Fixed shebang ordering in `bounty_scan.sh` (moved copyright comment after `#!/bin/bash`)

### Added
- `.gitignore`: Prevents accidental commit of `config.json`, `.env`, secrets, logs, and temp files

## [7.5.5] - 2026-07-09

### Added
- Full-auto execution strategy (scan → claim → develop → submit → next, no user confirmation)
- Automatic high-quality task scanning (≥$100 USDC/USDT or ≥50 RTC/LTD)
- Auto-claim and sequential execution workflow

### Changed
- Updated scanning intervals for full-auto mode

## [7.4.0] - 2026-04-29

### Added
- `payment_checker.py` - Payment method automatic checker
  - Auto-identify payment type (crypto/fiat/platform/RTC)
  - Validate wallet address format
  - Check if payment method is supported
  - Output payment feasibility report
- 5 mandatory rules (network/payment/Claim/segmentation/threshold)
- Rate limit protection for GitHub API

### Changed
- Enhanced payment verification before development

## [7.3.0] - 2026-04-28

### Added
- Payment method confirmation requirement
- Claim Issue format specification (lessons from Issue #2129)
- 6 iron rules checklist

### Changed
- Stricter claim format enforcement

## [7.0] - 2026-04-12

### Added
- Precision farming strategy (focus on verified platforms only)
- Three-step payment verification
- Repository health scoring system
- Sunk cost stop-loss mechanism

### Changed
- **BREAKING**: Only work on verified payment platforms (UbiquityOS verified)
- **BREAKING**: Minimum threshold ≥$100 USDC/USDT or ≥10 RTC
- **BREAKING**: Single task trial before scaling

### Fixed
- Historical data: 393 PR → 18 merged → $0 actual payment
- Root cause: broad-cast strategy without payment verification

## [6.3] - 2026-04-11

### Added
- Anti-blocking rules (lessons from coollabsio/coolify and archestra-ai/archestra bans)
- `/attempt` command prohibition
- Comment frequency rules (>30 min between comments)
- Bot behavior detection avoidance

## [6.2] - 2026-04-11

### Added
- Repository health scoring system
  - Maintainer activity (40 points)
  - PR review rate (30 points)
  - Average review time (20 points)
  - Payment history (10 points)
- Sunk cost stop-loss rules
  - PR count limits per repository
  - 7-day no-review automatic stop
  - Merge rate monitoring
- Repository blacklist (`data/repo-health.json`)

### Changed
- New repository verification checklist before claiming

## [6.1] - 2026-04-10

### Added
- RTC task special support (RustChain platform)
- Scoring algorithm adjustment (maintainer response speed +20%)
- Task type priority: security audit > integration > tools > content

## [6.0] - 2026-04-09

### Added
- Multi-platform scanning strategy (ubiquity-os, midnightntwrk, opire)
- High-value filtering mechanism (≥$100 only)
- Smart caching system (24-hour cache)
- Phased development (4 phases × 2 minutes each)

### Changed
- Task discovery rate increased 300%

## [5.2] - 2026-04-09

### Added
- Maintainer activity verification
- `/attempt` confirmation mechanism (wait 24h before developing)
- 30 failed PR case library

## [5.1] - 2026-04-08

### Added
- Development workspace isolation
- Fork + API upload mode for unstable GitHub HTTPS

## [5.0] - 2026-04-08

### Added
- Sub-agent batch development
- Fork + API upload hybrid mode
- Template reuse system

## [4.0] - 2026-04-07

### Added
- Automatic scanning cron (every 2 hours)
- Blacklist filtering
- Repository isolation
- Commit verification
- Hourly progress reporting

## [3.0] - 2026-04-06

### Added
- Phased development (4 stages, 2 min each, with progress persistence)
- Quick scan strategy (3 rounds, 180 seconds total)
- Smart timeout detection
- Competition analysis optimization

### Changed
- Sub-agent architecture for parallel processing

## [2.2] - 2026-04-05

### Added
- Workspace management (`workspace-sync.sh`, `qmd-update.sh`, `structure-audit.sh`)
- Multi-platform monitoring (Algora, Gitcoin, Bountysource, Superteam)
- QMD index auto-update
- Git sync automation
- Sensitive information protection

## [2.0] - 2026-04-04

### Added
- Algora专项监控
- Payment verification
- Claim Issue format

## [1.0] - 2026-04-03

### Added
- Initial release
- Basic bounty scanning
- GitHub issue monitoring
- PR submission

---

## Lessons Learned (Historical)

### 2026-04-12 Strategy Review

| Metric | Value |
|--------|-------|
| Total PRs | 393 |
| Merged | 18 (4.6%) |
| Open | 179 |
| Closed | 196 |
| Actual Payment | **$0** |
| Estimated Time | ~200 hours |
| Hourly Rate | **$0/hour** |

**Root Causes:**
1. **Broad-cast strategy** - No payment verification before investing time
2. **PR farm** - homelab-stack collected PRs but never reviewed
3. **Token scams** - RustChain/SolFoundry merged but never paid
4. **No stop-loss** - Repeatedly submitted to same repositories

### Key Incidents

| Date | Issue | Lesson |
|------|-------|--------|
| 2026-03-19 | #2129 spam claimer | Claim Issue must be professional and concise |
| 2026-03-23 | coollabsio ban | No batch comments on same repo |
| 2026-04-11 | archestra ban | `/attempt` is dangerous bot behavior |
| 2026-04-12 | $0 payment | Merge ≠ payment, verify actual receipt |

---

## Legacy Notes

### v1.0-v2.2: Breadth-first era
- Focus: PR quantity
- Result: 393 PRs, $0 actual income
- Lesson: Quality > Quantity

### v3.0-v4.0: Phased execution
- Focus: Timeout prevention
- Result: Better progress persistence
- Lesson: Phased execution prevents total loss

### v5.0-v6.0: Multi-platform expansion
- Focus: More platforms, more opportunities
- Result: 5 new platforms all unreliable
- Lesson: Only work on verified platforms

### v7.0+: Precision farming
- Focus: Payment verification first
- Result: TBD (in progress)
- Principle: Verify payment → small trial → scale up → confirm receipt → expand