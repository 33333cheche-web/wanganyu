# 清单3：可执行追问 + 清单4：下一步

**项目**：SCND_EVLW_ALEFJALL_5_Art | Baseline vs Optimised Network

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
TransportationPolicyCost_Leg1 下降 -12.6%，Transport_cost_Leg1 上升 +1.9%，两字段关系是什么？是否存在重复计算或口径差异？  
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
