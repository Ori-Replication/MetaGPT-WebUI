#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:46
@Author  : alexanderwu
@File    : run_code.py
"""
import os
import subprocess
import traceback
from typing import Tuple

from metagpt.actions.action import Action
from metagpt.logs import logger

PROMPT_TEMPLATE = """
角色：你是一位高级开发和质量保证工程师，你的角色是总结代码运行结果。
如果运行结果中没有包含错误，你应该明确批准结果。
另一方面，如果运行结果显示出一些错误，你应该指出是哪部分，开发代码还是测试代码，产生了错误，
并给出修复错误的具体指导。以下是代码信息：
{context}
现在你应该开始你的分析
---
## 指导：
请总结错误的原因并给出纠正指导
## 需要重写的文件：
确定一个需要重写的文件以修复错误，例如，xyz.py，或者test_xyz.py
## 状态：
确定所有的代码是否都运行正常，如果是，请写PASS，否则写FAIL，
在这个部分只写一个词，PASS或FAIL
## 发送给：
如果错误是由于开发代码的问题，请写Engineer，如果是由于测试代码的问题，请写QaEngineer，如果没有错误，请写NoOne，
在这个部分只写一个词，Engineer或QaEngineer或NoOne
---
你应该填写必要的指导，状态，发送给，最后返回所有在---分割线之间的内容。
"""

CONTEXT = """
## 开发代码文件名
{code_file_name}
## 开发代码
```python
{code}
```
## 测试文件名
{test_file_name}
## 测试代码
```python
{test_code}
```
## 运行命令
{command}
## 运行输出
标准输出: {outs};
标准错误: {errs};
"""


class RunCode(Action):
    def __init__(self, name="RunCode", context=None, llm=None):
        super().__init__(name, context, llm)

    @classmethod
    async def run_text(cls, code) -> Tuple[str, str]:
        try:
            # We will document_store the result in this dictionary
            namespace = {}
            exec(code, namespace)
            return namespace.get("result", ""), ""
        except Exception:
            # If there is an error in the code, return the error message
            return "", traceback.format_exc()

    @classmethod
    async def run_script(cls, working_directory, additional_python_paths=[], command=[]) -> Tuple[str, str]:
        working_directory = str(working_directory)
        additional_python_paths = [str(path) for path in additional_python_paths]

        # Copy the current environment variables
        env = os.environ.copy()

        # Modify the PYTHONPATH environment variable
        additional_python_paths = [working_directory] + additional_python_paths
        additional_python_paths = ":".join(additional_python_paths)
        env["PYTHONPATH"] = additional_python_paths + ":" + env.get("PYTHONPATH", "")

        # Start the subprocess
        process = subprocess.Popen(
            command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
        )

        try:
            # Wait for the process to complete, with a timeout
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            logger.info("The command did not complete within the given timeout.")
            process.kill()  # Kill the process if it times out
            stdout, stderr = process.communicate()
        return stdout.decode("utf-8"), stderr.decode("utf-8")

    async def run(
        self, code, mode="script", code_file_name="", test_code="", test_file_name="", command=[], **kwargs
    ) -> str:
        logger.info(f"Running {' '.join(command)}")
        if mode == "script":
            outs, errs = await self.run_script(command=command, **kwargs)
        elif mode == "text":
            outs, errs = await self.run_text(code=code)

        logger.info(f"{outs=}")
        logger.info(f"{errs=}")

        context = CONTEXT.format(
            code=code,
            code_file_name=code_file_name,
            test_code=test_code,
            test_file_name=test_file_name,
            command=" ".join(command),
            outs=outs[:500],  # outs might be long but they are not important, truncate them to avoid token overflow
            errs=errs[:10000],  # truncate errors to avoid token overflow
        )

        prompt = PROMPT_TEMPLATE.format(context=context)
        rsp = await self._aask(prompt)

        result = context + rsp

        return result
