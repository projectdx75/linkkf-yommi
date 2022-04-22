# -*- coding: utf-8 -*-
#########################################################
# python
import os
import sys
import traceback
import logging
import threading
import time

# third-party
from sqlalchemy import desc

# sjva 공용
from framework import db, scheduler, path_data
from framework.job import Job
from framework.util import Util
from framework.logger import get_logger

# 패키지
# from .plugin import package_name, logger
from .model import ModelSetting
from .logic_queue import LogicQueue
from .logic_linkkfyommi import LogicLinkkfYommi

#########################################################
package_name = __name__.split(".")[0]
logger = get_logger(package_name)


class Logic(object):
    db_default = {
        "linkkf_url": "https://linkkf.app",
        "download_path": os.path.join(path_data, "linkkf-yommi"),
        "linkkf_auto_make_folder": "True",
        "linkkf_auto_make_season_folder": "True",
        "linkkf_finished_insert": "[완결]",
        "include_date": "False",
        "date_option": "0",  # 0:YYMMDD, 1:YYYY-MM-DD
        "auto_make_folder": "True",
        "max_ffmpeg_process_count": "4",
        "auto_interval": "* 20 * * *",
        "auto_start": "False",
        "whitelist_program": "",
    }

    @staticmethod
    def db_init():
        try:
            logger.debug(Logic.db_default.items())
            for key, value in Logic.db_default.items():
                logger.debug(f"{key}: {value}")
                if db.session.query(ModelSetting).filter_by(key=key).count() == 0:
                    db.session.add(ModelSetting(key, value))
            db.session.commit()
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def plugin_load():
        try:
            logger.debug("%s plugin_load", package_name)
            # DB 초기화
            Logic.db_init()

            if ModelSetting.get("auto_start") == "True":
                Logic.scheduler_start()

            # 편의를 위해 json 파일 생성
            from .plugin import plugin_info

            Util.save_from_dict_to_json(
                plugin_info, os.path.join(os.path.dirname(__file__), "info.json")
            )
            LogicQueue.queue_start()
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def plugin_unload():
        try:
            logger.debug("%s plugin_unload", package_name)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_start():
        try:
            interval = ModelSetting.get("auto_interval")
            job = Job(
                package_name,
                package_name,
                interval,
                Logic.scheduler_function,
                "linkkf 다운로드",
                True,
            )
            scheduler.add_job_instance(job)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_stop():
        try:
            scheduler.remove_job(package_name)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def setting_save(req):
        try:
            for key, value in req.form.items():
                logger.debug("Key:%s Value:%s", key, value)
                entity = (
                    db.session.query(ModelSetting)
                    .filter_by(key=key)
                    .with_for_update()
                    .first()
                )
                entity.value = value
            db.session.commit()
            return True
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            logger.error("key:%s value:%s", key, value)
            return False

    @staticmethod
    def scheduler_function():
        try:
            LogicLinkkfYommi.scheduler_function()
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    # 기본 구조 End
    ##################################################################
