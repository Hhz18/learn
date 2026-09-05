export const meta = {
  name: 'china-us-diplomacy-2026-h1-and-us-iran-war-strategy-shift',
  description: '深度研究2026年1-6月中美外交官方新闻，以及美伊战争前后美国全球外交策略的转变',
  phases: [
    { title: 'Phase 1 - Scope 分解搜索角度' },
    { title: 'Phase 2 - Search 5路并行搜索' },
    { title: 'Phase 3 - Fetch 抓取官方来源' },
    { title: 'Phase 4 - Verify 对抗性验证' },
    { title: 'Phase 5 - Synthesize 综合报告' },
  ],
}

// ============================================================
// Phase 1: Scope —— 5个搜索角度
// ============================================================
phase('Phase 1 - Scope 分解搜索角度')
log('已锁定5个搜索角度，等待开始并行搜索')

// ============================================================
// Phase 2: Search —— 5路并行搜索
// ============================================================
phase('Phase 2 - Search 5路并行搜索')

// 每个搜索角度一个agent，每个agent返回搜索结果清单
const angles = [
  {
    key: 'cn-us-2026-jan-feb',
    prompt: `搜索2026年1月至2月期间中美外交方面的官方新闻。要求来源必须是官方渠道（中国外交部、新华社、人民日报、白宫、美国国务院、驻华使馆等），不要媒体二手报道。

请用 web_search_prime 工具检索，搜索关键词示例：
- "中美关系 2026年1月 外交部"
- "China US relations January February 2026 State Department"
- "中美高层互动 2026 王毅"
- "白宫 中国 2026年1月"
- "习近平 特朗普 2026 通话"

返回 JSON 数组，每条包含：日期、标题、来源、URL、核心内容简述、是否官方来源。
至少找到8-15条。`,
  },
  {
    key: 'cn-us-2026-mar-apr',
    prompt: `搜索2026年3月至4月期间中美外交方面的官方新闻。要求来源必须是官方渠道（中国外交部、新华社、人民日报、白宫、美国国务院、驻华使馆等），不要媒体二手报道。

请用 web_search_prime 工具检索，搜索关键词示例：
- "中美关系 2026年3月 外交部"
- "China US diplomacy March April 2026"
- "中美高层会晤 2026 春季"
- "白宫 中国 2026年3月"
- "中美贸易 2026年4月"

返回 JSON 数组，每条包含：日期、标题、来源、URL、核心内容简述、是否官方来源。
至少找到8-15条。`,
  },
  {
    key: 'cn-us-2026-may-jun',
    prompt: `搜索2026年5月至6月期间中美外交方面的官方新闻。要求来源必须是官方渠道（中国外交部、新华社、人民日报、白宫、美国国务院、驻华使馆等），不要媒体二手报道。

请用 web_search_prime 工具检索，搜索关键词示例：
- "中美关系 2026年5月 外交部"
- "China US relations May June 2026"
- "中美高层通话 2026年6月"
- "白宫 中国 2026年5月"
- "中美经贸 2026 夏季"

返回 JSON 数组，每条包含：日期、标题、来源、URL、核心内容简述、是否官方来源。
至少找到8-15条。`,
  },
  {
    key: 'us-iran-war-2026',
    prompt: `搜索2026年美伊战争/美伊冲突的相关信息。这是一个非常重要的背景任务。

请用 web_search_prime 工具检索，搜索关键词示例：
- "美伊战争 2026"
- "US Iran war 2026"
- "美国 伊朗 军事冲突 2026"
- "美伊冲突 时间线 2026"
- "Trump Iran 2026 conflict"
- "霍尔木兹海峡 2026"

返回 JSON 数组，每条包含：日期、标题、来源、URL、核心内容简述。
目标：搞清楚这场战争/冲突的时间线（何时开始、何时结束、关键事件）。
至少找到10-15条。`,
  },
  {
    key: 'us-global-diplomacy-shift',
    prompt: `搜索美伊战争（2026年）前后美国在全球外交策略上的官方新闻、表态和政策调整。重点关注：
1. 对华政策（关税、台湾、南海、科技）
2. 对欧政策（北约、欧盟、乌克兰）
3. 中东政策（以色列、沙特、海湾国家）
4. 亚太盟友（日韩澳菲）
5. 全球领导力（联合国、G7、G20）

请用 web_search_prime 工具检索，搜索关键词示例：
- "US foreign policy shift 2026 Iran war"
- "美国全球战略 调整 2026"
- "美国 中东政策 转变 2026"
- "美国 欧洲关系 2026"
- "美国 印太战略 2026"
- "State Department strategy 2026"

返回 JSON 数组，每条包含：日期、标题、来源、URL、核心内容简述、是否官方来源。
至少找到12-20条。`,
  },
]

// 用一个并行的搜索代理收集每个角度
const searchResults = await parallel(angles.map(a => () =>
  agent(a.prompt, {
    label: `search:${a.key}`,
    phase: 'Phase 2 - Search 5路并行搜索',
    agentType: 'general-purpose',
  })
))

// ============================================================
// Phase 3: Fetch —— 抓取前15个最有价值的官方URL
// ============================================================
phase('Phase 3 - Fetch 抓取官方来源')

// 聚合所有URL，过滤掉非官方来源，优先选择官方域名
const allUrls = []
for (const r of searchResults) {
  if (!r) continue
  try {
    const items = typeof r === 'string' ? JSON.parse(r) : r
    if (Array.isArray(items)) {
      for (const item of items) {
        if (item && item.url) allUrls.push(item)
      }
    }
  } catch (e) {
    // 容忍解析失败
  }
}

log(`共收集到 ${allUrls.length} 条URL/新闻条目`)

