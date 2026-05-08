#!/usr/bin/env python3
"""
中国公考信息获取工具
使用Python标准库实现，零外部依赖
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


class ExamInfoExtractor(HTMLParser):
    """HTML解析器，用于提取考试信息"""
    
    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.current_class = None
        self.current_id = None
        self.text_content = []
        self.links = []
        self.in_link = False
        self.current_link = None
        self.data_stack = []
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        self.current_class = attrs_dict.get('class', '')
        self.current_id = attrs_dict.get('id', '')
        
        if tag == 'a':
            href = attrs_dict.get('href', '')
            if href:
                self.in_link = True
                self.current_link = {'href': href, 'text': ''}
                
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            if self.current_link:
                self.links.append(self.current_link)
            self.in_link = False
            self.current_link = None
        self.current_tag = None
        
    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_content.append(text)
            if self.in_link and self.current_link:
                self.current_link['text'] += text


class ChinaExamInfo:
    """中国公考信息获取类"""
    
    # 数据源配置
    DATA_SOURCES = {
        'civil_service': [
            {
                'name': '国家公务员局',
                'url': 'http://www.scrs.gov.cn/',
                'type': '公务员考试'
            },
            {
                'name': '四川省公务员考试',
                'url': 'http://rst.sc.gov.cn/',
                'type': '公务员考试'
            }
        ],
        'public_institution': [
            {
                'name': '四川人事考试网',
                'url': 'http://www.scpta.org.cn/',
                'type': '事业单位考试'
            },
            {
                'name': '成都人事考试网',
                'url': 'http://cdpta.cdhrss.chengdu.gov.cn/',
                'type': '事业单位考试'
            },
            {
                'name': '泸州人事考试网',
                'url': 'http://www.lzhrss.gov.cn/',
                'type': '事业单位考试'
            }
        ],
        'enterprise': [
            {
                'name': '四川人才网',
                'url': 'http://www.scrc.com.cn/',
                'type': '企业招聘'
            },
            {
                'name': '成都人才网',
                'url': 'http://www.rc114.com/',
                'type': '企业招聘'
            }
        ]
    }
    
    # 地区配置
    REGIONS = {
        'chengdu': ['成都', '成都市', '郫都区', '双流区', '龙泉驿区', '温江区', '新都区'],
        'luzhou': ['泸州', '泸州市', '江阳区', '纳溪区', '龙马潭区'],
        'mianyang': ['绵阳', '绵阳市', '涪城区', '游仙区'],
        'deyang': ['德阳', '德阳市', '旌阳区'],
        'leshan': ['乐山', '乐山市', '市中区'],
        'yibin': ['宜宾', '宜宾市', '翠屏区'],
        'nanchong': ['南充', '南充市', '顺庆区'],
        'dazhou': ['达州', '达州市', '通川区']
    }
    
    # 学历要求映射
    EDUCATION_LEVELS = {
        'college': ['大专', '专科', '高职'],
        'bachelor': ['本科', '学士'],
        'master': ['硕士', '研究生'],
        'doctor': ['博士']
    }
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        
    def fetch_url(self, url: str) -> Optional[str]:
        """获取URL内容"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                charset = 'utf-8'
                content_type = response.headers.get('Content-Type', '')
                if 'charset=' in content_type:
                    charset = content_type.split('charset=')[-1]
                return response.read().decode(charset, errors='ignore')
        except Exception as e:
            print(f"获取URL失败 {url}: {e}", file=sys.stderr)
            return None
            
    def parse_html(self, html_content: str) -> ExamInfoExtractor:
        """解析HTML内容"""
        parser = ExamInfoExtractor()
        try:
            parser.feed(html_content)
        except Exception as e:
            print(f"解析HTML失败: {e}", file=sys.stderr)
        return parser
        
    def extract_exams_from_text(self, text: str, exam_type: str, source: str) -> List[Dict]:
        """从文本中提取考试信息（简单实现）"""
        exams = []
        
        # 简单的正则匹配
        patterns = {
            'title': r'(202[0-9]年[^公告考试招聘]+(?:公告|考试|招聘|简章))',
            'date': r'(202[0-9]年\d{1,2}月\d{1,2}日)',
            'deadline': r'(报名截止|截止日期|截止时间)[:：]?\s*(202[0-9]年\d{1,2}月\d{1,2}日)?',
            'age': r'(年龄|年纪)[:：]?\s*(\d{1,2}[-至]\d{1,2}岁?)',
            'education': r'(学历|文凭|学位)[:：]?\s*([^\n]{2,10})',
            'location': r'(地点|地址|工作地)[:：]?\s*([^\n]{2,20})'
        }
        
        # 模拟数据（实际使用时应从真实网站获取）
        if '成都' in text or '四川' in text or '泸州' in text:
            exam = {
                'exam_name': f'{source} - {exam_type}考试公告',
                'exam_type': exam_type,
                'region': self._detect_region(text),
                'publish_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': '',
                'exam_date': '',
                'requirements': {
                    'age': self._extract_pattern(text, patterns['age']),
                    'education': self._extract_pattern(text, patterns['education']),
                    'major': '不限',
                    'experience': '不限',
                    'politics': '不限'
                },
                'position': {
                    'location': self._extract_pattern(text, patterns['location']) or self._detect_region(text),
                    'organization': source,
                    'level': '科员'
                },
                'registration': {
                    'method': '网上报名',
                    'website': '',
                    'phone': '',
                    'fee': '100元'
                },
                'exam_content': {
                    'written_test': '行测、申论',
                    'interview': '结构化面试',
                    'score_calculation': '笔试60%+面试40%'
                }
            }
            exams.append(exam)
            
        return exams
        
    def _extract_pattern(self, text: str, pattern: str) -> str:
        """提取匹配的文本"""
        try:
            match = re.search(pattern, text)
            if match:
                return match.group(2) if match.lastindex >= 2 else match.group(1)
        except:
            pass
        return ''
        
    def _detect_region(self, text: str) -> str:
        """检测地区"""
        for region, keywords in self.REGIONS.items():
            for keyword in keywords:
                if keyword in text:
                    return keyword
        return '未知'
        
    def filter_by_age(self, exam: Dict, age_range: str) -> bool:
        """按年龄筛选"""
        if not age_range:
            return True
        exam_age = exam.get('requirements', {}).get('age', '')
        if not exam_age:
            return True
        # 简单匹配
        return age_range in exam_age or exam_age == age_range
        
    def filter_by_education(self, exam: Dict, education: str) -> bool:
        """按学历筛选"""
        if not education:
            return True
        exam_edu = exam.get('requirements', {}).get('education', '')
        if not exam_edu:
            return True
        # 检查是否包含要求的学历关键词
        edu_keywords = self.EDUCATION_LEVELS.get(education, [])
        return any(keyword in exam_edu for keyword in edu_keywords)
        
    def filter_by_region(self, exam: Dict, regions: List[str]) -> bool:
        """按地区筛选"""
        if not regions:
            return True
        exam_region = exam.get('region', '') or exam.get('position', {}).get('location', '')
        if not exam_region:
            return True
        # 地区关键词映射
        region_keywords = {
            'chengdu': ['成都', '成都市', '郫都区', '双流区', '龙泉驿区', '温江区', '新都区'],
            'luzhou': ['泸州', '泸州市', '江阳区', '纳溪区', '龙马潭区', '古蔺县'],
            'mianyang': ['绵阳', '绵阳市', '涪城区', '游仙区'],
            'deyang': ['德阳', '德阳市', '旌阳区'],
            'leshan': ['乐山', '乐山市', '市中区'],
            'yibin': ['宜宾', '宜宾市', '翠屏区'],
            'nanchong': ['南充', '南充市', '顺庆区'],
            'dazhou': ['达州', '达州市', '通川区']
        }
        # 收集所有需要匹配的关键词
        match_keywords = []
        for region in regions:
            if region.lower() in region_keywords:
                match_keywords.extend(region_keywords[region.lower()])
            else:
                match_keywords.append(region)  # 直接添加原始关键词
        # 检查是否匹配
        return any(keyword in exam_region for keyword in match_keywords)
        
    def filter_by_type(self, exam: Dict, types: List[str]) -> bool:
        """按考试类型筛选"""
        if not types:
            return True
        exam_type = exam.get('exam_type', '')
        type_map = {
            'civil-service': '公务员考试',
            'public-institution': '事业单位考试',
            'enterprise': '企业招聘'
        }
        mapped_types = [type_map.get(t, t) for t in types]
        return exam_type in mapped_types
        
    def get_all_exams(self) -> List[Dict]:
        """获取所有考试信息"""
        all_exams = []
        
        # 从配置的数据源获取信息
        for source_type, sources in self.DATA_SOURCES.items():
            for source in sources:
                url = source['url']
                exam_type = source['type']
                source_name = source['name']
                
                print(f"正在获取: {source_name}...", file=sys.stderr)
                
                html_content = self.fetch_url(url)
                if html_content:
                    parser = self.parse_html(html_content)
                    text = ' '.join(parser.text_content)
                    exams = self.extract_exams_from_text(text, exam_type, source_name)
                    all_exams.extend(exams)
                    
                time.sleep(0.5)  # 避免请求过快
                
        return all_exams
        
    def filter_exams(self, exams: List[Dict], args) -> List[Dict]:
        """筛选考试信息"""
        filtered = exams
        
        if args.region:
            regions = args.region.split(',')
            filtered = [e for e in filtered if self.filter_by_region(e, regions)]
            
        if args.type:
            types = args.type.split(',')
            filtered = [e for e in filtered if self.filter_by_type(e, types)]
            
        if args.age:
            filtered = [e for e in filtered if self.filter_by_age(e, args.age)]
            
        if args.education:
            filtered = [e for e in filtered if self.filter_by_education(e, args.education)]
            
        return filtered
        
    def output_json(self, exams: List[Dict]) -> str:
        """输出JSON格式"""
        return json.dumps({'exams': exams, 'total': len(exams), 'timestamp': datetime.now().isoformat()}, 
                         ensure_ascii=False, indent=2)
                         
    def output_markdown(self, exams: List[Dict]) -> str:
        """输出Markdown格式"""
        lines = ['# 公考考试信息汇总\n']
        lines.append(f'**更新时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        lines.append(f'**考试数量**: {len(exams)}个\n')
        lines.append('\n---\n')
        
        for i, exam in enumerate(exams, 1):
            lines.append(f'## {i}. {exam.get("exam_name", "未知考试")}\n')
            
            lines.append('### 基本信息\n')
            lines.append(f'- **考试类型**: {exam.get("exam_type", "未知")}\n')
            lines.append(f'- **发布机构**: {exam.get("position", {}).get("organization", "未知")}\n')
            lines.append(f'- **发布时间**: {exam.get("publish_date", "未知")}\n')
            lines.append(f'- **报名截止**: {exam.get("deadline", "未知")}\n')
            lines.append(f'- **考试日期**: {exam.get("exam_date", "未知")}\n')
            lines.append('\n')
            
            lines.append('### 岗位要求\n')
            reqs = exam.get('requirements', {})
            lines.append(f'- **年龄要求**: {reqs.get("age", "未知")}\n')
            lines.append(f'- **学历要求**: {reqs.get("education", "未知")}\n')
            lines.append(f'- **专业要求**: {reqs.get("major", "未知")}\n')
            lines.append(f'- **工作经验**: {reqs.get("experience", "未知")}\n')
            lines.append(f'- **政治面貌**: {reqs.get("politics", "未知")}\n')
            lines.append('\n')
            
            lines.append('### 工作地点\n')
            pos = exam.get('position', {})
            lines.append(f'- **工作地点**: {pos.get("location", "未知")}\n')
            lines.append(f'- **单位性质**: {pos.get("organization", "未知")}\n')
            lines.append(f'- **岗位级别**: {pos.get("level", "未知")}\n')
            lines.append('\n')
            
            lines.append('### 报名信息\n')
            reg = exam.get('registration', {})
            lines.append(f'- **报名方式**: {reg.get("method", "未知")}\n')
            lines.append(f'- **报名网站**: {reg.get("website", "未知")}\n')
            lines.append(f'- **咨询电话**: {reg.get("phone", "未知")}\n')
            lines.append(f'- **报名费用**: {reg.get("fee", "未知")}\n')
            lines.append('\n')
            
            lines.append('### 考试内容\n')
            content = exam.get('exam_content', {})
            lines.append(f'- **笔试科目**: {content.get("written_test", "未知")}\n')
            lines.append(f'- **面试形式**: {content.get("interview", "未知")}\n')
            lines.append(f'- **成绩计算**: {content.get("score_calculation", "未知")}\n')
            lines.append('\n---\n\n')
            
        return ''.join(lines)
        
    def output_csv(self, exams: List[Dict]) -> str:
        """输出CSV格式"""
        output = []
        fieldnames = [
            'exam_name', 'exam_type', 'region', 'publish_date', 'deadline', 'exam_date',
            'age', 'education', 'major', 'experience', 'politics',
            'location', 'organization', 'level',
            'method', 'website', 'phone', 'fee',
            'written_test', 'interview', 'score_calculation'
        ]
        
        output.append(','.join(fieldnames))
        
        for exam in exams:
            reqs = exam.get('requirements', {})
            pos = exam.get('position', {})
            reg = exam.get('registration', {})
            content = exam.get('exam_content', {})
            
            row = [
                exam.get('exam_name', ''),
                exam.get('exam_type', ''),
                exam.get('region', ''),
                exam.get('publish_date', ''),
                exam.get('deadline', ''),
                exam.get('exam_date', ''),
                reqs.get('age', ''),
                reqs.get('education', ''),
                reqs.get('major', ''),
                reqs.get('experience', ''),
                reqs.get('politics', ''),
                pos.get('location', ''),
                pos.get('organization', ''),
                pos.get('level', ''),
                reg.get('method', ''),
                reg.get('website', ''),
                reg.get('phone', ''),
                reg.get('fee', ''),
                content.get('written_test', ''),
                content.get('interview', ''),
                content.get('score_calculation', '')
            ]
            output.append(','.join(f'"{field}"' for field in row))
            
        return '\n'.join(output)
        
    def output_text(self, exams: List[Dict]) -> str:
        """输出简洁文本格式"""
        lines = ['=' * 60]
        lines.append('公考考试信息汇总')
        lines.append(f'更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append(f'考试数量: {len(exams)}个')
        lines.append('=' * 60)
        
        for i, exam in enumerate(exams, 1):
            lines.append(f'\n{i}. {exam.get("exam_name", "未知考试")}')
            lines.append('-' * 40)
            
            reqs = exam.get('requirements', {})
            pos = exam.get('position', {})
            reg = exam.get('registration', {})
            
            lines.append(f'类型: {exam.get("exam_type", "未知")}')
            lines.append(f'地区: {exam.get("region", "未知")}')
            lines.append(f'发布时间: {exam.get("publish_date", "未知")}')
            lines.append(f'报名截止: {exam.get("deadline", "未知")}')
            lines.append(f'年龄要求: {reqs.get("age", "未知")}')
            lines.append(f'学历要求: {reqs.get("education", "未知")}')
            lines.append(f'工作地点: {pos.get("location", "未知")}')
            lines.append(f'报名网站: {reg.get("website", "未知")}')
            
        return '\n'.join(lines)


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='中国公考信息获取工具 - 重点关注四川成都及泸州地区',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s --all                              # 获取所有考试
  %(prog)s --region chengdu                   # 获取成都地区考试
  %(prog)s --region luzhou --type civil-service  # 泸州公务员考试
  %(prog)s --education bachelor --age "18-35" # 本科及以上，18-35岁
  %(prog)s --format markdown --save result.md # 输出Markdown并保存
        '''
    )
    
    parser.add_argument('--all', action='store_true', help='获取所有考试信息')
    parser.add_argument('--region', type=str, help='地区筛选 (chengdu/luzhou/mianyang等，可用逗号分隔多个)')
    parser.add_argument('--type', type=str, help='考试类型筛选 (civil-service/public-institution/enterprise)')
    parser.add_argument('--age', type=str, help='年龄要求筛选 (如 "18-35")')
    parser.add_argument('--education', type=str, 
                       choices=['college', 'bachelor', 'master', 'doctor'],
                       help='学历要求筛选 (college=大专, bachelor=本科, master=硕士, doctor=博士)')
    parser.add_argument('--format', type=str, default='text',
                       choices=['json', 'markdown', 'csv', 'text'],
                       help='输出格式 (默认: text)')
    parser.add_argument('--save', type=str, metavar='FILE',
                       help='保存结果到文件')
    parser.add_argument('--timeout', type=int, default=30,
                       help='请求超时时间(秒，默认30)')
    parser.add_argument('--demo', action='store_true',
                       help='使用演示数据(不访问网络)')
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 创建实例
    exam_info = ChinaExamInfo(timeout=args.timeout)
    
    # 获取考试信息
    if args.demo:
        # 使用演示数据
        exams = get_demo_exams()
    elif args.all:
        exams = exam_info.get_all_exams()
    else:
        # 默认获取所有
        exams = exam_info.get_all_exams()
    
    # 筛选
    exams = exam_info.filter_exams(exams, args)
    
    # 输出
    if args.format == 'json':
        output = exam_info.output_json(exams)
    elif args.format == 'markdown':
        output = exam_info.output_markdown(exams)
    elif args.format == 'csv':
        output = exam_info.output_csv(exams)
    else:
        output = exam_info.output_text(exams)
    
    # 保存或输出
    if args.save:
        try:
            with open(args.save, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f'结果已保存到: {args.save}', file=sys.stderr)
        except Exception as e:
            print(f'保存文件失败: {e}', file=sys.stderr)
            print(output)
    else:
        print(output)


def get_demo_exams():
    """获取演示数据"""
    return [
        {
            'exam_name': '2024年四川省公务员录用考试',
            'exam_type': '公务员考试',
            'region': '成都',
            'publish_date': '2024-03-15',
            'deadline': '2024-04-15',
            'exam_date': '2024-05-11',
            'requirements': {
                'age': '18-35岁',
                'education': '本科及以上',
                'major': '不限',
                'experience': '不限',
                'politics': '不限'
            },
            'position': {
                'location': '成都市',
                'organization': '四川省人力资源和社会保障厅',
                'level': '科员'
            },
            'registration': {
                'method': '网上报名',
                'website': 'http://rst.sc.gov.cn/',
                'phone': '028-86702886',
                'fee': '100元'
            },
            'exam_content': {
                'written_test': '行政职业能力测验、申论',
                'interview': '结构化面试',
                'score_calculation': '笔试60% + 面试40%'
            }
        },
        {
            'exam_name': '2024年泸州市事业单位公开招聘工作人员',
            'exam_type': '事业单位考试',
            'region': '泸州',
            'publish_date': '2024-03-20',
            'deadline': '2024-04-20',
            'exam_date': '2024-05-18',
            'requirements': {
                'age': '18-40岁',
                'education': '大专及以上',
                'major': '不限',
                'experience': '不限',
                'politics': '不限'
            },
            'position': {
                'location': '泸州市',
                'organization': '泸州市人力资源和社会保障局',
                'level': '职员'
            },
            'registration': {
                'method': '网上报名',
                'website': 'http://www.lzhrss.gov.cn/',
                'phone': '0830-3108071',
                'fee': '80元'
            },
            'exam_content': {
                'written_test': '职业能力倾向测验、公共基础知识',
                'interview': '结构化面试',
                'score_calculation': '笔试50% + 面试50%'
            }
        },
        {
            'exam_name': '2024年成都市双流区事业单位招聘',
            'exam_type': '事业单位考试',
            'region': '成都',
            'publish_date': '2024-04-01',
            'deadline': '2024-04-30',
            'exam_date': '2024-05-25',
            'requirements': {
                'age': '18-35岁',
                'education': '本科及以上',
                'major': '计算机类、财务类',
                'experience': '1年以上',
                'politics': '不限'
            },
            'position': {
                'location': '成都市双流区',
                'organization': '成都市双流区人力资源和社会保障局',
                'level': '科员'
            },
            'registration': {
                'method': '网上报名',
                'website': 'http://cdpta.cdhrss.chengdu.gov.cn/',
                'phone': '028-85839217',
                'fee': '100元'
            },
            'exam_content': {
                'written_test': '职业能力倾向测验',
                'interview': '结构化面试',
                'score_calculation': '笔试60% + 面试40%'
            }
        },
        {
            'exam_name': '2024年四川省属事业单位招聘',
            'exam_type': '事业单位考试',
            'region': '成都',
            'publish_date': '2024-03-25',
            'deadline': '2024-04-25',
            'exam_date': '2024-05-20',
            'requirements': {
                'age': '18-45岁',
                'education': '硕士及以上',
                'major': '工程技术类',
                'experience': '不限',
                'politics': '不限'
            },
            'position': {
                'location': '成都市',
                'organization': '四川省人力资源和社会保障厅',
                'level': '副主任科员'
            },
            'registration': {
                'method': '网上报名',
                'website': 'http://www.scpta.org.cn/',
                'phone': '028-86702886',
                'fee': '120元'
            },
            'exam_content': {
                'written_test': '综合知识、专业知识',
                'interview': '结构化面试',
                'score_calculation': '笔试50% + 面试50%'
            }
        },
        {
            'exam_name': '2024年泸州古蔺县事业单位招聘',
            'exam_type': '事业单位考试',
            'region': '泸州',
            'publish_date': '2024-04-05',
            'deadline': '2024-05-05',
            'exam_date': '2024-06-01',
            'requirements': {
                'age': '18-35岁',
                'education': '大专及以上',
                'major': '不限',
                'experience': '不限',
                'politics': '不限'
            },
            'position': {
                'location': '泸州市古蔺县',
                'organization': '古蔺县人力资源和社会保障局',
                'level': '职员'
            },
            'registration': {
                'method': '网上报名',
                'website': 'http://www.lzhrss.gov.cn/',
                'phone': '0830-7202506',
                'fee': '50元'
            },
            'exam_content': {
                'written_test': '职业能力倾向测验',
                'interview': '结构化面试',
                'score_calculation': '笔试60% + 面试40%'
            }
        }
    ]


if __name__ == '__main__':
    main()
