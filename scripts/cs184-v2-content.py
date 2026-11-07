"""Authored derivation workshops; executable examples are independent stdlib programs."""
from pathlib import Path
import contextlib
import io
import runpy

ROOT = Path(__file__).resolve().parent
DATA = {}


def lab(title, sections, context, assumptions, steps, inputs, calculation, check, boundary,
        code, symptom, repair, question, answer, caption):
    return locals()


for source in sorted((ROOT / 'cs184-v2').glob('*.py')):
    if source.name.startswith('content_'):
        exec(compile(source.read_text(encoding='utf8'), str(source), 'exec'))


def render(key, course):
    result = []
    for j, item in enumerate(DATA[key], 1):
        pages = sorted({p for s in item['sections'] for p in course['sections'][s-1]['pages']})
        text = f'## 深入 {j}. {item["title"]}\n\n'
        text += '本节是根据前文课件主题展开的**补充推导与独立教学实验**，数值不是课件测量结果。\n\n'
        text += '回查原课件：' + '、'.join('p'+str(p) for p in pages) + '。\n\n'
        text += item['context'] + '\n\n### 先固定问题的边界\n\n'
        for name, value in item['assumptions']:
            text += f'- **{name}**：{value}\n'
        text += '\n### 从定义逐步推到可计算形式\n\n'
        for n, (explanation, formula) in enumerate(item['steps'], 1):
            text += f'**第 {n} 步。** {explanation}\n\n'
            if formula:
                text += '$$\n' + formula + '\n$$\n\n'
        text += f'![{item["title"]}](diagrams/d{20+j:02d}-workshop.png)\n\n*{item["caption"]}*\n\n'
        text += f'### 🔧 手算 {12+j}：{item["title"]}\n\n'
        text += '| 已知量 | 数值与含义 |\n| --- | --- |\n'
        for name, value in item['inputs']:
            text += f'| {name} | {value} |\n'
        text += '\n'
        for n, step in enumerate(item['calculation'], 1):
            text += f'{n}. {step}\n\n'
        text += '### 回代与第二条验证路线\n\n'
        text += '\n\n'.join(item['check']) + '\n\n'
        text += '### 改变一个条件，原结论还成立吗？\n\n'
        text += '\n\n'.join(item['boundary']) + '\n\n'
        text += '### 真正运行一次：保留正确与错误对照\n\n'
        text += '下列程序只依赖 Python 标准库，复制到一个文件即可运行。断言验证本节明确给出的解析关系；它不替代完整场景测试。\n\n'
        text += '```python\n' + item['code'].strip() + '\n```\n\n'
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(item['code'], f'cs184-{key}-lab-{j}', 'exec'), {})
        text += '实际运行输出：\n\n```text\n' + buf.getvalue().strip() + '\n```\n\n'
        text += '### 实现坑：从可观察症状回到原因\n\n'
        text += '**症状：** ' + item['symptom'] + '\n\n'
        text += '**定位与修正：** ' + item['repair'] + '\n\n'
        text += f'### 自测 {26+j}. {item["question"]}\n\n<details>\n<summary>推理与答案</summary>\n\n'
        text += item['answer'] + '\n\n</details>\n\n'
        result.append(text)
    connections = runpy.run_path(str(ROOT/'cs184-v2/connections.py'))['CONNECTIONS'][key]
    text = '## 深入练习的跨讲连接：这些工具会在哪里再出现？\n\n'
    text += '| 相关讲次 | 借用的工具 | 本次实际使用位置 |\n| --- | --- | --- |\n'
    for label, slug, tool, use in connections[0]:
        text += f'| [{label}](/notes/{slug}/) | {tool} | {use} |\n'
    text += '\n### 回头看才明白\n\n'
    for n, observation in enumerate(connections[1],1):
        text += f'{n}. {observation}\n\n'
    text += '### 这组实验已经验证什么，还差什么\n\n'
    text += '| 证据 | 可以支持的结论 | 下一步 |\n| --- | --- | --- |\n'
    text += '| 逐步推导与回代 | 在明确假设下，数值和关系一致 | 改变一个假设，重新预测边界行为 |\n'
    text += '| 本篇四段实际运行的程序 | 小模型和故障对照可复现 | 接入完整项目后继续核对坐标、单位和输入范围 |\n'
    text += '| 原生图解 | 几何与数值对应关系可检查 | 不把示意图当成真实设备或场景的测量 |\n\n'
    result.append(text)
    return ''.join(result)
