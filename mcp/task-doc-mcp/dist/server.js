"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const mcp_js_1 = require("@modelcontextprotocol/sdk/server/mcp.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const zod_1 = require("zod");
const fs = __importStar(require("node:fs"));
const path = __importStar(require("node:path"));
const DEFAULT_BASE_DIR = 'docs/tasks';
function ensureDirExists(absoluteDir) {
    if (!fs.existsSync(absoluteDir)) {
        fs.mkdirSync(absoluteDir, { recursive: true });
    }
}
function renderPlanMarkdown(args) {
    const { taskTitle, goal, requirements, environment, phases } = args;
    const goalSection = `## 1. 目标

${goal.trim()}
${requirements ? `

**任务要求：**

${requirements.trim()}
` : ''}`;
    const envSection = environment
        ? `## 2. 当前环境

${environment.trim()}
`
        : '## 2. 当前环境\n\n（TODO：补充环境信息）\n';
    const phasesLines = [];
    phases.forEach((phase, index) => {
        phasesLines.push(`### Phase ${index + 1}：${phase.name}`);
        if (phase.description) {
            phasesLines.push('');
            phasesLines.push(phase.description.trim());
        }
        phasesLines.push('');
        phase.items.forEach((item) => {
            const mark = item.done ? 'x' : ' ';
            phasesLines.push(`- [${mark}] ${item.label}`);
        });
        phasesLines.push('');
    });
    return [
        `# ${taskTitle}`,
        '',
        goalSection,
        '',
        envSection,
        '',
        '## 3. 当前进度',
        '',
        '（TODO：首轮创建时可以简单写“尚未开始”或由调用方传入）',
        '',
        '## 4. 分阶段清单',
        '',
        phasesLines.join('\n'),
        '## 5. MVP 当前状态',
        '',
        '（TODO：待首次跑通后补充）',
        '',
        '## 6. 已验证结果',
        '',
        '（TODO：按阶段补充验证记录）',
        '',
        '## 7. 下一步建议',
        '',
        '（TODO：结合当前阶段和风险列出）',
        '',
        '## 8. 下一窗口提示词',
        '',
        '```text',
        '（TODO：这里写给下一窗口 AI 的提示词示例）',
        '```',
        '',
    ].join('\n');
}
function renderHandoffMarkdown(args) {
    const { taskSlug, currentStatus, completedItemsSummary, changedFiles, verification, conclusion, nextWindowSteps, implementationScope, integrationConclusion, nextWindowPrompt, } = args;
    const summarySection = completedItemsSummary.trim()
        ? `${completedItemsSummary.trim()}\n`
        : '（本阶段完成项建议用要点形式简要列出）\n';
    const filesSection = changedFiles.length
        ? changedFiles.map((file) => `- ${file}`).join('\n')
        : '（本次未记录具体文件，建议补充）';
    return [
        `# ${taskSlug} 交接任务单`,
        '',
        '## 1. 当前状态',
        '',
        currentStatus.trim(),
        '',
        '### 本阶段完成摘要',
        '',
        summarySection,
        '## 2. 本次主要修改文件',
        '',
        filesSection,
        '',
        '## 3. 验证结果',
        '',
        verification.trim(),
        '',
        '## 4. 复核结论',
        '',
        conclusion.trim(),
        '',
        '## 5. 下一窗口建议直接做的事情',
        '',
        nextWindowSteps.trim(),
        '',
        '## 6. 当前实现口径',
        '',
        implementationScope.trim(),
        '',
        '## 7. 当前联调结论',
        '',
        integrationConclusion.trim(),
        '',
        '## 8. 下一窗口可直接复用的提示词',
        '',
        '```text',
        nextWindowPrompt.trim(),
        '```',
        '',
    ].join('\n');
}
async function main() {
    const server = new mcp_js_1.McpServer({
        name: 'task-doc-mcp',
        version: '0.1.0',
    });
    server.registerTool('create_task_docs', {
        title: '创建任务计划和交接文档',
        description: '在 docs/tasks/<taskSlug>/ 下创建 <slug>-plan.md 和 <slug>-handoff.md。',
        // 这里用宽松的 any schema，避免复杂泛型导致 TS2589。
        inputSchema: zod_1.z.any(),
    }, async (argsAny) => {
        const args = argsAny;
        const baseDir = args.baseDir ?? DEFAULT_BASE_DIR;
        const rootDir = path.resolve(process.cwd(), baseDir, args.taskSlug);
        ensureDirExists(rootDir);
        const planPath = path.join(rootDir, `${args.taskSlug}-plan.md`);
        const handoffPath = path.join(rootDir, `${args.taskSlug}-handoff.md`);
        const planContent = renderPlanMarkdown(args);
        const handoffContent = renderHandoffMarkdown({
            taskSlug: args.taskSlug,
            currentStatus: '尚未开始，等待首个开发窗口。',
            completedItemsSummary: '',
            changedFiles: [],
            verification: '尚未执行验证。',
            conclusion: '尚未开始实施。',
            nextWindowSteps: '请先阅读 plan.md，并补充第一阶段实施计划与验证策略。',
            implementationScope: '保持 MVP 口径，由 plan.md 中的设计边界约束。',
            integrationConclusion: '尚未联调。',
            nextWindowPrompt: '请先阅读 docs/tasks/<task-slug>/<task-slug>-plan.md 和 docs/tasks/<task-slug>/<task-slug>-handoff.md，然后根据第一阶段计划开始实现。',
            baseDir,
        });
        fs.writeFileSync(planPath, planContent, { encoding: 'utf8' });
        fs.writeFileSync(handoffPath, handoffContent, { encoding: 'utf8' });
        const summary = `已在 ${rootDir} 下生成:
- ${path.basename(planPath)}
- ${path.basename(handoffPath)}`;
        return {
            content: [
                {
                    type: 'text',
                    text: summary,
                },
            ],
            structured: {
                planPath,
                handoffPath,
            },
        };
    });
    server.registerTool('update_handoff', {
        title: '更新交接任务单',
        description: '根据本阶段完成情况更新 docs/tasks/<taskSlug>/<slug>-handoff.md。',
        inputSchema: zod_1.z.object({
            taskSlug: zod_1.z.string().min(1, 'taskSlug 不能为空'),
            currentStatus: zod_1.z.string().min(1, 'currentStatus 不能为空'),
            completedItemsSummary: zod_1.z.string().default(''),
            changedFiles: zod_1.z.array(zod_1.z.string()).default([]),
            verification: zod_1.z.string().min(1, 'verification 不能为空'),
            conclusion: zod_1.z.string().min(1, 'conclusion 不能为空'),
            nextWindowSteps: zod_1.z.string().min(1, 'nextWindowSteps 不能为空'),
            implementationScope: zod_1.z.string().min(1, 'implementationScope 不能为空'),
            integrationConclusion: zod_1.z.string().min(1, 'integrationConclusion 不能为空'),
            nextWindowPrompt: zod_1.z.string().min(1, 'nextWindowPrompt 不能为空'),
            baseDir: zod_1.z.string().optional(),
        }),
    }, async (rawArgs) => {
        const args = rawArgs;
        const baseDir = args.baseDir ?? DEFAULT_BASE_DIR;
        const rootDir = path.resolve(process.cwd(), baseDir, args.taskSlug);
        ensureDirExists(rootDir);
        const handoffPath = path.join(rootDir, `${args.taskSlug}-handoff.md`);
        const content = renderHandoffMarkdown(args);
        fs.writeFileSync(handoffPath, content, { encoding: 'utf8' });
        const summary = `已更新交接任务单: ${handoffPath}`;
        return {
            content: [
                {
                    type: 'text',
                    text: summary,
                },
            ],
            structured: {
                handoffPath,
            },
        };
    });
    const transport = new stdio_js_1.StdioServerTransport();
    await server.connect(transport);
}
void main();
