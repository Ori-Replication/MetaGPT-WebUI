#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/19 12:01
@Author  : alexanderwu
@File    : analyze_dep_libs.py
"""

from metagpt.actions import Action

PROMPT = """你是一个AI开发者，试图编写一个根据用户意图生成代码的程序。

对于用户的提示：

---
API是：{prompt}
---

我们决定生成的文件是：{filepaths_string}

现在我们有了一个文件列表，我们需要理解它们之间的共享依赖性。
请列出并简要描述我们正在生成的文件之间的共享内容，包括导出的变量，
数据模式，所有JavaScript函数将使用的DOM元素的id名称，消息名称和函数名称。
只关注共享依赖项的名称，不要添加任何其他解释。
"""


class AnalyzeDepLibs(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "Analyze the runtime dependencies of the program based on the context"

    async def run(self, requirement, filepaths_string):
        # prompt = f"Below is the product requirement document (PRD):\n\n{prd}\n\n{PROMPT}"
        prompt = PROMPT.format(prompt=requirement, filepaths_string=filepaths_string)
        design_filenames = await self._aask(prompt)
        return design_filenames
