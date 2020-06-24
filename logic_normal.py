# -*- coding: utf-8 -*-
#########################################################
# python
import os
import sys
import traceback
import time
from datetime import datetime, timedelta
import logging
import urllib
import urllib2
import re
import json

# third-party
import requests
from flask import Blueprint, request, Response, send_file, render_template, redirect, jsonify
from sqlalchemy import desc
from lxml import html

# sjva 공용
from framework import db, scheduler
from framework.job import Job
from framework.util import Util
from system import SystemLogicTrans
import framework.common.fileprocess as FileProcess

# 패키지
from .plugin import logger, package_name
from .model import ModelSetting
#########################################################

class LogicNormal(object):


    @staticmethod
    def proxy_init():
        try:
            logger.debug(FileProcess.Vars.proxies)
            if ModelSetting.get_bool('use_proxy'):
                tmp = ModelSetting.get('proxy_url')
                FileProcess.Vars.proxies = { 
                    "http"  : tmp, 
                    "https" : tmp, 
                }
            else:
                FileProcess.Vars.proxies = None
            logger.debug(FileProcess.Vars.proxies)
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    ########################################################
    
    


    @staticmethod
    def test(req):
        try:
            target = req.form['target']
            keyword = req.form['test']
            if target == 'dmm':
                return LogicNormal.test_dmm(keyword)
            elif target == 'javdb':
                return LogicNormal.test_javdb(keyword)
            elif target == 'avgle':
                return LogicNormal.test_avgle(keyword)
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def test_dmm(keyword):
        try:
            ret = {}
            ret['search'] = FileProcess.dmm_search(keyword)
            if len(ret['search']) == 1:
                ret['update'] = FileProcess.dmm_update(ret['search'][0]['id'], use_discord_proxy=ModelSetting.get_bool('use_discord_proxy'))
            else:
                for tmp in ret['search']:
                    if tmp['score'] == 100:
                        ret['update'] = FileProcess.dmm_update(tmp['id'])
                        break
            return ret
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())


    @staticmethod
    def test_javdb(keyword):
        try:
            ret = {}
            ret['search'] = FileProcess.javdb_search(keyword)
            if len(ret['search']) == 1:
                ret['update'] = FileProcess.javdb_update(ret['search'][0]['id'])
            else:
                for tmp in ret['search']:
                    if tmp['score'] == 100:
                        ret['update'] = FileProcess.javdb_update(tmp['id'])
                        break
            return ret
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return False

    
    
    @staticmethod
    def test_avgle(keyword):
        try:
            ret = {}
            ret['search'] = LogicNormal.avgle_search(keyword)
            
            if len(ret['search']['response']['videos']) >= 1:
                ret['update'] = LogicNormal.avgle_update(ret['search']['response']['videos'][0]['vid'])
            return ret
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return False

    @staticmethod
    def avgle_search(keyword):
        try:
            session = requests.Session()
            url = 'https://api.avgle.com/v1/jav/%s/0?limit=10' % keyword
            response = session.get(url, headers=LogicNormal.headers, proxies=LogicNormal.proxies)
            data = response.json()
            return data
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def avgle_update(vid):
        try:
            session = requests.Session()
            url = 'https://api.avgle.com/v1/video/%s' % vid
            response = session.get(url, headers=LogicNormal.headers, proxies=LogicNormal.proxies)
            data = response.json()
            return data
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return False


    ########################################################
    