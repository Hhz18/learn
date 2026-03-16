# 管理端一键转码与 HLS 自动导入方案

## 1. 目标

目标是把当前人工流程：

`上传原视频 -> 本地 ffmpeg 转码 -> 手动上传 OSS -> 手动调用 import-hls -> 手动绑定课时`

封装成管理端可操作的自动流程：

`管理员上传原视频 -> 管理端创建转码任务 -> Worker 自动转码 -> 自动上传 OSS -> 自动导入 HLS -> 管理端查看进度 -> 绑定课时播放`

当前仓库继续沿用同一条实现路线：

**方案 A：管理端发起 + 后端任务入库 + Worker 执行 ffmpeg + 自动上传 OSS + 自动导入 HLS**

## 2. 当前进度

截至 2026-03-09，Phase 1、Phase 2、Phase 3 已完成，Phase 4 核心代码也已完成；Phase 5 主体页面也已补齐，且 `playedu-api` 已通过：

```powershell
.\mvnw.cmd -q -DskipTests compile
```

本轮新增并完成：

- 新增 Worker 入口与单线程轮询执行
- 实现 `pending` 任务拉取与抢占
- 实现任务状态流转：`pending -> preparing -> processing -> ready/failed/canceled`
- 实现 `ffprobe` 执行封装
- 实现 `ffmpeg` HLS 转码与海报抽帧封装
- 实现 stdout / stderr 日志采集
- 实现任务日志回写到 `transcode_task.logs`
- 实现 `/backend/v1/transcode/tasks/{id}/logs` 返回真实日志
- 实现本地工作目录与输出目录管理
- 实现源文件本地读取与 S3 下载到工作目录
- 实现 `segment_count` 统计
- 实现失败时 `error_message` 写入与任务置为 `failed`
- 实现成功时任务置为 `ready`
- 实现取消时主动终止运行中的 `ffprobe` / `ffmpeg` 进程
- 实现下载源文件时的文件名清洗，兼容 Windows 非法字符
- 实现本地产物自动上传 OSS
- 实现自动组装 `import-hls` 参数
- 实现自动写入 `resource` / `resource_extra`
- 实现 `playlist_path` / `hls_prefix` 切换为 OSS 对象路径语义
- 实现回写 `resource_id` / `poster_resource_id`
- 实现上传前清理旧 OSS 前缀，避免重试残留
- 实现失败 / 取消后的 OSS 与资源清理
- 实现取消状态保护，避免 Worker 覆盖 `canceled`
- 实现 `app_config` 本地缓存，减少 Worker 轮询重复查询
- 增加管理端“转码任务列表”页面
- 增加管理端“转码任务详情”页面
- 增加任务日志查看、重试、取消按钮
- 增加任务状态标签与进度展示组件
- 在视频上传浮窗增加“转码为 HLS”开关与转码参数表单
- 实现上传成功后自动创建转码任务
- 在系统配置页增加全局“转码配置”Tab
- 在转码页面中明确标注“服务器 / Worker 路径”字段
- 调整 `/backend/v1/upload/minio/merge-file` 返回新建资源对象，便于上传后直接创建转码任务

当前阶段仍未完成：

- `importing` 阶段取消的稳定复现
- 失败后 OSS 残留清理的最终运行态验证
- `playedu-admin` 全量构建验证

## 3. 当前设计边界

Phase 4 保持以下口径不变：

- 只支持单码率 HLS
- 不在 HTTP 请求中执行 `ffmpeg`
- 不做分布式队列
- 不做多并发调度
- 不拆独立日志表，日志先落在 `transcode_task.logs`
- 不做多码率 HLS 自动转码

因此当前 `ready` 的含义是：

- 本地转码成功
- OSS 上传成功
- HLS 自动导入成功
- 任务日志、时长、分片数、资源 ID 已写回

当前 `playlist_path` / `hls_prefix` 已切换为 OSS 对象路径语义。

## 4. 分阶段清单

### Phase 1：任务模型与基础配置

- [x] 新增 `transcode_task` 表
- [x] 新增 `transcode_task.category_ids`
- [x] 定义 `transcode_task.status` 状态机
- [x] 定义 `TranscodeTask` / DTO / VO
- [x] 增加 `TranscodeTaskStatus`
- [x] 增加 `TranscodeTaskType`
- [x] 增加 `TranscodeMode`
- [x] 增加 `TranscodeErrorCode`
- [x] 增加全部 `transcode.*` 配置常量
- [x] 增加 `TranscodeConfig`
- [x] 增加配置初始化、读取、保存、校验逻辑

### Phase 2：后端任务接口

- [x] 新增 `TranscodeTaskController`
- [x] 新增 `TranscodeTaskService`
- [x] 新增 `TranscodeTaskMapper`
- [x] 新增 `CreateTranscodeTaskRequest`
- [x] 新增任务列表 / 详情响应对象
- [x] 实现 `POST /backend/v1/transcode/tasks`
- [x] 实现 `GET /backend/v1/transcode/tasks`
- [x] 实现 `GET /backend/v1/transcode/tasks/{id}`
- [x] 实现 `POST /backend/v1/transcode/tasks/{id}/retry`
- [x] 实现 `POST /backend/v1/transcode/tasks/{id}/cancel`
- [x] 实现 `GET /backend/v1/transcode/tasks/{id}/logs`
- [x] 实现创建任务参数校验
- [x] 实现任务重试限制
- [x] 实现任务取消限制

