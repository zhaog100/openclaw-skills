import json, datetime, os

with open('/tmp/open-prs.json') as f:
    open_prs = json.load(f)
with open('/tmp/merged-prs.json') as f:
    merged_prs = json.load(f)

tracker = {
    "lastUpdated": datetime.datetime.now().isoformat(),
    "summary": {"openPRs": len(open_prs), "mergedPRs": len(merged_prs), "blockedRepos": ["coollabsio/coolify", "archestra-ai/archestra"]},
    "openPRList": [{"number": p["number"], "title": p["title"][:80], "url": p["url"]} for p in open_prs],
    "waitingReplies": {"ubiquity-os": ["#12 ($450)", "#14 ($1800)"], "edgechains": ["#286", "#273"], "rustchain": ["PR #2982 (15 RTC)", "PR #2983 (5 RTC)", "PR #2984 (10 RTC)"]}
}
with open('data/bounty-pr-tracker.json', 'w') as f:
    json.dump(tracker, f, indent=2, ensure_ascii=False)
print(f"Done: {len(open_prs)} open, {len(merged_prs)} merged")
