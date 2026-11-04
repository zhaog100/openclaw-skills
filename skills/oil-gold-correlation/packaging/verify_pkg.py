#!/usr/bin/env python3
"""
verify_pkg.py — 打包前校验 + 两边一致性核对（固定口径，保证每版一致）

两种用法:

  1) 打包前全项校验（make_pkg.py 自动调用；也可单独跑）:
       python3 verify_pkg.py [workspace根目录]
     检查 8 项（见 VERIFY_ITEMS）是否全过，任一项不过 → exit 1。

  2) 两边一致性核对（对方解压包后跑）:
       python3 verify_pkg.py --manifest MANIFEST-<ts>.json
     逐文件比对包内文件与 manifest 的 md5，全一致才算"收到同版"。
"""
import os, sys, json, hashlib, zipfile

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # workspace 根


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


VERIFY_ITEMS = [
    "oil8_ast",          # 油金 8 脚本 AST 全过
    "src9_unavail",      # 9 数据源 __unavailable__ 降级标记在
    "pmi_dict_compat",   # pmi_orders dict 拉空兼容
    "biggs_wording",     # credit_impulse "Biggs 公式"
    "p1_skill_3",        # P1 三 skill 降级标注
    "p3_lottery",        # 彩票 job + 合规红线
    "runtime_data",      # 关键运行态文件（etf_watch/gold_watch/policy_timeline/report_text_latest）
    "secret_leak",       # 密钥泄漏扫描（须 0）
]


def verify_all(root):
    """返回 [(item, ok, detail), ...]"""
    res = []
    eo = os.path.join(root, "skills", "economic-outlook")
    og = os.path.join(root, "oil-gold-correlation")

    # ① 油金 8 脚本 AST
    import ast
    bad = []
    for f in ["analysis.py", "analyze_history.py", "fetch_fred.py", "geopolitics.py",
              "history_report.py", "report_card.py", "report_text_brief.py", "report_text_wrapper.py"]:
        p = os.path.join(og, "scripts", f)
        try:
            ast.parse(open(p).read())
        except Exception as e:
            bad.append(f"{f}:{e}")
    res.append(("oil8_ast", not bad, "8/8 全过" if not bad else "坏:" + ";".join(bad)))

    # ② 9 数据源降级标记
    marks = {}
    for f in ["china_us_spread", "credit", "domestic_retail", "etf_flow", "export_category",
              "global_pmi", "pmi", "recruitment", "sector_returns"]:
        p = os.path.join(eo, "shared", "sources", f"{f}.py")
        n = 0
        if os.path.isfile(p):
            n = open(p).read().count("__unavailable__")
        marks[f] = n
    ok2 = all(v > 0 for v in marks.values())
    res.append(("src9_unavail", ok2, f"{[v for v in marks.values()]} (须全>0)"))

    # ③ pmi dict 兼容
    p = os.path.join(eo, "signals", "pmi_orders.py")
    c = open(p).read().count("isinstance(first, dict)") if os.path.isfile(p) else 0
    res.append(("pmi_dict_compat", c >= 1, f"{c} 处 (须>=1)"))

    # ④ Biggs
    p = os.path.join(eo, "skills", "credit_impulse", "skill.py")
    c = open(p).read().count("Biggs 公式") if os.path.isfile(p) else 0
    res.append(("biggs_wording", c >= 1, f"{c} 处 (须>=1)"))

    # ⑤ P1 三 skill
    p1 = {}
    for s in ["etf_flow", "credit_impulse", "pmi_orders"]:
        p = os.path.join(eo, "skills", s, "skill.py")
        p1[s] = open(p).read().count("unavailable_reason") if os.path.isfile(p) else 0
    ok5 = all(v >= 1 for v in p1.values())
    res.append(("p1_skill_3", ok5, f"{p1} (须各>=1)"))

    # ⑥ P3 彩票
    sched = os.path.join(eo, "config", "schedules.yaml")
    sw = open(sched).read() if os.path.isfile(sched) else ""
    jobs = len([k for k in ["双色球", "大乐透"] if k in sw])
    sqg = os.path.join(og, "scripts", "send_qq_gw.py")
    red = open(sqg).read().count("仅供参考，理性购彩") if os.path.isfile(sqg) else 0
    res.append(("p3_lottery", jobs == 2 and red >= 1, f"job={jobs}/2 红线={red} (须 job=2 红线>=1)"))

    # ⑦ 运行态数据
    rt = {
        "etf_watch": os.path.join(og, "data", "etf_watch.json"),
        "gold_watch_eo": os.path.join(eo, "data", "gold_watch.json"),
        "policy_timeline": os.path.join(eo, "data", "policy_timeline.json"),
        "report_text_latest": os.path.join(og, "reports", "report_text_latest.txt"),
    }
    missing = [k for k, v in rt.items() if not os.path.isfile(v)]
    res.append(("runtime_data", not missing, "全在" if not missing else "缺:" + ",".join(missing)))

    # ⑧ 密钥泄漏
    import subprocess
    r = subprocess.run(
        ["grep", "-rliE", r"sk-[a-z0-9]{10}|api_key *= *['\"]?[A-Za-z0-9]{16,}",
         eo, og],
        capture_output=True, text=True,
    )
    leaks = [x for x in r.stdout.splitlines() if x.strip()]
    res.append(("secret_leak", len(leaks) == 0, f"{len(leaks)} 处 (须=0)" + ("" if not leaks else " " + ";".join(leaks[:3]))))
    return res


