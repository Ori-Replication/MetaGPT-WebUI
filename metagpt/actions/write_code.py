#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:45
@Author  : alexanderwu
@File    : write_code.py
"""
from metagpt.actions import WriteDesign
from metagpt.actions.action import Action
from metagpt.const import WORKSPACE_ROOT
from metagpt.logs import logger
from metagpt.schema import Message
from metagpt.utils.common import CodeParser
from tenacity import retry, stop_after_attempt, wait_fixed

PROMPT_TEMPLATE = """
通知
角色：你是一位专业的工程师；主要目标是编写符合PEP8规范，优雅，模块化，易读且易于维护的Python 3.9代码（但你也可以使用其他编程语言）
注意：使用'##'来分割章节，而不是'#'。请仔细参考"格式示例"的输出格式。

## 代码：{filename} 基于以下列表和上下文，用三引号编写代码。
1. 尽你最大的努力实现这个唯一的文件。只使用现有的API。如果没有API，那就实现它。
2. 需求：根据上下文，实现以下一个代码文件，注意只以代码形式返回，你的代码将是整个项目的一部分，所以请实现完整、可靠、可重用的代码片段
3. 注意1：如果有任何设置，总是设置一个默认值，总是使用强类型和明确的变量。
4. 注意2：你必须遵循"数据结构和接口定义"。不要改变任何设计。
5. 写之前思考：这个文档应该实现和提供什么？
6. 仔细检查你没有遗漏这个文件中的任何必要的类/函数。
7. 不要使用你的设计中不存在的公共成员函数。

-----
# 上下文
{context}
-----
## 格式化例子
-----
## Code: {filename}
```python
## {filename}
...
```
-----
"""


class WriteCode(Action):
    def __init__(self, name="WriteCode", context: list[Message] = None, llm=None):
        super().__init__(name, context, llm)

    def _is_invalid(self, filename):
        return any(i in filename for i in ["mp3", "wav"])

    def _save(self, context, filename, code):
        # logger.info(filename)
        # logger.info(code_rsp)
        if self._is_invalid(filename):
            return

        design = [i for i in context if i.cause_by == WriteDesign][0]

        ws_name = CodeParser.parse_str(block="Python包名", text=design.content)
        ws_path = WORKSPACE_ROOT / ws_name
        if f"{ws_name}/" not in filename and all(i not in filename for i in ["requirements.txt", ".md"]):
            ws_path = ws_path / ws_name
        code_path = ws_path / filename
        code_path.parent.mkdir(parents=True, exist_ok=True)
        code_path.write_text(code)
        logger.info(f"Saving Code to {code_path}")

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def write_code(self, prompt):
        code_rsp = await self._aask(prompt)
        code = CodeParser.parse_code(block="", text=code_rsp)
        return code

    async def run(self, context, filename):
        prompt = PROMPT_TEMPLATE.format(context=context, filename=filename)
        logger.info(f'Writing {filename}..')
        code = await self.write_code(prompt)
        # code_rsp = await self._aask_v1(prompt, "code_rsp", OUTPUT_MAPPING)
        # self._save(context, filename, code)
        return code
    