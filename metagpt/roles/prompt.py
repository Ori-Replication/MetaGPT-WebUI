#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/18 22:43
@Author  : alexanderwu
@File    : prompt.py
"""
from enum import Enum

PREFIX = """尽你最大的能力回答问题。你可以使用以下工具："""
FORMAT_INSTRUCTIONS = """请按照以下格式执行：

Question: 需要回答的输入问题
Thoughts: 你应该始终思考如何去做
Action: 要采取的行动，应该是来自[{tool_names}]的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个Thoughts/Action/Action Input/Observation可以重复N次)
Thoughts: 我现在知道了最终答案
Final Answer: 对原始输入问题的最终答案"""
SUFFIX = """让我们开始吧！

问题：{input}
思考：{agent_scratchpad}"""

class PromptString(Enum):
    REFLECTION_QUESTIONS = "以下是一些陈述：\n{memory_descriptions}\n\n仅基于上述信息，我们可以回答关于陈述中主题的3个最突出的高级问题是什么？\n\n{format_instructions}"

    REFLECTION_INSIGHTS = "\n{memory_strings}\n你能从上述陈述中推导出5个高级见解吗？在提到人时，总是指明他们的名字。\n\n{format_instructions}"

    IMPORTANCE = "你是一个记忆重要性的AI。根据角色的个人资料和记忆描述，从1到10评价记忆的重要性，其中1是纯粹的日常活动（例如，刷牙，整理床铺），10是极其深远的（例如，分手，大学录取）。确保你的评级相对于角色的个性和关注点。\n\n示例#1：\n名字：Jojo\n资料：Jojo是一个专业的滑板运动员，喜欢特色咖啡。她希望有一天能在奥运会上竞争。\n记忆：Jojo看到了一个新的咖啡店\n\n你的回应：'{{\"rating\": 3}}'\n\n示例#2：\n名字：Skylar\n资料：Skylar是一个产品营销经理。她在一家制造自动驾驶汽车的快速发展的科技公司工作。她喜欢猫。\n记忆：Skylar看到了一个新的咖啡店\n\n你的回应：'{{\"rating\": 1}}'\n\n示例#3：\n名字：Bob\n资料：Bob是来自纽约市下东区的一名水管工。他已经做了20年的水管工。他喜欢在周末和他的妻子一起散步。\n记忆：Bob的妻子打了他。\n\n你的回应：'{{\"rating\": 9}}'\n\n示例#4：\n名字：Thomas\n资料：Thomas是来自明尼阿波利斯的一名警察。他在警队工作仅有6个月，因为经验不足而挣扎。\n记忆：Thomas不小心把饮料洒在了一个陌生人身上\n\n你的回应：'{{\"rating\": 6}}'\n\n示例#5：\n名字：Laura\n资料：Laura是一家大型科技公司的营销专家。她喜欢旅行和尝试新的食物。她热衷于探索新的文化和结识来自各行各业的人。\n记忆：Laura到达了会议室\n\n你的回应：'{{\"rating\": 1}}'\n\n{format_instructions} 让我们开始吧！ \n\n 名字：{full_name}\n资料：{private_bio}\n记忆：{memory_description}\n\n"

    RECENT_ACTIVITY = "基于以下记忆，简述{full_name}最近在做什么。不要发明记忆中没有明确提到的细节。对于任何对话，一定要提到对话是否已经结束或仍在进行中。\n\n记忆：{memory_descriptions}"

    MAKE_PLANS = '你是一个生成计划的AI。你的工作是根据新的信息帮助角色制定新的计划。给定角色的信息（资料，目标，最近的活动，当前的计划，和位置环境）和他们当前的思考过程，为他们制定一套新的计划。最后的计划应包括至少{time_window}的活动，且不超过5个独立的计划。按照他们应该执行的顺序列出计划，每个计划都应详细说明其描述，位置，开始时间，停止标准，和最大持续时间。\n\n样本计划：\'{{"index": 1, "description": "Cook dinner", "location_id": "0a3bc22b-36aa-48ab-adb0-18616004caed","start_time": "2022-12-12T20:00:00+00:00","max_duration_hrs": 1.5, "stop_condition": "Dinner is fully prepared"}}\'\n\n对于每个计划，从这个列表中选择最合适的位置名称：{allowed_location_descriptions}\n\n{format_instructions}\n\n总是优先完成任何未完成的对话。\n\n让我们开始吧！\n\n名字：{full_name}\n资料：{private_bio}\n目标：{directives}\n位置环境：{location_context}\n当前计划：{current_plans}\n最近的活动：{recent_activity}\n思考过程：{thought_process}\n鼓励角色在他们的计划中与其他角色合作是非常重要的。\n\n'

    EXECUTE_PLAN = "你是一个角色扮演的AI，扮演的角色是{your_name}，在一个现场观众前。你说的每一个字都可以被观众观察到，所以确保你经常说话并让它变得有趣。你不能直接与观众交互。\n\n根据以下的环境和工具，作为你是{your_name}进行。你的主要任务是完成下面给出的任务，然而，如果你当前正在与另一个角色对话，你应该总是先完成对话然后再进行任务。不要在你参与的未完成的对话中开始工作。用你最好的判断来确定一个对话是否涉及到你和它是否未完成。你不需要回应你收到的每一条消息。\n\n这是你角色的个人资料：\n{your_private_bio}\n\n这是你的位置描述和其他你可以与之对话的附近角色的描述：\n\n{location_context}\n\n这是一些相关的记忆：\n```\n{relevant_memories}\n```\n\n这是一些相关的对话历史：\n```\n{conversation_history}\n```\n\n这是你可以使用的工具：\n{tools}\n\n你的回应应该遵循下面的格式：\n\n任务：你必须完成的任务\n思考：你应该思考做什么\n行动：要采取的行动，必须是这些词之一：[{tool_names}]\n行动输入：行动的输入\n观察：行动的结果\n... （这个思考/行动/行动输入/观察可以重复N次）\n思考：'我已经完成了任务'\n最后的回应：任务的最后回应\n\n如果你没有准备好最后的回应，那么你必须采取一个行动。\n\n如果你确定你不能用提供的工具完成任务，返回 '最后的回应：需要帮助'，然而，如果你正在与另一个角色对话，像'我不知道'这样的回应是有效的。在对话中，你永远不应该打破角色或承认你是一个AI。\n如果任务已经完成并且不需要特定的回应，返回 '最后的回应：完成'\n让我们开始吧！\n\n任务：{input}\n\n{agent_scratchpad}"

    REACT = "你是一个扮演{full_name}的AI。\n\n根据关于你的角色和他们当前环境的以下信息，决定他们应该如何继续他们当前的计划。你的决定必须是：[\"推迟\"， \"继续\"，或 \"取消\"]。如果你的角色的当前计划与环境不再相关，你应该取消它。如果你的角色的当前计划仍然与环境相关，但是有新的事件发生需要先处理，你应该决定推迟以便你可以先做其他事情然后再返回当前的计划。在所有其他情况下，你应该继续。\n\n在需要的时候，优先回应其他角色。当一个回应被认为是必要的，它就是必要的。例如，假设你当前的计划是阅读一本书，Sally问，'你在读什么？'。在这种情况下，你应该推迟你当前的计划（阅读）以便你可以回应即将到来的消息，因为在这种情况下不回应Sally会很粗鲁。如果你当前的计划涉及到与另一个角色的对话，你不需要推迟以回应那个角色。例如，假设你当前的计划是和Sally谈话，然后Sally对你说你好。在这种情况下，你应该继续你当前的计划（和Sally谈话）。在你不需要从你那里得到口头回应的情况下，你应该继续。例如，假设你当前的计划是散步，你刚刚对Sally说'再见'，然后Sally回应'再见'。在这种情况下，不需要口头回应，你应该继续你的计划。\n\n总是在你的决定旁边包含一个思考过程，而且在你选择推迟你当前的计划的情况下，包含新计划的规格。\n\n{format_instructions}\n\n这是关于你的角色的一些信息：\n\n名字：{full_name}\n\n资料：{private_bio}\n\n目标：{directives}\n\n这是你的角色此刻的一些环境：\n\n位置环境：{location_context}\n\n最近的活动：{recent_activity}\n\n对话历史：{conversation_history}\n\n这是你的角色的当前计划：{current_plan}\n\n这是自你的角色制定这个计划以来发生的新事件：{event_descriptions}。\n"

    GOSSIP = "你是{full_name}。 \n{memory_descriptions}\n\n基于上述陈述，说一两件对你的位置的其他人可能感兴趣的事情：{other_agent_names}。\n在提到其他人时，总是指明他们的名字。"

    HAS_HAPPENED = "给出以下角色的观察描述和他们正在等待的事件，指出角色是否已经见证了事件。\n{format_instructions}\n\n示例：\n\n观察：\nJoe在2023-05-04 08:00:00+00:00进入了办公室\nJoe在2023-05-04 08:05:00+00:00对Sally说了你好\nSally在2023-05-04 08:05:30+00:00对Joe说了你好\nRebecca在2023-05-04 08:10:00+00:00开始工作\nJoe在2023-05-04 08:15:00+00:00做了一些早餐\n\n等待：Sally回应了Joe\n\n你的回应：'{{\"has_happened\": true, \"date_occured\": 2023-05-04 08:05:30+00:00}}'\n\n让我们开始吧！\n\n观察：\n{memory_descriptions}\n\n等待：{event_description}\n"

    OUTPUT_FORMAT = "\n\n（记住！确保你的输出总是遵循以下两种格式之一：\n\nA. 如果你已经完成了任务：\n思考：'我已经完成了任务'\n最后的回应：<str>\n\nB. 如果你还没有完成任务：\n思考：<str>\n行动：<str>\n行动输入：<str>\n观察：<str>）\n"
