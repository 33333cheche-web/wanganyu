# SCND_EVLW_ALEFJALL_5_Art 模型输出合理性检查报告

**项目**：SCND_EVLW_ALEFJALL_5_Art  
**分析范围**：ALLEFJALL 5 article，Network path + Cost to serve  
**场景对比**：Baseline vs Optimised Network  
**生成时间**：2026-06-05  

> ⚠️ **声明**：基于 openpyxl 全量读取 Excel，未进行人工逐行复核。优化目标函数未在输入中提供，R01/R09 相关判断依赖 Model owner 确认。本报告不代替业务签字，所有 🔴/🟡 标注仅代表"需人工确认"。

---

## 关键数字

| 指标 | Baseline | Optimised | 变化 |
|------|----------|-----------|------|
| TotalCost（Network path） | 180,410.01 | 195,522.15 | +15,112.14（+8.38%） |
| FlowUnits | 49,578.89 | 49,578.89 | **守恒** |
| FlowCubic（m³） | 5,456.75 | 5,456.75 | **守恒** |
| 路径数 | 160 | 160 | 不变 |
| Mode/MidReceiver 变化路径数 | — | 149/160 | 93% 路径发生切换 |
| CostUOM | CMTR | CMTR | — |
| DutyCost | 0.00 | 0.00 | 零（待核实） |

---

## 表1：规则扫描（R01–R11）

| 规则 ID | 规则名称 | 规则类型 | 结论 | 严重程度 | 一句依据 |
|---------|---------|------|---------|---------|---------|
| R01 | 总成本变化方向应与优化目标函数一致 | 方向性 | 信息不足 | 🟡 | Optimised TotalCost +8.38%，优化目标函数未提供，无法判断方向是否合理 |
| R02 | CDC 成本应与流量变化联动 | 方向性 | 疑似违反 | 🔴 | CDC085 FlowUnits 不变，成本 +29.2%（31,647→40,880）；需确认 cost rate 是否调整 |
| R03 | 库存持有成本应与库存水平联动 | 方向性 | 疑似违反 | 🟡 | Network path InvHoldingCost_Leg1 +11.2%；CTS InventoryCost +122.1%，两 sheet 幅度严重不一致 |
| R04 | 流量不变时各 CDC 成本分布应稳定 | 联动性 | 疑似违反 | 🔴 | STO459 +69.1%，STO833 +52.9%，CDC085 +29.2%，但全网 FlowUnits 守恒 |
| R05 | Cost to serve 变化应与模型参数调整一致 | 联动性 | 疑似违反 | 🟡 | TransportCost_SUP +191.2%、HandlingCost_DTS +126.6%，但 HandlingCost_CDC 不变（0%），同类成本变化幅度极不一致 |
| R06 | 网络结构不变时路线数和流量应一致 | 联动性 | 满足（部分） | 🟡 | 路线数 160=160，FlowUnits/FlowCubic 守恒；但 149/160 路径 Mode 或 MidReceiver 发生变化 |
| R07 | 单个 CDC 成本变化幅度不应过大 | 边界 | 疑似违反 | 🔴/🟡 | STO459 +69.1%、STO833 +52.9%（🔴）；CDC085 +29.2%、STO624 +42.4%（🟡）；均超 ±20% 参考线 |
| R08 | 成本增幅超过客户决策容忍线时需有优化指标说明 | 边界 | 信息不足 | 🟡 | 整网 +8.38%，客户决策容忍线未提供；需客户确认阈值再定级（与 R01 同源） |
| R09 | 成本上升时应能找到对应的优化指标改善 | 矛盾排除 | 信息不足 | 🟡 | 输入未提供服务水平/lead time/碳排等非成本指标，无法判断成本上升是否有收益对冲 |
| R10 | 参数变化不能解释所有异常 | 矛盾排除 | 疑似违反 | 🟡 | 149/160 路径 Mode 切换，但运输成本整体仅 +1.9%；部分路径成本涨幅 70–91%，与参数均匀调整预期不符 |
| R11 | 整网汇总与各节点变化不应完全矛盾 | 矛盾排除 | 疑似违反 | 🟡 | 整网 +8.38%，但 CDC037 -9.4%、CDC085 +29.2%；总体方向掩盖节点级别的反向变化 |

