# HLS 管理端自动转码交接任务单

## 1. 当前状态

截至 2026-03-09，`hls-admin-transcode-automation-plan.md` 的 Phase 1、Phase 2、Phase 3 已完成，Phase 4 核心代码已完成，后端编译通过；Phase 5 管理端 UI 主体也已完成。Phase 7 已补充完成重试清理、课时绑定 HLS 资源、PC / H5 播放链路与旧 `mp4` 回归验证；成功链路、`processing` 取消、`uploading` 取消也已验证通过。

已完成内容：

- 新增 `transcode_task` 表迁移
- 新增 `transcode_task.category_ids` 字段迁移
- 新增 `transcode_task.logs` 字段迁移
- 新增转码任务基础模型与接口：
  - `TranscodeTask`
  - `TranscodeTaskMapper`
  - `TranscodeTaskService`
  - `TranscodeTaskServiceImpl`
- 新增转码配置与常量：
  - `TranscodeConfig`
  - `TranscodeTaskStatus`
  - `TranscodeTaskType`
  - `TranscodeMode`
  - `TranscodeErrorCode`
  - 全部 `transcode.*` 配置常量
- 已完成转码配置初始化、读取、保存前校验
- 已完成转码任务接口：
  - `POST /backend/v1/transcode/tasks`
  - `GET /backend/v1/transcode/tasks`
  - `GET /backend/v1/transcode/tasks/{id}`
  - `POST /backend/v1/transcode/tasks/{id}/retry`
  - `POST /backend/v1/transcode/tasks/{id}/cancel`
  - `GET /backend/v1/transcode/tasks/{id}/logs`
- 已完成 Phase 3 Worker 最小执行链路：
  - Worker 轮询入口
  - `pending` 任务拉取 / 抢占
  - 状态流转
  - `ffprobe` 执行封装
  - `ffmpeg` 单码率 HLS 执行封装
  - 海报抽帧
  - stdout / stderr 日志采集
  - 本地工作目录 / 输出目录管理
  - 源文件本地读取与 S3 下载
  - `segment_count` 统计
  - `error_message` 写入
  - 任务成功 / 失败 / 取消落库
  - `/logs` 接口返回真实日志
- 已补充两个运行态问题修复：
  - 取消任务时主动终止运行中的 `ffprobe` / `ffmpeg`
  - 下载源文件时清洗文件名，避免 Windows 非法文件名失败
- 已完成 Phase 4 核心代码：
  - 本地产物自动上传 OSS
  - 自动组装 HLS 导入参数
  - 复用导入逻辑写入 `resource` / `resource_extra`
  - 任务 `playlist_path` / `hls_prefix` 切换为 OSS 路径语义
  - 回写任务 `resource_id` / `poster_resource_id`
- 已补充本轮运行态修复：
  - 取消状态保护，避免 Worker 覆盖 `canceled`
  - 上传前清理旧 OSS 前缀，避免重试残留分片
  - 失败 / 取消后清理 OSS 产物、HLS 资源与海报资源
  - `app_config` 本地缓存，减少 Worker 轮询重复查询
- 已完成 Phase 5 管理端 UI：
  - 新增转码任务列表页
  - 新增转码任务详情页
  - 新增日志查看、重试、取消按钮
  - 新增任务状态标签与进度展示
  - 在视频上传浮窗增加“转码为 HLS”开关与转码参数表单
  - 实现上传成功后自动创建转码任务
  - 在系统配置页增加“转码配置”Tab
  - 页面中明确标注配置项为“服务器 / Worker 路径”
- 已补一个前后端衔接改动：
  - `/backend/v1/upload/minio/merge-file` 现在返回新建资源对象，供上传成功后立即创建转码任务

未完成内容：

- Phase 6：并发、重试、清理、健康检查等稳定性补强
- Phase 7：`importing` 阶段取消的稳定复现
- Phase 7：失败任务后的 OSS 残留清理
- `playedu-admin` 全量 `npm run build` 验证
- 上传浮窗一个低风险 DOM 清理问题修复

## 2. 本次主要修改文件

