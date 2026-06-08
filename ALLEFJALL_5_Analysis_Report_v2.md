# ALLEFJALL 5 Article 网络路径分析报告

**分析日期**: 2026-06-04
**数据文件**: ALLEFJALL 5 article network path.xlsx
**声明**: 未纳入逐行 Excel 复核；未提供原始素材-客户真实资料索引.md 的 Case1 部分；规则模板基于提供的模板文件

---

## 缺口清单

| 缺口项 | 状态 | 影响 |
|--------|------|------|
| 原始素材-客户真实资料索引.md Case1 | ❌ 缺失 | 字段口径未确认，未解释字段标「待补充字段口径」 |
| 优化目标函数说明 | ❌ 缺失 | 无法判断 R01 方向是否合理 |
| 客户决策容忍线 | ❌ 缺失 | R08 无法判定，需客户补充 |
| 参数变化表 | ❌ 缺失 | R05/R10 无法验证 |

---

## 表1：规则扫描

| 规则 ID | 规则类型 | 结论 | 严重程度 | 一句依据 |
|---------|----------|------|----------|----------|
| **R01** | 方向性 | 🟡 信息不足 | 🟡 | 优化目标函数未提供，无法判断总成本上升 8.38% 是否合理；需向 Model owner 确认目标函数（确认前不下"变贵=有问题"的结论） |
| **R02** | 方向性 | 🟡 需要追问 | 🟡 | CDC037 流量不变（1,439.87→1,439.87）但 HandlingCost_CDC 从 1,799→0（推断为模式变化导致 CDC handling 归集方式改变），需确认 cost rate 或归集逻辑是否调整 |
| **R03** | 方向性 | 🟡 需要追问 | 🟡 | 库存水平 TotalStock_Leg1 增加 3%（8,712→8,974），库存持有成本 FlowInvHoldingCost_Leg1 增加 11%（7,758→8,624），变化幅度不成比例，需确认 holding cost rate 是否调整 |
| **R04** | 联动性 | ✅ 满足 | 🟢 | 流量分配不变（总 FlowUnits 49,578.89 完全一致），各 CDC 成本占比变化需结合 R02 逐条确认 |
| **R05** | 联动性 | 🟡 信息不足 | 🟡 | 未提供参数变化表，无法验证 cost component 变化是否由参数差异解释；同类型 cost 在各 CDC 变化幅度差异大（如 Transportation_cost 变化 -7%~+52%） |
| **R06** | 联动性 | ✅ 满足 | 🟢 | 路线总数 160 条不变，各产品流量完全一致（如产品 587524: 5,232.47→5,232.47） |
| **R07** | 边界 | 🔴 高度可疑 | 🔴 | 产品 587524 成本变化 +52.40%（15,508→23,635），产品 20587523 成本变化 +52.35%（13,138→20,015），远超 ±20% 边界；需确认是否有特殊业务原因 |
| **R08** | 边界 | 🟡 需要追问 | 🟡 | 总成本上升 8.38%，客户决策容忍线未提供；若容忍线为 ±5%，则已超线，需优化指标说明 |
| **R09** | 矛盾排除 | 🟡 需要追问 | 🟡 | 成本上升 8.38% 但输入未提供服务水平/碳排/风险等非成本指标；需向 Model owner 确认优化目标与非成本收益（不写"退化"等定性结论） |
| **R10** | 矛盾排除 | 🟡 信息不足 | 🟡 | 未提供参数变化表，无法验证参数变化率与成本变化率是否成比例；HandlingCost_CDC 变化 +60% 与 Transportation 变化 +1.85% 差异巨大，需追问是否有其他因素 |
| **R11** | 矛盾排除 | 🟡 需要追问 | 🟡 | 整网总成本 +8.38%，但 HandlingCost_CDC 分项 +60% 且无说明；需确认该分项变化是否被其他分项抵消（Transportation +1.85%, Inventory +11%） |

---

## 表2：异常与矛盾寄存

| 编号 | 异常描述 | 涉及字段/场景 | 严重程度 | 分类 |
|------|----------|--------------|----------|------|
| A1 | 优化目标函数未提供 | TotalCost 变化 +8.38% | 🟡 | 数据口径 |
| A2 | 产品 587524 成本飙升 52.40% | TotalCost: 15,508→23,635 | 🔴 | 成本拆分 |
| A3 | 产品 20587523 成本飙升 52.35% | TotalCost: 13,138→20,015 | 🔴 | 成本拆分 |
| A4 | HandlingCost_CDC 激增 60% | FlowHandlingCost_CDC_Leg1: 11,941→19,125 | 🔴 | 成本拆分 |
| A5 | 库存持有成本增幅 11% 但库存仅增 3% | FlowInvHoldingCost_Leg1 vs TotalStock_Leg1 | 🟡 | 模型假设 |
| A6 | 多段运输（Leg2）激增 144% | Mode_Leg2 非空: 54→132 | 🟡 | 模型假设 |
| A7 | Leg3 始终未使用 | Mode_Leg3 全为 NaN | 🟡 | 数据口径 |
| A8 | FlowSourcingCost 全为 0 | 所有场景、所有 Leg | 🟡 | 数据口径 |
| A9 | FlowDutyCost 全为 0 | 所有场景、所有 Leg | 🟡 | 数据口径 |
| A10 | MidReceiver 种类减少 | B: [DTT258, DTT068, DTT012, CP332] → O: [DTT258, NaN] | 🟡 | 模型假设 |
| A11 | 参数变化表未提供 | 无法验证 R05/R10 | 🟡 | 数据口径 |
| A12 | 客户决策容忍线未提供 | 无法验证 R08 | 🟡 | 数据口径 |

