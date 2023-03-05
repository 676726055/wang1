# -*- coding: utf-8 -*

import json

import logging

import os

import sys

import requests

logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_configs():

   if "MI_STEP" in os.environ:

       configs = os.environ['MI_STEP']

       if len(configs) > 0:

           try:

               return json.loads(configs)

           except Exception as e:

               logging.error(f"MI_STEP变量格式错误: {e}")

               sys.exit(1)

       else:

           logging.info("MI_STEP变量未启用")

           sys.exit(1)

   else:

       logging.info("未添加MI_STEP变量")

       sys.exit(0)

def sign_in(config):

   phone = config.get('phone')

   body = {'phone': phone, 'password': config.get('password'), "step": config.get('step')}

   try:

       res = requests.post("http://gateway.500error.cn:30000/ap/sign-in/mi-step", json=body).json()

       data = res.get('data')

       if data == 0:

           logging.info(phone + res.data)

       else:

           logging.info(phone + ": " + res.get('msg'))

   except Exception as e:

       logging.error(f"接口异常: {e}")

if __name__ == '__main__':

   configs = get_configs()

   for config in configs:

       sign_in(config)

   sys.exit(0)