---

## 表2：异常与矛盾寄存

| # | 异常描述 | 涉及字段 | 分类 | 严重程度 |
|---|---------|---------|------|---------|
| A1 | CDC085 流量不变，成本 +29.2%（绝对增量 +9,232，全网最大） | FlowUnits, TotalCost, HandlingCost_CDC_Leg1 | 成本拆分 | 🔴 |
| A2 | CDC037 成本 -9.4%，但 5 个产品路径全部反转（DD_DTT258 ↔ DTS258_unc/con）；与其他节点路径切换后成本上升方向相反 | Mode_Leg1, MidReceiver, TotalCost @ CDC037 | 模型假设 | 🔴 |
| A3 | STO459 +69.1%，STO833 +52.9%，STO164 单 route +91.2%，STO885 +77.7%；多 STO 超 50% 涨幅 | TotalCost @ STO459/833/164/885 | 潜在业务风险 | 🔴 |
| A4 | 149/160 路径 Mode 或 MidReceiver 发生变化，但 FlowUnits/FlowCubic 完全守恒 | Mode_Leg1/2/3, MidReceiver, FlowUnits | 模型假设 | 🟡 |
| A5 | CTS TransportCost_SUP +191.2%，但 Network path Transport_cost_Leg1 仅 +1.9%；同一业务含义成本变化幅度相差 100 倍 | TransportCost_SUP vs Transportation_cost_Leg1 | 数据口径 | 🔴 |
| A6 | CTS InventoryCost +122.1%（157.6→350.1），Network path InvHoldingCost_Leg1 仅 +11.2%；跨 sheet 库存成本变化幅度差异 10 倍 | InventoryCost, InvHoldingCost_Leg1 | 数据口径 | 🟡 |
| A7 | Network path HandlingCost_CDC_Leg1 +60.2%（11,941→19,125），但 CTS HandlingCost_CDC 完全不变（136.86=136.86） | FlowHandlingCost_CDC_Leg1 vs HandlingCost_CDC | 数据口径 | 🔴 |
| A8 | DutyCost 在两个 sheet 均为 0.00 | DutyCost | 数据口径 | 🟡（待核实） |
| A9 | 产品编码跨 sheet 不一致（587524 vs 00587524_22107），无法直接关联 | ProductName | 数据口径 | 🟡 |
| A10 | TranspPolicyCost_Leg1 -12.6%（88,911→77,715），但 Transport_cost_Leg1 +1.9%；两运输成本字段一降一升 | TransportationPolicyCost_Leg1, Transportation_cost_Leg1 | 成本拆分 | 🟡 |

---

## 清单3：可执行追问

**Q1 → Model owner**  
优化目标函数是什么？单目标最小化总成本，还是多目标（服务/lead time/碳排/约束满足）？请提供目标函数说明，否则无法判断 +8.38% 总成本是否合理。  
（关联字段：TotalCost；规则 R01/R09）

**Q2 → Model owner**  
CDC037 的路径切换逻辑：5 个产品的 Mode_Leg1 和 MidReceiver 在 Optimised 中全部反转，但节点成本 -9.4%，与其他节点路径切换后成本上升方向相反。是约束驱动还是成本参数驱动？  
（关联字段：Mode_Leg1, MidReceiver, TotalCost @ CDC037）

**Q3 → Model owner**  
149/160 条路径发生 Mode 或 MidReceiver 变化。本次优化是"参数变化场景"还是"网络再优化场景"？如为参数变化场景，路径切换的触发机制是什么？  
（关联字段：Mode_Leg1/2/3, MidReceiver）

