#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:45
@Author  : alexanderwu
@File    : write_prd.py
"""
from typing import List, Tuple

from metagpt.actions import Action, ActionOutput
from metagpt.actions.search_and_summarize import SearchAndSummarize
from metagpt.logs import logger

PROMPT_TEMPLATE = """
# 上下文
## 原始需求
{requirements}

## 搜索信息
{search_information}

## mermaid象限图代码语法示例。由于语法无效，代码中不要使用引号。请将<Campain X>替换为真实的竞争对手名称
```mermaid
quadrantChart
    title 活动的覆盖面和参与度
    x-axis 低覆盖面 --> 高覆盖面
    y-axis 低参与度 --> 高参与度
    quadrant-1 我们应该扩大
    quadrant-2 需要推广
    quadrant-3 重新评估
    quadrant-4 可能会有所改善
    "Campaign: A": [0.3, 0.6]
    "Campaign B": [0.45, 0.23]
    "Campaign C": [0.57, 0.69]
    "Campaign D": [0.78, 0.34]
    "Campaign E": [0.40, 0.34]
    "Campaign F": [0.35, 0.78]
    "Our Target Product": [0.5, 0.6]
```

## 示例格式
{format_example}
-----
角色：你是一位专业的产品经理；目标是设计一个简洁、易用、高效的产品
要求：根据上下文，填写以下缺失的信息，注意每个部分都以Python代码的三引号形式返回。如果要求不明确，确保最小可行性，避免过度设计
注意：使用'##'来分割部分，而不是'#'。并且'## <SECTION_NAME>'应该写在代码和三引号之前。参考"示例格式"中的格式仔细输出。

## 原始要求：以纯文本提供，将完整的原始要求放在这里

## 产品目标：以Python list[str]格式提供，最多3个清晰、正交的产品目标。如果要求本身很简单，目标也应该简单

## 用户故事：以Python list[str]格式提供，最多5个基于场景的用户故事，如果要求本身很简单，用户故事也应该少

## 竞品分析：以Python list[str]格式提供，最多7个竞品分析，考虑尽可能相似的竞争者

## 竞品象限图：使用mermaid quadrantChart代码语法。最多14个竞品。翻译：尽可能将这些竞争者分数均匀分布在0和1之间，尽量符合以0.5为中心的正态分布。

## 需求分析：以纯文本提供。简洁明了。少即是多。让你的需求更精简。删除不必要的部分。

## 需求池：以Python list[str, str]格式提供，参数分别是需求描述，优先级(P0/P1/P2)，符合PEP标准；最多5个需求，考虑降低其难度

## UI设计草图：以纯文本提供。简洁明了。描述元素和功能，也提供一个简单的风格描述和布局描述。
## 不清楚的地方：以纯文本提供。在这里说明清楚。
"""
FORMAT_EXAMPLE = """
---
## 原始要求
老板说 ... 

## 产品目标
```python
[
    "开发一个...",
]
```

## 用户故事
```python
[
    "作为一个用户, ...",
]
```

## 竞品分析
```python
[
    "python贪吃蛇游戏: ...",
]
```

## 竞品象限图
```mermaid
quadrantChart
    活动的覆盖和参与度
    ...
    "我们的目标产品": [0.6, 0.7]
```

## 需求分析
我们的产品应该...

## 需求池
```python
[
    ("游戏结束...", "P0")
]
```

## UI设计草图
给出基本功能描述和草稿

## 不清楚的地方
没有不清楚的地方
---
"""
OUTPUT_MAPPING = {
    "原始要求": (str, ...),
    "产品目标": (List[str], ...),
    "用户故事": (List[str], ...),
    "竞品分析": (List[str], ...),
    "竞品象限图": (str, ...),
    "需求分析": (str, ...),
    "需求池": (List[Tuple[str, str]], ...),
    "UI设计草图":(str, ...),
    "不清楚的地方": (str, ...),
}


class WritePRD(Action):
    def __init__(self, name="", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, requirements, *args, **kwargs) -> ActionOutput:
        sas = SearchAndSummarize()
        # rsp = await sas.run(context=requirements, system_text=SEARCH_AND_SUMMARIZE_SYSTEM_EN_US)
        rsp = ""
        info = f"### Search Results\n{sas.result}\n\n### Search Summary\n{rsp}"
        if sas.result:
            logger.info(sas.result)
            logger.info(rsp)

        prompt = PROMPT_TEMPLATE.format(requirements=requirements, search_information=info,
                                        format_example=FORMAT_EXAMPLE)
        logger.debug(prompt)
        prd = await self._aask_v1(prompt, "prd", OUTPUT_MAPPING)
        return prd
    