# 表2：异常与矛盾寄存

**项目**：SCND_EVLW_ALEFJALL_5_Art | Baseline vs Optimised Network

| # | 异常描述 | 涉及字段 | 分类 | 严重程度 |
|---|---------|---------|------|---------|
| A1 | CDC085 流量不变，成本 +29.2%（31,647→40,880，绝对增量 +9,232，全网最大） | FlowUnits, TotalCost, HandlingCost_CDC_Leg1 | 成本拆分 | 🔴 |
| A2 | CDC037 成本 -9.4%，但 5 个产品路径全部反转（DD_DTT258 ↔ DTS258_unc/con）；与其他节点路径切换后成本上升方向相反 | Mode_Leg1, MidReceiver, TotalCost @ CDC037 | 模型假设 | 🔴 |
| A3 | 多 STO 成本涨幅超 50%：STO459 +69.1%、STO833 +52.9%、STO164 单 route +91.2%、STO885 +77.7% | TotalCost @ STO459/833/164/885 | 潜在业务风险 | 🔴 |
| A4 | 149/160 路径 Mode 或 MidReceiver 发生变化，但 FlowUnits/FlowCubic 完全守恒 | Mode_Leg1/2/3, MidReceiver, FlowUnits | 模型假设 | 🟡 |
| A5 | CTS TransportCost_SUP +191.2%，Network path Transport_cost_Leg1 仅 +1.9%；同一业务含义成本变化相差 100 倍 | TransportCost_SUP vs Transportation_cost_Leg1 | 数据口径 | 🔴 |
| A6 | CTS InventoryCost +122.1%（157.6→350.1），Network path InvHoldingCost_Leg1 仅 +11.2%；跨 sheet 库存成本幅度差异 10 倍 | InventoryCost, InvHoldingCost_Leg1 | 数据口径 | 🟡 |
| A7 | Network path HandlingCost_CDC_Leg1 +60.2%（11,941→19,125），但 CTS HandlingCost_CDC 完全不变（136.86=136.86） | FlowHandlingCost_CDC_Leg1 vs HandlingCost_CDC | 数据口径 | 🔴 |
| A8 | DutyCost 在两个 sheet 均为 0.00 | DutyCost | 数据口径 | 🟡（待核实）|
| A9 | 产品编码跨 sheet 不一致（587524 vs 00587524_22107），无法直接关联 | ProductName | 数据口径 | 🟡 |
| A10 | TranspPolicyCost_Leg1 -12.6%（88,911→77,715），Transport_cost_Leg1 +1.9%；两运输成本字段一降一升 | TransportationPolicyCost_Leg1, Transportation_cost_Leg1 | 成本拆分 | 🟡 |

---

### 分类汇总

| 分类 | 异常编号 |
|------|---------|
| 🔴 数据口径 | A5、A7 |
| 🟡 数据口径 | A6、A8、A9 |
| 🔴 模型假设 | A2 |
| 🟡 模型假设 | A4 |
| 🔴 成本拆分 | A1 |
| 🟡 成本拆分 | A10 |
| 🔴 潜在业务风险 | A3 |
