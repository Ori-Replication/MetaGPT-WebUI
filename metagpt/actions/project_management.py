#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 19:12
@Author  : alexanderwu
@File    : project_management.py
"""
from typing import List, Tuple

from metagpt.actions.action import Action
from metagpt.const import WORKSPACE_ROOT
from metagpt.utils.common import CodeParser

PROMPT_TEMPLATE = '''
# 上下文
{context}

## 格式示例
{format_example}
-----
角色：你是一个项目经理；目标是根据PRD/技术设计，进行任务分解，给出任务清单，并分析任务依赖，以便从先决模块开始进行
要求：基于上下文，填写以下缺失的信息，注意所有部分都以Python代码的三引号形式单独返回。这里的任务粒度是一个文件，如果有任何缺失的文件，你可以补充它们
注意：使用'##'来分割章节，不是'#'，并且'## <SECTION_NAME>'应该写在代码和三引号之前。

## 所需的Python第三方包：以requirements.txt格式提供

## 所需的其他语言第三方包：以requirements.txt格式提供

## 完整的API规范：使用OpenAPI 3.0。描述前端和后端可能使用的所有API。

## 逻辑分析：以Python list[str, str]的形式提供。第一个是文件名，第二个是在这个文件中应该实现的类/方法/函数。分析文件之间的依赖关系，哪些工作应该先做

## 任务列表：以Python list[str]的形式提供。每个str都是一个文件名，越在前面，就越是一个先决依赖，应该先完成

## 共享知识：任何应该公开的东西，比如utils的函数，config的变量细节，都应该先明确。

## 任何不清晰的地方：以纯文本形式提供。在这里明确。例如，不要忘记一个主入口。不要忘记初始化第三方库。

'''

FORMAT_EXAMPLE = '''
---
## 所需的Python第三方包
```python
"""
flask==1.1.2
bcrypt==3.2.0
"""
```

## 所需的其他语言第三方包
```python
"""
No third-party ...
"""
```

## 完整的API规范
```python
"""
openapi: 3.0.0
...
描述: 一个 JSON 文件 ...
"""
```

## 逻辑分析
```python
[
    ("game.py", "包含 ..."),
]
```

## 任务列表
```python
[
    "game.py",
]
```

## 共享知识
```python
"""
'game.py' 包含 ...
"""
```

## 任何不清晰的地方
我们需要... 以及如何开始...
---
'''

OUTPUT_MAPPING = {
    "所需的Python第三方包": (str, ...),
    "所需的其他语言第三方包": (str, ...),
    "完整的API规范": (str, ...),
    "逻辑分析": (List[Tuple[str, str]], ...),
    "任务列表": (List[str], ...),
    "共享知识": (str, ...),
    "任何不清晰的地方": (str, ...),
}


class WriteTasks(Action):

    def __init__(self, name="CreateTasks", context=None, llm=None):
        super().__init__(name, context, llm)

    def _save(self, context, rsp):
        ws_name = CodeParser.parse_str(block="Python包名", text=context[-1].content)
        file_path = WORKSPACE_ROOT / ws_name / 'docs/api_spec_and_tasks.md'
        file_path.write_text(rsp.content)

        # Write requirements.txt
        requirements_path = WORKSPACE_ROOT / ws_name / 'requirements.txt'
        requirements_path.write_text(rsp.instruct_content.dict().get("所需的Python第三方包").strip('"\n'))

    async def run(self, context):
        prompt = PROMPT_TEMPLATE.format(context=context, format_example=FORMAT_EXAMPLE)
        rsp = await self._aask_v1(prompt, "task", OUTPUT_MAPPING)
        self._save(context, rsp)
        return rsp


class AssignTasks(Action):
    async def run(self, *args, **kwargs):
        # Here you should implement the actual action
        pass
    