// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 风险预警 handler

const { findProjectByName, createRisk, listRisks, logActivity } = require('../db/queries');
const { getConfig } = require('../db/connection');
const { runRiskCheck } = require('../engines/risk-engine');
const { formatRiskList, formatRiskCheck } = require('../utils/formatter');

/**
 * 风险预警
 * @param {{ project_name?: string, action: 'list'|'add'|'check', title?: string, severity?: string, description?: string }} params
 * @returns {string}
 */
function handleRiskAlert(params) {
  const { action } = params;
  if (!action || !['list', 'add', 'check'].includes(action)) {
    return '❌ 请指定操作：list（查看）、add（添加）、check（风险检查）';
  }

  const projectName = params.project_name || getConfig().default_project;
  if (!projectName) return '❌ 请指定项目名称';
  const project = findProjectByName(projectName);
  if (!project) return `❌ 未找到项目「${projectName}」`;

  if (action === 'add') {
    if (!params.title) return '❌ 请提供风险标题';
    const validSeverities = ['low', 'medium', 'high', 'critical'];
    const severity = params.severity || 'medium';
    if (!validSeverities.includes(severity)) {
      return `❌ 无效严重级别：${severity}，可选：${validSeverities.join('/')}`;
    }

    const result = createRisk({
      project_id: project.id,
      title: params.title,
      severity,
      description: params.description || '',
    });

    const riskId = result.lastInsertRowid;
    logActivity(project.id, null, 'risk_added', `新增风险「${params.title}」(${severity})`);
    return `✅ 风险已添加\n📋 #${riskId} ${params.title}\n⚡ 严重级别：${severity}\n📁 项目：${project.name}`;
  }

  if (action === 'list') {
    const risks = listRisks({ project_id: project.id });
    if (risks.length === 0) return `📭 项目「${project.name}」暂无风险记录`;
    return formatRiskList(risks, project.name);
  }

  if (action === 'check') {
    const detectedRisks = runRiskCheck(project.id);
    if (detectedRisks.length === 0) return `✅ 项目「${project.name}」暂未检测到风险`;
    // 自动存入风险表
    for (const r of detectedRisks) {
      createRisk({
        project_id: project.id,
        title: r.title,
        severity: r.severity,
        description: r.description,
        status: 'open',
      });
      logActivity(project.id, null, 'risk_detected', `自动检测风险「${r.title}」(${r.severity})`);
    }
    return formatRiskCheck(detectedRisks, project.name);
  }
}

module.exports = { handleRiskAlert };
