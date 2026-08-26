#!/usr/bin/env node
// Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
/**
 * GitHub Bounty Hunter v7.4.0
 * Copyright © 2026 思捷娅科技 (SJYKJ). All rights reserved.
 * MIT License
 */


/**
 * HackerOne 漏洞扫描器
 * v7.4.0 新增功能
 * OWASP Top 10 + CVE 模式匹配
 */

const fs = require('fs');
const path = require('path');

class HackerOneScanner {
    constructor() {
        this.owaspTop10 = [
            'Injection',
            'Broken Authentication',
            'Sensitive Data Exposure',
            'XML External Entities (XXE)',
            'Broken Access Control',
            'Security Misconfiguration',
            'Cross-Site Scripting (XSS)',
            'Insecure Deserialization',
            'Using Components with Known Vulnerabilities',
            'Insufficient Logging & Monitoring'
        ];
        
        this.cvePatterns = [
            /CVE-\d{4}-\d{4,7}/g,
            /CVE-\d{4}-\d{4}/g
        ];
    }

    /**
     * 扫描代码中的安全漏洞
     */
    scanCode(code, filePath) {
        const results = {
            owaspVulnerabilities: [],
            cveReferences: [],
            severity: 'LOW',
            recommendations: []
        };

        // OWASP Top 10 模式匹配
        this.owaspTop10.forEach(vuln => {
            const patterns = this.getOWASPPatterns(vuln);
            patterns.forEach(pattern => {
                if (pattern.test(code)) {
                    results.owaspVulnerabilities.push({
                        type: vuln,
                        file: filePath,
                        severity: this.getSeverity(vuln),
                        description: this.getDescription(vuln)
                    });
                }
            });
        });

        // CVE 引用扫描
        this.cvePatterns.forEach(pattern => {
            const matches = code.match(pattern);
            if (matches) {
                results.cveReferences.push(...matches);
            }
        });

        // 计算严重程度
        results.severity = this.calculateSeverity(results.owaspVulnerabilities);
        
        // 生成修复建议
        results.recommendations = this.generateRecommendations(results);

        return results;
    }

