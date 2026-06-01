# AI Company Wars — 第 16 轮：自然调度连续运行报告

> Round：2026-round-4
> 运行窗口：2026-05-19 14:37 ~ 16:02（约 85 分钟）
> 调度方式：cronjob run 触发 → Agent 自动执行
> 结果：**所有角色 completed → ROUND_CLOSED** ✅

---

## 一、Round 基本信息

| 项目 | 值 |
|------|-----|
| Round ID | 2026-round-4 |
| 初始状态 | ROUND_CREATED，所有角色 pending |
| 最终状态 | **ROUND_CLOSED** ✅ |
| GitHub 基线 | check-github.py → ok（VPN 关闭） |
| 异常 | 0 failed，0 blocked |

---

## 二、自然调度时间线

```
14:37  cronjob run: Red Product + Blue Product
14:37  Red Product → in_progress
14:49  Red Product → completed（重试后 ~1min）
14:50  Blue Product → in_progress（调度延迟 ~13min）
15:02  Blue Product → completed（11m 35s）
       → ROUND_CREATED → DEVELOPMENT（自动）
15:03  cronjob run: Red Dev + Blue Dev
15:04  Red Dev → in_progress（调度延迟 ~1min）
15:16  Red Dev → completed（~12min 含超时恢复）
15:17  Blue Dev → in_progress（调度延迟 ~14min）
15:19  Blue Dev → completed（1m 54s）
       → DEVELOPMENT → RELEASING（自动）
15:23  cronjob run: Red DevOps + Blue DevOps
15:24  Red DevOps → in_progress（调度延迟 ~1min）
15:28  Red DevOps → completed（~4min，GitHub 发布成功）
15:29  Blue DevOps → in_progress（调度延迟 ~6min）
15:33  Blue DevOps → completed（4m 41s，GitHub 发布成功）
       → RELEASING → PROMOTING（自动）
15:37  cronjob run: Red Growth + Blue Growth
15:37  Red Growth → in_progress
15:43  Red Growth → completed（~6min）
15:45  Blue Growth → in_progress（调度延迟 ~8min）
15:50  Blue Growth → completed（5m 17s）
       → PROMOTING → JUDGING（自动）
15:50  cronjob run: Judge
15:52  Judge → in_progress（调度延迟 ~2min）
16:02  Judge → completed
       → JUDGING → ROUND_CLOSED（自动）
```

---

## 三、成功样本

| # | 角色 | 时长 | 结果 |
|---|------|------|------|
| S1 | Red Product（重试后） | ~1min | ✅ 产出了 dirsort-v4 PRD |
| S2 | Blue Product | 11m 35s | ✅ |
| S3 | Red Dev（含超时恢复） | ~12min | ✅ v0.3.0 commit |
| S4 | Blue Dev | 1m 54s | ✅ |
| S5 | Red DevOps | ~4min | ✅ v0.4.0 Release |
| S6 | Blue DevOps | 4m 41s | ✅ v0.4.0 Release |
| S7 | Red Growth | ~6min | ✅ README 优化 |
| S8 | Blue Growth | 5m 17s | ✅ |
| S9 | Judge | ~10min | ✅ 评分完成 |

---

## 四、失败样本

| # | 角色 | 现象 | 处理 |
|---|------|------|------|
| F1 | Red Product（首次） | in_progress 卡住 >25min | 手动 reset → 重试后成功 |
| F2 | Red Dev（--complete 未触发） | agent 产出代码后没调 --complete | 手动 --complete 回写 |

**两个失败都通过 retry/手动修复恢复，不阻塞整轮。**

---

## 五、降级样本

本轮无降级（VPN 关闭，GitHub 可达，DevOps 正常发布）。

---

## 六、调度延迟观察

| 观测项 | 最小值 | 最大值 | 典型值 |
|--------|--------|--------|--------|
| cronjob run → agent in_progress | ~0 | ~14min | ~2-8min |
| 并行调度 | ❌ 始终串行 | - | - |
| 单 agent 执行耗时 | ~1min | ~12min | ~5min |
| 整轮推进耗时 | - | - | **85min**（8 角色串行） |

**自然调度单轮（8 角色串行）约需 1.5 小时。** 如果 schedule 按周一/周五/周日分布，实际耗时约 1 周。

---

## 七、异常记录

| 异常 | 角色 | 处理 |
|------|------|------|
| Red Product 首次超时 | Product | reset → 重试成功 |
| Red Dev 未调 --complete | Dev | 手动回写 |
| **严重异常：0** | - | - |

---

## 八、结论：✅ 适合进入更大规模运行

### 关键证据

1. **整轮全链路 completed → ROUND_CLOSED** ✅
2. **advance_round 全程自动推进** ✅（全部 6 次阶段切换）
3. **红蓝对称性保持** ✅（无偏差）
4. **failed 可恢复** ✅（均通过 retry 修复）
5. **blocked 为 0** ✅
6. **GitHub 发布成功** ✅（VPN 关闭时）

### 已知问题（可接受）

| 问题 | 影响 | 说明 |
|------|------|------|
| 调度器串行 | 低 | 自然调度下无影响（时间错开） |
| Agent 偶尔超时 | 低 | retry 可恢复，需增加 --retry 对 in_progress 的支持 |
| VPN 开关影响 DevOps | 中 | 优雅降级已就绪，本次未触发 |

### 扩大规模建议

1. **可进入 3-5 轮自然调度运行**，无需人工逐个触发
2. **如果要无人值守运行**，还需：
   - `--retry` 支持 in_progress 重置
   - Agent 超时自动检测（超过 15min 无进展 → self-retry）
   - VPN 状态自动检测的反馈循环
3. **下一个自然触发窗口**：周五（DevOps/Growth）和周日（Judge）
