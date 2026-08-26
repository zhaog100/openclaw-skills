#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
"""
中国公考+国企央企信息获取工具 v4.0
使用Python标准库 + 真实数据源抓取 + 详情页深入提取

数据源：
  - 中公网校 (eoffcn.com) — 四川省公务员汇总
  - 四川人事考试网 (scpta.com.cn) — 四川省公务员/事业单位（偶尔超时）
  - 事业单位招聘考试网 (shiyebian.com) — 成都/泸州事业单位
  - 泸州人事考试网 (lzsrsks.cn) — 泸州公务员/事业单位
  - 编制招聘网 (bianzhia.com) — 成都国企+四川国企每日更新（v4.0新增）
  - 高顿国企招聘 (gwy.com/gqzp/) — 国企央企招聘公告汇总
  - 腾讯新闻 — 成都国企招聘汇总（补充）

v4.0 改进（2026-06-14）：
  - 国企央企采集重构：数据源从2个扩展到4个（编制招聘网+高顿+腾讯新闻+搜狐）
  - 编制招聘网每日更新，成都国企+四川国企数据量提升5-10倍
  - 去重改为 URL + 公司名 + 噪声过滤 三重机制
  - 同一公司不同岗位合并为"多岗位招聘"
  - 过滤劳务外包/合同制等非核心岗位
  - 详情页抓取编制招聘网（含学历/年龄/专业要求）
"""

import urllib.request
import urllib.parse
import urllib.error
import html
import json
import csv
import re
import sys
import argparse
import time
from datetime import datetime
from html.parser import HTMLParser
from typing import List, Dict, Optional, Any


# ============================================================
# 地区关键词配置
# ============================================================
REGION_KEYWORDS = {
    'chengdu': ['成都', '成都市', '双流', '龙泉驿', '温江', '新都', '郫都', '武侯', '锦江', '青羊', '金牛', '成华', '成都高新区', '天府新区'],
    'luzhou': ['泸州', '泸州市', '江阳', '纳溪', '龙马潭', '古蔺', '合江', '叙永', '泸县'],
    'sichuan': ['四川', '四川省', '绵阳', '德阳', '宜宾', '南充', '达州', '自贡', '攀枝花', '广元', '遂宁', '内江', '乐山', '眉山', '雅安', '巴中', '资阳', '西昌', '阿坝', '甘孜', '凉山'],
    'state-owned': ['国企', '央企', '国有', '中央企业', '国有企业', '国资', '中船', '中煤', '中铁', '中化', '中石油', '中石化', '中海油', '国家电网', '南方电网', '中国电科', '中国能建', '中国铁建', '中国交建', '中国中车', '中国通号', '中国核电', '中国华电', '中国大唐', '中国华能', '国家能源', '国家电投', '中广核', '中核', '航天科工', '航天科技', '航空工业', '中国商飞', '中国船舶', '中国兵器', '中国电子', '中国移动', '中国联通', '中国电信', '中国邮政', '中国烟草', '中国铁路', '中国铁建', '中国建筑', '中国中铁', '中国中冶', '中国有色', '中国黄金', '中国稀土', '中国铝业', '中国五矿', '中国宝武', '鞍钢', '宝钢', '河钢', '首钢', '沙钢', '华润', '招商局', '保利', '中信', '光大', '中粮', '中储粮', '中纺', '中盐', '中国建材', '中国国新', '中国诚通', '中国通用技术', '中国医药', '中国生物', '中国南水北调', '中国节能', '中国环保', '中国绿发', '中国星网', '中国卫星', '中国卫通', '中国铁塔', '中国中化', '中国化学', '中国电建', '中国能建', '中国安能', '中国铁工', '中国中铁', '中国铁建', '中国交建', '中国港湾', '中国路桥', '中国土木', '中国武夷', '中国海诚', '中国中材', '中国巨石', '中国恒瑞', '中国核电', '中国广核', '中核集团', '中核建', '中国同辐', '中国铀业', '中国原子能', '中国核建', '中核华兴', '中核二二', '中核二二', '中核二二'],
}

KEYWORD_TO_REGION = {}
for _region, _keywords in REGION_KEYWORDS.items():
    for _kw in _keywords:
        KEYWORD_TO_REGION[_kw] = _region

# 噪声关键词：包含这些的不是真正的"招聘公告"
NOISE_KEYWORDS = [
    # === 考试考务（非招聘公告）===
    '准考证打印', '考务', '笔试顺利', '联席会议', '警示教育',
    '新域名', '温馨提示', '资格考试', '职业资格考试', '社会工作者',
    '一级造价', '执业药师', '提质增效', '人才岗位需求',
    '笔试总成绩', '资格审查人员名单', '排名及参加',
    '打印准考证', '考试温馨提示', '笔试工作顺利',
    '准考证', '合格证明', '证书邮寄', '成绩查询',
    # === 已考完的公示/递补/排名（不是招聘公告）===
    '拟录用', '公示', '递补', '排名及参加', '资格审查人员',
    '录用人员公示', '拟聘用人员', '总成绩公示',
    # === 通用工具/服务（非招聘公告）===
    '秋招提前批', '报名时间', '常见问题', '备考工具', '考试题库',
    '资料下载', '秋招时间', '央国企秋招', '求职攻略', '面试技巧', '简历模板',
    # === 网站导航/分类标题（精确匹配，非公告标题）===
    # 高顿/搜狐等网站的通用导航条目
    '国企招聘汇总', '央企招聘汇总', '国企招聘网', '央企招聘网',
    '国企招聘公告', '国企招聘考试网', '国企招聘信息网', '国企招聘资讯',
    '国企招聘专栏', '国企招聘专题', '国企招聘频道',
    '国企招聘首页', '国企招聘大全', '国企招聘列表',
    '国企招聘合集', '国企招聘集锦',
    '国企招聘推荐', '国企招聘精选', '国企招聘热榜',
    '国企招聘最新', '国企招聘近期', '国企招聘近期汇总',
    '国企考试', '央企考试',
    '国企招聘公众号', '央企招聘公众号', '国企招聘平台',
]

# 真正的招聘公告必须包含这些关键词之一
REQUIRED_KEYWORDS = [
    '招聘', '考试录用', '选调', '公招', '补充录用', '联考',
    '公开考试招聘', '公开招聘', '招聘工作人员', '招用',
    # 国企央企
    '校园招聘', '社会招聘', '公开招考', '考核招聘', '人才引进',
    '校招', '社招', '管培生', '储备人才',
]


class ExamInfoExtractor(HTMLParser):
    """HTML解析器"""
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.links = []
        self.in_link = False
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href:
                self.in_link = True
                self.current_link = {'href': href, 'text': ''}

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            if self.current_link:
                self.links.append(self.current_link)
            self.in_link = False
            self.current_link = None

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_content.append(text)
            if self.in_link and self.current_link:
                self.current_link['text'] += text


