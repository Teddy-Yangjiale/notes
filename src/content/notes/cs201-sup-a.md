---
title: "补充篇 A · 作业反推考点速记"
date: 2026-09-26
summary: "从 Written Assignment #1（14 题 / 110 分）反推回课件的考点清单：先给每道题在考什么的映射表，再按「词 → 它对应的那条逻辑」列四组核心词表，配六连接词真值表、12 条等价律、8+4 条推理规则三张必背表，以及英文→公式翻译词典、五种证明方法的触发信号、十个易错判断和 30 条自测。"
tags: ["离散数学", "数理逻辑", "考点速记", "课程笔记"]
series: "cs201"
order: 91
shortTitle: "考点速记 Takeaway"
---

> 从 **Written Assignment #1**（14 题 / 110 分）反推的考点清单。
> 每一节都是「**词 → 它对应的那条逻辑**」，右列就是要背的东西。
> 建议用法：先看 §1 知道每题考什么，然后死磕 §3 §4 §5 三张表，最后用 §8 自测。

---

## 1. 作业题 → 考点映射

一眼看出每道题在考课件的哪一块。**分值越高的考点越要背死。**

| 题 | 分 | 在考什么 | 对应讲义 |
| --- | --- | --- | --- |
| Q1 | 5 | 自然语言 → 公式：充分/必要、but/nevertheless、either-or、iff | §1.9 七种读法 |
| Q2 | 10 | 六个连接词真值表 + 优先级拆式子 + 2ⁿ 行穷举 | §1.4–1.11 |
| Q3 | 15 | **12 条等价律**，且每步要写律名 | §2.4–2.5 |
| Q4 | 10 | 等价的定义 + 用**一个反例**推翻 | §2.3 |
| Q5 | 5 | 不画真值表，靠 ∨/∧ 的结构性质推赋值集合 | §1.5–1.6 + 德摩根 |
| Q6 | 5 | **推理规则**（逆否 + 假言三段论 + 消解） | §4.5 |
| Q7 | 7 | 推理规则（简化/MP/德摩根/析取三段论/MT） | §4.5 |
| Q8 | 5 | ∃ 配 ∧、∀ 配 →、"No…" 的两种写法 | §3.11 黄金法则 |
| Q9 | 8 | 嵌套量词顺序 + 用 =/≠ 表达"唯一""恰好两个" | §3.13–3.14 |
| Q10 | 8 | 量词德摩根 + ¬(p→q) 的展开 + 量词优先级 | §3.10、§3.12、§3.16 |
| Q11 | 10 | UI / UG / EI / EG 四条量词推理规则 | §4.7–4.8 |
| Q12 | 6 | 反证法 + 奇偶代数表示 + 互质矛盾 | §5.5、§5.10 |
| Q13 | 6 | 反证法 + 有理数四则封闭性 | §5.5 |
| Q14 | 10 | **分情况证明**（穷尽 + 每种都证） | §5.6 |

**结论：等价律（15 分）+ 推理规则（12 分）+ 量词翻译与规则（31 分）= 58 分，是绝对重心。**

---

## 2. 核心词表：词 → 逻辑

### 2.1 命题逻辑