**Q4 → Finance / Model owner**  
Network path 的 TransportationPolicyCost_Leg1 下降 -12.6%，Transport_cost_Leg1 上升 +1.9%，两字段关系是什么？是否存在重复计算或口径差异？  
（关联字段：TransportationPolicyCost_Leg1, Transportation_cost_Leg1）

**Q5 → Data owner**  
Network path HandlingCost_CDC_Leg1 +60.2%，但 CTS HandlingCost_CDC 完全不变（0%）。请确认两个 sheet 的 CDC handling 成本口径是否一致，是否使用相同 rate 版本。  
（关联字段：FlowHandlingCost_CDC_Leg1 vs HandlingCost_CDC）

**Q6 → Data owner**  
CTS TransportCost_SUP +191.2%，Network path Transport_cost_Leg1 仅 +1.9%。两个 sheet 的运输成本定义和 CostUOM 是否一致？请提供字段映射关系。  
（关联字段：TransportCost_SUP_DTS\STO\CDC, Transportation_cost_Leg1, CostUOM）

**Q7 → Data owner / Master data owner**  
产品编码在两个 sheet 存在补零和供应源后缀差异（587524 vs 00587524_22107）。请提供正式映射表，否则跨 sheet 成本分析可能错配。  
（关联字段：ProductName）

**Q8 → Data owner**  
DutyCost 在两个 sheet 均为 0.00。请确认是真实关税为零（豁免/FTA），还是字段未填充。  
（关联字段：DutyCost）

**Q9 → Finance / Network design**  
CDC085 流量完全不变，但成本 +29.2%（绝对增量 +9,232，全网最大）。请确认是 handling rate 调整、cost rate 版本更新，还是其他因素。  
（关联字段：FlowUnits, TotalCost, HandlingCost_CDC_Leg1 @ CDC085）

**Q10 → Network design**  
STO459、STO833、STO164 等节点成本涨幅 50–91%。是否超过客户决策容忍线？是否影响对这些 STO 的服务承诺或运营可行性？  
（关联字段：TotalCost @ STO459/STO833/STO164）

---

## 清单4：下一步（≤10 条）

1. **【最高优先】向 Model owner 确认优化目标函数**——在目标函数明确前，所有"成本上升=问题"的判断均不成立（R01/R09）。
2. **向 Data owner 索取两个 sheet 字段口径对照表**，重点澄清 CDC handling 成本（A7）和运输成本（A5）的跨 sheet 口径差异。
3. **向 Data owner 索取产品编码映射表**（A9），补全跨 sheet 产品级别正式对比能力。
4. **重点追问 CDC037 路径反转逻辑**（A2）——唯一成本下降的大节点，且路径切换方向与其他节点完全相反，需 Model owner 提供运行日志或约束说明。
5. **向 Finance 确认 CDC085 成本 +29.2% 的 rate 版本**（A1）——全网绝对增量最大节点，需锁定是 rate 调整还是模型异常。
6. **澄清"参数变化场景"定义**（A4）——如为参数变化场景，为何 149/160 路径 Mode/MidReceiver 均变化？需 Model owner 区分"参数驱动的路径切换"与"网络再优化"。
7. **向 Finance 确认 TransportationPolicyCost 与 Transportation_cost 关系**（A10），排除重复计算风险。
8. **确认 DutyCost 全零是否合理**（A8），补充字段填充说明或 FTA 依据。
9. **向客户确认决策容忍线**，替换 R07/R08 中的 ±20% 占位阈值，再对 STO459/STO833 等高涨幅节点重新定级。
10. **上述 Q1–Q9 回复后重跑本次扫描**，用正式口径替换"待核实"标注，形成可汇报版本。

---

*报告生成：WangAnyu | 基于 ALLEFJALL_5_article_network_path.xlsx + 字段口径文档 + 规则模板 R01–R11*
