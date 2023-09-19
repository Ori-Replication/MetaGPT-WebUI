#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/19 11:50
@Author  : alexanderwu
@File    : design_filenames.py
"""
from metagpt.actions import Action
from metagpt.logs import logger

PROMPT = """你是一名AI开发者，试图为用户编写一个根据他们的意图生成代码的程序。
在给出他们的意图时，提供一个完整且详尽的文件路径列表，以便为用户编写程序。
只列出你将编写的文件路径，并将它们作为Python字符串列表返回。
不要添加任何其他解释，只返回一个Python字符串列表。"""


class DesignFilenames(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "根据PRD，考虑系统设计，并进行相应的API、数据结构和数据库表的基础设计。请详细明确地给出你的设计，反馈。"


    async def run(self, prd):
        prompt = f"The following is the Product Requirement Document (PRD):\n\n{prd}\n\n{PROMPT}"
        design_filenames = await self._aask(prompt)
        logger.debug(prompt)
        logger.debug(design_filenames)
        return design_filenames
    