| 词（中 / 英） | 对应的逻辑 |
| --- | --- |
| 命题 Proposition | **陈述句**且**真假唯一确定**。不要求你知道真假（`P = NP` 也是命题） |
| 复合命题 Compound | 基本命题 + 连接词拼出来的 |
| 真值表 Truth Table | n 个变量 ⇒ **2ⁿ 行**，必须穷举，按 TT/TF/FT/FF 降序写 |
| 否定 Negation ¬ | 真假对调 |
| 合取 Conjunction ∧ | **全真才真**（只有第一行真） |
| 析取 Disjunction ∨ | **全假才假**（只有末行假）。数学里是**包容或**，两个都真仍为真 |
| 异或 Exclusive Or ⊕ | **恰好一个真**才真 ⟺ 两者**不同**才真 |
| 蕴含 Implication → | **只有「真推假」才假**，其余三种全真 |
| 前提 / 假设 Premise, Hypothesis | `p → q` 里的 p |
| 结论 Conclusion | `p → q` 里的 q |
| 双条件 Biconditional ↔ | 真值**相同**才真。`¬(p⊕q) ≡ p↔q` |
| 逆命题 Converse | `q → p` —— **与原命题不等价** |
| 否命题 Inverse | `¬p → ¬q` —— **与原命题不等价** |
| 逆否命题 Contrapositive | `¬q → ¬p` —— **唯一与原命题等价的那个** |
| 优先级 Precedence | `¬ > ∧ > ∨ > → > ↔`；多个 → **从右往左**结合 |
| 比特 / 比特串 Bit / Bit String | 1=T，0=F；串长可为 0（空串） |
| 按位运算 Bitwise | C++：`~` `&` `\|` `^`，逐位做 |
| 布尔代数 Boolean Algebra | 只取 1/0 的变量；George Boole 创立；数字电路的数学基础 |

### 2.2 逻辑等价

| 词 | 对应的逻辑 |
| --- | --- |
| 恒真式 Tautology | **永远为真** |
| 恒假式 Contradiction | **永远为假** |
| 偶然式 Contingency | 既非恒真也非恒假 |
| 逻辑等价 ≡ | `p ≡ q` ⟺ `p ↔ q` **是恒真式** ⟺ 所有行真值相同 |
| ↔ 与 ≡ 的区别 | `↔` 是**连接词**（造出新命题）；`≡` 是**断言**（说两式恒同） |
| 有用律 Useful law | `p → q ≡ ¬p ∨ q` —— 学名条件-析取等价。**看到 → 第一步就用它** |
| 反例 Counterexample | 推翻等价**只需一行**真值不同 |

### 2.3 谓词逻辑

| 词 | 对应的逻辑 |
| --- | --- |
| 谓词 Predicate `P(x)` | **不是命题**；代入具体值后才是 |
| 常量 Constant | 特定对象（`1`、`SUSTech`、`Lynn`） |
| 变量 Variable | 代表论域中的某个对象（`x, y, z`） |
| 论域 Universe / Domain | 变量可取的**全部值**。换论域会换答案 |
| 真值集 Truth Set | 使 `P(x)` 为真的取值集合，**是论域的子集** |
| 全称量化 **Universal quantification** `∀x P(x)` | 对论域中**所有** x 都真。假 ⟺ **存在一个反例** |
| 全称量词 **Universal quantifier** `∀` | 读作 *"for every x, P(x) is true"* |
| 存在量化 **Existential quantification** `∃x P(x)` | **存在某个** x 使其真。假 ⟺ 对所有 x 都假 |
| 存在量词 **Existential quantifier** `∃` | 读作 *"there is an x such that P(x) is true"* |
| 量词优先级 **Precedence of quantifiers** | `∀/∃` **高于所有**逻辑运算符。`∃xP(x)∨Q(x)` = `(∃xP(x))∨Q(x)` |
| 嵌套量词 **Nested quantifiers** | 多个量词连用 |
| 量词顺序 **Order of quantifiers** | **不同类**换序**改变含义**；**同类**换序**不变** |
| 有限论域展开 Expansion over a finite domain | `∀` = 无限个 ∧；`∃` = 无限个 ∨ |

### 2.4 证明相关

| 词 | 对应的逻辑 |
| --- | --- |
| 公理 / 公设 Axiom / Postulate | 不证自明、直接接受为真的起点 |
| 定理 Theorem | **能被证明**为真的语句 |
| 证明 Proof | 确立定理为真的**有效论证** |
| 引理 Lemma | 为证主定理服务的次要定理 |
| 推论 Corollary | 由定理**直接**得出的语句 |
| 猜想 Conjecture | 被提出、**尚未证明**的语句 |
| 定理的形式 | `p₁ ∧ p₂ ∧ … ∧ pₙ → q`（前提 → 结论） |
| 形式证明 Formal Proof | 每步注明**编号 · 步骤 · 理由**，不许跳步 |
| 非形式证明 Informal Proof | 写给人看的；可跳步但必须保持**一致性**与**可靠性** |
| 构造式 Constructive | 给出具体例子 |
| 非构造式 Nonconstructive | 证明存在但指不出是谁（如"素数无穷多"） |
| 空证明 Vacuous Proof | **p 恒假** ⇒ `p→q` 恒真 |
| 平凡证明 Trivial Proof | **q 恒真** ⇒ `p→q` 恒真 |

