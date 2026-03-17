# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""meeting-minutes-generator v1.0 综合测试"""

import datetime
import json
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.minutes_parser import parse_text
from src.action_extractor import extract_actions, _extract_deadline, _infer_priority
from src.summary_generator import generate_summary, _extract_decisions
from src.formatter import format_markdown, format_plain, format_json
from src.pipeline import generate_minutes

# ============================================================
# 样例文本
# ============================================================
SAMPLE_FULL = """议题：Q1产品规划讨论
时间：2026-03-17 14:00
地点：一号会议室
参与者：张三、李四、王五、@赵六

今天我们讨论了Q1产品规划的方向。

第一个议题是用户增长策略。张三分享了上季度的数据，月活增长了15%。李四建议加大社交媒体投放。

决定：采用A/B测试方案验证投放效果。

第二个议题是技术架构升级。@赵六负责调研微服务架构。需要在本周五前完成调研报告。

第三个议题是设计改版。王五负责整理设计规范，下周一前提交。

本次会议讨论了三个重要议题，确认了增长策略和技术升级方向。
"""

SAMPLE_SIMPLE = """会议纪要草稿

大家讨论了下个版本的排期。
张三负责前端开发，李四负责后端。
下周三前完成需求文档。
"""

SAMPLE_EMPTY = ""
SAMPLE_NO_ACTIONS = """今天大家聊了聊最近的天气和午餐。"""


# ============================================================
# minutes_parser 测试
# ============================================================
class TestMinutesParser(unittest.TestCase):

    def test_parse_returns_dict_with_all_keys(self):
        result = parse_text(SAMPLE_FULL)
        self.assertIsInstance(result, dict)
        for key in ('topic', 'participants', 'time', 'location', 'paragraphs', 'discussion_points'):
            self.assertIn(key, result)

    def test_extract_topic_from_label(self):
        result = parse_text(SAMPLE_FULL)
        self.assertEqual(result['topic'], 'Q1产品规划讨论')

    def test_extract_topic_fallback_first_line(self):
        result = parse_text("随便聊聊版本排期\n大家讨论了一下")
        self.assertEqual(result['topic'], '随便聊聊版本排期')

    def test_extract_topic_议题_label(self):
        result = parse_text("议题：新功能上线计划")
        self.assertEqual(result['topic'], '新功能上线计划')

    def test_extract_topic_bracket_label(self):
        result = parse_text("【议题】系统性能优化")
        self.assertEqual(result['topic'], '系统性能优化')

    def test_extract_participants_from_colon(self):
        result = parse_text(SAMPLE_FULL)
        self.assertIn('张三', result['participants'])
        self.assertIn('李四', result['participants'])
        self.assertIn('王五', result['participants'])

    def test_extract_participants_at_mention(self):
        result = parse_text(SAMPLE_FULL)
        self.assertIn('赵六', result['participants'])

    def test_extract_time_full_datetime(self):
        result = parse_text(SAMPLE_FULL)
        self.assertIn('2026-03-17', result['time'])

    def test_extract_time_label(self):
        result = parse_text("会议时间：3月20日 10:00")
        self.assertIn('3月20日', result['time'])

    def test_extract_location(self):
        result = parse_text(SAMPLE_FULL)
        self.assertEqual(result['location'], '一号会议室')

    def test_extract_location_from_sentence(self):
        result = parse_text("我们在三楼大会议室开会。")
        self.assertEqual(result['location'], '三楼大会议室')

    def test_paragraphs_split(self):
        result = parse_text(SAMPLE_FULL)
        self.assertIsInstance(result['paragraphs'], list)
        self.assertTrue(len(result['paragraphs']) > 1)

    def test_discussion_points_extracted(self):
        result = parse_text(SAMPLE_FULL)
        self.assertIsInstance(result['discussion_points'], list)
        self.assertTrue(len(result['discussion_points']) > 0)

    def test_empty_text(self):
        result = parse_text(SAMPLE_EMPTY)
        self.assertEqual(result['topic'], '未定议题')
        self.assertEqual(result['participants'], [])

    def test_no_location(self):
        result = parse_text("议题：测试\n时间：今天")
        self.assertEqual(result['location'], '')


