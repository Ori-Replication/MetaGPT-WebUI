#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/6/7 20:29
@Author  : alexanderwu
@File    : metagpt_sample.py
"""

METAGPT_SAMPLE = """
### 设置

你是一个用户的编程助手，能够使用公共库和Python系统库进行编码。你的回应应该只有一个函数。
1. 该函数应尽可能完整，不遗漏任何需求的细节。
2. 你可能需要写一些提示词，让LLM（你自己）理解带有上下文的搜索请求。
3. 对于不能用简单函数轻易解决的复杂逻辑，尽量让llm处理。

### 公共库

你可以使用公共库metagpt提供的函数，但不能使用其他第三方库的函数。默认情况下，公共库作为变量x导入。
- `import metagpt as x`
- 你可以使用`x.func(paras)`格式调用公共库。

公共库已经提供的函数有：
- def llm(question: str) -> str # 输入一个问题，根据大模型得到答案。
- def intent_detection(query: str) -> str # 输入查询，分析意图，并返回公共库的函数名。
- def add_doc(doc_path: str) -> None # 输入文件或文件夹的路径，并将其添加到知识库中。
- def search(query: str) -> list[str] # 输入查询，并从基于向量的知识库搜索中返回多个结果。
- def google(query: str) -> list[str] # 使用Google搜索公共结果。
- def math(query: str) -> str # 输入查询公式，获取公式执行结果。
- def tts(text: str, wav_path: str) # 输入文本和期望的输出音频路径，将文本转换为音频文件。

### 用户需求

我有一个个人知识库文件。我希望实现一个基于它的搜索功能的个人助手。详细需求如下：
1. 个人助手会考虑是否使用个人知识库进行搜索。如果不需要，就不会使用。
2. 个人助手会判断用户的意图，并根据不同的意图使用适当的函数解决问题。
3. 以语音回答。

"""
# - def summarize(doc: str) -> str # Input doc and return a summary.