---

## 3. 三张必背表

### 3.1 六连接词真值表（背这一张就够）

| p | q | ¬p | p∧q | p∨q | p⊕q | p→q | p↔q |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T | T | F | T | T | F | T | T |
| T | F | F | F | T | T | **F** | F |
| F | T | T | F | T | T | T | F |
| F | F | T | F | F | F | T | T |

> 记：∧ 只有首行真 · ∨ 只有末行假 · ⊕ 中间两行真 · **→ 只有第二行假** · ↔ 首末两行真

### 3.2 12 条逻辑等价律（Q3 每步要写名字）

| 律名 | 内容 |
| --- | --- |
| 同一律 Identity | `p ∧ T ≡ p` · `p ∨ F ≡ p` |
| 支配律 Domination | `p ∨ T ≡ T` · `p ∧ F ≡ F` |
| 幂等律 Idempotent | `p ∨ p ≡ p` · `p ∧ p ≡ p` |
| 交换律 Commutative | `p ∨ q ≡ q ∨ p` · `p ∧ q ≡ q ∧ p` |
| 结合律 Associative | `(p∨q)∨r ≡ p∨(q∨r)` · `(p∧q)∧r ≡ p∧(q∧r)` |
| 分配律 Distributive | `p∧(q∨r) ≡ (p∧q)∨(p∧r)` · `p∨(q∧r) ≡ (p∨q)∧(p∨r)` |
| 德摩根律 De Morgan's | `¬(p∨q) ≡ ¬p∧¬q` · `¬(p∧q) ≡ ¬p∨¬q` |
| 吸收律 Absorption | `p∨(p∧q) ≡ p` · `p∧(p∨q) ≡ p` |
| 双重否定 Double negation | `¬(¬p) ≡ p` |
| 否定律 Negation | `p ∨ ¬p ≡ T` · `p ∧ ¬p ≡ F` |
| 逆否 Contrapositive | `p → q ≡ ¬q → ¬p` |
| 有用律 Useful law | `p → q ≡ ¬p ∨ q` |

**Q3 的固定套路**：`→` 用有用律换掉 → 德摩根把 ¬ 推到最里 → 交换/结合/分配凑出 `p∨¬p` → 否定律变 T → 支配律收尾得 T。

### 3.3 推理规则（Q6/Q7/Q11 要写名字）

**命题部分 · 8 条**

| 规则 | 前提 ⊢ 结论 | 记忆 |
| --- | --- | --- |
| 假言推理 Modus ponens | `p→q`, `p` ⊢ `q` | 肯定前件 |
| 拒取式 Modus tollens | `p→q`, `¬q` ⊢ `¬p` | 否定后件（= 走逆否） |
| 假言三段论 Hypothetical syllogism | `p→q`, `q→r` ⊢ `p→r` | → 的传递性 |
| 析取三段论 Disjunctive syllogism | `p∨q`, `¬p` ⊢ `q` | 二选一排除一个 |
| 附加 Addition | `p` ⊢ `p∨q` | 往结论里塞项 |
| 简化 Simplification | `p∧q` ⊢ `q`（也可得 `p`） | 从前提里拆零件 |
| 合取 Conjunction | `p`, `q` ⊢ `p∧q` | 简化的反向 |
| 消解 Resolution | `¬p∨r`, `p∨q` ⊢ `q∨r` | p 非真即假，两头都通 |

**量词部分 · 4 条**

