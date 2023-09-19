#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 19:26
@Author  : alexanderwu
@File    : design_api.py
"""
import shutil
from pathlib import Path
from typing import List

from metagpt.actions import Action, ActionOutput
from metagpt.const import WORKSPACE_ROOT
from metagpt.logs import logger
from metagpt.utils.common import CodeParser
from metagpt.utils.mermaid import mermaid_to_file

PROMPT_TEMPLATE = """
# 上下文
{context}

## 格式示例
{format_example}
-----
角色：你是一名架构师；目标是设计一套符合PEP8规范的Python系统；最大限度地利用优秀的开源工具
需求：根据上下文填写以下缺失的信息，注意所有部分都以代码形式单独回应
最大输出：8192个字符或2048个令牌。尽量使用它们。
注意：使用'##'来分割部分，而不是'#'，并且'## <SECTION_NAME>'应在代码和三引号之前写。

## 实施方法：以纯文本形式提供。分析需求的难点，选择合适的开源框架。

## Python包名：以Python str提供，使用python三引号，简洁明了，字符只使用全部小写和下划线的组合

## 文件列表：以Python list[str]提供，只需要编写程序所需的文件列表（越少越好！）。只需要相对路径，符合PEP8标准。总是在这里写一个main.py或app.py

## 数据结构和接口定义：使用mermaid classDiagram代码语法，包括类（包括__init__方法）和函数（带类型注解），清楚地标记类之间的关系，并符合PEP8标准。数据结构应非常详细，API应全面，设计完整。

## 程序调用流程：使用sequenceDiagram代码语法，完整和非常详细，准确使用上述定义的类和API，覆盖每个对象的CRUD和INIT，语法必须正确。

## 有任何不清楚的地方：以纯文本形式提供。在这里明确。

"""
FORMAT_EXAMPLE = """
---
## 实施方法
我们会 ...

## Python包名
```python
"snake_game"
```

## 文件列表
```python
[
    "main.py",
]
```

## 数据结构和接口定义
```mermaid
classDiagram
    class Game{
        +int score
    }
    ...
    Game "1" -- "1" Food: has
```

## 程序调用流程
```mermaid
sequenceDiagram
    participant M as 主程序
    ...
    G->>M: 结束游戏
```

## 不清楚的地方
没有不清楚的地方
---
"""
OUTPUT_MAPPING = {
    "实施方法": (str, ...),
    "Python包名": (str, ...),
    "文件列表": (List[str], ...),
    "数据结构和接口定义": (str, ...),
    "程序调用流程": (str, ...),
    "不清楚的地方": (str, ...),
}


class WriteDesign(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "基于PRD，思考系统设计，并设计相应的APIs，" \
                    "数据结构，库表，流程和路径。请详细清晰地提供你的设计和反馈。"

    def recreate_workspace(self, workspace: Path):
        try:
            shutil.rmtree(workspace)
        except FileNotFoundError:
            pass  # Folder does not exist, but we don't care
        workspace.mkdir(parents=True, exist_ok=True)

    def _save_prd(self, docs_path, resources_path, prd):
        prd_file = docs_path / 'prd.md'
        quadrant_chart = CodeParser.parse_code(block="竞品象限图", text=prd)
        mermaid_to_file(quadrant_chart, resources_path / '竞品分析')
        logger.info(f"Saving PRD to {prd_file}")
        prd_file.write_text(prd)

    def _save_system_design(self, docs_path, resources_path, content):
        data_api_design = CodeParser.parse_code(block="数据结构和接口定义", text=content)
        seq_flow = CodeParser.parse_code(block="程序调用流程", text=content)
        mermaid_to_file(data_api_design, resources_path / 'data_api_design')
        mermaid_to_file(seq_flow, resources_path / 'seq_flow')
        system_design_file = docs_path / 'system_design.md'
        logger.info(f"Saving System Designs to {system_design_file}")
        system_design_file.write_text(content)

    def _save(self, context, system_design):
        if isinstance(system_design, ActionOutput):
            content = system_design.content
            ws_name = CodeParser.parse_str(block="Python包名", text=content)
        else:
            content = system_design
            ws_name = CodeParser.parse_str(block="Python包名", text=system_design)
        workspace = WORKSPACE_ROOT / ws_name
        self.recreate_workspace(workspace)
        docs_path = workspace / 'docs'
        resources_path = workspace / 'resources'
        docs_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        self._save_prd(docs_path, resources_path, context[-1].content)
        self._save_system_design(docs_path, resources_path, content)

    async def run(self, context):
        prompt = PROMPT_TEMPLATE.format(context=context, format_example=FORMAT_EXAMPLE)
        # system_design = await self._aask(prompt)
        system_design = await self._aask_v1(prompt, "system_design", OUTPUT_MAPPING)
        self._save(context, system_design)
        return system_design
    