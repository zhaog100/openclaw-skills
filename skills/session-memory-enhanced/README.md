# Session Memory Enhanced v2.0.0

> Three-in-one solution: Save session memory + Update QMD + Commit Git

## 🎯 What It Does

Automatically manages your OpenClaw session memory, knowledge base, and Git repository in one seamless operation.

**Three Actions, One Trigger**:
1. ✅ Save session context (native hook)
2. ✅ Update QMD knowledge base (`qmd update`)
3. ✅ Commit to Git repository (auto-commit)

## ✨ Key Features

- **Multiple Triggers**: Crontab (hourly) + /new + /reset
- **Detailed Logging**: Track every update with statistics
- **Smart Commits**: Only commit when changes exist
- **Performance**: <15 seconds total execution time
- **Zero Configuration**: Works out of the box

## 🚀 Quick Start

### Install

```bash
# From ClawHub
clawhub install session-memory-enhanced

# Or manual installation
bash /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

### Configure Crontab

```bash
# Edit crontab
crontab -e

# Add hourly execution
0 * * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

## 📊 How It Works

```
Trigger (/new or /reset or crontab)
    ↓
Save session memory (2s wait)
    ↓
Update QMD knowledge base (<10s)
    ↓
Check Git changes
    ↓
Auto commit if needed (<5s)
    ↓
Log with statistics
```

## 📈 Performance Impact

- **QMD Update**: <10 seconds
- **Git Commit**: <5 seconds
- **Total**: <15 seconds
- **Frequency**: 1x/hour (configurable)
- **System Impact**: Negligible

## 🔧 Configuration

### Change Update Frequency

```bash
# Every 30 minutes
*/30 * * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh

# Every 10 minutes
*/10 * * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

### View Logs

```bash
# Real-time monitoring
tail -f /root/.openclaw/workspace/logs/session-memory-enhanced.log

# Recent 30 entries
tail -30 /root/.openclaw/workspace/logs/session-memory-enhanced.log
```

## 🎯 Use Cases

### Case 1: Long Conversations
- User chats with AI for hours
- Session memory automatically saved
- Knowledge base stays updated
- Git repository synced

### Case 2: Development Work
- Make changes to workspace
- Automatic Git commits
- No manual intervention needed

### Case 3: Knowledge Management
- Add new documents
- QMD automatically indexes
- Knowledge base stays current

## 💡 Comparison

| Feature | Native Hook | Enhanced Hook |
|---------|------------|---------------|
| Save memory | ✅ | ✅ |
| Triggers | /new, /reset | /new, /reset + crontab ⭐ |
| Update QMD | ❌ | ✅ ⭐ |
| Git commit | ❌ | ✅ ⭐ |
| Detailed logs | ❌ | ✅ ⭐ |
| Statistics | ❌ | ✅ ⭐ |

## 📁 Files

```
/root/.openclaw/workspace/
├── scripts/
│   └── session-memory-enhanced.sh    # Main script (1.97KB)
├── logs/
│   └── session-memory-enhanced.log   # Execution log
└── skills/
    └── session-memory-enhanced/
        ├── SKILL.md                   # This file
        └── README.md                  # Documentation
```

## 📞 Support

**Issues?**
1. Check logs: `tail -50 logs/session-memory-enhanced.log`
2. Test manually: `bash scripts/session-memory-enhanced.sh`
3. Verify crontab: `crontab -l`

**Community**:
- ClawHub: https://clawhub.com/skills/session-memory-enhanced
- Discord: https://discord.com/invite/clawd
- Docs: https://docs.openclaw.ai

## 📝 Changelog

### v2.0.0 (2026-03-07)
- Unified session-memory + enhanced-session-memory
- Three trigger methods
- Detailed logging
- Performance optimization

---

**Install now**: `clawhub install session-memory-enhanced`
