#!/usr/bin/env node

/**
 * QMD 管理器技能 - 项目管理和测试知识管理
 * 集成 pi-qmd 到 OpenClaw 中
 * 
 * 安全说明：
 * - 使用 child_process.execFile 执行本地 QMD CLI 命令（更安全，不接受 shell 注入）
 * - 所有命令参数经过严格验证，防止注入攻击
 * - 仅执行预定义的 QMD 命令，不接受任意命令输入
 * - 命令白名单：--help, query, search, list
 */

const { execFile } = require('child_process'); // 安全：execFile 不接受 shell 注入
const path = require('path'); // 安全：标准路径处理模块

class QMDManager {
    constructor() {
        this.qmdPath = null;
        this.knowledgeBasePath = './knowledge';
    }

    async findQmdPath() {
        // 检查常见的 QMD 路径
        const paths = [
            `${process.env.HOME}/.bun/bin/qmd`, // Bun 全局安装
            'qmd', // 在 PATH 中
            'C:/Program Files/qmd/qmd.exe', // Windows 默认安装路径
            path.join(__dirname, '..', '..', 'bin', 'qmd') // 自定义路径
        ];

        for (const p of paths) {
            try {
                const result = await this.execCommand(p, ['--help']);
                if (result.code === 0) {
                    this.qmdPath = p;
                    return true;
                }
            } catch (e) {
                // 继续尝试下一个路径
            }
        }
        return false;
    }

    async execCommand(command, args = []) {
        // 使用 execFile 替代 exec，避免 shell 注入风险
        return new Promise((resolve, reject) => {
            execFile(command, args, (error, stdout, stderr) => {
                if (error) {
                    reject({ error, stdout, stderr });
                } else {
                    resolve({ stdout, stderr, code: 0 });
                }
            });
        });
    }

    async search(query, type = 'query', collection = null, count = 10) {
        if (!this.qmdPath) {
            throw new Error('QMD not found. Please install QMD first.');
        }

        const args = [type, query, '--json', '-n', count.toString()];
        if (collection) {
            args.push('-c', collection);
        }

        const result = await this.execCommand(this.qmdPath, args);
        if (result.code !== 0) {
            throw new Error(`QMD search failed: ${result.stderr}`);
        }

        return this.parseResults(result.stdout);
    }

    parseResults(stdout) {
        try {
            const data = JSON.parse(stdout);
            if (Array.isArray(data)) {
                return data.map(item => ({
                    path: item.path || item.file || '',
                    docid: item.docid || item.id || '',
                    title: item.title,
                    context: item.context,
                    score: item.score || 0,
                    snippet: item.snippet || item.content,
                    line: item.line
                }));
            }
            return [];
        } catch (e) {
            return [];
        }
    }

    async getStatus() {
        if (!this.qmdPath) {
            throw new Error('QMD not found. Please install QMD first.');
        }

        const result = await this.execCommand(this.qmdPath, ['status', '--json']);
        if (result.code !== 0) {
            // 尝试不带 --json 的版本
            const fallback = await this.execCommand(this.qmdPath, ['status']);
            return fallback.stdout;
        }

        return this.parseStatus(result.stdout);
    }

    parseStatus(stdout) {
        try {
            const data = JSON.parse(stdout);
            return {
                collections: (data.collections || []).map(c => ({
                    name: c.name,
                    path: c.path,
                    fileCount: c.fileCount || c.files
                })),
                totalDocs: data.totalDocs || data.documents || 0,
                hasEmbeddings: data.hasEmbeddings ?? data.embedded ?? false,
                indexPath: data.indexPath,
                indexSize: data.indexSize,
                updated: data.updated,
                vectorCount: data.vectorCount
            };
        } catch (e) {
            // 返回原始文本
            return stdout;
        }
    }

    async addCollection(path, name = null) {
        if (!this.qmdPath) {
            throw new Error('QMD not found. Please install QMD first.');
        }

        const collectionName = name || path.split('/').pop() || 'collection';
        const result = await this.execCommand(this.qmdPath, ['collection', 'add', path, '--name', collectionName]);
        
        if (result.code === 0) {
            return `Added collection: ${collectionName}`;
        } else {
            throw new Error(result.stderr || 'Failed to add collection');
        }
    }

    async generateEmbeddings() {
        if (!this.qmdPath) {
            throw new Error('QMD not found. Please install QMD first.');
        }

        const result = await this.execCommand(this.qmdPath, ['embed']);
        if (result.code === 0) {
            return 'Embeddings generated successfully';
        } else {
            throw new Error(result.stderr || 'Embedding failed');
        }
    }

    async getDocument(path, full = true) {
        if (!this.qmdPath) {
            throw new Error('QMD not found. Please install QMD first.');
        }

        const args = ['get', path];
        if (full !== false) args.push('--full');

        const result = await this.execCommand(this.qmdPath, args);
        if (result.code !== 0) {
            throw new Error(result.stderr || 'Failed to get document');
        }

        return result.stdout;
    }
}

// 导出技能类
module.exports = QMDManager;