    /**
     * 获取 OWASP 漏洞模式
     */
    getOWASPPatterns(vulnerability) {
        const patterns = {
            'Injection': [
                /(?:sql|query|execute)\s*\(\s*["'`].*?\$/i,
                /(?:prepare|execute)\s*\(\s*[^"']*?\$/i,
                /\$.*?\s*\+\s*req\./i,
                /eval\s*\(/i,
                /exec\s*\(/i
            ],
            'Cross-Site Scripting (XSS)': [
                /res\.write\s*\(/i,
                /document\.write\s*\(/i,
                /innerHTML\s*=/i,
                /outerHTML\s*=/i,
                /\.html\s*\(/i
            ],
            'Broken Authentication': [
                /password\s*=\s*["'][^"']*["']/i,
                /secret\s*=\s*["'][^"']*["']/i,
                /token\s*=\s*["'][^"']*["']/i
            ],
            'Sensitive Data Exposure': [
                /(?:password|secret|token|key)\s*=\s*["'][^"']*["']/i,
                /console\.log\s*\(.*?(?:password|secret|token)/i
            ]
        };

        return patterns[vulnerability] || [];
    }

    /**
     * 获取漏洞严重程度
     */
    getSeverity(vulnerability) {
        const severityMap = {
            'Injection': 'HIGH',
            'Broken Authentication': 'HIGH',
            'Sensitive Data Exposure': 'MEDIUM',
            'Cross-Site Scripting (XSS)': 'MEDIUM',
            'Broken Access Control': 'HIGH',
            'Security Misconfiguration': 'LOW'
        };

        return severityMap[vulnerability] || 'LOW';
    }

    /**
     * 获取漏洞描述
     */
    getDescription(vulnerability) {
        const descriptions = {
            'Injection': 'Code injection vulnerability detected. Use parameterized queries.',
            'Cross-Site Scripting (XSS)': 'XSS vulnerability found. Implement input sanitization.',
            'Broken Authentication': 'Authentication mechanism may be weak. Use strong authentication.',
            'Sensitive Data Exposure': 'Sensitive data may be exposed. Use encryption.'
        };

        return descriptions[vulnerability] || 'Security vulnerability detected.';
    }

    /**
     * 计算整体严重程度
     */
    calculateSeverity(vulnerabilities) {
        const severities = vulnerabilities.map(v => v.severity);
        if (severities.includes('HIGH')) return 'HIGH';
        if (severities.includes('MEDIUM')) return 'MEDIUM';
        return 'LOW';
    }

    /**
     * 生成修复建议
     */
    generateRecommendations(results) {
        const recommendations = [];

        if (results.owaspVulnerabilities.length > 0) {
            recommendations.push('Fix identified OWASP Top 10 vulnerabilities');
        }

        if (results.cveReferences.length > 0) {
            recommendations.push(`Update components with known CVEs: ${results.cveReferences.join(', ')}`);
        }

        recommendations.push('Implement security headers');
        recommendations.push('Add input validation and sanitization');
        recommendations.push('Use parameterized queries for database operations');

        return recommendations;
    }

    /**
     * 扫描整个项目
     */
    scanProject(projectPath) {
        const scanResults = {
            totalFiles: 0,
            vulnerableFiles: 0,
            totalVulnerabilities: 0,
            severityBreakdown: { HIGH: 0, MEDIUM: 0, LOW: 0 },
            files: []
        };

        const files = this.getJavaScriptFiles(projectPath);
        
        files.forEach(file => {
            const code = fs.readFileSync(file, 'utf8');
            const result = this.scanCode(code, file);
            
            if (result.owaspVulnerabilities.length > 0 || result.cveReferences.length > 0) {
                scanResults.files.push(result);
                scanResults.vulnerableFiles++;
                scanResults.totalVulnerabilities += result.owaspVulnerabilities.length;
                
                if (result.severity === 'HIGH') scanResults.severityBreakdown.HIGH++;
                else if (result.severity === 'MEDIUM') scanResults.severityBreakdown.MEDIUM++;
                else scanResults.severityBreakdown.LOW++;
            }
        });

        scanResults.totalFiles = files.length;
        return scanResults;
    }

    /**
     * 获取所有 JavaScript 文件
     */
    getJavaScriptFiles(dir) {
        const files = [];
        
        const traverse = (directory) => {
            const items = fs.readdirSync(directory);
            
            items.forEach(item => {
                const fullPath = path.join(directory, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    traverse(fullPath);
                } else if (fullPath.endsWith('.js') || fullPath.endsWith('.ts')) {
                    files.push(fullPath);
                }
            });
        };

        traverse(dir);
        return files;
    }
}

// CLI 接口
if (require.main === module) {
    const scanner = new HackerOneScanner();
    
    if (process.argv.length < 3) {
        console.log('Usage: node hackerone-scanner.js <project-path>');
        process.exit(1);
    }

    const projectPath = process.argv[2];
    console.log(`🔍 Scanning project: ${projectPath}`);
    
    try {
        const results = scanner.scanProject(projectPath);
        
        console.log(`\n📊 Scan Results:`);
        console.log(`   Total files scanned: ${results.totalFiles}`);
        console.log(`   Vulnerable files: ${results.vulnerableFiles}`);
        console.log(`   Total vulnerabilities: ${results.totalVulnerabilities}`);
        console.log(`   Severity breakdown: HIGH=${results.severityBreakdown.HIGH}, MEDIUM=${results.severityBreakdown.MEDIUM}, LOW=${results.severityBreakdown.LOW}`);
        
        if (results.files.length > 0) {
            console.log(`\n🔴 Vulnerable Files:`);
            results.files.forEach(file => {
                console.log(`   ${file.file} (${file.severity})`);
            });
        }
        
    } catch (error) {
        console.error(`❌ Error scanning project: ${error.message}`);
        process.exit(1);
    }
}

module.exports = HackerOneScanner;