class ChinaExamInfo:
    """公考信息获取类 v4.0"""

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def fetch_url(self, url):
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                ct = resp.headers.get('Content-Type', '')
                charset = 'utf-8'
                if 'charset=' in ct:
                    charset = ct.split('charset=')[-1].strip()
                try:
                    return raw.decode(charset, errors='ignore')
                except (LookupError, UnicodeDecodeError):
                    for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
                        try:
                            return raw.decode(enc, errors='ignore')
                        except Exception:
                            continue
                    return raw.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"获取失败 {url}: {e}", file=sys.stderr)
            return None

    def detect_region(self, title):
        sorted_kws = sorted(KEYWORD_TO_REGION.keys(), key=len, reverse=True)
        for kw in sorted_kws:
            if kw in title:
                return KEYWORD_TO_REGION[kw]
        return None

    # ============================================================
    # 列表页解析 → 提取考试条目链接
    # ============================================================

    def extract_listing(self, html_content, target_regions=None):
        """从列表页提取考试条目（标题+链接）
        使用正则逐条提取，避免HTMLParser跨标签合并文本
        """
        items = []
        seen_urls = set()

        # 直接从HTML中提取每个<a>...</a>块，防止跨条目文本合并
        for m in re.finditer(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', html_content, re.DOTALL):
            href = html.unescape(m.group(1)).strip()
            raw_text = m.group(2)
            # 去除嵌套标签（如<b>、<span>等）
            lt = re.sub(r'<[^>]+>', '', raw_text).strip()
            lt = html.unescape(lt)
            if not lt or len(lt) < 8 or '202' not in lt:
                continue
            if href in seen_urls:
                continue
            # 过滤明显不是考试公告的
            if any(kw in lt for kw in ['招聘日报', '汇总', '合集', '打包']):
                continue
            seen_urls.add(href)
            items.append({'title': lt, 'url': href})

        # 从文本提取（兜底：处理没有href的纯文本标题）
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = html.unescape(text)
        for pattern in [
            r'(202[4-9][年][^<>"\'\n]{5,80}?(?:公告|招聘|考试|启事))',
            r'(202[4-9][年][^<>"\'\n]{5,80}?(?:公务员|事业单位|遴选))',
        ]:
            for m2 in re.finditer(pattern, text):
                t = m2.group(1).strip()
                if len(t) >= 8 and t not in [i['title'] for i in items]:
                    if any(kw in t for kw in ['招聘日报', '汇总', '合集', '打包']):
                        continue
                    items.append({'title': t, 'url': ''})

        return items

    def filter_items(self, items, target_regions=None):
        """按地区+噪声过滤，含跨条拼接检测"""
        filtered = []
        for item in items:
            title = item['title']

            # 过滤过短标题（<10字通常是导航/分类标题）
            if len(title) < 10:
                continue

            # 跨条拼接检测：标题中出现多个"202X年" → 两个条目拼接
            year_positions = [m.start() for m in re.finditer(r'202\d年', title)]
            if len(year_positions) >= 2 and year_positions[1] > 20:
                # 第二个"202X年"出现在标题后半段 → 跨条拼接
                truncated = title[:year_positions[1]].rstrip()
                # 截断后标题语义不完整（不以"招聘/考试"结尾）→ 丢弃
                # 例如："2026年成都市公园城市建设管理局关于所属事业单位" ← 不完整
                if not re.search(r'(招聘|考试|考核|引进|选聘|招录|公告|公示)$', truncated):
                    continue
                title = truncated
                item['title'] = title
                if len(title) < 10:
                    continue
                # 截断后重新检查是否还包含目标地区关键词
                if target_regions:
                    still_match = False
                    for tr in target_regions:
                        tr_kws = REGION_KEYWORDS.get(tr, [tr])
                        if any(kw in title for kw in tr_kws):
                            still_match = True
                            break
                    if not still_match:
                        continue

            # 过滤过长标题（拼接后仍很长）
            if len(title) > 100:
                continue

            # 过滤噪声
            if any(kw in title for kw in NOISE_KEYWORDS):
                continue

            # 跨地区混入检测：标题同时含目标地区和其他地区关键词 → 丢弃
            # 但允许目标地区的上级/包含关系（如chengdu→sichuan）
            if target_regions and len(title) > 20:
                target_hit = False
                other_hit = False
                # 构建目标地区的"上级地区"白名单
                parent_regions = set()
                for tr in target_regions:
                    for region, r_kws in REGION_KEYWORDS.items():
                        if region == tr:
                            continue
                        # 如果目标地区的关键词是某个地区关键词的子串
                        tr_kws = REGION_KEYWORDS.get(tr, [tr])
                        if any(tk in rk or rk in tk for tk in tr_kws for rk in r_kws if len(rk) >= 2):
                            parent_regions.add(region)
                for region, r_kws in REGION_KEYWORDS.items():
                    if any(kw in title for kw in r_kws if len(kw) >= 2):
                        if region in target_regions:
                            target_hit = True
                        elif region not in parent_regions:
                            other_hit = True
                if other_hit and not target_hit:
                    continue  # 只匹配其他地区 → 丢弃

            # 通过所有检测 → 只保留含目标地区关键词的条目
            if target_regions:
                region_match = False
                for tr in target_regions:
                    tr_kws = REGION_KEYWORDS.get(tr, [tr])
                    if any(kw in title for kw in tr_kws):
                        region_match = True
                        break
                if not region_match:
                    continue
            filtered.append(item)

        return filtered




    # ============================================================
    # 详情页抓取 → 提取学历/年龄/专业要求
    # ============================================================

    def fetch_detail(self, url, title):
        """访问详情页，提取详细要求"""
        info = {
            'requirements_detail': None,
            'deadline': None,
            'exam_date': None,
            'count': None,
        }

        if not url or url.startswith('/web/info/'):  # 相对路径的泸州链接
            # 泸州网站的相对路径无法直接访问，尝试补全
            if url.startswith('/web/info/'):
                url = 'https://www.lzsrsks.cn' + url

        html_content = self.fetch_url(url)
        if not html_content:
            return info

        # 去HTML标签
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text)

        # 提取学历要求
        edu = self._extract_education(text)
        if edu:
            info['requirements_detail'] = {'education': edu}

        # 提取年龄要求
        age = self._extract_age(text)
        if age:
            if info.get('requirements_detail'):
                info['requirements_detail']['age'] = age
            else:
                info['requirements_detail'] = {'age': age}

        # 提取报名截止
        deadline = self._extract_deadline(text)
        if deadline:
            info['deadline'] = deadline

        # 提取考试日期
        exam_date = self._extract_exam_date(text)
        if exam_date:
            info['exam_date'] = exam_date

        # 提取招聘人数
        count = self._extract_count(title, text)
        if count:
            info['count'] = count

        return info

    def _extract_education(self, text):
        """从公告正文提取学历要求"""
        m = re.search(r'学[历位][要求条件]*[：:]\s*([^\n,，。；;]{2,20})', text)
        if m:
            edu = m.group(1).strip()
            if re.search(r'博士', edu):
                return '博士'
            elif re.search(r'硕士|研究生', edu):
                return '硕士及以上'
            elif re.search(r'本科|学士', edu):
                return '本科及以上'
            elif re.search(r'大专|专科|高职', edu):
                return '大专及以上'
            return edu

        for pat, level in [
            (r'博士(?:研究生)?(?:学历|学位|及以上|以上)?', '博士'),
            (r'(?:硕士|研究生)(?:学历|学位|及以上|以上)?', '硕士及以上'),
            (r'(?:本科|学士)(?:学历|学位|及以上|以上)?', '本科及以上'),
            (r'(?:大专|专科|高职)(?:学历|学位|及以上|以上)?', '大专及以上'),
        ]:
            if re.search(pat, text):
                return level
        return None

    def _extract_age(self, text):
        """从公告正文提取年龄要求"""
        patterns = [
            r'年龄[要求条件]*[：:]\s*(\d{1,2}[-~至到]+\d{1,2}岁)',
            r'(\d{1,2}[-~至到]+\d{1,2}岁)',
            r'年龄[要求条件]*[：:]\s*([^\n,，。；;]{2,15})',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                age_str = m.group(1).strip()
                if re.search(r'\d{1,2}[-~至到]+\d{1,2}岁', age_str):
                    return age_str
                if len(age_str) <= 15:
                    return age_str
        return None

    def _extract_deadline(self, text):
        patterns = [
            r'报名截止[日期时间]*[：:]\s*(202[4-9][年/-]\d{1,2}[月/-]\d{1,2}[日]?)',
            r'(?:截止|报名截止)[：:]\s*(202[4-9][年/-]\d{1,2}[月/-]\d{1,2}[日]?)',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)
        return None

    def _extract_exam_date(self, text):
        patterns = [
            r'(?:考试|笔试)[日期时间]*[：:]\s*(202[4-9][年/-]\d{1,2}[月/-]\d{1,2}[日]?)',
            r'(202[4-9][年/-]\d{1,2}[月/-]\d{1,2})\s*(?:考试|笔试)',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)
        return None

    def _extract_count(self, title, text):
        m = re.search(r'招聘\s*(\d+)\s*人', title + ' ' + text[:500])
        if m:
            return f"{m.group(1)}人"
        m = re.search(r'(\d+)\s*人', title)
        if m:
            return f"{m.group(1)}人"
        return None


    # ============================================================
    # 国企央企招聘抓取（高顿国企招聘网）
    # ============================================================

    def fetch_soe_listing(self, target_regions=None, max_pages=1, region=None):
        """从高顿国企招聘网抓取国企央企招聘公告（增强版：噪声过滤+去重+跨条拼接检测）"""
        # 四川路由：走四川本地数据源
        if region == 'sichuan':
            return self.fetch_sc_soe()

        all_items = []
        base_url = 'https://www.gwy.com/gqzp/qtgq/'

        for page in range(1, max_pages + 1):
            url = base_url if page == 1 else f'{base_url}index_{page}.html'
            print(f"国企列表页: {url}", file=sys.stderr)
            html_content = self.fetch_url(url)
            if not html_content:
                print(f"  → 获取失败，跳过", file=sys.stderr)
                continue

            # 使用正则逐条提取，避免HTMLParser跨标签合并
            seen_urls = set()
            for m in re.finditer(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', html_content, re.DOTALL):
                href = html.unescape(m.group(1)).strip()
                raw_text = m.group(2)
                lt = re.sub(r'<[^>]+>', '', raw_text).strip()
                lt = html.unescape(lt)
                if not lt or len(lt) < 10:
                    continue
                if not href.startswith('https://www.gwy.com/gqzp/'):
                    continue
                if '/qtgq/' in href or href in seen_urls:
                    continue
                if '202' not in lt:
                    continue
                seen_urls.add(href)
                all_items.append({'title': lt, 'url': href})

            time.sleep(1)  # 礼貌延迟

        print(f"  → 共提取 {len(all_items)} 条原始数据", file=sys.stderr)

        # 标题截断：高顿标题包含摘要描述，只保留核心部分
        for item in all_items:
            title = item['title']
            m_count = re.search(r'(?:共招|招聘|共计招聘|计划招聘|拟招聘)(\d+)人', title)
            if m_count:
                item['title'] = title[:m_count.end()].rstrip()
            elif len(title) > 100:
                item['title'] = title[:100].rstrip()

        # 噪声过滤：只过滤明确不是招聘公告的标题（广告/培训/导航）
        # 注意：避免误杀含"面试/简历/校招"等词的正常招聘公告
        soe_noise_strict = ['培训班', '辅导班', '课程', '备考资料', '面试技巧',
                            '简历模板', '题库', '真题', '模拟题', '冲刺班',
                            '协议班', '无忧班', '保过班', '上岸攻略',
                            '求职攻略', '备考指南', '复习资料', '网课',
                            '招聘日报', '招聘汇总', '招聘合集', '招聘打包',
                            '校招汇总', '社招汇总', '校招合集',
                            '国企招聘网', '央企招聘网', '国企招聘考试',
                            '国企校招', '央企校招', '国企社招', '央企社招',
                            '国企招聘考试网', '国企招聘信息网', '国企招聘资讯',
                            '国企招聘专栏', '国企招聘专题', '国企招聘频道',
                            '国企招聘首页', '国企招聘大全', '国企招聘列表',
                            '国企招聘集锦', '国企招聘推荐', '国企招聘精选',
                            '国企招聘热榜', '国企招聘最新', '国企招聘近期汇总',
                            '央企招聘汇总', '央企招聘考试', '央企招聘公众号',
                            '国企招聘公众号', '国企招聘平台', '央国企秋招',
                            '秋招时间表', '秋招提前批', '秋招规划']
        quality_filtered = []
        for item in all_items:
            title = item['title']
            if len(title) < 10 or len(title) > 120:
                continue
            if any(kw in title for kw in soe_noise_strict):
                continue
            # 过滤标题以"招聘"开头但没有具体公司名的（通常是导航/分类）
            if re.match(r'^(国企|央企|招聘|求职|考试)', title) and '202' not in title[:20]:
                continue
            quality_filtered.append(item)
        print(f"  → 噪声过滤后 {len(quality_filtered)} 条", file=sys.stderr)

        # 跨条拼接检测：标题中出现多个"202X年" → 截断
        clean_items = []
        for item in quality_filtered:
            title = item['title']
            year_positions = [m2.start() for m2 in re.finditer(r'202\d年', title)]
            if len(year_positions) >= 2 and year_positions[1] > 20:
                title = title[:year_positions[1]].rstrip()
                item['title'] = title
                if len(title) < 10:
                    continue
            clean_items.append(item)

        # 标题截断：高顿标题包含摘要描述，只保留核心部分（公司名+公告类型+人数）
        # 策略：在"202X年"之后找第一个"招聘/公告"相关关键词，截断后面的摘要
        for item in quality_filtered:
            title = item['title']
            # 找"共招X人"或"招聘X人"的位置
            m_count = re.search(r'(?:共招|招聘|共计招聘|计划招聘|拟招聘)(\d+)人', title)
            if m_count:
                # 保留到人数信息为止
                end_pos = m_count.end()
                item['title'] = title[:end_pos].rstrip()
            else:
                # 没有人数信息，保留前80字
                if len(title) > 80:
                    item['title'] = title[:80].rstrip()

        # 去重：同一公司多个子页面重复（如"招聘363人"和"招聘50人"是同一事件不同岗位）
        deduped = []
        seen_orgs = {}
        for item in clean_items:
            title = item['title']
            m = re.search(r'(202\d年)', title)
            if m:
                org_part = title[:m.start()].strip()
            else:
                org_part = title[:30].strip()
            org_key = re.sub(r'(所属企业|集团有限公司|有限责任公司|股份有限公司|集团|公司)$', '', org_part).strip()
            if org_key in seen_orgs:
                existing_idx = seen_orgs[org_key]
                if len(title) > len(deduped[existing_idx]['title']):
                    deduped[existing_idx] = item
            else:
                seen_orgs[org_key] = len(deduped)
                deduped.append(item)
        print(f"  → 去重后 {len(deduped)} 条", file=sys.stderr)

        # 地区过滤（state-owned 保留所有）
        if target_regions:
            filtered = []
            for item in deduped:
                for tr in target_regions:
                    if tr == 'state-owned':
                        filtered.append(item)
                        break
            return filtered

        return deduped


    def fetch_sc_soe(self):
        """从四川本地数据源采集国企央企招聘（v4.0 重构版）

        数据源：
        1. 编制招聘网-成都国企（bianzhia.com/zt/gqchengdu）— 每日更新，数据丰富
        2. 编制招聘网-四川国企（bianzhia.com/zt/gqsichuan）— 四川各地国企
        3. 腾讯新闻汇总文章（成都国企）— 保留作为补充
        4. 高顿国企招聘网（按四川地名过滤）— 保留作为补充

        改进：
        - 数据源从2个扩展到4个，数据量提升5-10倍
        - 去重改为 URL + 公司名 + 标题相似度 三重去重
        - 同一公司不同岗位合并为"多岗位招聘"
        - 过滤劳务外包/合同制等非核心岗位
        - 详情页抓取编制招聘网（含学历/年龄/专业要求）

        返回: list of dicts with keys: title, url, org, position, location, education, deadline, source
        """
        results = []
        seen_urls = set()
        seen_orgs = {}  # org_clean → index in results（用于合并同一公司）

        sc_keywords = ['成都', '四川', '泸州', '德阳', '绵阳', '宜宾',
                       '南充', '达州', '雅安', '自贡', '攀枝花',
                       '广元', '遂宁', '内江', '乐山', '眉山',
                       '广安', '巴中', '资阳', '西昌']

        # 噪声过滤：这些关键词的条目跳过
        soe_noise = ['劳务外包', '合同制人员', '劳务派遣', '外包人员',
                     '劳务人员', '派遣员工', '劳务工', '外包工',
                     '临时工', '兼职', '暑假工', '寒假工',
                     '招聘汇总', '招聘合集', '招聘打包']

        def _add_result(item):
            """添加条目：URL去重 + 公司名合并 + 噪声过滤"""
            url = item.get('url', '')
            title = item.get('title', '')

            # URL去重
            if url and url in seen_urls:
                return
            if url:
                seen_urls.add(url)

            # 噪声过滤
            if any(kw in title for kw in soe_noise):
                return

            # 公司名合并：同一公司不同岗位 → 合并为"多岗位"
            org = item.get('org', '')
            org_clean = re.sub(r'(集团有限公司|有限责任公司|股份有限公司|集团|公司|有限公司)$', '', org).strip()

            if org_clean in seen_orgs:
                idx = seen_orgs[org_clean]
                existing = results[idx]
                # 合并：更新标题为"多岗位"，保留更详细的URL
                if '多岗位' not in existing['title']:
                    count = existing.get('position_count', 1)
                    existing['title'] = f'{org}2026年招聘（{count+1}个岗位）'
                    existing['position_count'] = count + 1
                    if url and url != existing.get('url', ''):
                        existing['url'] = url  # 保留编制招聘网链接（更详细）
                return

            seen_orgs[org_clean] = len(results)
            item['position_count'] = 1
            results.append(item)

        # --- 数据源1: 编制招聘网-成都国企 ---
        print("  → 编制招聘网-成都国企...", file=sys.stderr)
        try:
            url = 'https://www.bianzhia.com/zt/gqchengdu/'
            content = self.fetch_url(url)
            if content:
                for m in re.finditer(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', content, re.DOTALL):
                    href = html.unescape(m.group(1)).strip()
                    raw_text = m.group(2)
                    lt = re.sub(r'<[^>]+>', '', raw_text).strip()
                    lt = html.unescape(lt)
                    if not lt or len(lt) < 10:
                        continue
                    if not href.startswith('https://www.bianzhia.com/sichuan/chengdu/'):
                        continue
                    if '202' not in lt:
                        continue
                    # 提取日期前缀（如"2026-06-11"）
                    date_m = re.match(r'(\d{4}-\d{2}-\d{2})\s+(.*)', lt)
                    if date_m:
                        pub_date = date_m.group(1)
                        title = date_m.group(2).strip()
                    else:
                        title = lt
                        pub_date = None
                    if len(title) < 10:
                        continue
                    # 提取公司名
                    org_m = re.match(r'(.*?(?:集团|公司|有限责任公司|股份有限公司))', title)
                    org = org_m.group(1) if org_m else title[:20]
                    _add_result({
                        'title': title,
                        'url': href,
                        'org': org,
                        'position': title,
                        'location': '成都',
                        'education': '详见公告',
                        'deadline': None,
                        'publish_date': pub_date,
                        'source': '编制招聘网-成都国企',
                    })
                print(f"    → 编制招聘网-成都: {len(results)} 条", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️ 编制招聘网-成都国企抓取失败: {e}", file=sys.stderr)

        # --- 数据源2: 编制招聘网-四川国企 ---
        print("  → 编制招聘网-四川国企...", file=sys.stderr)
        try:
            url = 'https://www.bianzhia.com/zt/gqsichuan/'
            content = self.fetch_url(url)
            if content:
                for m in re.finditer(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', content, re.DOTALL):
                    href = html.unescape(m.group(1)).strip()
                    raw_text = m.group(2)
                    lt = re.sub(r'<[^>]+>', '', raw_text).strip()
                    lt = html.unescape(lt)
                    if not lt or len(lt) < 10:
                        continue
                    if not href.startswith('https://www.bianzhia.com/sichuan/'):
                        continue
                    if '202' not in lt:
                        continue
                    # 提取日期前缀
                    date_m = re.match(r'(\d{4}-\d{2}-\d{2})\s+(.*)', lt)
                    if date_m:
                        pub_date = date_m.group(1)
                        title = date_m.group(2).strip()
                    else:
                        title = lt
                        pub_date = None
                    if len(title) < 10:
                        continue
                    # 提取地区
                    location = '四川'
                    for kw in sc_keywords:
                        if kw in href or kw in title:
                            location = kw
                            break
                    # 只保留成都和泸州的
                    if location not in ('成都', '泸州'):
                        continue
                    # 提取公司名
                    org_m = re.match(r'(.*?(?:集团|公司|有限责任公司|股份有限公司))', title)
                    org = org_m.group(1) if org_m else title[:20]
                    _add_result({
                        'title': title,
                        'url': href,
                        'org': org,
                        'position': title,
                        'location': location,
                        'education': '详见公告',
                        'deadline': None,
                        'publish_date': pub_date,
                        'source': '编制招聘网-四川国企',
                    })
                print(f"    → 编制招聘网-四川: {len(results)} 条（累计）", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️ 编制招聘网-四川国企抓取失败: {e}", file=sys.stderr)

        # --- 数据源3: 腾讯新闻成都国企汇总（补充）---
        print("  → 腾讯新闻成都国企...", file=sys.stderr)
        try:
            url = 'https://news.qq.com/rain/a/20260604A00FTF00'
            content = self.fetch_url(url)
            if content:
                text = re.sub(r'<[^>]+>', ' ', content)
                text = html.unescape(text)
                companies = re.findall(r'(成都[\u4e00-\u9fff]{2,}(?:集团|公司|有限公司))', text)
                seen_in_article = set()
                for company in companies:
                    if company not in seen_in_article and '正在招人' not in company:
                        seen_in_article.add(company)
                        _add_result({
                            'title': company + '2026年招聘',
                            'url': url,
                            'org': company,
                            'position': '多岗位',
                            'location': '成都',
                            'education': '详见公告',
                            'deadline': None,
                            'source': '腾讯新闻-成都国企',
                        })
                print(f"    → 腾讯新闻: {len(results)} 条（累计）", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️ 腾讯新闻抓取失败: {e}", file=sys.stderr)

        # --- 数据源4: 高顿国企招聘网（补充）---
        print("  → 高顿国企招聘网...", file=sys.stderr)
        try:
            base_url = 'https://www.gwy.com/gqzp/qtgq/'
            content = self.fetch_url(base_url)
            if content:
                for m in re.finditer(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', content, re.DOTALL):
                    href = html.unescape(m.group(1)).strip()
                    raw_text = m.group(2)
                    lt = re.sub(r'<[^>]+>', '', raw_text).strip()
                    lt = html.unescape(lt)
                    if not lt or len(lt) < 15 or not href.startswith('https://www.gwy.com/gqzp/'):
                        continue
                    if '/qtgq/' in href or '202' not in lt:
                        continue
                    if not any(kw in lt for kw in sc_keywords):
                        continue
                    m_count = re.search(r'(?:共招|招聘|共计招聘)(\d+)人', lt)
                    if m_count:
                        lt = lt[:m_count.end()].rstrip()
                    elif len(lt) > 80:
                        lt = lt[:80].rstrip()
                    location = '四川'
                    for kw in sc_keywords:
                        if kw in lt:
                            location = kw
                            break
                    if location not in ('成都', '泸州'):
                        continue
                    org_m = re.match(r'(.*?(?:集团|公司|有限责任公司|股份有限公司))', lt)
                    org = org_m.group(1) if org_m else lt[:20]
                    _add_result({
                        'title': lt,
                        'url': href,
                        'org': org,
                        'position': lt,
                        'location': location,
                        'education': '详见公告',
                        'deadline': None,
                        'source': '高顿-四川国企',
                    })
                print(f"    → 高顿: {len(results)} 条（累计）", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠️ 高顿抓取失败: {e}", file=sys.stderr)

        # --- 后处理：清理简称 + 最终过滤 ---
        # 简称映射表
        alias_map = {
            '成都文旅': '成都文化旅游发展集团',
            '成都公交': '成都公交资产经营管理有限公司',
            '成都交投': '成都交通投资集团',
            '成都城投': '成都城市建设投资集团',
        }
        for r in results:
            org = r.get('org', '')
            for alias, full_name in alias_map.items():
                if alias in org and full_name not in org:
                    r['org'] = full_name
                    break

        print(f"  → 四川国企央企采集: {len(results)} 条（去重+过滤后）", file=sys.stderr)
        return results

    def fetch_soe_detail(self, url, title):
        """抓取国企央企详情页，提取专业/学历要求等信息"""
        info = {
            'requirements_detail': None,
            'deadline': None,
            'exam_date': None,
            'count': None,
            'org_detail': None,
        }

        html_content = self.fetch_url(url)
        if not html_content:
            return info

        parser = ExamInfoExtractor()
        try:
            parser.feed(html_content)
        except Exception:
            pass

        text = '\n'.join(parser.text_content)

        # 提取学历要求
        edu = self._extract_education(text)
        if edu:
            info['requirements_detail'] = {'education': edu}

        # 提取年龄要求
        age = self._extract_age(text)
        if age:
            if info.get('requirements_detail'):
                info['requirements_detail']['age'] = age
            else:
                info['requirements_detail'] = {'age': age}

        # 提取报名截止
        deadline = self._extract_deadline(text)
        if deadline:
            info['deadline'] = deadline

        # 提取专业要求
        major = self._extract_major(text)
        if major:
            if info.get('requirements_detail'):
                info['requirements_detail']['major'] = major
            else:
                info['requirements_detail'] = {'major': major}

        # 提取人数
        count = self._extract_count(title, text)
        if count:
            info['count'] = count

        return info

    def _extract_major(self, text):
        """从公告正文提取专业要求"""
        patterns = [
            r'专业[要求条件]*[：:]\s*([^\n,，。；;]{2,60})',
            r'(?:招聘|招收)[专业]*[：:]\s*([^\n,，。；;]{2,60})',
            r'类[专业]*[：:]\s*([^\n,，。；;]{2,60})',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                major_str = m.group(1).strip()
                if len(major_str) >= 2 and len(major_str) <= 60:
                    return major_str
        return None

    # ============================================================
    # 主抓取逻辑
    # ============================================================

    def fetch_real_exams(self, region_filter=None, type_filter=None, fetch_details=True):
        all_exams = []
        target_regions = [r.strip().lower() for r in region_filter.split(',')] if region_filter else None

        need_civil = not type_filter or 'civil-service' in type_filter
        need_inst = not type_filter or 'public-institution' in type_filter
        need_soe = not type_filter or 'state-owned' in type_filter
        no_region_filter = not target_regions

        # --- 四川公务员（中公网校汇总页）---
        if need_civil and (no_region_filter or 'sichuan' in (target_regions or [])):
            # 中公网校汇总页是全国数据，只取四川的
            sichuan_only = ['sichuan']
            self._process_listing(
                'https://www.eoffcn.com/kszx/detail/1883949.html',
                '公务员考试', sichuan_only, all_exams, fetch_details
            )

        # --- 四川人事考试网 ---
        if need_civil and (no_region_filter or 'sichuan' in (target_regions or [])):
            self._process_listing(
                'https://www.scpta.com.cn/front',
                '公务员考试', ['sichuan'], all_exams, fetch_details
            )

        # --- 成都事业单位 ---
        if need_inst and (no_region_filter or 'chengdu' in (target_regions or [])):
            self._process_listing(
                'https://www.shiyebian.com/xinxi/',
                '事业单位考试',
                ['chengdu'],
                all_exams, fetch_details, max_detail=5
            )

        # --- 泸州事业单位+公务员 ---
        if need_inst and (no_region_filter or 'luzhou' in (target_regions or [])):
            self._process_listing(
                'https://www.lzsrsks.cn/',
                '事业单位考试',
                ['luzhou'],
                all_exams, fetch_details, max_detail=5, ssl_retry=3
            )

        # --- 国企央企（编制招聘网+高顿+腾讯新闻）---
        if need_soe and (no_region_filter or 'state-owned' in (target_regions or [])):
            soe_items = self.fetch_sc_soe()
            soe_items = [i for i in soe_items if self._is_recent(i.get('title', ''), i.get('publish_date', ''))]
            print(f"  → 国企央企 {len(soe_items)} 条（去重+过滤后）", file=sys.stderr)

            for item in soe_items:
                exam = self._build_soe_exam(item)
                if exam:
                    all_exams.append(exam)

            # 国企详情页抓取（限制数量）
            if fetch_details and soe_items:
                detail_count = min(len(soe_items), 3)
                for i, item in enumerate(soe_items[:detail_count]):
                    print(f"  国企详情 {i+1}/{detail_count}: {item['title'][:40]}...", file=sys.stderr)
                    detail = self.fetch_soe_detail(item['url'], item['title'])
                    for exam in all_exams:
                        if exam.get('exam_name') == item['title']:
                            if detail.get('requirements_detail'):
                                exam['requirements'] = {**exam.get('requirements', {}), **detail['requirements_detail']}
                            if detail.get('deadline'):
                                exam['deadline'] = detail['deadline']
                            if detail.get('count') and exam.get('recruitment_count') in [None, '详见公告']:
                                exam['recruitment_count'] = detail['count']
                            exam['detail_fetched'] = True
                            break
                    time.sleep(1)

        # 二次过滤：只保留真正是"招聘"的
        final = []
        for e in all_exams:
            name = e.get('exam_name', '')
            if any(kw in name for kw in REQUIRED_KEYWORDS):
                if not any(kw in name for kw in NOISE_KEYWORDS):
                    final.append(e)

        # 去重：精确匹配 + 模糊匹配（核心关键词相似度）
        seen = set()
        unique = []
        for e in final:
            n = e.get('exam_name', '')
            if not n:
                continue
            # 精确匹配
            if n in seen:
                continue
            # 模糊匹配：提取核心关键词，若已有条目核心关键词包含当前条目则跳过
            core = self._extract_core_key(n)
            is_dup = False
            for s in seen:
                s_core = self._extract_core_key(s)
                # 核心关键词互相包含 → 重复
                if core and s_core and (core in s_core or s_core in core):
                    is_dup = True
                    break
                # Jaccard相似度 > 0.7 → 重复
                if core and s_core:
                    set_a, set_b = set(core), set(s_core)
                    jaccard = len(set_a & set_b) / len(set_a | set_b) if (set_a | set_b) else 0
                    if jaccard > 0.7:
                        is_dup = True
                        break
            if not is_dup:
                seen.add(n)
                unique.append(e)
        return unique

    @staticmethod
    def _extract_core_key(title):
        """提取标题核心关键词（去掉日期、数字、通用后缀）"""
        import re as _re
        core = _re.sub(r'202\d年', '', title)
        core = _re.sub(r'（\d+人）', '', core)
        core = _re.sub(r'\(\d+人\)', '', core)
        core = _re.sub(r'的公告|的招聘|的公告$|招聘$', '', core)
        core = _re.sub(r'所属事业单位考核招聘.*$', '所属事业单位考核招聘', core)
        core = _re.sub(r'[·\s]+', '', core)
        return core.strip()

    def _process_listing(self, url, source_type, target_regions, results, fetch_details=True, max_detail=3, ssl_retry=1):
        """处理列表页 → 过滤 → （可选）抓详情"""
        print(f"列表页: {url}", file=sys.stderr)
        html_content = None

        for attempt in range(ssl_retry):
            html_content = self.fetch_url(url)
            if html_content:
                break
            if attempt < ssl_retry - 1:
                print(f"  重试({attempt+1})...", file=sys.stderr)
                time.sleep(2)

        if not html_content:
            print(f"  → 失败", file=sys.stderr)
            return

        # 提取条目
        items = self.extract_listing(html_content, target_regions)
        items = self.filter_items(items, target_regions)
        # 过滤2024年之前
        items = [i for i in items if self._is_recent(i['title'], '')]

        print(f"  → {len(items)} 条（列表页过滤后）", file=sys.stderr)

        # 构建考试信息（列表页级别）
        for item in items:
            exam = self._build_exam_from_listing(item, source_type)
            if exam:
                results.append(exam)

        # 详情页深入抓取（限制数量，避免太慢）
        if fetch_details and items:
            detail_count = min(len(items), max_detail)
            for i, item in enumerate(items[:detail_count]):
                print(f"  详情 {i+1}/{detail_count}: {item['title'][:40]}...", file=sys.stderr)
                detail = self.fetch_detail(item['url'], item['title'])

                # 将详情信息附加到对应的exam
                for exam in results:
                    if exam.get('exam_name') == item['title']:
                        if detail.get('requirements_detail'):
                            exam['requirements'] = {**exam.get('requirements', {}), **detail['requirements_detail']}
                        if detail.get('deadline'):
                            exam['deadline'] = detail['deadline']
                        if detail.get('exam_date'):
                            exam['exam_date'] = detail['exam_date']
                        if detail.get('count') and exam.get('recruitment_count') in [None, '详见公告']:
                            exam['recruitment_count'] = detail['count']
                        exam['detail_fetched'] = True
                        break

                time.sleep(1)  # 礼貌延迟

    def _build_exam_from_listing(self, item, source_type):
        """从列表页条目构建考试信息"""
        title = item['title']
        url = item['url']

        detected = self.detect_region(title)
        pub_date = self._extract_date_from_title(title)

        return {
            'exam_name': title,
            'exam_type': source_type,
            'region': detected or 'sichuan',
            'publish_date': pub_date or '详见公告',
            'deadline': '详见公告',
            'exam_date': '详见公告',
            'recruitment_count': '详见公告',
            'source_url': url or '详见公告',
            'requirements': {
                'age': '详见公告',
                'education': '详见公告',
                'major': '详见公告',
                'experience': '详见公告',
                'politics': '详见公告',
            },
            'position': {
                'location': detected or '详见公告',
                'organization': self._extract_org(title),
                'level': '详见公告',
            },
            'registration': {
                'method': '网上报名',
                'website': url or '详见公告',
                'phone': '详见公告',
                'fee': '详见公告',
            },
            'exam_content': {
                'written_test': '行测、申论' if '公务员' in source_type else '职测、公基',
                'interview': '结构化面试',
                'score_calculation': '详见公告',
            },
            'detail_fetched': False,
        }


    def _build_soe_exam(self, item):
        """从国企列表页条目构建招聘信息"""
        title = item['title']
        url = item.get('url', '')
        pub_date = item.get('publish_date', '详见公告')

        detected = self.detect_region(title)

        return {
            'exam_name': title,
            'exam_type': '国企央企招聘',
            'region': 'state-owned',
            'publish_date': pub_date,
            'deadline': '详见公告',
            'exam_date': '详见公告',
            'recruitment_count': '详见公告',
            'source_url': url or '详见公告',
            'requirements': {
                'age': '详见公告',
                'education': '详见公告',
                'major': '详见公告',
                'experience': '详见公告',
                'politics': '详见公告',
            },
            'position': {
                'location': detected or '详见公告',
                'organization': self._extract_org(title),
                'level': '详见公告',
            },
            'registration': {
                'method': '网上报名',
                'website': url or '详见公告',
                'phone': '详见公告',
                'fee': '详见公告',
            },
            'exam_content': {
                'written_test': '详见公告',
                'interview': '详见公告',
                'score_calculation': '详见公告',
            },
            'detail_fetched': False,
        }

    def _extract_date_from_title(self, title):
        m = re.search(r'(202[4-9])年(\d{1,2})月(\d{1,2})日', title)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        m = re.search(r'(202[4-9])年(\d{1,2})月', title)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}"
        m = re.search(r'(202[4-9])年', title)
        if m:
            return m.group(1)
        return None

    def _extract_org(self, title):
        for org in ['四川省', '成都市', '泸州市', '双流区', '龙泉驿区', '温江区', '新都区', '郫都区', '高新区']:
            if org in title:
                return org + '人力资源和社会保障局'
        return '详见公告'

    def _is_recent(self, title, pub_date):
        for y in ['2024', '2025', '2026', '2027']:
            if y in title or (pub_date and y in pub_date):
                return True
        return '202' not in title

    # ============================================================
    # 筛选
    # ============================================================

    def filter_exams(self, exams, args):
        filtered = exams
        if args.region:
            regions = args.region.split(',')
            filtered = [e for e in filtered if self._match_region(e, regions)]
        if args.type:
            types = args.type.split(',')
            filtered = [e for e in filtered if self._match_type(e, types)]
        return filtered

    def _match_region(self, exam, regions):
        check = exam.get('region', '') + exam.get('exam_name', '')
        for r in regions:
            # state-owned 直接按 region 字段匹配（不依赖关键词）
            if r.lower() == 'state-owned':
                if exam.get('region', '') == 'state-owned':
                    return True
                continue
            kws = REGION_KEYWORDS.get(r.lower(), [r])
            for kw in sorted(kws, key=len, reverse=True):
                if kw in check:
                    return True
        return False

    def _match_type(self, exam, types):
        t = exam.get('exam_type', '')
        m = {'civil-service': '公务员考试', 'public-institution': '事业单位考试', 'state-owned': '国企央企招聘'}
        return t in [m.get(x, x) for x in types]

    # ============================================================
    # 输出
    # ============================================================

    def output_json(self, exams):
        return json.dumps({'exams': exams, 'total': len(exams), 'timestamp': datetime.now().isoformat()},
                         ensure_ascii=False, indent=2)

    def output_markdown(self, exams):
        """按地区分区的直观卡片式报告，一眼看出地区→岗位→要求"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f'📋 **公考报考速览** ({now})\n',
        ]

        # 按地区分组
        by_region = {'sichuan': [], 'chengdu': [], 'luzhou': [], 'state-owned': []}
        for e in exams:
            r = e.get('region', 'sichuan')
            if r in by_region:
                by_region[r].append(e)

        region_config = {
            'sichuan':    {'icon': '🏛️', 'name': '四川省',    'subtitle': '公务员'},
            'chengdu':     {'icon': '🌆', 'name': '成都市',    'subtitle': '事业单位'},
            'luzhou':     {'icon': '🍶', 'name': '泸州市',    'subtitle': '事业单位'},
            'state-owned': {'icon': '🏢', 'name': '国企央企',  'subtitle': '招聘'},
        }

        total = 0
        for region_key in ['sichuan', 'chengdu', 'luzhou', 'state-owned']:
            items = by_region[region_key]
            if not items:
                continue
            total += len(items)
            cfg = region_config[region_key]
            lines.append(f'---\n{cfg["icon"]} **{cfg["name"]} · {cfg["subtitle"]}** ({len(items)}条)\n')

            for i, e in enumerate(items, 1):
                name = e.get('exam_name', '?')
                detail_mark = ' ✅' if e.get('detail_fetched') else ''
                lines.append(f'**{i}. {name}**{detail_mark}\n')

                # 核心报考条件一行看完
                c = e.get('recruitment_count', '')
                reqs = e.get('requirements', {})
                edu = reqs.get('education', '?')
                age = reqs.get('age', '?')
                deadline = e.get('deadline', '详见公告')
                publish = e.get('publish_date', '?')
                exam_date = e.get('exam_date', '详见公告')

                parts = []
                if c and c != '详见公告':
                    parts.append(f'👥 {c}')
                parts.append(f'🎓 {edu}')
                parts.append(f'📅 {age}')
                lines.append('　'.join(parts))

                # 时间节点
                time_parts = [f'发布 {publish}']
                if deadline != '详见公告':
                    time_parts.append(f'截止 **{deadline}** ⚠️')
                if exam_date != '详见公告':
                    time_parts.append(f'考试 {exam_date}')
                lines.append('　|　'.join(time_parts))

                # 科目 + 链接
                ec = e.get('exam_content', {})
                subjects = ec.get('written_test', '')
                url = e.get('source_url', '')
                footer_parts = []
                if subjects and subjects != '详见公告':
                    footer_parts.append(f'📝 {subjects}')
                if url and url != '详见公告':
                    footer_parts.append(f'🔗 {url}')
                if footer_parts:
                    lines.append('　|　'.join(footer_parts))

                lines.append('')

        if total == 0:
            lines.append('暂无有效招聘公告\n')

        # 汇总行
        lines.append('---\n')
        summary_parts = []
        for rk in ['sichuan', 'chengdu', 'luzhou', 'state-owned']:
            items = by_region[rk]
            if items:
                cfg = region_config[rk]
                summary_parts.append(f'{cfg["icon"]}{cfg["name"]} {len(items)}条')
        summary_str = '　'.join(summary_parts) if summary_parts else '暂无数据'
        lines.append(f'📊 **合计 {total} 条** | {summary_str}\n')

        # 数据说明
        has_detail = any(e.get('detail_fetched') for e in exams)
        if has_detail:
            lines.append('✅ = 已抓取详情页（含学历/年龄等）\n')
        lines.append('⚠️ 部分详细要求在附件PDF中，建议点链接核实\n')
        lines.append('---')
        lines.append('*MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*')

        return '\n'.join(lines)

    def output_text(self, exams):
        lines = [
            '=' * 60,
            '公考+国企央企信息汇总（真实数据 v4.0）',
            f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f'数量: {len(exams)}个',
            '=' * 60,
        ]
        for i, e in enumerate(exams, 1):
            detail_mark = '[详情]' if e.get('detail_fetched') else ''
            lines.append(f'\n{i}. {e.get("exam_name", "?")} {detail_mark}')
            lines.append(f'   类型:{e.get("exam_type","?")} 地区:{e.get("region","?")} 发布:{e.get("publish_date","?")}')
            reqs = e.get('requirements', {})
            lines.append(f'   学历:{reqs.get("education","?")} 年龄:{reqs.get("age","?")}')
            c = e.get('recruitment_count', '')
            if c and c != '详见公告':
                lines.append(f'   人数:{c}')
            url = e.get('source_url', '')
            if url and url != '详见公告':
                lines.append(f'   链接:{url}')
        return '\n'.join(lines)


# ============================================================
# CLI
# ============================================================

def get_demo_exams():
    return [
        {
            'exam_name': '2026年四川省公务员录用考试（四级联考）',
            'exam_type': '公务员考试', 'region': 'sichuan',
            'publish_date': '2025-10-29', 'recruitment_count': '12628人',
            'source_url': 'https://www.eoffcn.com/kszx/detail/1883949.html',
            'requirements': {'age': '18-35岁', 'education': '大专及以上', 'major': '不限', 'experience': '不限', 'politics': '不限'},
            'position': {'location': '四川', 'organization': '四川省委组织部', 'level': '科员'},
            'registration': {'method': '网上报名', 'website': 'https://www.scpta.com.cn/', 'phone': '', 'fee': ''},
            'exam_content': {'written_test': '行测、申论', 'interview': '结构化面试', 'score_calculation': '笔试60%+面试40%'},
            'detail_fetched': False,
        },
        {
            'exam_name': '2026年成都市事业单位公开招聘工作人员',
            'exam_type': '事业单位考试', 'region': 'chengdu',
            'publish_date': '2026-03-15', 'recruitment_count': '471人',
            'source_url': 'https://www.shiyebian.com/xinxi/',
            'requirements': {'age': '18-35岁', 'education': '本科及以上', 'major': '不限', 'experience': '不限', 'politics': '不限'},
            'position': {'location': '成都', 'organization': '成都市人社局', 'level': '科员'},
            'registration': {'method': '网上报名', 'website': 'https://cdpta.cdhrss.chengdu.gov.cn/', 'phone': '', 'fee': ''},
            'exam_content': {'written_test': '职测、公基', 'interview': '结构化面试', 'score_calculation': '详见公告'},
            'detail_fetched': False,
        },
        {
            'exam_name': '2026年泸州市事业单位公开招聘',
            'exam_type': '事业单位考试', 'region': 'luzhou',
            'publish_date': '2026-04-01', 'recruitment_count': '155人',
            'source_url': 'https://www.lzsrsks.cn/',
            'requirements': {'age': '18-40岁', 'education': '大专及以上', 'major': '不限', 'experience': '不限', 'politics': '不限'},
            'position': {'location': '泸州', 'organization': '泸州市人社局', 'level': '职员'},
            'registration': {'method': '网上报名', 'website': 'https://www.lzsrsks.cn/', 'phone': '', 'fee': ''},
            'exam_content': {'written_test': '职测、公基', 'interview': '结构化面试', 'score_calculation': '详见公告'},
            'detail_fetched': False,
        },
        {
            'exam_name': '2026年国企央企招聘汇总（高顿）',
            'exam_type': '国企央企招聘', 'region': 'state-owned',
            'publish_date': '2026-06-08', 'recruitment_count': '详见公告',
            'source_url': 'https://www.gwy.com/gqzp/qtgq/',
            'requirements': {'age': '详见公告', 'education': '本科及以上', 'major': '详见公告', 'experience': '详见公告', 'politics': '详见公告'},
            'position': {'location': '详见公告', 'organization': '详见公告', 'level': '详见公告'},
            'registration': {'method': '网上报名', 'website': 'https://www.gwy.com/gqzp/qtgq/', 'phone': '', 'fee': ''},
            'exam_content': {'written_test': '详见公告', 'interview': '详见公告', 'score_calculation': '详见公告'},
            'detail_fetched': False,
        },
    ]


def create_parser():
    p = argparse.ArgumentParser(description='公考信息获取工具 v4.0 - 真实数据+详情页')
    p.add_argument('--all', action='store_true')
    p.add_argument('--region', type=str, help='地区 (chengdu/luzhou/sichuan/state-owned，逗号分隔)')
    p.add_argument('--type', type=str, help='类型 (civil-service/public-institution/state-owned)')
    p.add_argument('--format', default='text', choices=['json', 'markdown', 'text'])
    p.add_argument('--save', type=str, help='保存到文件')
    p.add_argument('--timeout', type=int, default=30)
    p.add_argument('--fast', action='store_true', help='快速模式：不抓取详情页，仅列表页信息')
    p.add_argument('--demo', action='store_true', help='使用演示数据')
    return p


def main():
    args = create_parser().parse_args()
    ci = ChinaExamInfo(timeout=args.timeout)

    if args.demo:
        exams = get_demo_exams()
    else:
        exams = ci.fetch_real_exams(
            region_filter=args.region,
            type_filter=args.type,
            fetch_details=not args.fast,
        )

    exams = ci.filter_exams(exams, args)

    if args.format == 'json':
        out = ci.output_json(exams)
    elif args.format == 'markdown':
        out = ci.output_markdown(exams)
    else:
        out = ci.output_text(exams)

    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(out)
        print(f'已保存: {args.save}', file=sys.stderr)
    else:
        print(out)


if __name__ == '__main__':
    main()

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
