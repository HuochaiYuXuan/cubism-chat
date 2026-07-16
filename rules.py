"""规则系统 — 加载/匹配/管理 Cubism Chat 编辑规则

规则文件格式：Markdown + YAML frontmatter
存储位置：rules/ 目录
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import sys
_BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
RULES_DIR = _BASE / "rules"

# 匹配 YAML frontmatter
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class Rule:
    """一条编辑规则"""
    name: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)
    body: str = ""

    @property
    def slash_names(self) -> list[str]:
        """返回所有 / 开头的触发词"""
        return [t for t in self.triggers if t.startswith("/")]

    @property
    def natural_triggers(self) -> list[str]:
        """返回所有自然语言触发词"""
        return [t for t in self.triggers if not t.startswith("/")]


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (frontmatter_dict, body_text)"""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text

    fm = {}
    current_key = None
    for line in m.group(1).split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 列表项:   - value
        if stripped.startswith("- ") and current_key:
            val = stripped[2:].strip().strip("'\"")
            if current_key not in fm or fm[current_key] is None:
                fm[current_key] = []
            fm[current_key].append(val)
            continue

        # 新的 key: value
        if ":" in stripped:
            # 处理 key: value（同行值）
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            current_key = key
            if val:
                if val.startswith("[") and val.endswith("]"):
                    # 行内列表: [a, b, c]
                    items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                    fm[key] = items
                else:
                    fm[key] = val.strip("'\"")
            # val 为空 → 可能是多行列表开始，保持 current_key 等待后续行
            # 如果该 key 还没有赋值，标记为 None（后续 - 行会覆盖）
            if key not in fm:
                fm[key] = None

    # 清理没有被列表填充的 None 值
    for k in list(fm.keys()):
        if fm[k] is None:
            fm[k] = ""

    body = text[m.end():].strip()
    return fm, body


def load_rules() -> list[Rule]:
    """加载所有规则文件"""
    rules = []
    if not RULES_DIR.exists():
        return rules
    for f in sorted(RULES_DIR.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
            fm, body = _parse_frontmatter(text)
            rule = Rule(
                name=fm.get("name", f.stem),
                description=fm.get("description", ""),
                triggers=fm.get("triggers", []),
                body=body,
            )
            # 自动添加 /name 为触发词
            slash = f"/{rule.name}"
            if slash not in rule.triggers:
                rule.triggers.append(slash)
            rules.append(rule)
        except Exception as e:
            print(f"[rules] 加载 {f.name} 失败: {e}")
    return rules


def find_rule(user_input: str, rules: list[Rule]) -> Optional[tuple[Rule, str]]:
    """根据用户输入查找匹配的规则。

    Returns:
        (Rule, user_args) 如果匹配到，否则 None。
        user_args 是去掉触发词后剩余的用户输入。
    """
    text = user_input.strip()

    # 1. 精确匹配 /name
    for rule in rules:
        for slash in rule.slash_names:
            if text == slash:
                return (rule, "")
            if text.startswith(slash + " "):
                args = text[len(slash):].strip()
                return (rule, args)

    # 2. 精确匹配自然语言触发词
    for rule in rules:
        for trigger in rule.natural_triggers:
            if text == trigger:
                return (rule, "")
            if text.startswith(trigger) and len(text) > len(trigger):
                args = text[len(trigger):].strip()
                return (rule, args)

    # 3. 包含匹配（触发词出现在用户输入中）
    for rule in rules:
        for trigger in rule.natural_triggers:
            if trigger in text:
                return (rule, text)

    return None


def list_rules_summary(rules: list[Rule]) -> str:
    """生成规则摘要（用于未匹配时注入 system prompt）"""
    if not rules:
        return "（暂无规则）"
    lines = []
    for r in rules:
        triggers_str = ", ".join(r.triggers[:3])
        lines.append(f"- **/{r.name}**: {r.description} (触发: {triggers_str})")
    return "\n".join(lines)


def format_rule_for_prompt(rule: Rule) -> str:
    """将规则格式化为注入 system prompt 的文本"""
    triggers_str = ", ".join(rule.triggers)
    return f"""## 当前规则: {rule.name}
**描述**: {rule.description}
**触发词**: {triggers_str}

**执行步骤**（严格遵循）:
{rule.body}
"""


def save_rule(name: str, description: str, triggers: list[str], body: str) -> Path:
    """保存规则到 rules/ 目录"""
    RULES_DIR.mkdir(exist_ok=True)

    triggers_yaml = "\n".join(f"  - {t}" for t in triggers)
    content = f"""---
name: {name}
description: {description}
triggers:
{triggers_yaml}
---

{body}
"""
    path = RULES_DIR / f"{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


def delete_rule(name: str) -> bool:
    """删除规则文件"""
    path = RULES_DIR / f"{name}.md"
    if path.exists():
        path.unlink()
        return True
    return False