| 规则 | 前提 ⊢ 结论 | 使用条件 |
| --- | --- | --- |
| 全称实例化<br>**Universal instantiation (UI)** | `∀xP(x)` ⊢ `P(c)` | 把全称规律用到任意一个具体 c 上 |
| 全称概括<br>**Universal generalization (UG)** | `P(c)`（c **任取**）⊢ `∀xP(x)` | 课件原文 *P(c) for an **arbitrary** c*；c 不能带任何特殊假设 |
| 存在实例化<br>**Existential instantiation (EI)** | `∃xP(x)` ⊢ `P(c)`（某个 c） | 课件原文 *P(c) for **some** element c*；**c 必须是全新符号** |
| 存在概括<br>**Existential generalization (EG)** | `P(c)`（某个 c）⊢ `∃xP(x)` | 找到一个例子即可 |

**Q11 的固定套路**：**先 EI 落地 → 再 UI 套用 → 中间用 8 条命题规则推 → 最后 EG/UG 升回去。**
顺序不能反：必须先 EI 拿到常量 a，再 UI 把全称规律用到这个 a 上。

---

## 4. 英文 → 公式 翻译词典

Q1 + Q8 + Q9 共 18 分，全靠这张表。

### 4.1 命题层（Q1）

| 英文 | 公式 |
| --- | --- |
| if p then q / p implies q | `p → q` |
| **p is sufficient for q** | `p → q`（充分条件在**箭尾**） |
| **q is necessary for p** | `p → q`（必要条件在**箭头**） |
| q follows from p | `p → q` |
| q unless ¬p | `p → q`（即 `q ∨ ¬p`） |
| **p only if q** | `p → q` ⚠️ 不是 `q → p` |
| p if q | `q → p` ⚠️ 和 only if 方向相反 |
| p if and only if q / p iff q | `p ↔ q` |
| p is necessary and sufficient for q | `p ↔ q` |
| but / nevertheless / however / although / yet | `∧`（都是"并且"） |
| either … or（数学默认） | `∨` |
| exactly one of p, q | `p ⊕ q` |
| neither p nor q | `¬p ∧ ¬q` |
| not both p and q | `¬(p∧q) ≡ ¬p ∨ ¬q` |

### 4.2 量词层（Q8 / Q9）

| 中文/英文 | 公式 |
| --- | --- |
| **所有 A 都是 B** / All A are B | `∀x (A(x) → B(x))` —— **∀ 配 →** |
| **有的 A 是 B** / Some A is B | `∃x (A(x) ∧ B(x))` —— **∃ 配 ∧** |
| 没有 A 是 B / No A is B | `¬∃x(A(x)∧B(x))` ≡ `∀x(A(x)→¬B(x))` |
| 并非所有 A 都是 B / Not all A are B | `∃x (A(x) ∧ ¬B(x))` |
| 每个人都爱某个人 / Everybody loves somebody | `∀x ∃y L(x,y)` |
| 存在一个被所有人爱的人 / There is someone who is loved by everyone | `∃y ∀x L(x,y)`（比上一条**强**） |
| 只爱自己、不爱别人 / There is someone who loves only himself or herself but no other person | `∃x ( L(x,x) ∧ ∀y (y≠x → ¬L(x,y)) )` |
| **恰好一个** P / There is **exactly one** x such that P(x) | `∃x ( P(x) ∧ ∀y (P(y) → y=x) )` |
| **恰好两个** P / There are **exactly two** x such that P(x) | `∃x∃y ( x≠y ∧ P(x) ∧ P(y) ∧ ∀z (P(z) → (z=x ∨ z=y)) )` |

> **"恰好 k 个"的通用骨架 = 至少 k 个（k 个互不相等且都满足）+ 至多 k 个（任何满足的都必须是这 k 个之一）。**

### 4.3 否定推进（Q10）

前两条的学名是**量词的德摩根律 De Morgan's laws for quantifiers**。

