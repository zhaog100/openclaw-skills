#!/usr/bin/env python3
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""分类标已读：GitHub 通知类全标已读，非 GitHub 类保留未读（进早报提醒）。
用法: python3 mark_github_seen.py [--dry]
  --dry  只统计不真改
GitHub 类特征: From 含 github.com / noreply@github / Ollie520 / github-actions
"""
import logging, imaplib, email, os, sys
from email.header import decode_header

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def _env(key, path):
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(p):
        for line in open(p):
            if line.startswith(key + "="):
                return line.split("=",1)[1].strip()
    return os.environ.get(key, "")

def decode_hdr(v):
    if not v: return ""
    parts=[]
    for p,c in decode_header(v):
        if isinstance(p,bytes): parts.append(p.decode(c or "utf-8", errors="ignore"))
        else: parts.append(p)
    return "".join(parts)

def is_github(msg):
    frm = (decode_hdr(msg.get("From","")) + " " + (msg.get("From","") or "")).lower()
    subj = (decode_hdr(msg.get("Subject",""))).lower()
    hints = ["github.com", "noreply@github", "github-actions", "ollie520",
             "actionable", "issue #", "pull request", "[ci/cd", "workflow"]
    return any(h in frm or h in subj for h in hints)

def main():
    dry = "--dry" in sys.argv
    user = _env("GMAIL_USER", ".env"); pw = _env("GMAIL_APP_PASSWORD", ".env")
    if not user or not pw:
        log.error("缺邮箱凭据"); return 1
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(user, pw)
    m.select("INBOX")
    st, all_ids = m.search(None, "ALL")
    unseen, _ = m.search(None, "UNSEEN")
    unseen_ids = [i for i in unseen[0].split() if i]
    log.info("收件箱 ALL %d 封 | 未读 %d 封", len(all_ids[0].split()), len(unseen_ids))

    gh_seen = 0; keep_unseen = []
    if not dry:
        for eid in unseen_ids:
            st, data = m.fetch(eid, "(RFC822.HEADER)")
            msg = email.message_from_bytes(data[0][1])
            if is_github(msg):
                m.store(eid, '+FLAGS', r'(\Seen)')
                gh_seen += 1
            else:
                keep_unseen.append(eid)
    else:
        # dry: 统计
        gh_cnt = 0
        for eid in unseen_ids:
            st, data = m.fetch(eid, "(RFC822.HEADER)")
            msg = email.message_from_bytes(data[0][1])
            if is_github(msg): gh_cnt += 1
            else: keep_unseen.append(eid)
        log.info("[dry] GitHub类可标已读 %d 封, 非GitHub保留未读 %d 封", gh_cnt, len(keep_unseen))

    m.logout()
    if not dry:
        log.info("✅ 已标记 %d 封 GitHub 类为已读, 保留 %d 封非 GitHub 未读（进早报提醒）", gh_seen, len(keep_unseen))
        # 把保留的未读存一份, 供早报读取
        out = os.path.join(os.getcwd(), "data", "kept_unseen.json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        import json
        json.dump([i.decode() for i in keep_unseen], open(out,"w"))
        log.info("保留未读清单已写: %s", out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