---

## 清单3：追问（编号）

### 给 Model Owner
1. **Q1-MO**: 本次 Optimised Network 的优化目标函数是什么？（成本最小化 / 服务最大化 / lead time / 风险 / 多目标权衡）→ 复查字段：优化目标函数文档
2. **Q2-MO**: 产品 587524 和 20587523 成本飙升 52% 的根因是什么？是运输模式变化、供应商切换还是参数调整？→ 复查字段：ProductName, Mode_Leg1, SourceName, TotalCost
3. **Q3-MO**: 成本上升 8.38% 对应的非成本收益（服务水平、碳排、风险等）有哪些？→ 复查字段：服务水平指标、碳排指标（未提供）
4. **Q4-MO**: 多段运输（Leg2）增加 144% 的驱动因素是什么？是否与 MidReceiver 策略变化相关？→ 复查字段：Mode_Leg2, MidReceiver

### 给 Data Owner
5. **Q5-DO**: FlowSourcingCost 和 FlowDutyCost 为何全为 0？是数据缺失还是业务上确实无 sourcing/duty 成本？→ 复查字段：FlowSourcingCost_Leg1/2/3, FlowDutyCost_Leg1/2/3
6. **Q6-DO**: Mode_Leg3 全为空的含义——系统是否支持 3 段运输？还是当前业务场景最多 2 段？→ 复查字段：Mode_Leg3
7. **Q7-DO**: 参数变化表（cost rate, transport rate, holding rate 等）能否提供？→ 复查字段：参数变化表
8. **Q8-DO**: Deviating_Price 存在负值（如 -0.0002），是否表示价格偏差或折扣？→ 复查字段：Deviating_Price_Leg1/2/3

### 给 Network Design
9. **Q9-ND**: HandlingCost_CDC 激增 60% 是否与新 CDC 启用或 CDC 费率调整有关？→ 复查字段：FlowHandlingCost_CDC_Leg1, DestinationName, DC_Code
10. **Q10-ND**: MidReceiver 在 Optimised 中种类大幅减少（从 4 种减至 1 种），是网络设计变更还是数据问题？→ 复查字段：MidReceiver, Mode_Leg1
11. **Q11-ND**: 供应商 SUP23073_3（中山）在 Optimised 中占比提升，是否有供应商切换策略？→ 复查字段：SourceName, SupplierName

### 给 Finance
12. **Q12-FI**: 总成本上升 8.38% 是否在预算范围内？优化网络的投资回报周期如何计算？→ 复查字段：TotalCost, 预算文档（未提供）
13. **Q13-FI**: 客户决策容忍线（如 ±X%）是多少？→ 复查字段：决策容忍线（未提供）

---

## 清单4：下一步

| 优先级 | 行动 | 负责人 | 复查字段 |
|--------|------|--------|----------|
| P0 | 确认优化目标函数（成本 / 服务 / lead time / 风险 / 多目标） | Model Owner | 优化目标函数文档 |
| P0 | 解释产品 587524/20587523 成本飙升 52% 的根因 | Model Owner | ProductName, TotalCost, Mode_Leg1, SourceName |
| P1 | 提供参数变化表（cost rate, transport rate, holding rate） | Data Owner | 参数变化表 |
| P1 | 确认客户决策容忍线 | Finance | 决策容忍线 |
| P1 | 验证 HandlingCost_CDC 激增 60% 的合理性 | Network Design | FlowHandlingCost_CDC_Leg1, DestinationName |
| P2 | 补充 FlowSourcingCost 和 FlowDutyCost 口径说明 | Data Owner | FlowSourcingCost_Leg1, FlowDutyCost_Leg1 |
| P2 | 确认 Leg3 未使用是系统限制还是业务选择 | Data Owner | Mode_Leg3 |
| P2 | 评估供应商 SUP23073_3 占比提升的供应风险 | Network Design | SourceName, SupplierName |
| P3 | 建立 Baseline vs Optimised 的自动对比监控 | Data Owner | 全量字段 |
| P3 | 补充原始素材-客户真实资料索引.md Case1 部分 | 全体 | 文档体系 |

---

## 附录：关键数据对比

### 流量守恒
| 指标 | Baseline | Optimised | 变化 |
|------|----------|-----------|------|
| 总 FlowUnits | 49,578.89 | 49,578.89 | 0% |
| 总 FlowCubic | 5,456.75 | 5,456.75 | 0% |
| 路线数 | 160 | 160 | 0% |

### 成本对比
| 成本项 | Baseline | Optimised | 变化率 |
|--------|----------|-----------|--------|
| 总成本 | ¥180,410 | ¥195,522 | **+8.38%** |
| Handling_CDC | ¥11,941 | ¥19,125 | **+60.17%** |
| Transportation | ¥65,007 | ¥66,213 | +1.85% |
| Inventory Holding | ¥7,758 | ¥8,624 | +11.16% |

### 产品级成本变化
| 产品 | Baseline | Optimised | 变化率 | 风险等级 |
|------|----------|-----------|--------|----------|
| 587524 | ¥15,508 | ¥23,635 | **+52.40%** | 🔴 |
| 20587523 | ¥13,138 | ¥20,015 | **+52.35%** | 🔴 |
| 50367459 | ¥11,854 | ¥11,770 | -0.71% | 🟢 |
| 60320225 | ¥43,028 | ¥43,495 | +1.08% | 🟢 |
| 20419983 | ¥96,882 | ¥96,607 | -0.28% | 🟢 |

---

*本报告基于提供的规则模板逐条扫描生成。🔴/🟡 只代表"需人工确认"，不代表模型错误。*