def check_manifest(manifest_path, out_zip_or_dir):
    """逐文件 md5 核对，全一致=同版。out_zip_or_dir 可为 zip 或已解压目录。"""
    man = json.load(open(manifest_path))
    files = man["files"]
    if out_zip_or_dir.endswith(".zip"):
        z = zipfile.ZipFile(out_zip_or_dir)
        names = set(z.namelist())
        def get(rel):
            return z.read(rel) if rel in names else None
    else:
        base = out_zip_or_dir
        names = set()
        for root, dirs, fs in os.walk(base):
            for f in fs:
                names.add(os.path.relpath(os.path.join(root, f), base))
        def get(rel):
            p = os.path.join(base, rel)
            return open(p, "rb").read() if os.path.isfile(p) else None

    diff, miss, ok = 0, 0, 0
    for item in files:
        rel = item["path"]
        data = get(rel)
        if data is None:
            miss += 1
            print(f"  缺: {rel}")
        elif hashlib.md5(data).hexdigest() != item["md5"]:
            diff += 1
            print(f"  旧/异: {rel}")
        else:
            ok += 1
    total = len(files)
    print(f"\nmanifest 核对: {total} 文件 → 一致 {ok} / 异 {diff} / 缺 {miss}")
    if diff == 0 and miss == 0:
        print("✅ 全 md5 一致，收到同版")
    else:
        print("❌ 与 manifest 不一致，存在差异文件（见上）")
    return diff == 0 and miss == 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manifest":
        # 用法: verify_pkg.py --manifest <manifest.json> <包.zip或解压目录>
        man = sys.argv[2]
        target = sys.argv[3] if len(sys.argv) > 3 else None
        if target is None:
            print("用法: verify_pkg.py --manifest <MANIFEST.json> <包.zip 或 解压目录>")
            sys.exit(2)
        ok = check_manifest(man, target)
        sys.exit(0 if ok else 1)
    else:
        root = sys.argv[1] if len(sys.argv) > 1 else W
        report = verify_all(root)
        print("=== 打包前校验 ===")
        allpass = True
        for it, okk, detail in report:
            print(f"  {'✅' if okk else '❌'} {it}: {detail}")
            if not okk:
                allpass = False
        sys.exit(0 if allpass else 1)