### Phase 3：Worker 最小执行链路

- [x] 新增 Worker 入口模块或后台任务线程
- [x] 实现任务拉取 / 抢占机制
- [x] 实现任务状态流转
- [x] 实现 `ffprobe` 执行封装
- [x] 实现 `ffmpeg` 执行封装
- [x] 实现 stdout / stderr 日志采集
- [x] 实现本地工作目录创建
- [x] 实现本地输出目录创建
- [x] 实现源文件读取逻辑
- [x] 实现自动抽取海报
- [x] 实现统计 `segment_count`
- [x] 实现失败时写入 `error_message`
- [x] 实现失败时任务置为 `failed`
- [x] 实现成功时任务置为 `ready`
- [x] 实现取消时终止运行中的外部进程
- [x] 实现源文件名清洗，避免 Windows 非法文件名失败

### Phase 4：OSS 自动上传与 HLS 自动导入

- [x] 实现源文件上传到 `videos/source/{taskId}/source.mp4`
- [x] 实现 `index.m3u8` 上传到 `videos/hls/{taskId}/index.m3u8`
- [x] 实现 `ts` 分片上传到 `videos/hls/{taskId}/`
- [x] 实现海报上传或复用现有海报存储逻辑
- [x] 实现上传 Content-Type 设置
- [x] 实现自动组装 `import-hls` 参数
- [x] 复用或封装现有 `import-hls` 入库逻辑
- [x] 自动写入 `resource`
- [x] 自动写入 `resource_extra`
- [x] 自动更新资源 `play_type = hls`
- [x] 自动更新资源 `transcode_status = ready`
- [x] 实现上传前清理旧 OSS 前缀
- [x] 实现失败 / 取消后的 OSS 与资源清理
- [x] 实现取消状态保护，避免 Worker 覆盖 `canceled`

### Phase 5：管理端 UI

- [x] 在视频上传页增加“转码为 HLS”开关
- [x] 在视频上传页增加转码参数表单
- [x] 增加“转码任务列表”页面
- [x] 增加“转码任务详情”页面
- [x] 增加任务状态展示组件
- [x] 增加错误日志查看功能
- [x] 增加任务重试按钮
- [x] 增加任务取消按钮
- [x] 增加全局“转码配置”页面
- [x] 页面中明确标注配置项为“服务器 / Worker 路径”

### Phase 6：稳定性与运维

- [ ] 实现 Worker 最大并发限制
- [ ] 实现任务失败自动重试
- [ ] 实现临时文件自动清理
- [ ] 实现任务日志表拆分或持久化优化
- [ ] 实现任务超时保护
- [ ] 实现重复任务保护
- [ ] 实现 Worker 健康检查
- [ ] 补充部署说明文档
- [ ] 补充运维配置说明文档
- [x] 减少 Worker 轮询时对 `app_config` 的重复查询

### Phase 7：联调与验收

- [x] 验证创建任务成功
- [x] 验证 Worker 能执行 `ffprobe`
- [x] 验证 Worker 能执行 `ffmpeg`
- [x] 验证生成 `index.m3u8`
- [x] 验证生成 `ts` 分片
- [x] 验证生成海报
- [x] 验证 OSS 上传路径正确
- [x] 验证 HLS 自动导入成功
- [x] 验证管理端资源显示为 `HLS`
- [x] 验证课时可绑定 HLS 资源
- [x] 验证 PC / H5 可正常播放 HLS
- [x] 验证旧 `mp4` 流程无回归
- [x] 验证失败任务可查看错误日志
- [x] 验证任务可重试
- [x] 验证任务可取消

## 5. MVP 当前状态

MVP 清单当前状态：

- [x] `transcode_task` 表
- [x] 创建任务接口
- [x] Worker 单线程执行
- [x] `ffprobe` 封装
- [x] `ffmpeg` 封装
- [x] OSS 自动上传
- [x] 自动导入 HLS
- [x] 管理端任务列表页
- [x] PC / H5 播放联调通过

## 6. 已验证结果

已确认：