- [hls-admin-transcode-automation-plan.md](/c:/Users/23075/Desktop/playedu-main/docs/hls-admin-transcode-automation-plan.md)
- [MigrationCheck.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-system/src/main/java/xyz/playedu/system/checks/MigrationCheck.java)
- [TranscodeTask.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-common/src/main/java/xyz/playedu/common/domain/TranscodeTask.java)
- [TranscodeTaskService.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-common/src/main/java/xyz/playedu/common/service/TranscodeTaskService.java)
- [TranscodeTaskServiceImpl.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-common/src/main/java/xyz/playedu/common/service/impl/TranscodeTaskServiceImpl.java)
- [S3Util.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-common/src/main/java/xyz/playedu/common/util/S3Util.java)
- [TranscodeTaskController.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/controller/backend/TranscodeTaskController.java)
- [ProcessExecutor.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/ProcessExecutor.java)
- [ProcessExecutionResult.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/ProcessExecutionResult.java)
- [TranscodeTaskException.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/TranscodeTaskException.java)
- [FfprobeExecutor.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/FfprobeExecutor.java)
- [FfmpegExecutor.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/FfmpegExecutor.java)
- [TranscodeTaskRunner.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/TranscodeTaskRunner.java)
- [TranscodeWorker.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/TranscodeWorker.java)
- [TranscodeArtifactUploadService.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/TranscodeArtifactUploadService.java)
- [HlsImportService.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/HlsImportService.java)
- [TranscodeCleanupService.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/transcode/TranscodeCleanupService.java)
- [UploadController.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-api/src/main/java/xyz/playedu/api/controller/backend/UploadController.java)
- [AppConfigServiceImpl.java](/c:/Users/23075/Desktop/playedu-main/playedu-api/playedu-common/src/main/java/xyz/playedu/common/service/impl/AppConfigServiceImpl.java)
- [routes/index.tsx](/c:/Users/23075/Desktop/playedu-main/playedu-admin/src/routes/index.tsx)
- [left-menu/index.tsx](/c:/Users/23075/Desktop/playedu-main/playedu-admin/src/compenents/left-menu/index.tsx)
- [transcode.ts](/c:/Users/23075/Desktop/playedu-main/playedu-admin/src/api/transcode.ts)
- [upload-video-float-button/index.tsx](/c:/Users/23075/Desktop/playedu-main/playedu-admin/src/compenents/upload-video-float-button/index.tsx)
- [transcode-tasks/index.tsx](/c:/Users/23075/Desktop/playedu-main/playedu-admin/src/pages/resource/transcode-tasks/index.tsx)
- [transcode-task-detail/index.tsx](/c:/Users/23075/Desktop/playedu-main/playedu-admin/src/pages/resource/transcode-task-detail/index.tsx)
- [system/config/index.tsx](/c:/Users/23075/Desktop/playedu-main/playedu-admin/src/pages/system/config/index.tsx)

## 3. 验证结果

已执行：

```powershell
.\mvnw.cmd -q -DskipTests compile
```

执行目录：

```powershell
c:\Users\23075\Desktop\playedu-main\playedu-api
```

结果：

- 后端编译通过

本轮前端验证补充结论：

- 本次新增的 Phase 5 相关文件已做定向语法校验，可通过
- `playedu-admin` 全量 `npm run build` 仍失败
- 失败原因不是本轮 Phase 5 新增代码，而是仓库内既有文件 `src/pages/member/learn.tsx` 存在语法错误

本轮真实联调已验证：

- 转码配置已在联调环境启用，`ffmpeg` / `ffprobe` / `work_dir` / `output_root` 已完成实配
- 真实 OSS 下单个任务可完整跑通 `pending -> preparing -> processing -> uploading -> importing -> ready`
- 成功任务会写入 `playlist_path=videos/hls/{taskId}/index.m3u8`
- 成功任务会写入 `hls_prefix=videos/hls/{taskId}/`
- 成功任务会写入 `resource_id` / `poster_resource_id`
- `processing` 阶段取消已验证成功，日志包含 `cancellation requested, stopping process`
- `uploading` 阶段取消已验证成功，日志包含 `cleanup uploaded artifacts finished`
- `uploading` 阶段取消后任务保持 `canceled`，不会进入资源导入
- 已对真实任务 `6` 执行 `/backend/v1/transcode/tasks/6/retry`
- 任务 `6` 已从 `canceled` 重新进入真实执行链路，并最终转为 `ready`
- 任务 `6` 重试日志包含 `cleaning stale source object=videos/source/6/source.mp4`
- 任务 `6` 重试日志包含 `cleaning stale hls prefix=videos/hls/6/`
- 任务 `6` 重试成功后回写 `resource_id=48`、`poster_resource_id=47`
- 管理端课程 `19` 的课时 `23` 已确认绑定 HLS 资源 `rid=35`
- 前台接口 `GET /api/v1/course/19/hour/23/play` 已确认返回 `play_type=hls`
- HLS 播放地址已确认切到站内 `/api/v1/media/hls/index.m3u8?token=...`
- HLS playlist 已确认被重写为带签名的 `.ts` 分片 URL
- 首个 HLS 分片已确认可返回 `206 Partial Content`，`Content-Type=video/mp2t`
- 前台接口 `GET /api/v1/course/17/hour/21/play` 已确认仍返回 `play_type=mp4`
- 旧 `mp4` 播放地址已确认可返回 `206 Partial Content`
- 管理端上传浮窗已确认可为新上传视频自动创建转码任务 `#9`
- 任务 `#9` 已确认成功转为 `ready`
- 任务 `#9` 详情页已确认展示 `playlist_path=videos/hls/9/index.m3u8`
- 任务 `#9` 详情页已确认展示 `hls_prefix=videos/hls/9/`
- 资源页视频 `admin` 已确认显示 `play_type=HLS`
- 资源页视频 `admin` 已确认显示 `transcode_status=ready`