| 原式 | 推到底 |
| --- | --- |
| `¬ ∀x P(x)` | `∃x ¬P(x)` |
| `¬ ∃x P(x)` | `∀x ¬P(x)` |
| `¬ (p → q)` | `p ∧ ¬q` ⚠️ **不是** `¬p → ¬q` |
| `¬ (p ∧ q)` | `¬p ∨ ¬q` |
| `¬ (p ∨ q)` | `¬p ∧ ¬q` |
| `¬ ∀x∃y P(x,y)` | `∃x∀y ¬P(x,y)` |
| `¬ ∃x∀y P(x,y)` | `∀x∃y ¬P(x,y)` |

> **口诀：否定号一路往右穿，穿过一个量词翻一次面（∀↔∃），最后停在谓词前。有几个量词翻几次。**

---

## 5. 五种证明方法：看到什么用哪个

| 方法 | 做法 | **触发信号** |
| --- | --- | --- |
| 直接证明 Direct | 设 p 真，推出 q | 从前提能顺着走下去 |
| 逆否证明 Contrapositive | 改证 `¬q → ¬p` | 前提难用、**结论的否定好用**（如"3n+2 奇 ⇒ n 奇"） |
| 反证法 Contradiction | 设 `p ∧ ¬q`，推出矛盾 | 结论含**无理数 / 不存在 / 无穷多**这类否定或无限断言 |
| 分情况 Cases | 情况**穷尽** + **每种都证** | 前提天然分裂：正负、奇偶、大小比较 |
| 等价性 Equivalence | 拆成 `(p→q) ∧ (q→p)` | 出现 **iff / 当且仅当 / 充要条件** |

**分情况的依据**：`(p₁∨…∨pₙ) → q ≡ (p₁→q) ∧ … ∧ (pₙ→q)`（有用律 → 德摩根 → 分配律 → 有用律）。

### 5.1 量化命题的证明策略（对角线规律）

|  | 证明它真 | 证明它假 |
| --- | --- | --- |
| `∀x P(x)` | **穷尽 exhaustive**（分情况） | 给**一个反例 counterexample** 即可 |
| `∃x P(x)` | 给**一个例子**即可（构造式 **constructive**；也可非构造式 **nonconstructive**） | **穷尽 exhaustive**（反证法） |

> 证 ∀ 和 驳 ∃ 是苦活；驳 ∀ 和 证 ∃ 只要一个例子。先判断自己在哪一格。

### 5.2 数论证明的固定零件（Q12 / Q13）

| 要用的事实 | 写法 |
| --- | --- |
| 偶数 | `n = 2k`（k 为整数） |
| 奇数 | `n = 2k + 1` |
| 有理数 | `m/n`，整数，`n≠0`，且 **gcd(m,n)=1**（最简） |
| 无理数矛盾的落点 | 推出 m、n **都是偶数** ⇒ 与互质矛盾 |
| `m² 偶 ⇒ m 偶` | 逆否：m 奇 ⇒ `m²=2(2t²+2t)+1` 奇 |
| `m³ 偶 ⇒ m 偶` | 逆否：m 奇 ⇒ `m³=2(4t³+6t²+3t)+1` 奇 ⚠️ 立方要单独证 |
| 有理数封闭性 | 加减乘、除以非零有理数，结果仍是有理数 |
| 两有理数间插无理数 | 取 `x = a + (b−a)/√2`，因 `0 < 1/√2 < 1` 故 `a<x<b` |

---

## 6. 十个最容易翻车的判断

| # | 错的直觉 | 正确 |
| --- | --- | --- |
| 1 | "p only if q" 译成 `q→p` | 是 `p→q` |
| 2 | 充分/必要搞反 | **箭尾充分，箭头必要** |
| 3 | 逆命题 `q→p` 与原命题等价 | 只有**逆否** `¬q→¬p` 等价 |
| 4 | `¬(p→q)` = `¬p→¬q` | = `p ∧ ¬q` |
| 5 | `→` 可以随便结合 | **不满足结合律**：`(p→q)→r ≢ p→(q→r)`（反例 p=F,r=F） |
| 6 | `p⊕q` = `¬p∨¬q` | 只在 **FF 行**不同（⊕ 为 F，后者为 T） |
| 7 | 全称句写成 `∀x(A∧B)` | 必须 `∀x(A→B)`，否则变成"人人都是 A" |
| 8 | 存在句写成 `∃x(A→B)` | 必须 `∃x(A∧B)`，否则被**空真**钻空子 |
| 9 | `∃xP(x)∨Q(x)` 里量词管到底 | 量词**只管紧跟的那个谓词**，要管住全式必须加括号 |
| 10 | EI 的常量随便取名 / UG 的 c 带假设 | EI 必须**全新符号**；UG 的 c 必须**任取无假设** |