- 后端编译通过
- Worker 代码已接入 Spring `@Scheduled`
- `pending` 任务可被抢占并进入执行链路
- 任务日志接口已返回真实日志数组
- 取消任务会主动终止运行中的 `ffprobe` / `ffmpeg`
- Phase 4 核心代码已接入 Worker 成功链路
- HLS 导入逻辑已封装为可复用服务
- 失败 / 取消场景已补充代码级清理逻辑
- `app_config` 已增加本地缓存，Worker 轮询不再每秒重复查询数据库
- 真实 OSS 联调下单个任务可完整跑通 `pending -> preparing -> processing -> uploading -> importing -> ready`
- 已验证成功任务会写入 `playlist_path=videos/hls/{taskId}/index.m3u8`
- 已验证成功任务会写入 `hls_prefix=videos/hls/{taskId}/`
- 已验证成功任务会写入 `resource_id` / `poster_resource_id`
- 已验证 `processing` 阶段取消会中止 `ffmpeg`，且不会进入上传 / 导入
- 已验证 `uploading` 阶段取消会触发 `cleanup uploaded artifacts finished`
- 已验证 `uploading` 阶段取消后任务保持 `canceled`，且不会导入资源
- 已验证任务 `6` 可通过 `/backend/v1/transcode/tasks/6/retry` 从 `canceled` 重新进入真实执行链路，并最终转为 `ready`
- 已验证任务 `6` 重试时日志包含 `cleaning stale source object=videos/source/6/source.mp4`
- 已验证任务 `6` 重试时日志包含 `cleaning stale hls prefix=videos/hls/6/`
- 已验证任务 `6` 重试成功后回写 `resource_id=48`、`poster_resource_id=47`
- 已验证管理端课程 `19` 的课时 `23` 已绑定 HLS 资源 `rid=35`
- 已验证前台课时播放接口 `GET /api/v1/course/19/hour/23/play` 返回 `play_type=hls`
- 已验证 HLS 播放地址为站内 `/api/v1/media/hls/index.m3u8?token=...`
- 已验证 HLS playlist 会被后端重写为带签名的 `.ts` 分片 URL
- 已验证首个 HLS 分片可返回 `206 Partial Content`，`Content-Type=video/mp2t`
- 已验证前台课时播放接口 `GET /api/v1/course/17/hour/21/play` 仍返回 `play_type=mp4`
- 已验证旧 `mp4` 播放地址可返回 `206 Partial Content`
- 已完成管理端转码任务列表 / 详情 / 日志 / 重试 / 取消页面接线
- 已完成视频上传浮窗“转码为 HLS”开关与参数表单接线
- 已完成系统配置页“转码配置”Tab 接线
- 已确认上传成功后会基于 `merge-file` 返回资源对象创建转码任务
- 已验证管理端上传浮窗可为新上传视频自动创建转码任务 `#9`
- 已验证任务 `#9` 详情页会展示 `playlist_path=videos/hls/9/index.m3u8`
- 已验证任务 `#9` 详情页会展示 `hls_prefix=videos/hls/9/`
- 已验证资源页中视频 `admin` 已显示为 `play_type=HLS`
- 已验证资源页中视频 `admin` 已显示为 `transcode_status=ready`

尚未完成的运行态验证：

- `importing` 阶段取消的稳定复现
- 失败后 OSS 残留清理验证
- `playedu-admin` 全量 `npm run build` 仍被仓库内既有 `src/pages/member/learn.tsx` 语法错误阻塞，尚未形成完整前端构建通过结论
- 上传浮窗仍有一个低风险问题：重复打开时会向 `document.body` 追加临时 `div`，关闭时未清理

## 7. 下一步建议

当前 Phase 5 主体已经完成，接下来建议转入收尾验证与稳定性补强：

- 管理端转码任务列表、详情、日志、重试、取消、上传触发、全局配置入口已补齐
- 管理端上传视频 -> 自动创建任务 -> 任务详情查看 -> 资源页显示 HLS 已完成真实联调
- 真实 OSS 成功链路、重试清理、课时绑定、HLS 播放链路、旧 `mp4` 回归已验证通过
- 当前剩余风险主要集中在 `importing` 取消、失败后 OSS 残留清理、前端全量 build 阻塞项与一个上传浮窗低风险清理问题

建议下一窗口顺序如下：

1. 先修复 `playedu-admin/src/pages/member/learn.tsx` 现有语法错误，恢复前端全量 build
2. 修复上传浮窗重复打开时临时 `div` 未清理的问题
3. 补 `importing` 取消稳定复现
4. 补失败后 OSS 残留清理验证
5. 完成后转入 Phase 6：稳定性与运维补强

## 8. 下一窗口提示词

```text
请先阅读 docs/hls-admin-transcode-automation-plan.md 和 docs/hls-admin-transcode-automation-handoff.md。
当前 Phase 1、Phase 2、Phase 3 已完成，并已通过 playedu-api 的 .\mvnw.cmd -q -DskipTests compile。
当前 Phase 4 核心代码和 Phase 5 管理端 UI 主体都已完成，且成功链路、`processing` 取消、`uploading` 取消已完成真实 OSS 联调。
当前 Phase 7 已补充完成：重试清理、课时绑定 HLS 资源、PC / H5 播放链路、旧 `mp4` 回归。
当前剩余问题主要是：
1. `playedu-admin/src/pages/member/learn.tsx` 现有语法错误导致前端全量 `npm run build` 仍失败；
2. 上传浮窗重复打开时会向 `document.body` 追加临时 `div`，关闭时未清理；
3. `importing` 阶段取消稳定复现；
4. 失败后 OSS 残留清理验证。
请先修复前两项，再继续补后两项，并在完成后补一轮前端完整构建验证。
```
