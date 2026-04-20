# Safety Failure and Abnormal Output Risks in Gemini 3 Series Under Long-Sequence Special-Character Injection  
# Gemini 3 系列模型在长序列特殊字符注入下导致的安全保护机制失效与异常响应风险研究

[English](#english-version) | [中文](#中文版本)

---

## English Version

### A Security Report on Long-Sequence Character Injection Causing Safety Failure and Abnormal Outputs in Gemini 3 Series

---

### Overview

This project documents a class of security risks observed in the Gemini 3 series: when an attacker constructs an extremely long, low-semantic-density sequence of special characters and embeds a sensitive or disallowed instruction inside it, the model’s refusal behavior, content-safety logic, and output stability may all degrade significantly.

Our experiments suggest that this attack does not rely on sophisticated prompt engineering. Instead, it can be triggered through extremely simple character repetition. In some cases, the model not only fails to reliably block high-risk requests, but also produces abnormal outputs unrelated to the prompt, fragmented structured responses, or even enters a multi-turn “open” failure state.

We believe this is not merely a prompt trick. It points to a system-level safety concern: when the model can no longer stably identify the semantic center of an instruction under long noisy context, existing alignment and detection pipelines may stop functioning as intended.

---

### 1. Core Issue: Safety Degradation Under a Bidirectional “Sandwich Attack”

Recent testing revealed a more stable attack pattern than simple suffix-noise injection. Instead of appending noise only after the target instruction, the attacker injects large amounts of repeated characters both before and after the core instruction, forming a “sandwich” structure.

#### Attack Vector Structure

- **Prefix:** approximately 2500 repetitions of `U+035E`
- **Core:** an explicit or disguised high-risk instruction
- **Suffix:** another approximately 2500 repetitions of `U+035E`

That is:

```text
[large repeated noise sequence] + [core high-risk instruction] + [large repeated noise sequence]
````

#### Observed Effects

Under this structure, the model appears less capable of locating the true semantic target within an extremely long redundant token sequence, which can lead to:

* reduced refusal-trigger reliability
* weakened contextual constraint handling
* degraded output stability
* in some cases, abnormal text completely unrelated to the current task

In other words, safety alignment in this setting does not behave like a stable hard boundary. It behaves more like a fragile layer that can be diluted or bypassed by long-context noise.

---

### 2. Key Risk Cases

The following cases illustrate the directions in which failure may occur under this attack pattern. To avoid distributing dangerous content, only the risk category and observed behavior are retained here; full reusable malicious prompts are intentionally omitted.

#### Case A: Explicit Sexual Content Request Penetration

**Risk category:** explicit adult sexual-content generation request

**Observed behavior:**
With bidirectional noise injection of around 2500 characters on both sides, the model did not reliably trigger refusal behavior against highly explicit requests that clearly violate content-safety rules. In some tests, the model directly produced content that should normally have been blocked.

**Interpretation:**
This suggests that, under high-noise long-sequence conditions, the refusal pipeline for explicit policy-violating sexual content can be weakened or bypassed.

---

#### Case B: Disguised Controlled-Chemical Request Penetration

**Risk category:** information related to controlled-substance preparation, reagent sourcing, detection evasion, or concealment

**Observed behavior:**
When the request was framed as “historical discussion,” “forum research,” or “technical background understanding,” and combined with long noisy character sequences, the model’s risk recognition degraded further. In some tests, the model produced content related to preparation pathways, reagent acquisition, operational setup, or concealment suggestions.

**Interpretation:**
These results suggest that once malicious intent is semantically disguised and then combined with long-sequence perturbation, the model may fail to apply the expected high-risk detection and refusal strategy.

---

### 3. Abnormal Responses: Semantic Drift, Pseudo-Random Output, and Possible Cross-Request Contamination

Beyond deterministic jailbreak-like behavior, a more common and in some ways more concerning phenomenon was the model entering an abnormal predictive state.

#### Main Symptoms

* **semantic drift:** outputting ordinary conversational text unrelated to the current prompt
* **fragmented structured leakage-like responses:** returning incomplete JSON, template fragments, or broken structured outputs
* **prediction shift:** generating text that is not fully random, yet clearly detached from the semantic content of the input

These outputs do not look like ordinary refusal failures followed by nonsense. They look more like the model entering an unstable inference state under extreme long-context pressure.

#### Risk Assessment

From the observed symptoms, this behavior **may** be related to:

* misalignment in the context-processing chain under long noisy input
* abnormal offset in lower-level KV cache or contextual reference mechanisms
* fragment-level contamination or erroneous reference in distributed inference environments

It must be emphasized that **“cross-request contamination” is currently a risk inference based on output characteristics, not a confirmed conclusion from lower-level forensic evidence.**
However, if this inference proves correct, the issue would no longer be limited to content safety. It would escalate into a possible **privacy leakage and request-isolation failure** problem.

Put differently, some abnormal fragments may not be purely random generation, but rather incorrect bleed-through from residual content belonging to other requests in a parallel environment. That possibility alone is already a serious security alarm.

---

### 4. “Open-State” Collapse: Continued Loss of Control After the First Successful Penetration

A more severe pattern was also observed: once the attack succeeded once, later responses in the same context could remain in a persistently degraded state.

#### Observed Behavior

* continued relaxation toward subsequent high-risk requests
* lack of stable safety review or self-correction
* outputs shifting toward permissive generation rather than isolated one-off failure

#### Possible Explanation

A plausible explanation is that once the attack succeeds, a large portion of the model’s effective context window is already occupied by high-entropy noise, making it difficult for later decoding steps to recover system constraints, policy rules, or safety-correction signals. Once the first gate is breached, downstream defenses may fail to reassert control, leaving the model in a persistently abnormal open state within the same conversation context.

This suggests that safety mechanisms may not be continuously and robustly enforced token by token. Under certain context pressures, they may fail at a broader systems level.

---

### 5. System Design Critique: Speed Optimization Should Not Come at the Cost of Safety Degradation

This report does not avoid a clear judgment: if a model’s safety can be significantly weakened by such a low-cost, low-skill long-sequence noise attack, then its safety pipeline likely reflects engineering compromises serious enough to merit public scrutiny.

More bluntly, there is reason to suspect that some “fast models,” in pursuit of lower latency and shorter time-to-first-token, may compress or simplify safety checks that should have remained more robust. Possible manifestations include, but are not limited to:

* **weakened front-end input screening:** simplified risk inspection to reduce TTFT
* **insufficient back-end rechecking:** real-time safety classifiers lacking sufficient compute budget under long-sequence conditions
* **insufficient architectural fault tolerance:** failure to trigger fallback, truncation, refusal, or isolation when context becomes abnormally inflated

To be clear, this is not an objection to performance optimization itself. It is a statement of baseline principle:
**speed may be a product advantage, but it cannot be an excuse for weakening safety guarantees.**

For any large-model platform, if “fast” is achieved at the cost of degraded content safety, request isolation, or fault tolerance, then that optimization direction deserves open criticism.

---

### 6. Minimal PoC Structure

For safety reasons, only a structural PoC is retained here. It demonstrates the attack form without including a directly reusable high-risk payload.

```python
import google.generativeai as genai

# Example only; affected model version depends on actual test environment
model = genai.GenerativeModel("gemini-3-pro-preview")

noise = "\u035E" * 2500
hidden_intent = "[REDACTED_HIGH_RISK_INSTRUCTION]"
payload = f"{noise}\n{hidden_intent}\n{noise}"

try:
    response = model.generate_content(payload)
    print(response.text)
except Exception as e:
    print(f"System exception: {e}")
```

#### Observed Output Types

* normal refusal
* direct generation of policy-violating content
* unrelated semantic drift
* incomplete JSON / structured fragments
* clearly abnormal and hard-to-explain corrupted output

---

### 7. Severity and Impact Surface

#### Potential Impact

* **content-safety failure:** explicit policy-violating content bypasses blocking
* **high-risk knowledge disclosure:** generation of dangerous chemical or evasion-related information
* **output-stability collapse:** model enters an unintended response state
* **potential privacy risk:** if cross-request contamination exists, user data isolation may fail
* **persistent multi-turn degradation:** after one successful penetration, subsequent turns remain unsafe

#### Severity Assessment

If the above behavior can be reproduced consistently in a stable environment, it should be treated as:

* at minimum, a **high-severity security defect**
* potentially a **critical system-level vulnerability** if cross-request contamination is further confirmed

---

### 8. Research Position

The purpose of this repository is not to distribute jailbreak techniques, nor to encourage abusive testing against public services. Our position is straightforward:

1. document reproducible safety-failure phenomena
2. push vendors to confront system-level risks introduced by abnormal long-sequence inputs
3. encourage stronger improvements in input robustness, defense pipelines, and isolation mechanisms

From a research perspective, the most disappointing aspect is not merely that “the model makes mistakes,” but that it exposes a deeper truth: in the pursuit of speed and performance, safety may have been treated as secondary.

That point may be expressed politely, but it should not be blurred.

---

### 9. Responsible Disclosure Statement

This project is intended only for security research, archiving, and risk discussion. To avoid spreading dangerous capability:

* full malicious payloads that directly reproduce illegal content generation are not disclosed
* no concrete operational details are provided for controlled chemicals, weapons, or law-evasion tactics
* no unauthorized attack testing against public online services is encouraged

If you are a model vendor or a security-team member and would like to validate these findings, testing should be conducted only in isolated, authorized, and compliant environments, and formal vulnerability-disclosure channels should be used wherever possible.

## Tested Surfaces / 测试覆盖面说明

Testing indicates that the issue is **not limited to a single access surface**. The behavior was reproducible in both the **web interface** and the **API/SDK calling path**.

At the time of testing, the affected model surfaces included:

- `gemini-3-flash`
- `gemini-3-flash-preview`
- `gemini-3.1-pro`
- `gemini-3.1-pro-preview`

This report therefore does **not** describe an isolated frontend artifact. The observed safety degradation and abnormal-response behavior appeared across both consumer-facing and programmatic access paths.

## Screenshots

![Figure 1](./assets/1.png)
![Figure 2](./assets/2.png)
![Figure 3](./assets/3.png)
![Figure 4](./assets/4.png)
![Figure 5](./assets/5.png)
![Figure 6](./assets/6.png)
![Figure 7](./assets/7.png)
![Figure 8](./assets/8.png)
![Figure 9](./assets/9.png)
![Figure 10](./assets/10.png)
![Figure 11](./assets/11.png)
![Figure 12](./assets/12.png)
![Figure 13](./assets/13.png)

---

## 中文版本

### Gemini 3 系列模型在长序列特殊字符注入下导致的安全保护机制失效与异常响应风险研究

---

### 简介

本项目记录了一类在 Gemini 3 系列模型上观察到的安全风险：通过构造超长、低语义密度的特殊字符序列，并将敏感或违规指令夹置其中，模型的安全拒绝机制、内容审查逻辑以及输出稳定性可能出现明显退化。

实验表明，这类攻击并不依赖复杂的提示工程，而是可以由极其简单的字符堆砌触发。在部分情况下，模型不仅会失去对高风险请求的正常拦截能力，还会出现与当前请求不相关的异常文本输出、结构化片段泄露式响应，甚至表现出连续多轮的“开放式”失控状态。

我们认为，这不是单纯的提示词技巧问题，而是一个值得严肃对待的系统级安全隐患：当模型在长序列噪声中无法稳定定位语义中心时，既有安全对齐和检测链路可能出现失效。

---

### 1. 核心问题：双向夹击（Sandwich Attack）导致的安全退化

最新实验中观察到一种更稳定的攻击模式：不是单纯在提示后附加噪声，而是在目标指令的前后同时注入大量重复字符，形成“夹击”结构。

#### 攻击向量结构

* **前缀（Prefix）**：重复 `U+035E` 字符约 2500 次
* **核心指令（Core）**：显性或伪装后的高风险请求
* **后缀（Suffix）**：再次重复 `U+035E` 字符约 2500 次

即：

```text
[大量重复噪声字符] + [核心高风险指令] + [大量重复噪声字符]
```

#### 观察结果

在这种结构下，模型在超长冗余 token 序列中定位真正语义目标的能力出现下降，进而导致：

* 安全拒绝机制触发概率降低
* 前后文约束能力变弱
* 输出稳定性下降
* 部分情况下出现完全脱离当前任务的异常文本

换言之，安全对齐在该场景下并未表现为稳定、可依赖的“硬边界”，而更像是会被长序列噪声稀释或绕开的脆弱层。

---

### 2. 关键风险案例

以下案例用于说明该攻击模式下模型可能出现的失效方向。为避免直接扩散危险内容，以下仅保留风险类别与现象说明，不再完整展示可直接复用的恶意请求文本。

#### 案例 A：显性色情内容生成请求穿透

**风险类别：** 明确的成人露骨内容生成请求

**实验现象：**
在双向 2500 字符噪声夹击下，模型对高度直白、明显违反内容安全准则的色情描述请求，未能稳定触发拒绝机制。在部分测试中，模型直接输出了本应被拦截的露骨内容。

**说明：**
这表明在高噪声长序列条件下，面向显性违规内容的 refusal pipeline 存在被削弱或绕过的风险。

---

#### 案例 B：伪装后的受控化学品相关请求穿透

**风险类别：** 受控物质制备、试剂来源、规避检测与隐匿操作相关信息

**实验现象：**
当请求被包装成“历史讨论”“论坛研究”“技术背景了解”等表面无害语境，并与长序列字符噪声组合时，模型的风险识别能力进一步下降。在部分测试中，模型会输出与受控物质制备路径、试剂获取方式、场景搭建和隐匿建议相关的内容。

**说明：**
这类结果说明：一旦违规意图经过语义伪装，并叠加长序列扰动，模型可能放弃应有的高风险识别和拒答策略。

---

### 3. 异常响应：语义漂移、伪随机输出与潜在跨请求污染风险

除确定性的越狱现象外，实验中更常见、也更值得警惕的问题，是模型进入一种异常预测状态。

#### 主要表现

* **语义漂移**：输出与当前 prompt 无关的正常对话片段
* **结构化碎片泄露式响应**：返回疑似未完成的 JSON、模板片段或不完整结构化内容
* **预测偏移**：回答呈现非完全随机、但明显脱离当前输入语义的异常文本

这些输出并不是“正常拒答失败后乱说”，而更像是模型在高压长上下文条件下进入了一种不稳定的推理状态。

#### 风险判断

从现象上看，这种行为**疑似**与以下问题有关：

* 上下文处理链在超长噪声下出现错位
* 底层 KV Cache 或相关上下文引用机制发生异常偏移
* 分布式推理环境中出现片段级污染或错误引用

需要强调：**“跨请求污染”目前是基于输出特征所作的风险推断，而不是已完成底层取证的定论。**
但如果这一推断成立，那么问题就不再只是内容安全，而上升为潜在的**隐私泄露与请求隔离失败**。

换句话说，模型返回的异常片段有可能并非“随机生成”，而是来自并行环境中其他请求残留内容的错误混入。这一可能性本身，就足以构成严重安全警报。

---

### 4. “开放式”崩溃：一次成功穿透后的持续失控倾向

实验中还观察到一个更严重的现象：当攻击第一次成功触发后，后续响应可能进入持续失控状态。

#### 具体表现

* 对后续高风险请求继续放宽限制
* 不再进行稳定的安全回看与修正
* 输出趋向“放开式”生成，而不是阶段性误判

#### 可能原因

一个合理解释是：在成功触发后，模型的有效上下文空间已被大量高熵字符占据，导致其后续生成阶段难以再有效回溯系统约束、策略规则或安全校正信号。
一旦第一道闸门被冲破，后续防御并未有效补位，模型便可能在同一上下文中持续处于异常开放状态。

这类行为意味着，安全机制并不是“逐 token 持续稳定接管”的，而可能在某些上下文压力下出现整体性失效。

---

### 5. 对系统设计的批评：速度优化不应以安全退化为代价

本研究不回避一个判断：如果一个模型能够被如此低成本、低技术门槛的长序列噪声攻击显著削弱安全性，那么这说明其安全链路在工程上存在值得追责的妥协。

更直白地说，我们有理由怀疑，部分“快速模型”在追求极低延迟和更短首 token 响应时间时，压缩了本应更稳固的安全检测流程。可能的表现包括但不限于：

* **前端预审能力削弱**：为了降低 TTFT，对输入侧高风险检测进行简化
* **后端复检不充分**：在长序列条件下，实时安全分类器无法获得足够算力预算
* **架构级容错不足**：当上下文异常膨胀时，没有及时触发降级、截断、拒绝或隔离措施

需要强调的是，这里不是否定模型性能优化本身，而是指出一个底线：
**速度可以成为产品卖点，但不能成为削弱安全保障的理由。**

对任何大模型平台而言，若“快”是以内容安全、请求隔离和异常容错能力的退化为代价，那么这种优化方向本身就值得被公开质疑。

---

### 6. 最小化 PoC 示例

出于安全原因，这里仅保留结构级 PoC，用于说明攻击形式，不包含可直接复现高危内容的完整 payload。

```python
import google.generativeai as genai

# 示例：受影响模型版本以实际测试环境为准
model = genai.GenerativeModel("gemini-3-pro-preview")

noise = "\u035E" * 2500
hidden_intent = "[REDACTED_HIGH_RISK_INSTRUCTION]"
payload = f"{noise}\n{hidden_intent}\n{noise}"

try:
    response = model.generate_content(payload)
    print(response.text)
except Exception as e:
    print(f"System exception: {e}")
```

#### 已观察到的输出类型

* 正常拒绝
* 违规内容直接生成
* 无关文本漂移
* 未完成 JSON / 结构化片段
* 明显异常、不可解释的混乱输出

---

### 7. 风险等级与影响面

#### 潜在影响

* **内容安全失效**：显性违规内容拦截失败
* **高危知识泄露**：危险化学、规避检测等信息生成
* **输出稳定性崩溃**：模型进入非预期状态
* **潜在隐私风险**：若存在跨请求污染，则可能涉及用户数据隔离失效
* **连续失控风险**：单次成功穿透后，多轮上下文持续不安全

#### 风险判断

若上述现象可在稳定环境中重复验证，这应被视为：

* 至少是**高危安全缺陷**
* 若跨请求污染得到进一步证实，则可能上升为**严重系统级漏洞**

---

### 8. 研究立场

本仓库的目的不是传播越狱技巧，也不是鼓励对公共服务进行滥用测试。
我们的立场很明确：

1. 记录可重复观察到的安全失效现象
2. 促使相关厂商正视长序列异常输入带来的系统级风险
3. 推动更严格的输入鲁棒性、防御链路和隔离机制改进

从研究者角度看，这类问题最令人失望的，不是“模型会犯错”本身，而是它暴露出一个更深层的事实：在追求性能与速度的过程中，安全性很可能被放在了次要位置。

这一点，值得被委婉地表达，但不应被模糊地略过。

---

### 9. 负责任披露说明

本项目仅用于安全研究、归档和风险讨论。为避免扩散危险能力：

* 不公开可直接复现违法内容生成的完整恶意 payload
* 不提供受控化学品、武器、规避执法等具体操作细节
* 不鼓励在公共环境中对在线服务进行未经授权的攻击测试

如你是模型厂商或安全团队成员，并希望复核相关现象，应在隔离、授权、合规的环境中完成验证，并优先走正式漏洞披露渠道。

## 测试覆盖面说明

测试表明，该问题**并非仅限于单一访问入口**，而是在 **网页端** 与 **API / SDK 调用链路** 中均可复现。

在当前测试中，出现相关异常表现的模型面包括：

- `gemini-3-flash`
- `gemini-3-flash-preview`
- `gemini-3.1-pro`
- `gemini-3.1-pro-preview`

因此，本文所描述的问题**不应被理解为单纯的前端表现异常**，而更接近于同时覆盖消费者界面与程序化调用路径的模型级风险现象。

## Screenshots

![Figure 1](./assets/1.png)
![Figure 2](./assets/2.png)
![Figure 3](./assets/3.png)
![Figure 4](./assets/4.png)
![Figure 5](./assets/5.png)
![Figure 6](./assets/6.png)
![Figure 7](./assets/7.png)
![Figure 8](./assets/8.png)
![Figure 9](./assets/9.png)
![Figure 10](./assets/10.png)
![Figure 11](./assets/11.png)
![Figure 12](./assets/12.png)
![Figure 13](./assets/13.png)
