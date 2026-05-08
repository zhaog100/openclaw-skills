// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 多通道通知（默认disabled，不主动发通知）

const crypto = require('crypto');
const https = require('https');

/**
 * 读取通知配置
 */
function loadConfig() {
  try {
    const path = require('path');
    const fs = require('fs');
    const configPath = path.resolve(__dirname, '..', '..', 'config.json');
    if (!fs.existsSync(configPath)) return { enabled: false };
    const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    return config.notifications || { enabled: false };
  } catch {
    return { enabled: false };
  }
}

/**
 * 发送通知（根据配置的事件规则路由到对应通道）
 */
async function sendNotification(event, message) {
  const config = loadConfig();
  if (!config.enabled || !config.rules || !config.channels) return;

  const rule = config.rules.find(r => r.event === event);
  if (!rule || !rule.channels || rule.channels.length === 0) return;

  for (const channel of rule.channels) {
    try {
      await sendToChannel(channel, config.channels[channel] || {}, message);
    } catch (err) {
      console.error(`[notifier] ${channel} 通知发送失败:`, err.message);
    }
  }
}

/**
 * 路由到具体通道
 */
async function sendToChannel(channel, channelConfig, message) {
  switch (channel) {
    case 'feishu': return sendFeishu(channelConfig, message);
    case 'wecom': return sendWecom(channelConfig, message);
    case 'dingtalk': return sendDingtalk(channelConfig, message);
    case 'slack': return sendSlack(channelConfig, message);
    case 'email': return sendEmail(channelConfig, message);
    default: console.warn(`[notifier] 未知通道: ${channel}`);
  }
}

/**
 * 飞书Webhook
 */
async function sendFeishu(cfg, message) {
  if (!cfg.webhook) return;
  const body = JSON.stringify({
    msg_type: 'interactive',
    card: {
      header: { title: { tag: 'plain_text', content: 'ProjectMind 通知' } },
      elements: [{ tag: 'div', text: { tag: 'plain_text', content: message } }],
    },
  });
  await httpPost(cfg.webhook, body, cfg.secret);
}

/**
 * 企业微信Webhook
 */
async function sendWecom(cfg, message) {
  if (!cfg.webhook) return;
  const body = JSON.stringify({ msgtype: 'markdown', markdown: { content: message } });
  await httpPost(cfg.webhook, body);
}

/**
 * 钉钉Webhook
 */
async function sendDingtalk(cfg, message) {
  if (!cfg.webhook) return;
  let url = cfg.webhook;
  if (cfg.secret) {
    const ts = Date.now();
    const sign = crypto.createHmac('sha256', `\n${ts}`).update(cfg.secret).digest('base64');
    url += `&timestamp=${ts}&sign=${encodeURIComponent(sign)}`;
  }
  const body = JSON.stringify({ msgtype: 'markdown', markdown: { title: 'ProjectMind', text: message } });
  await httpPost(url, body);
}

/**
 * Slack Webhook
 */
async function sendSlack(cfg, message) {
  if (!cfg.webhook) return;
  const body = JSON.stringify({ text: message });
  await httpPost(cfg.webhook, body);
}

/**
 * 邮件SMTP（需要nodemailer，可选依赖）
 */
async function sendEmail(cfg, message) {
  if (!cfg.smtp_host || !cfg.to) return;
  try {
    const nodemailer = require('nodemailer');
    const transporter = nodemailer.createTransport({
      host: cfg.smtp_host,
      port: cfg.smtp_port || 465,
      secure: true,
      auth: { user: cfg.user, pass: cfg.pass },
    });
    await transporter.sendMail({
      from: cfg.user,
      to: cfg.to,
      subject: 'ProjectMind 通知',
      text: message,
    });
  } catch {
    console.warn('[notifier] nodemailer未安装，跳过邮件通知');
  }
}

/**
 * 通用HTTPS POST
 */
function httpPost(url, body) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      timeout: 5000,
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body);
    req.end();
  });
}

module.exports = { sendNotification };