# ============================================================
# action_extractor 测试
# ============================================================
class TestActionExtractor(unittest.TestCase):

    def test_basic_action(self):
        actions = extract_actions("@张三负责完成需求文档")
        self.assertTrue(len(actions) >= 1)
        self.assertEqual(actions[0]['assignee'], '张三')
        self.assertIn('需求文档', actions[0]['task'])

    def test_at_mention_assignee(self):
        actions = extract_actions("@李四 跟进用户反馈问题")
        self.assertEqual(actions[0]['assignee'], '李四')

    def test_由_assignee(self):
        actions = extract_actions("由王五协调各部门资源")
        self.assertEqual(actions[0]['assignee'], '王五')

    def test_交给_assignee(self):
        actions = extract_actions("交给赵六审核代码")
        self.assertEqual(actions[0]['assignee'], '赵六')

    def test_no_assignee(self):
        actions = extract_actions("需要尽快完成系统部署")
        self.assertEqual(actions[0]['assignee'], '')

    def test_absolute_date_deadline(self):
        actions = extract_actions("3月20日前提交报告", reference_date=datetime.date(2026, 3, 17))
        self.assertEqual(actions[0]['deadline'], '2026-03-20')

    def test_full_date_deadline(self):
        actions = extract_actions("2026-04-01前完成", reference_date=datetime.date(2026, 3, 17))
        self.assertEqual(actions[0]['deadline'], '2026-04-01')

    def test_tomorrow_deadline(self):
        actions = extract_actions("明天前搞定", reference_date=datetime.date(2026, 3, 17))
        self.assertEqual(actions[0]['deadline'], '2026-03-18')

    def test_day_after_tomorrow(self):
        actions = extract_actions("后天完成", reference_date=datetime.date(2026, 3, 17))
        self.assertEqual(actions[0]['deadline'], '2026-03-19')

    def test_next_week_deadline(self):
        # 2026-03-17 is Tuesday; 下周一 = 2026-03-23
        actions = extract_actions("下周一前提交", reference_date=datetime.date(2026, 3, 17))
        self.assertEqual(actions[0]['deadline'], '2026-03-23')

    def test_next_friday_deadline(self):
        # 2026-03-17 is Tuesday; 下周五 = 2026-03-27
        actions = extract_actions("下周五前完成", reference_date=datetime.date(2026, 3, 17))
        self.assertEqual(actions[0]['deadline'], '2026-03-27')

    def test_days_later(self):
        actions = extract_actions("3天后搞定", reference_date=datetime.date(2026, 3, 17))
        self.assertEqual(actions[0]['deadline'], '2026-03-20')

    def test_no_deadline(self):
        actions = extract_actions("张三负责日常维护")
        self.assertEqual(actions[0]['deadline'], '')

    def test_high_priority(self):
        self.assertEqual(_infer_priority('紧急完成部署'), '高')
        self.assertEqual(_infer_priority('尽快搞定'), '高')
        self.assertEqual(_infer_priority('务必今天完成'), '高')

    def test_low_priority(self):
        self.assertEqual(_infer_priority('有空再看吧'), '低')
        self.assertEqual(_infer_priority('不急，后续再说'), '低')

    def test_medium_priority(self):
        self.assertEqual(_infer_priority('完成日常维护'), '中')

    def test_non_action_ignored(self):
        actions = extract_actions("今天天气不错啊")
        self.assertEqual(len(actions), 0)

    def test_multiple_actions(self):
        actions = extract_actions("@张三负责前端开发。@李四跟进后端接口。王五整理文档。")
        self.assertEqual(len(actions), 3)

    def test_sample_full_has_actions(self):
        actions = extract_actions(SAMPLE_FULL)
        self.assertTrue(len(actions) >= 2)

    def test_priority_in_extracted_actions(self):
        actions = extract_actions("@张三 紧急修复线上bug")
        self.assertEqual(actions[0]['priority'], '高')