---

## 7. 课件里有、但这次作业没考的

考试可能补上，优先级低于上面，但别完全空白：

| 考点 | 要点 |
| --- | --- |
| 按位运算 | T/F ↔ 1/0，逐位做 `~ & \| ^`；`1011 0011 ∨ 0110 1010 = 1111 1011` |
| 布尔代数 | George Boole（1815–1864）创立，独立于 Leibniz；数字电路的数学基础 |
| 逻辑的应用 | 逻辑电路、布尔搜索（and/or/not）、专家系统、Lean 定理证明器 |
| 吸收律 / 幂等律 | 12 条律里作业没直接用到的两条，仍要背 |
| 恒真/恒假/偶然式的判别 | Q3 只考了恒真式，恒假与偶然式的定义也要会说 |
| 数学归纳法 | 课件说后续讲；空证明/平凡证明常出现在归纳的**基础步骤** |

---

## 8. 自测（盖住右列）

| 提问 | 答案 |
| --- | --- |
| `p → q` 什么时候假？ | 只有 p 真 q 假 |
| 与 `p → q` 等价的三种写法 | `¬p∨q`、`¬q→¬p`、"q unless ¬p" |
| "q is necessary for p" | `p → q` |
| "p only if q" | `p → q` |
| 恒真式的定义 | 所有赋值下都为真 |
| `p ≡ q` 的定义 | `p ↔ q` 是恒真式 |
| 德摩根两条 | `¬(p∨q)≡¬p∧¬q`，`¬(p∧q)≡¬p∨¬q` |
| 有用律 | `p→q ≡ ¬p∨q` |
| 推翻一个等价要几行？ | 一行（一个反例） |
| Modus tollens | `p→q`, `¬q` ⊢ `¬p` |
| 消解 Resolution | `¬p∨r`, `p∨q` ⊢ `q∨r` |
| 「所有 A 都是 B」 | `∀x(A(x)→B(x))` |
| 「有的 A 是 B」 | `∃x(A(x)∧B(x))` |
| `¬∀xP(x)` | `∃x¬P(x)` |
| `¬(p→q)` | `p ∧ ¬q` |
| `∀x∃y` 与 `∃y∀x` 哪个强？ | `∃y∀x` 强（它能推出前者） |
| 量词优先级 | 高于 `¬ ∧ ∨ → ↔` 全部 |
| EI 的限制 | 引入的常量必须是全新符号 |
| UG 的限制 | c 必须是任取的、不带特殊假设 |
| 四条量词规则的使用顺序 | 先 EI，再 UI，推完再 EG/UG |
| UI / UG / EI / EG 的英文全称 | Universal instantiation / Universal generalization / Existential instantiation / Existential generalization |
| 全称量化 / 存在量化 的英文 | Universal quantification / Existential quantification |
| 「量词的德摩根律」英文 | De Morgan's laws for quantifiers |
| 证 `∀x P(x)` 为假 | 给一个反例 |
| 证 `∃x P(x)` 为真 | 给一个例子 |
| 空证明 / 平凡证明 | p 恒假 / q 恒真 |
| 看到 "iff" 要做什么 | 证两个方向 |
| 反证法证 √2 无理的矛盾落点 | m、n 都是偶数，与 gcd=1 矛盾 |
| 分情况证明的两个必要条件 | 情况穷尽 + 每种都真的证一遍 |
| 引理 vs 推论 | 引理为主定理服务；推论由定理直接得出 |

---

*配套完整讲义见本专栏的「Chapter 2：逻辑与证明」。*
