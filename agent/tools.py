#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/26 16:47
# @Author  : 李明轩
# @File    : tools.py
import traceback
from typing import Dict, Any, Optional
from loguru import logger

from libs.easy_llm import *
from libs.easy_llm.utils import extract_struct, json_parse_dirty
from prompt.agent import EmotionRecognition


def emotion_response(query: str) -> Optional[Dict[str, Any]]:
    """
    情绪识别函数
    
    Args:
        query: 用户查询文本
        
    Returns:
        情绪识别结果字典，包含情绪类型、强度等信息
        如果识别失败则返回None
    """
    if not query or not query.strip():
        logger.warning("查询文本为空，无法进行情绪识别")
        return None

    try:
        # 构建情绪识别提示
        emotion_prompt = EmotionRecognition().format(content=query)
        logger.info(f"开始情绪识别，查询: {query[:50]}...")

        # 调用LLM进行情绪识别
        messages = MsgList(git_mode=False)
        messages.append(HumanMsg(content=emotion_prompt))
        llm_response = qwen_chat.chat_complete(messages=messages.to_json())

        if not llm_response:
            logger.warning("LLM响应为空")
            return None

        # 提取结构化数据
        emotion_result = json_parse_dirty(llm_response)

        if not emotion_result:
            logger.warning("无法从LLM响应中提取情绪识别结果")
            return None

        # 验证结果格式
        if not isinstance(emotion_result, dict):
            logger.warning(f"情绪识别结果格式错误: {type(emotion_result)}")
            return None

        logger.info(f"情绪识别成功: {emotion_result}")
        if emotion_result.get('text') != 0:
            return emotion_result
        else:
            return None

    except Exception as e:

        logger.error(f"情绪识别过程中发生异常: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    # 测试情绪识别功能
    test_queries = [
        "机器人不回复了，为什么？",
        "太生气了！这个系统怎么这么烂！",
        "谢谢你的帮助，很满意",
        "有点担心这个功能是否正常",
        "非常高兴能解决这个问题"
    ]

    print("🔧 情绪识别功能测试")
    print("=" * 50)

    for i, query in enumerate(test_queries, 1):
        print(f"\n测试用例 {i}: {query}")

        result = emotion_response(query)
        if result:
            print(f"✅ 识别成功: {result}")
        else:
            print("❌ 识别失败")

        print("-" * 30)