# ============================================================
# summary_generator 测试
# ============================================================
class TestSummaryGenerator(unittest.TestCase):

    def setUp(self):
        self.parsed = parse_text(SAMPLE_FULL)
        self.actions = extract_actions(SAMPLE_FULL)
        self.summary = generate_summary(self.parsed, self.actions)

    def test_summary_has_all_sections(self):
        for key in ('meeting_info', 'summary', 'discussion_points', 'decisions', 'action_items'):
            self.assertIn(key, self.summary)

    def test_meeting_info_topic(self):
        self.assertEqual(self.summary['meeting_info']['topic'], 'Q1产品规划讨论')

    def test_meeting_info_participants(self):
        self.assertIn('张三', self.summary['meeting_info']['participants'])

    def test_overview_mentions_topic(self):
        self.assertIn('Q1产品规划讨论', self.summary['summary'])

    def test_decisions_extracted(self):
        self.assertTrue(len(self.summary['decisions']) > 0)

    def test_decisions_content(self):
        self.assertTrue(any('A/B测试' in d for d in self.summary['decisions']))

    def test_action_items_passed_through(self):
        self.assertEqual(len(self.summary['action_items']), len(self.actions))

    def test_empty_input(self):
        parsed = {'topic': '', 'time': '', 'location': '', 'participants': [], 'paragraphs': [], 'discussion_points': []}
        summary = generate_summary(parsed, [])
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary['decisions'], [])


# ============================================================
# formatter 测试
# ============================================================
class TestFormatter(unittest.TestCase):

    def setUp(self):
        self.minutes = generate_summary(parse_text(SAMPLE_FULL), extract_actions(SAMPLE_FULL))

    def test_markdown_contains_headers(self):
        md = format_markdown(self.minutes)
        self.assertIn('# 会议纪要', md)
        self.assertIn('## 基本信息', md)

    def test_markdown_contains_topic(self):
        md = format_markdown(self.minutes)
        self.assertIn('Q1产品规划讨论', md)

    def test_plain_no_markdown_syntax(self):
        plain = format_plain(self.minutes)
        self.assertNotIn('#', plain.strip().split('\n')[0])
        self.assertNotIn('**', plain)

    def test_json_valid(self):
        j = format_json(self.minutes)
        data = json.loads(j)
        self.assertIsInstance(data, dict)
        self.assertIn('meeting_info', data)

    def test_json_no_ascii_escape(self):
        j = format_json(self.minutes)
        self.assertIn('Q1产品规划讨论', j)

    def test_empty_minutes_formats(self):
        empty = {'meeting_info': {}, 'summary': '', 'discussion_points': [], 'decisions': [], 'action_items': []}
        self.assertIsInstance(format_markdown(empty), str)
        self.assertIsInstance(format_plain(empty), str)
        self.assertIsInstance(format_json(empty), str)


# ============================================================
# pipeline 集成测试
# ============================================================
class TestPipeline(unittest.TestCase):

    def test_generate_minutes_markdown(self):
        result = generate_minutes(SAMPLE_FULL, 'markdown')
        self.assertIn('# 会议纪要', result)
        self.assertIn('Q1产品规划讨论', result)

    def test_generate_minutes_plain(self):
        result = generate_minutes(SAMPLE_FULL, 'plain')
        self.assertIn('会议纪要', result)
        self.assertNotIn('##', result)

    def test_generate_minutes_json(self):
        result = generate_minutes(SAMPLE_FULL, 'json')
        data = json.loads(result)
        self.assertIn('meeting_info', data)

    def test_default_format_is_markdown(self):
        result = generate_minutes(SAMPLE_FULL)
        self.assertIn('# 会议纪要', result)

    def test_simple_text(self):
        result = generate_minutes(SAMPLE_SIMPLE)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 50)

    def test_empty_text(self):
        result = generate_minutes(SAMPLE_EMPTY)
        self.assertIsInstance(result, str)

    def test_no_actions_text(self):
        result = generate_minutes(SAMPLE_NO_ACTIONS)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
