#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东智能任务推荐脚本
功能：
- 扫描可用脚本
- 评估收益潜力
- 自动推荐新任务
- 一键添加
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

class JDSmartTaskRecommender:
    def __init__(self):
        self.db_path = "/ql/data/db/jd_monitor.db"
        self.scripts_dir = "/ql/scripts/jd_faker2"
        self.qinglong_api = "http://localhost:5700/api"
        self.config_path = "/ql/data/config/jd_recommender.json"
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        default_config = {
            "min_potential_beans": 3,  # 最低推荐收益
            "auto_add_enabled": False,  # 自动添加（默认关闭）
            "blacklist": [  # 黑名单（不推荐的任务）
                "jd_test", "jd_debug", "jd_example"
            ]
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def scan_available_scripts(self):
        """扫描可用脚本"""
        scripts = []
        
        for script_file in Path(self.scripts_dir).glob('jd_*.js'):
            script_name = script_file.stem
            
            # 检查黑名单
            if any(black in script_name.lower() for black in self.config['blacklist']):
                continue
            
            # 读取脚本内容分析
            script_info = self.analyze_script(script_file)
            scripts.append(script_info)
        
        return scripts
    
    def analyze_script(self, script_path):
        """分析脚本"""
        script_name = script_path.stem
        
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000)  # 只读取前5000字符
            
            # 提取脚本信息
            info = {
                'name': script_name,
                'path': str(script_path),
                'description': self.extract_description(content),
                'cron': self.extract_cron(content),
                'estimated_beans': self.estimate_beans(content, script_name),
                'difficulty': self.estimate_difficulty(content),
                'dependencies': self.check_dependencies(content),
                'is_running': self.check_if_running(script_name)
            }
            
            return info
        except Exception as e:
            return {
                'name': script_name,
                'path': str(script_path),
                'error': str(e),
                'estimated_beans': 0
            }
    
    def extract_description(self, content):
        """提取脚本描述"""
        # 查找注释中的描述
        lines = content.split('\n')
        for line in lines[:10]:  # 只检查前10行
            if '活动名称' in line or '脚本说明' in line:
                return line.split('：')[-1].strip()
            elif line.startswith('/**') or line.startswith('*'):
                desc = line.replace('*', '').strip()
                if len(desc) > 5:
                    return desc
        return "未知"
    
    def extract_cron(self, content):
        """提取定时规则"""
        import re
        cron_match = re.search(r'cron[:\s]+([0-9*,\s]+)', content)
        if cron_match:
            return cron_match.group(1).strip()
        return None
    
    def estimate_beans(self, content, script_name):
        """估算收益潜力"""
        score = 0
        
        # 关键词评分
        keywords = {
            'bean': 5,
            'sign': 3,
            'farm': 4,
            'fruit': 4,
            'joy': 3,
            'bonus': 4,
            'carnival': 3,
            'plant': 4,
            'daily': 2,
            'home': 3,
            'money': 4,
            'cash': 5
        }
        
        for keyword, value in keywords.items():
            if keyword in script_name.lower():
                score += value
        
        # 检查脚本内容关键词
        if '京豆' in content or 'bean' in content.lower():
            score += 3
        if '奖励' in content:
            score += 2
        if '签到' in content:
            score += 2
        
        return min(score, 15)  # 最大15分
    
    def estimate_difficulty(self, content):
        """估算难度"""
        difficulty = "easy"
        
        # 检查复杂度指标
        if 'encrypt' in content.lower() or 'h5st' in content.lower():
            difficulty = "hard"
        elif 'token' in content.lower() or 'api' in content.lower():
            difficulty = "medium"
        
        return difficulty
    
    def check_dependencies(self, content):
        """检查依赖"""
        dependencies = []
        
        if 'sendNotify' in content:
            dependencies.append('sendNotify')
        if 'USER_AGENTS' in content:
            dependencies.append('USER_AGENTS')
        if 'h5st' in content.lower():
            dependencies.append('h5st')
        
        return dependencies
    
    def check_if_running(self, script_name):
        """检查脚本是否已在运行"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM task_execution
                WHERE task_name LIKE ?
                AND execution_time >= datetime('now', '-7 day')
            ''', (f'%{script_name}%',))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except:
            conn.close()
            return False
    
    def recommend_tasks(self):
        """推荐任务"""
        print("🔍 扫描可用脚本...")
        scripts = self.scan_available_scripts()
        
        print("📊 评估任务收益潜力...")
        # 过滤未运行且高收益的任务
        recommended = [
            s for s in scripts
            if not s['is_running']
            and s['estimated_beans'] >= self.config['min_potential_beans']
            and 'error' not in s
        ]
        
        # 按收益潜力排序
        recommended.sort(key=lambda x: x['estimated_beans'], reverse=True)
        
        return recommended[:10]  # 返回前10个
    
    def add_task_to_qinglong(self, task_info, token):
        """添加任务到青龙面板"""
        try:
            # 构建任务数据
            task_data = {
                'name': f"京东{task_info['description']}",
                'command': f"/ql/scripts/jd_wrapper.sh node {task_info['path']}",
                'schedule': task_info['cron'] or '0 8 * * *'
            }
            
            # 调用青龙API添加任务
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.qinglong_api}/crons",
                headers=headers,
                json=task_data
            )
            
            if response.status_code == 200:
                return True, f"✅ 任务添加成功: {task_info['name']}"
            else:
                return False, f"❌ 添加失败: {response.text}"
        except Exception as e:
            return False, f"❌ 添加出错: {str(e)}"
    
    def generate_recommendation_report(self, auto_add=False):
        """生成推荐报告"""
        print("🔍 开始智能推荐...")
        recommended = self.recommend_tasks()
        
        if not recommended:
            print("✅ 当前已运行所有高收益任务，无需新增")
            return
        
        # 生成报告
        report = f"""
