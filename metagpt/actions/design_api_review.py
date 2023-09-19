#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 19:31
@Author  : alexanderwu
@File    : design_api_review.py
"""
from metagpt.actions.action import Action


class DesignReview(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, prd, api_design):
        prompt =  prompt = f"这是产品需求文档（PRD）：\n\n{prd}\n\n这是基于此PRD设计的API列表：\n\n{api_design}\n\n请审查此API设计是否满足PRD的要求，以及是否符合良好的设计实践。"

        api_review = await self._aask(prompt)
        return api_review
    