# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
一致性算法模块：Levenshtein 编辑距离 + TF-IDF 余弦相似度 + 综合评分
"""

import math
import re
from collections import Counter


def levenshtein_distance(s1, s2):
    """计算两个字符串的 Levenshtein 编辑距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def levenshtein_similarity(s1, s2):
    """将编辑距离转为相似度分数 [0.0, 1.0]"""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    max_len = max(len(s1), len(s2))
    dist = levenshtein_distance(s1, s2)
    return 1.0 - (dist / max_len)


def tokenize(text):
    """分词：转小写 + 按非字母数字拆分"""
    return [w.lower() for w in re.findall(r'\b\w+\b', text)]


def tfidf_cosine_similarity(text_a, text_b):
    """TF-IDF 余弦相似度，纯本地实现"""
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    corpus = [tokens_a, tokens_b]
    N = len(corpus)
    vocab = set(tokens_a) | set(tokens_b)
    idf = {}
    for term in vocab:
        df = sum(1 for doc in corpus if term in doc)
        idf[term] = math.log(N / df) + 1
    def tfidf_vector(tokens):
        tf = Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        vec = {}
        for term in set(tokens):
            vec[term] = (tf[term] / max_tf) * idf[term]
        return vec
    vec_a = tfidf_vector(tokens_a)
    vec_b = tfidf_vector(tokens_b)
    dot = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in vocab)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def composite_score(char_sim, sem_sim, char_weight=0.4, sem_weight=0.6):
    """综合评分 = char_weight × 字符相似度 + sem_weight × 语义相似度"""
    return char_weight * char_sim + sem_weight * sem_sim
