import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import * as fs from 'node:fs';
import * as path from 'node:path';

const DEFAULT_BASE_DIR = 'docs/tasks';

interface PhaseItem {
  label: string;
  done?: boolean;
}

interface Phase {
  name: string;
  description?: string;
  items: PhaseItem[];
}

interface CreateTaskDocsArgs {
  taskSlug: string;
  taskTitle: string;
  goal: string;
  requirements?: string;
  environment?: string;
  phases: Phase[];
  baseDir?: string;
}

interface UpdateHandoffArgs {
  taskSlug: string;
  currentStatus: string;
  completedItemsSummary: string;
  changedFiles: string[];
  verification: string;
  conclusion: string;
  nextWindowSteps: string;
  implementationScope: string;
  integrationConclusion: string;
  nextWindowPrompt: string;
  baseDir?: string;
}

function ensureDirExists(absoluteDir: string): void {
  if (!fs.existsSync(absoluteDir)) {
    fs.mkdirSync(absoluteDir, { recursive: true });
  }
}

function renderPlanMarkdown(args: CreateTaskDocsArgs): string {
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

  const phasesLines: string[] = [];
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

function renderHandoffMarkdown(args: UpdateHandoffArgs): string {
  const {
    taskSlug,
    currentStatus,
    completedItemsSummary,
    changedFiles,
    verification,
    conclusion,
    nextWindowSteps,
    implementationScope,
    integrationConclusion,
    nextWindowPrompt,
  } = args;

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

async function main(): Promise<void> {
  const server = new McpServer(
    {
      name: 'task-doc-mcp',
      version: '0.1.0',
    },
  );

  (server as any).registerTool(
    'create_task_docs',
    {
      title: '创建任务计划和交接文档',
      description: '在 docs/tasks/<taskSlug>/ 下创建 <slug>-plan.md 和 <slug>-handoff.md。',
      // 这里用宽松的 any schema，避免复杂泛型导致 TS2589。
      inputSchema: z.any() as z.ZodTypeAny,
    },
    async (argsAny: any) => {
      const args = argsAny as CreateTaskDocsArgs;

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
        nextWindowPrompt:
          '请先阅读 docs/tasks/<task-slug>/<task-slug>-plan.md 和 docs/tasks/<task-slug>/<task-slug>-handoff.md，然后根据第一阶段计划开始实现。',
        baseDir,
      } as UpdateHandoffArgs);

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
    },
  );

  (server as any).registerTool(
    'update_handoff',
    {
      title: '更新交接任务单',
      description: '根据本阶段完成情况更新 docs/tasks/<taskSlug>/<slug>-handoff.md。',
      inputSchema: z.object({
        taskSlug: z.string().min(1, 'taskSlug 不能为空'),
        currentStatus: z.string().min(1, 'currentStatus 不能为空'),
        completedItemsSummary: z.string().default(''),
        changedFiles: z.array(z.string()).default([]),
        verification: z.string().min(1, 'verification 不能为空'),
        conclusion: z.string().min(1, 'conclusion 不能为空'),
        nextWindowSteps: z.string().min(1, 'nextWindowSteps 不能为空'),
        implementationScope: z.string().min(1, 'implementationScope 不能为空'),
        integrationConclusion: z.string().min(1, 'integrationConclusion 不能为空'),
        nextWindowPrompt: z.string().min(1, 'nextWindowPrompt 不能为空'),
        baseDir: z.string().optional(),
      }) as z.ZodTypeAny,
    },
    async (rawArgs: unknown) => {
      const args = rawArgs as UpdateHandoffArgs;

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
    },
  );

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

void main();

