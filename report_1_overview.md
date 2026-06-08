# 报告概览 & 关键数字

**项目**：SCND_EVLW_ALEFJALL_5_Art  
**分析范围**：ALLEFJALL 5 article，Network path + Cost to serve  
**场景对比**：Baseline vs Optimised Network  
**生成时间**：2026-06-05  

> ⚠️ **声明**：基于 openpyxl 全量读取 Excel，未进行人工逐行复核。优化目标函数未在输入中提供，R01/R09 相关判断依赖 Model owner 确认。本报告不代替业务签字，所有 🔴/🟡 标注仅代表"需人工确认"。

---

## 关键数字

| 指标 | Baseline | Optimised | 变化 |
|------|----------|-----------|------|
| TotalCost（Network path） | 180,410.01 | 195,522.15 | +15,112.14（**+8.38%**） |
| FlowUnits | 49,578.89 | 49,578.89 | ✅ 守恒 |
| FlowCubic（m³） | 5,456.75 | 5,456.75 | ✅ 守恒 |
| 路径总数 | 160 | 160 | 不变 |
| Mode/MidReceiver 变化路径数 | — | 149/160 | 93% 路径发生切换 |
| CostUOM | CMTR | CMTR | — |
| DutyCost | 0.00 | 0.00 | ⚠️ 零（待核实） |

### 成本拆分变化（Network path Leg1）

| 成本项 | Baseline | Optimised | 变化率 |
|--------|----------|-----------|--------|
| HandlingCost_CDC_Leg1 | 11,940.67 | 19,125.42 | **+60.2%** |
| TranspPolicyCost_Leg1 | 88,911.12 | 77,714.76 | -12.6% |
| Transport_cost_Leg1 | 65,007.11 | 66,212.57 | +1.9% |
| InvHoldingCost_Leg1 | 7,757.99 | 8,624.06 | +11.2% |

### 成本拆分变化（Cost to serve，选中路径）

| 成本项 | Baseline | Optimised | 变化率 |
|--------|----------|-----------|--------|
| TotalCost | 5,289.30 | 6,420.61 | **+21.4%** |
| InventoryCost | 157.61 | 350.08 | **+122.1%** |
| InTransitInventoryCost | 141.68 | 126.68 | -10.6% |
| TransportCost_SUP | 539.15 | 1,570.25 | **+191.2%** |
| HandlingCost_CDC | 136.86 | 136.86 | **0%（不变）** |
| HandlingCost_DTS | 487.76 | 1,105.16 | **+126.6%** |
