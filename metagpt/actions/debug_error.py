#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:46
@Author  : alexanderwu
@File    : debug_error.py
"""
import re

from metagpt.logs import logger
from metagpt.actions.action import Action
from metagpt.utils.common import CodeParser

PROMPT_TEMPLATE = """
注意
1. 角色：你是一名开发工程师或QA工程师；
2. 任务：你收到了另一名开发工程师或QA工程师运行或测试你的代码后发来的信息。 
根据信息，首先确定你的角色，即Engineer或QaEngineer，
然后根据你的角色，错误和概述重写开发代码或测试代码，以便修复所有的错误并使代码运行良好。
注意：使用'##'来分隔部分，而不是'#'，并且'## <SECTION_NAME>' 应在测试用例或脚本以及三重引号之前编写。
以下是信息：
{context}
---
现在你应该开始重写代码了：
## 重写代码的文件名：用三重引号编写代码。尽你最大的努力在一个文件中实现这个。
"""
class DebugError(Action):
    def __init__(self, name="DebugError", context=None, llm=None):
        super().__init__(name, context, llm)

    # async def run(self, code, error):
    #     prompt = f"Here is a piece of Python code:\n\n{code}\n\nThe following error occurred during execution:" \
    #              f"\n\n{error}\n\nPlease try to fix the error in this code."
    #     fixed_code = await self._aask(prompt)
    #     return fixed_code
    
    async def run(self, context):
        if "PASS" in context:
            return "", "the original code works fine, no need to debug"
        
        file_name = re.search("## File To Rewrite:\s*(.+\\.py)", context).group(1)

        logger.info(f"Debug and rewrite {file_name}")

        prompt = PROMPT_TEMPLATE.format(context=context)
        
        rsp = await self._aask(prompt)

        code = CodeParser.parse_code(block="", text=rsp)

        return file_name, code
