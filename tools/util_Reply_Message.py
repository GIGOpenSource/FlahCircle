#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：FlahCircle 
@File    ：util_Reply_Message.py
@Author  ：LYP
@Date    ：2025/10/28 16:26 
@description : 回复评论相关工具
"""
import logging
import requests
import random
import json
from django.db import transaction
from datetime import datetime, timedelta
from typing import List, Dict
from pyexpat.errors import messages
from contents.models import Content
from societies.models import Dynamic
from comments.models import Comment
from ai_comment.models import AIConfig as Config
from user.models import User

logger = logging.getLogger('info')


class LargeModelUnit(object):
    def __init__(self, model: str, api_key: str, base_url: str, temperature: float = 0.7):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.payload = {"model": self.model, "temperature": random.uniform(temperature, 2), "top_p": 0.9,
                        "presence_penalty": 0.5}
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                        'Authorization': f'Bearer {self.api_key}'}

    def generateToOpenAI(self, messages: List[Dict[str, str]]) -> tuple[int, str]:
        """
        千问生成提示词
        :param messages:
        :return:
        """
        self.payload["messages"] = messages
        resp = requests.post(self.base_url, json=self.payload, headers=self.headers).json()
        try:
            return True, resp["choices"][0]["message"]["content"]
        except:
            return False, ""

    def generateToDeepSeek(self, messages: List[Dict[str, str]]) -> tuple[int, str]:
        """
        DeepSeek生成提示词
        :param messages:
        :return:
        """
        self.payload["messages"] = messages
        resp = requests.post(self.base_url, data=json.dumps(self.payload), headers=self.headers).json()

        try:
            return True, resp["choices"][0]["message"]["content"]
        except:
            return False, ""


def genterateReplyMessages(obj: Content | Dynamic | Comment, obj_type: str = "content"):
    """
    生成回复消息
    :param obj:
    :param obj_type: 对象类型，"content" 或 "dynamic" 或 "comment"
    :return:
    """
    prompt_text = ""
    if obj_type == "content":
        prompt_text = obj.title
    if obj_type == "dynamic":
        prompt_text = obj.title
    if obj_type == "comment":
        prompt_text = obj.content
    base_sys = '你是一个社交媒体助理，请生成简短中文内容。'
    messages = [
        {'role': 'system', 'content': base_sys + f',{prompt_text}'},
        {'role': 'user',
         'content': f"请生成适合 {prompt_text} 的回复消息,请勿添加任何多余的文字"}]
    return messages


def getFewDays(n: int):
    """
    获取n天前的日期
    :param n:
    :return:
    """
    today = datetime.now()
    n_days_ago = today - timedelta(days=n)
    s1 = n_days_ago.strftime("%Y-%m-%d")
    s2 = today.strftime("%Y-%m-%d")
    return s1, s2


def sendMessagesToComment(botId: int, sendType: str = "comment"):
    """
    发送消息
    :param botId:机器人ID
    :param sendType 发送消息类型 comment 评论 reply 回复
    :return:
    """
    """
    1.获取机器人list
    2.获取n天前的内容和动态
    3.生成提示词并保存
    """
    aiConfig = Config.objects.filter(enabled=True).first()
    if sendType == "comment":
        contentData = Content.objects.filter(create_time__range=getFewDays(7))
        dynamicData = Dynamic.objects.filter(create_time__range=getFewDays(7))
        dataList = list(contentData) + list(dynamicData)
    else:
        commentData = Comment.objects.filter(create_time__range=getFewDays(2))
        dataList = list(commentData)
    client = LargeModelUnit(aiConfig.model, aiConfig.api_key, aiConfig.base_url)
    sum_count = dataList.__len__()
    success_count = 0
    error_count = 0
    error_list = []
    for data in dataList:
        if sendType == "reply":
            message_prompt = genterateReplyMessages(data, "comment")
        else:
            message_prompt = genterateReplyMessages(data, data.type)
        falg, message = client.generateToDeepSeek(message_prompt)
        if falg:
            success_count += 1
            saveComment(data, message, User.objects.get(id=botId), sendType)
        else:
            error_count += 1
            error_list.append(data.title)
            logger.error(f"{data.title}生成失败,原因为：{message}")
    logger.info(f"总{sum_count}条，成功{success_count}条，失败{error_count}条")
    # return


def saveComment(data: Content | Dynamic | Comment, message: str, user: User, sendType: str = "comment"):
    """
    保存评论
    :param data:
    :param sendType
    :param message:
    :param user:
    :return:
    """
    createData = Comment.objects.create()
    createData.id = createData.id
    if sendType == "comment":
        createData.parent_comment_id = 0
        createData.target_id = data.id
        createData.user_id = user.id
        createData.user_nickname = user.user_nickname
    else:
        createData.user_id = data.user_id
        createData.user_nickname = data.user_nickname
        createData.parent_comment_id = data.id
        createData.target_id = data.target_id
        createData.reply_to_user_id = user.id
        createData.reply_to_user_nickname = data.user_nickname
    createData.type = data.type if data.type == "dynamic" else "content"
    createData.content = message
    createData.like_count = 0
    createData.reply_count = 0
    createData.create_time = datetime.now()
    createData.save()
    return createData