## 4. 复核结论

当前可以直接进入 Phase 5：管理端 UI 开发，没有阻塞 UI 开发的编译级问题。

当前 Phase 5 主体已经完成，下一步不再是“进入 Phase 5”，而是做 UI 收尾验证与剩余异常态补齐。

需要注意的非阻塞点：

- 当前 `ready` 已表示“本地转码 + OSS 上传 + HLS 导入完成”
- 当前 `playlist_path` / `hls_prefix` 已是 OSS 对象路径语义
- 当前日志先存放在 `transcode_task.logs`，后续如日志量变大，可在 Phase 6 再拆日志表
- 当前 Worker 仍是单线程轮询，不做并发与自动重试
- `importing` 阶段取消窗口很短，纯手工终端 / 断点方式未稳定打中
- 当前尚未完成失败任务后的 OSS 残留清理验证
- 当前 `playedu-admin` 全量构建仍被既有 `src/pages/member/learn.tsx` 语法错误阻塞
- 当前上传浮窗重复打开时会向 `document.body` 追加临时 `div`，关闭时未清理；属于低风险问题，不影响主流程

当前可以确认的 Phase 5 结果：

- 后端任务接口已被管理端页面消费完毕
- 转码任务列表、详情、日志、重试、取消已完成页面接线
- 视频上传浮窗已能在上传成功后自动创建转码任务
- 视频上传浮窗 -> 转码任务详情 -> 资源页 HLS 展示已完成真实链路验证
- 系统配置页已补齐全局“转码配置”入口
- 剩余风险已经从“页面缺失”转移为“构建收尾 + 异常态验证”

## 5. 下一窗口建议直接做的事情

建议下一窗口顺序如下：

1. 先修复 `playedu-admin/src/pages/member/learn.tsx` 现有语法错误，恢复前端全量 build
2. 修复上传浮窗重复打开时临时 `div` 未清理问题
3. 补 `importing` 取消稳定复现
4. 补失败后 OSS 残留清理验证
5. 完成后转入 Phase 6：稳定性与运维补强

## 6. 当前实现口径

建议保持 MVP 口径：

- 继续只支持单码率 HLS
- 继续以任务表中的持久化参数为准
- 继续复用现有 `import-hls` 逻辑，不重造资源入库链路

本阶段代码已经完成的事情：

- 上传源文件到 OSS
- 上传 `index.m3u8`
- 上传 `ts` 分片
- 上传海报或复用现有图片存储逻辑
- 调用或复用 `import-hls`
- 自动写入 `resource`
- 自动写入 `resource_extra`
- 更新资源 `play_type = hls`
- 更新资源 `transcode_status = ready`
- 上传前清理旧 OSS 前缀
- 失败 / 取消后清理 OSS 与资源
- Worker 轮询配置读取缓存

当前阶段先不要做：

- 多码率 HLS
- GPU 转码
- 分布式队列
- 复杂优先级调度
- 管理端大页面改造

## 7. 当前联调结论

当前真实联调与页面接线结论如下：

- 成功链路已通过
- `processing` 阶段取消已通过
- `uploading` 阶段取消已通过
- 重试清理已通过真实任务 `6` 验证
- 课时绑定 HLS 资源已通过
- PC / H5 播放链路已通过接口与资源级验证
- 旧 `mp4` 流程回归已通过
- 管理端转码任务列表 / 详情 / 日志 / 重试 / 取消已完成页面接线
- 视频上传浮窗“转码为 HLS”开关与参数表单已接线
- 系统配置页“转码配置”Tab 已接线
- 管理端上传新视频并自动创建任务 `#9` 已通过
- 任务 `#9` 完成后资源页已显示 HLS 与可播放状态
- `importing` 阶段取消逻辑已存在，但在纯手工联调条件下尚未稳定复现
- 前端完整 build 仍被仓库既有 `member/learn.tsx` 语法错误阻塞
- 下一优先级不再是做新 UI，而是补齐构建验证与异常态收尾

## 8. 下一窗口可直接复用的提示词

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
