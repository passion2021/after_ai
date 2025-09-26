#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/1/27
# @Author  : AI Assistant
# @File    : query_preprocessor.py
"""
查询预处理工具
用于处理微信群中的问题查询，去除标点符号、@符号等
"""

import re
import string
from typing import Optional
from loguru import logger


class QueryPreprocessor:
    """查询预处理器"""
    
    def __init__(self):
        # 中文标点符号
        self.chinese_punctuation = '，。！？；：""''（）【】《》〈〉「」『』〔〕〖〗〘〙〚〛、'
        
        # 英文标点符号
        self.english_punctuation = string.punctuation
        
        # 特殊符号（包括@符号等）
        self.special_symbols = '@#$%^&*+=|\\~`'
        
        # 微信相关符号
        self.wechat_symbols = '【】《》'
        
        # 组合所有需要去除的符号
        self.all_punctuation = (
            self.chinese_punctuation + 
            self.english_punctuation + 
            self.special_symbols + 
            self.wechat_symbols
        )
    
    def clean_query(self, query: str) -> str:
        """
        清理查询文本
        
        Args:
            query: 原始查询文本
            
        Returns:
            清理后的查询文本
        """
        if not query:
            return ""
        
        original_query = query
        # 1. 去除@符号及其后面的用户名
        query = self._remove_mentions(query)
        
        # 2. 去除多余的空格
        query = self._remove_extra_spaces(query)
        
        # 3. 去除标点符号
        query = self._remove_punctuation(query)
        
        # 4. 去除数字编号（如1. 2. 等）
        query = self._remove_numbering(query)
        
        # 5. 去除特殊字符
        query = self._remove_special_chars(query)
        
        # 6. 最终清理
        query = query.strip()
        
        return query
    
    def _remove_mentions(self, text: str) -> str:
        """去除@符号及其后面的用户名"""
        # 去除@用户名
        text = re.sub(r'@\w+', '', text)
        # 去除@符号
        text = text.replace('@', '')
        return text
    
    def _remove_extra_spaces(self, text: str) -> str:
        """去除多余的空格"""
        # 将多个连续空格替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _remove_punctuation(self, text: str) -> str:
        """去除标点符号"""
        # 创建翻译表，将所有标点符号映射为None
        translator = str.maketrans('', '', self.all_punctuation)
        text = text.translate(translator)
        return text
    
    def _remove_numbering(self, text: str) -> str:
        """去除数字编号"""
        # 去除开头的数字编号，如 "1. 问题内容" -> "问题内容"
        text = re.sub(r'^\d+\.\s*', '', text)
        # 去除行首的数字编号
        text = re.sub(r'^\d+\s*', '', text)
        return text
    
    def _remove_special_chars(self, text: str) -> str:
        """去除特殊字符"""
        # 去除控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # 去除零宽字符
        text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
        return text
    
    def is_valid_query(self, query: str) -> bool:
        """
        检查查询是否有效
        
        Args:
            query: 查询文本
            
        Returns:
            是否有效
        """
        if not query or not query.strip():
            return False
        
        # 检查是否只包含标点符号
        cleaned = self.clean_query(query)
        if not cleaned or len(cleaned.strip()) < 2:
            return False
        
        return True
    
    def preprocess_for_rag(self, query: str) -> Optional[str]:
        """
        为RAG检索预处理查询
        
        Args:
            query: 原始查询
            
        Returns:
            预处理后的查询，如果无效则返回None
        """
        if not query:
            return None
        
        # 清理查询
        cleaned_query = self.clean_query(query)
        
        # 检查是否有效
        if not self.is_valid_query(cleaned_query):
            logger.warning(f"查询无效，已过滤: {query}")
            return None
        
        return cleaned_query


# 创建全局预处理器实例
query_preprocessor = QueryPreprocessor()


def preprocess_query(query: str) -> Optional[str]:
    """
    预处理查询的便捷函数
    
    Args:
        query: 原始查询文本
        
    Returns:
        预处理后的查询文本，如果无效则返回None
    """
    return query_preprocessor.preprocess_for_rag(query)


if __name__ == "__main__":
    # 测试用例
    test_queries = [
        "机器人不回复了，为什么？",
        "@张三 机器人不回复了，为什么？",
        "1. 表格揽收失败，提示请使用专用模版",
        "【申通】揽收失败怎么办？",
        "！！！紧急！！！机器人坏了",
        "@所有人 请问这个怎么处理？",
        "  多个  空格  的问题  ",
        "？。！@#$%^&*()",
        "",
        "   ",
        "a",  # 太短
    ]
    
    print("🔧 查询预处理测试")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试用例 {i}:")
        print(f"原始查询: '{query}'")
        
        preprocessed = preprocess_query(query)
        if preprocessed:
            print(f"预处理后: '{preprocessed}'")
            print("✅ 有效查询")
        else:
            print("❌ 无效查询，已过滤")
        
        print("-" * 30)

