#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:45
@Author  : alexanderwu
@File    : write_prd_review.py
"""
from metagpt.actions.action import Action


class WritePRDReview(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)
        self.prd = None
        self.desc = "基于PRD，进行PRD审查，提供清晰详细的反馈"
        self.prd_review_prompt_template = """
        给出以下的产品需求文档(PRD)：
        {prd}

        作为项目经理，请审查并提供您的反馈和建议。
        """

    async def run(self, prd):
        self.prd = prd
        prompt = self.prd_review_prompt_template.format(prd=self.prd)
        review = await self._aask(prompt)
        return review
    