🎯 京东智能任务推荐报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 💎 推荐新增任务（TOP 10）

| 序号 | 任务名称 | 描述 | 预估收益 | 难度 | 依赖 |
|------|---------|------|---------|------|------|
"""
        
        for i, task in enumerate(recommended, 1):
            deps = ', '.join(task['dependencies']) if task['dependencies'] else '无'
            report += f"| {i} | {task['name']} | {task['description']} | {task['estimated_beans']} 京豆/天 | {task['difficulty']} | {deps} |\n"
        
        report += "\n## 📝 详细信息\n\n"
        
        for i, task in enumerate(recommended, 1):
            report += f"### {i}. {task['name']}\n"
            report += f"- **描述**: {task['description']}\n"
            report += f"- **预估收益**: {task['estimated_beans']} 京豆/天\n"
            report += f"- **难度**: {task['difficulty']}\n"
            report += f"- **定时**: {task['cron'] or '建议每天8:00'}\n"
            if task['dependencies']:
                report += f"- **依赖**: {', '.join(task['dependencies'])}\n"
            report += f"- **路径**: {task['path']}\n\n"
        
        report += "\n## 🚀 快速添加命令\n\n"
        report += "```bash\n"
        for task in recommended[:5]:
            report += f"# {task['description']}\n"
            report += f"curl -X POST 'http://localhost:5700/api/crons' \\\n"
            report += f"  -H 'Authorization: Bearer YOUR_TOKEN' \\\n"
            report += f"  -H 'Content-Type: application/json' \\\n"
            report += f"  -d '{{\n"
            report += f"    \"name\": \"京东{task['description']}\",\n"
            report += f"    \"command\": \"/ql/scripts/jd_wrapper.sh node {task['path']}\",\n"
            report += f"    \"schedule\": \"{task['cron'] or '0 8 * * *'}\"\n"
            report += f"  }}'\n\n"
        report += "```\n"
        
        # 保存报告
        report_path = f"/ql/data/log/jd_recommender_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n📄 报告已保存: {report_path}")
        
        # 自动添加（如果启用）
        if auto_add and self.config['auto_add_enabled']:
            print("\n🤖 自动添加任务中...")
            for task in recommended[:3]:  # 只自动添加前3个
                success, message = self.add_task_to_qinglong(task, "YOUR_TOKEN")
                print(message)
        
        return recommended

if __name__ == "__main__":
    recommender = JDSmartTaskRecommender()
    recommender.generate_recommendation_report()
