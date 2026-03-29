# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""MajorityVoter — 多数投票与输出聚类"""

from typing import List, Dict, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout, as_completed


def cluster_outputs(outputs: List[str], threshold: float = 0.85) -> List[List[str]]:
    """基于编辑距离的层次聚类

    将相似输出归为同一聚类。相似度 >= threshold 的归为一组。

    Returns:
        聚类列表，每个聚类是一组相似的输出
    """
    if not outputs:
        return []
    if len(outputs) == 1:
        return [[outputs[0]]]

    n = len(outputs)
    # 计算相似度矩阵
    sim_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            sim = _similarity(outputs[i], outputs[j])
            sim_matrix[i][j] = sim
            sim_matrix[j][i] = sim

    # 简单聚类：贪心分配
    clusters: List[List[str]] = []
    assigned = [False] * n

    for i in range(n):
        if assigned[i]:
            continue
        cluster = [outputs[i]]
        assigned[i] = True
        for j in range(i + 1, n):
            if assigned[j]:
                continue
            if sim_matrix[i][j] >= threshold:
                cluster.append(outputs[j])
                assigned[j] = True
        clusters.append(cluster)

    return clusters


def majority_vote(outputs: List[str], similarity_threshold: float = 0.85) -> Dict:
    """多数投票：返回最一致的输出 + 一致性比例

    Args:
        outputs: 多次生成的输出列表
        similarity_threshold: 相似度阈值

    Returns:
        {winner, confidence, agreement_ratio, cluster_sizes, total}
    """
    if not outputs:
        return {"winner": "", "confidence": 0, "agreement_ratio": 0, "cluster_sizes": [], "total": 0}

    clusters = cluster_outputs(outputs, similarity_threshold)
    largest = max(clusters, key=len)

    return {
        "winner": largest[0],
        "confidence": round(len(largest) / len(outputs), 4),
        "agreement_ratio": round(len(largest) / len(outputs), 4),
        "cluster_sizes": sorted([len(c) for c in clusters], reverse=True),
        "total": len(outputs),
    }


def vote_with_timeout(prompt_fn: Callable[[], str], n: int = 5,
                      timeout: float = 30) -> Dict:
    """带超时的多数投票（并发，总超时控制）

    Args:
        prompt_fn: 无参数的可调用对象，返回字符串
        n: 采样次数
        timeout: 总超时（秒），所有调用共享此时间预算
    """
    import time as _time
    import threading

    outputs: List[str] = []
    results_lock = threading.Lock()
    deadline = _time.monotonic() + timeout

    def worker():
        try:
            r = prompt_fn()
            if r is not None:
                with results_lock:
                    outputs.append(r)
        except Exception:
            pass

    threads = []
    for _ in range(n):
        remaining = deadline - _time.monotonic()
        if remaining <= 0:
            break
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        remaining = deadline - _time.monotonic()
        if remaining <= 0:
            break
        t.join(timeout=remaining)

    return majority_vote(outputs)


def _similarity(s1: str, s2: str) -> float:
    """计算两个字符串的相似度（基于编辑距离）"""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = _levenshtein(s1, s2)
    return 1.0 - dist / max_len


def _levenshtein(s1: str, s2: str) -> int:
    """Levenshtein 编辑距离"""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev[j + 1] + 1
            deletions = curr[j] + 1
            substitutions = prev[j] + (c1 != c2)
            curr.append(min(insertions, deletions, substitutions))
        prev = curr
    return prev[-1]