// 排序：官方来源优先
const officialDomains = [
  'fmprc.gov.cn', 'xinhuanet.com', 'people.com.cn', 'china.com.cn',
  'whitehouse.gov', 'state.gov', 'defense.gov', 'usembassy.gov',
  'un.org', 'nato.int',
]
function isOfficial(item) {
  const url = (item.url || '').toLowerCase()
  return officialDomains.some(d => url.includes(d)) || item.isOfficial === true
}

const sorted = allUrls
  .map((item, idx) => ({...item, idx, official: isOfficial(item)}))
  .sort((a, b) => (b.official ? 1 : 0) - (a.official ? 1 : 0))

log(`官方来源条目数：${sorted.filter(s => s.official).length}`)

// 用一个agent来抓取并整理这些URL的内容
const fetchPrompt = `请从以下搜索结果中，选择最重要的15-20条官方来源URL，使用 web_reader 工具抓取内容。

任务列表：
${sorted.slice(0, 60).map((s, i) => `${i+1}. [${s.official ? '官方' : '媒体'}] ${s.title || ''} | ${s.url} | ${s.summary || ''}`).join('\n')}

要求：
1. 优先抓取官方来源（外交部、白宫、国务院、新华社、人民日报等）
2. 对每条抓取的内容提取：发布日期、发布机构、核心要点、原文关键句
3. 按主题分类：中美双边 / 美伊战争 / 美国全球战略 / 其他

返回 JSON 数组，每条包含：url, source_type(官方/媒体), date, publisher, key_points, quotes(原文引用), category。
`

const fetchResults = await agent(fetchPrompt, {
  label: 'fetch:top-official-sources',
  phase: 'Phase 3 - Fetch 抓取官方来源',
  agentType: 'general-purpose',
})

// ============================================================
// Phase 4: Verify —— 对抗性验证关键声明
// ============================================================
phase('Phase 4 - Verify 对抗性验证')

const verifyPrompt = `基于抓取到的内容，请提炼出以下关键声明，每条声明请评估其可信度：

A. 中美关系方面（2026年1-6月）：
   A1. 中美是否有高层互访/通话？日期、参与者、议题
   A2. 中美在哪些议题上有进展？（贸易、台湾、气候、AI、芬太尼等）
   A3. 中美在哪些议题上分歧加剧？
   A4. 中方在外交场合对美表态的官方口径变化

B. 美伊战争方面：
   B1. 战争/冲突的准确开始时间、结束时间（如果已结束）
   B2. 战争的直接导火索
   B3. 战争涉及的范围（军事打击、制裁、外交断裂等）

C. 美国全球外交策略转变：
   C1. 对华政策在战前战后是否有调整？（关税、技术、台湾、南海）
   C2. 对欧政策（北约、乌克兰、欧盟贸易）是否有调整？
   C3. 中东政策（沙特、以色列、海湾）是否有调整？
   C4. 亚太盟友政策（日韩澳）是否有调整？
   C5. 多边机制（联合国、G7、G20、WHO）参与度是否有变化？

对每个声明给出：
- 声明内容
- 支持证据（至少2个官方来源）
- 反对/质疑证据（如果有）
- 评估等级：高/中/低（高=多源官方确认，低=单一来源或推测）

返回 JSON 对象。`

const verifyResults = await agent(verifyPrompt, {
  label: 'verify:key-claims',
  phase: 'Phase 4 - Verify 对抗性验证',
  agentType: 'general-purpose',
})

// ============================================================
// Phase 5: Synthesize —— 综合报告
// ============================================================
phase('Phase 5 - Synthesize 综合报告')

const synthPrompt = `基于前面所有阶段的搜索结果、抓取的官方内容、验证评估，请撰写一份完整的研究报告。

报告要求：

【报告结构】

# 第一部分：2026年1-6月中美外交官方新闻
## 1月（按时间顺序，每条标注：日期 | 标题 | 来源 | URL | 核心要点）
## 2月
## 3月
## 4月
## 5月
## 6月
## 阶段性小结：1-6月中美关系走势

# 第二部分：美伊战争（2026年）背景
## 战争概况：时间线、起因、关键事件、当前状态
## 战争中各方的官方表态（中国、美国、伊朗、其他主要国家）

# 第三部分：美伊战争前后美国全球外交策略对比
## 对华政策：战前 vs 战后
## 对欧政策：战前 vs 战后
## 中东政策：战前 vs 战后
## 亚太盟友政策：战前 vs 战后
## 多边机制参与度：战前 vs 战后
## 总体评估：美国是否在外交策略上有重大转变？转变的方向是什么？

# 第四部分：综合判断
## 美国外交策略是否发生转变：Y/N
## 转变的核心驱动力是什么？
## 对中美关系的潜在影响

【格式要求】
1. 严格区分官方来源（外交部、白宫、国务院、新华社等）与媒体报道
2. 每条新闻必须标注：日期 | 来源机构 | URL | 核心要点
3. 引用原文时使用引号并注明出处
4. 分析要有事实依据，避免空泛判断
5. 如果某些信息无法核实或存在争议，明确说明
6. 使用Markdown格式，标题层级清晰

【特别注意】
- 中国官方来源：fmprc.gov.cn, xinhuanet.com, people.com.cn
- 美国官方来源：whitehouse.gov, state.gov, defense.gov
- 多边机构：un.org, nato.int
- 必须诚实标注"未能核实"的部分`

const finalReport = await agent(synthPrompt, {
  label: 'synthesize:final-report',
  phase: 'Phase 5 - Synthesize 综合报告',
  agentType: 'general-purpose',
})

return {
  searchResultsCount: allUrls.length,
  officialCount: sorted.filter(s => s.official).length,
  finalReport,
}