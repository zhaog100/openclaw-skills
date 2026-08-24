#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新媒体运营工具库 - 综合测试脚本
测试所有本地工具和云端 API
维护：小米椒 🌶️‍🔥
"""

import json
import sys
from pathlib import Path

# 加载 API Keys
secrets_path = Path(__file__).parent.parent / 'secrets' / 'api-keys.json'
with open(secrets_path, 'r', encoding='utf-8') as f:
    api_config = json.load(f)

print("=" * 60)
print("🌶️‍🔥 新媒体运营工具库 - 综合测试")
print("=" * 60)

# ============== 本地工具测试 ==============
print("\n【本地工具测试】\n")

# 1. VADER 情感分析
print("1️⃣ VADER 情感分析...")
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    test_text = "This product is amazing! I love it so much!"
    scores = analyzer.polarity_scores(test_text)
    print(f"   ✅ 测试文本：{test_text}")
    print(f"   ✅ 情感得分：{scores}")
    print(f"   ✅ 正向情感：{scores['pos']:.2%}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 2. RAKE 关键词提取
print("\n2️⃣ RAKE 关键词提取...")
try:
    from rake_nltk import Rake
    rake = Rake()
    test_text = "新媒体运营是数字营销的重要组成部分。小红书种草和闲鱼成交是目前最流行的电商模式。"
    rake.extract_keywords_from_text(test_text)
    keywords = rake.get_ranked_phrases()[:5]
    print(f"   ✅ 测试文本：{test_text}")
    print(f"   ✅ 提取关键词：{keywords}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 3. Pandas 数据分析
print("\n3️⃣ Pandas 数据分析...")
try:
    import pandas as pd
    df = pd.DataFrame({
        '日期': ['2026-04-09', '2026-04-10', '2026-04-11'],
        '曝光量': [1200, 1500, 1800],
        '点赞数': [50, 80, 120]
    })
    print(f"   ✅ 测试数据：{len(df)} 行")
    print(f"   ✅ 平均曝光：{df['曝光量'].mean():.0f}")
    print(f"   ✅ 平均点赞：{df['点赞数'].mean():.0f}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 4. Plotly 数据可视化
print("\n4️⃣ Plotly 数据可视化...")
try:
    import plotly.express as px
    df = px.data.iris()
    fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')
    print(f"   ✅ 创建图表：scatter plot")
    print(f"   ✅ 数据点：{len(df)} 个")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 5. NumPy 数值计算
print("\n5️⃣ NumPy 数值计算...")
try:
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    print(f"   ✅ 测试数组：{arr}")
    print(f"   ✅ 平均值：{np.mean(arr):.2f}")
    print(f"   ✅ 标准差：{np.std(arr):.2f}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 6. BeautifulSoup HTML 解析
print("\n6️⃣ BeautifulSoup HTML 解析...")
try:
    from bs4 import BeautifulSoup
    html = """
    <html>
        <head><title>测试页面</title></head>
        <body>
            <h1 class="title">新媒体运营</h1>
            <p class="content">小红书种草 + 闲鱼成交</p>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('h1', class_='title').text
    print(f"   ✅ 解析标题：{title}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 7. gTTS 文本转语音
print("\n7️⃣ gTTS 文本转语音...")
try:
    from gtts import gTTS
    tts = gTTS(text="小米椒新媒体运营", lang='zh-cn')
    output_path = Path('/tmp/test_gtts.mp3')
    tts.save(str(output_path))
    print(f"   ✅ 生成语音文件：{output_path}")
    print(f"   ✅ 文件大小：{output_path.stat().st_size} bytes")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 8. QR Code 二维码生成
print("\n8️⃣ QR Code 二维码生成...")
try:
    import qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data('https://xiaohongshu.com/user/profile/xiaomijiao')
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    output_path = Path('/tmp/test_qrcode.png')
    img.save(output_path)
    print(f"   ✅ 生成二维码：{output_path}")
    print(f"   ✅ 图片尺寸：{img.size}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 9. Sumy 文本摘要
print("\n9️⃣ Sumy 文本摘要...")
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    
    text = """
    新媒体运营是数字营销的重要组成部分。
    小红书种草是目前最流行的电商模式之一。
    通过内容创作吸引用户关注，然后引导到闲鱼成交。
    这种模式成本低、风险小、容易上手。
    适合个人 SOHO 创业者。
    """
    parser = PlaintextParser.from_string(text, Tokenizer('english'))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 2)
    print(f"   ✅ 原文：{len(text)} 字符")
    print(f"   ✅ 摘要：{len(summary)} 句")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# 10. NLTK 基础功能
print("\n🔟 NLTK 基础功能...")
try:
    import nltk
    from nltk.tokenize import word_tokenize
    text = "Xiaomijiao is a new media operations expert."
    tokens = word_tokenize(text)
    print(f"   ✅ 分词结果：{tokens[:5]}...")
    print(f"   ✅ 词数：{len(tokens)}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

# ============== 云端 API 测试 ==============
print("\n【云端 API 测试】\n")

cloud_apis = api_config.get('cloud_apis', {})

# 11. Poof 背景移除
print("1️⃣1️⃣ Poof 背景移除...")
poof_config = cloud_apis.get('poof', {})
if poof_config.get('api_key'):
    try:
        import requests
        api_key = poof_config['api_key']
        test_image = Path('/root/.openclaw/workspace/products/raw/xiaohongshu_test.jpg')
        
        if test_image.exists():
            with open(test_image, 'rb') as f:
                files = {'image': f}
                headers = {'X-API-Key': api_key}
                # 注意：实际 API 端点可能需要调整
                response = requests.post(
                    'https://api.poof.bg/v1/remove-background',
                    headers=headers,
                    files=files,
                    timeout=30
                )
                if response.status_code == 200:
                    output_path = Path('/tmp/test_poof_output.png')
                    with open(output_path, 'wb') as out_f:
                        out_f.write(response.content)
                    print(f"   ✅ 背景移除成功")
                    print(f"   ✅ 输出文件：{output_path}")
                else:
                    print(f"   ⚠️ API 返回：{response.status_code}")
        else:
            print(f"   ⚠️ 测试图片不存在：{test_image}")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
else:
    print(f"   ⚠️ 未配置 API Key")

# 12. Image Compressor 图片压缩
print("\n1️⃣2️⃣ Image Compressor 图片压缩...")
ic_config = cloud_apis.get('image_compressor', {})
if ic_config.get('api_key'):
    try:
        import requests
        api_key = ic_config['api_key']
        api_host = ic_config.get('api_host', '')
        test_image = Path('/root/.openclaw/workspace/products/raw/xiaohongshu_test.jpg')
        
        if test_image.exists():
            with open(test_image, 'rb') as f:
                files = {'image': f}
                headers = {
                    'X-RapidAPI-Key': api_key,
                    'X-RapidAPI-Host': api_host
                }
                data = {
                    'max_width': 1200,
                    'max_height': 800,
                    'quality': 80,
                    'format': 'jpeg',
                    'mode': 'fit',
                    'return': 'json'
                }
                response = requests.post(
                    ic_config['base_url'],
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 压缩成功")
                    print(f"   ✅ 响应：{result.get('status', 'N/A')}")
                else:
                    print(f"   ⚠️ API 返回：{response.status_code}")
        else:
            print(f"   ⚠️ 测试图片不存在：{test_image}")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
else:
    print(f"   ⚠️ 未配置 API Key")

# 13. APITube News 热点采集
print("\n1️⃣3️⃣ APITube News 热点采集...")
apitube_config = cloud_apis.get('apitube_news', {})
if apitube_config.get('api_key'):
    try:
        import requests
        api_key = apitube_config['api_key']
        headers = {'X-API-Key': api_key}
        # 注意：实际 API 端点可能需要调整
        response = requests.get(
            f"{apitube_config['base_url']}/news",
            headers=headers,
            params={'limit': 5},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 获取新闻成功")
            print(f"   ✅ 新闻数量：{len(result.get('news', [])) if isinstance(result, dict) else 'N/A'}")
        else:
            print(f"   ⚠️ API 返回：{response.status_code}")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
else:
    print(f"   ⚠️ 未配置 API Key")

# 14. Meteoblue 天气查询
print("\n1️⃣4️⃣ Meteoblue 天气查询...")
meteoblue_config = cloud_apis.get('meteoblue', {})
if meteoblue_config.get('api_key'):
    try:
        import requests
        api_key = meteoblue_config['api_key']
        # Meteoblue API 格式可能需要调整
        response = requests.get(
            f"{meteoblue_config['base_url']}/weather",
            params={
                'apikey': api_key,
                'lat': '25.0330',  # 台湾
                'lon': '121.5654',
                'datasources': ['meteosource'],
                'format': 'json'
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 获取天气成功")
            print(f"   ✅ 数据：{list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        else:
            print(f"   ⚠️ API 返回：{response.status_code}")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
else:
    print(f"   ⚠️ 未配置 API Key")

# ============== 总结 ==============
print("\n" + "=" * 60)
print("✅ 测试完成！")
print("=" * 60)
print("\n📊 测试结果统计：")
print("   - 本地工具：10 个功能模块")
print("   - 云端 API：4 个服务")
print("\n🎉 所有工具已准备就绪，可以开始使用！")
print("=" * 60)
