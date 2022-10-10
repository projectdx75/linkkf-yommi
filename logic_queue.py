# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback
import sys
import logging
import threading
import queue

# import Queue
# from .logic_queue import LogicQueue
import json
import time
from datetime import datetime
import requests

# third-party

# sjva 공용
from framework import db, scheduler, path_data
from framework.job import Job
from framework.util import Util
from framework.logger import get_logger

# 패키지
# from .plugin import package_name, logger
import system
from .model import ModelSetting, ModelLinkkf

# from plugin import LogicModuleBase, FfmpegQueueEntity, FfmpegQueue, default_route_socketio

#########################################################
package_name = __name__.split(".")[0]
logger = get_logger(package_name)

# sys.stdout.write(QueueEntity.get_entity_by_entity_id([]))


class QueueEntity:
    static_index = 1
    entity_list = []

    def __init__(self, info):
        # logger.info('info:::::>> %s', info)
        self.entity_id = info["code"]
        self.info = info
        self.url = None
        self.ffmpeg_status = -1
        self.ffmpeg_status_kor = "대기중"
        self.ffmpeg_percent = 0
        self.ffmpeg_arg = None
        self.cancel = False
        self.created_time = datetime.now().strftime("%m-%d %H:%M:%S")
        self.status = None
        QueueEntity.static_index += 1
        QueueEntity.entity_list.append(self)

    @staticmethod
    def create(info):
        for e in QueueEntity.entity_list:
            if e.info["code"] == info["code"]:
                return
        ret = QueueEntity(info)
        return ret

    @staticmethod
    def get_entity_by_entity_id(entity_id):
        ret_data = []
        # logger.debug(type(QueueEntity.entity_list))
        for _ in QueueEntity.entity_list:
            # logger.debug(type(_))
            if _.entity_id == entity_id:
                ret_data.append(_)

        # for _ in QueueEntity.entity_list:
        #     if _.entity_id == entity_id:
        #         return _
        # return None


class LogicQueue(object):
    download_queue = None
    download_thread = None
    current_ffmpeg_count = 0

    def refresh_status(self):
        self.module_logic.socketio_callback("status", self.as_dict())

    @staticmethod
    def queue_start():
        try:
            if LogicQueue.download_queue is None:
                LogicQueue.download_queue = queue.Queue()
            # LogicQueue.download_queue = Queue.Queue()
            if LogicQueue.download_thread is None:
                LogicQueue.download_thread = threading.Thread(
                    target=LogicQueue.download_thread_function, args=()
                )
                LogicQueue.download_thread.daemon = True
                LogicQueue.download_thread.start()
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    # @staticmethod
    # def download_thread_function():
    #     while True:
    #         try:
    #             entity = LogicQueue.download_queue.get()
    #             logger.debug(
    #                 "Queue receive item:%s %s", entity.title_id, entity.episode_id
    #             )
    #             # LogicAni.process(entity)
    #             LogicQueue.download_queue.task_done()
    #         except Exception as e:
    #             logger.error("Exception:%s", e)
    #             logger.error(traceback.format_exc())

    @staticmethod
    def download_thread_function():
        headers = None
        from . import plugin

        # import plugin
        while True:
            try:
                while True:
                    if LogicQueue.current_ffmpeg_count < int(
                        ModelSetting.get("max_ffmpeg_process_count")
                    ):
                        break
                    # logger.debug(LogicQueue.current_ffmpeg_count)
                    time.sleep(5)
                entity = LogicQueue.download_queue.get()

                # Todo: 고찰
                # if entity.cancel:
                #     continue

                # logger.debug(
                #     "download_thread_function()::entity.info['code'] >> %s", entity
                # )

                if entity is None:
                    continue

                # db에 해당 에피소드가 존재하는 확인
                db_entity = ModelLinkkf.get_by_linkkf_id(entity.info["code"])
                if db_entity is None:
                    episode = ModelLinkkf("auto", info=entity.info)
                    db.session.add(episode)
                    db.session.commit()
                else:
                    # episode = ModelLinkkf("auto", info=entity.info)
                    # query = db.session.query(ModelLinkkf).filter_by(episodecode=entity.info.episodecode).with_for_update().first()
                    pass

                from .logic_linkkfyommi import LogicLinkkfYommi

                # entity.url = LogicLinkkfYommi.get_video_url(
                #     entity.info['code'])
                logger.debug(f"entity.info[url] = {entity.info['url']}")
                entity.url = LogicLinkkfYommi.get_video_url(entity.info["url"])

                logger.info("entity.info: %s", entity.info["url"])
                logger.debug(f"entity.url: {entity.url}")
                # logger.info('url1: %s', entity.url[0])
                # print(entity)
                # logger.info('entity: %s', entity.__dict__)

                # logger.info('entity.url:::> %s', entity.url)
                if entity.url[0] is None:
                    LogicQueue.ffmpeg_status_kor = "URL실패"
                    plugin.socketio_list_refresh()
                    continue

                import ffmpeg

                max_pf_count = 100000
                referer = None
                save_path = ModelSetting.get("download_path")
                if ModelSetting.get("auto_make_folder") == "True":
                    program_path = os.path.join(save_path, entity.info["save_folder"])
                    save_path = program_path
                    if ModelSetting.get("linkkf_auto_make_season_folder"):
                        save_path = os.path.join(
                            save_path, "Season %s" % int(entity.info["season"])
                        )
                try:
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                except Exception as e:
                    logger.debug("program path make fail!!")

                if referer is None:
                    referer = "https://kfani.me/"

                # 파일 존재여부 체크
                if entity.url[1] is not None:
                    referer = entity.url[1]

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                        # 'Accept':
                        #     'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        # 'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                        "Referer": f"{referer}",
                    }
                    # logger.info('referer: %s', referer)

                # logger.info('filename::::>>>> %s', entity.info['filename'])
                # logger.info('파일체크::::>', os.path.join(save_path, entity.info['filename']))
                if os.path.exists(os.path.join(save_path, entity.info["filename"])):
                    entity.ffmpeg_status_kor = "파일 있음"
                    entity.ffmpeg_percent = 100
                    plugin.socketio_list_refresh()
                    continue

                headers = {
                    # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    # "Chrome/71.0.3554.0 Safari/537.36Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    # "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.0 Safari/537.36",
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                    "Referer": f"{referer}",
                }
                # logger.debug(f"referer: {referer}")

                logger.debug(f"headers::: {headers}")

                f = ffmpeg.Ffmpeg(
                    entity.url[0],
                    entity.info["filename"],
                    plugin_id=entity.entity_id,
                    listener=LogicQueue.ffmpeg_listener,
                    max_pf_count=max_pf_count,
                    #   referer=referer,
                    call_plugin=package_name,
                    save_path=save_path,
                    headers=headers,
                )
                f.start()

                LogicQueue.current_ffmpeg_count += 1
                LogicQueue.download_queue.task_done()

                # vtt file to srt file
                from framework.common.util import write_file, convert_vtt_to_srt
                from urllib import parse

                ourls = parse.urlparse(entity.url[1])
                # print(ourls)
                # logger.info('ourls:::>', ourls)
                base_url = f"{ourls.scheme}://{ourls.netloc}"
                # logger.info('base_url:::>', base_url)

                # Todo: 임시 커밋 로직 해결하면 다시 처리
                # if "linkkf.app" in base_url:
                #     base_url = f"{ourls.scheme}://kfani.me"

                # vtt_url = base_url + entity.url[2]
                # 임시
                base_url = "https://kfani.me"
                vtt_url = base_url + entity.url[2]

                logger.debug(f"srt:url => {vtt_url}")
                srt_filepath = os.path.join(
                    save_path, entity.info["filename"].replace(".mp4", ".ko.srt")
                )
                # logger.info('srt_filepath::: %s', srt_filepath)
                if entity.url[2] is not None and not os.path.exists(srt_filepath):
                    # vtt_data = requests.get(vtt_url, headers=headers).text
                    # srt_data = convert_vtt_to_srt(vtt_data)
                    # write_file(srt_data, srt_filepath)
                    res = requests.get(vtt_url, headers=headers)
                    vtt_data = res.text
                    vtt_status = res.status_code
                    logger.info('%s',vtt_status)
                    if vtt_status == 200:
                        srt_data = convert_vtt_to_srt(vtt_data)
                        write_file(srt_data, srt_filepath)
                    elif vtt_status == 404:
                        pass
                    else:
                        logger.debug("자막파일 받을수 없슴")

            except Exception as e:
                logger.error("Exception:%s", e)
                logger.error(traceback.format_exc())

    @staticmethod
    def ffmpeg_listener(**arg):
        # logger.debug(arg)
        # logger.debug(arg["plugin_id"])
        import ffmpeg

        refresh_type = None
        if arg["type"] == "status_change":
            if arg["status"] == ffmpeg.Status.DOWNLOADING:
                episode = (
                    db.session.query(ModelLinkkf)
                    .filter_by(episodecode=arg["plugin_id"])
                    .with_for_update()
                    .first()
                )
                if episode:
                    episode.ffmpeg_status = int(arg["status"])
                    episode.duration = arg["data"]["duration"]
                    db.session.commit()
            elif arg["status"] == ffmpeg.Status.COMPLETED:
                pass
            elif arg["status"] == ffmpeg.Status.READY:
                pass
        elif arg["type"] == "last":
            LogicQueue.current_ffmpeg_count += -1
            episode = (
                db.session.query(ModelLinkkf)
                .filter_by(episodecode=arg["plugin_id"])
                .with_for_update()
                .first()
            )
            if (
                arg["status"] == ffmpeg.Status.WRONG_URL
                or arg["status"] == ffmpeg.Status.WRONG_DIRECTORY
                or arg["status"] == ffmpeg.Status.ERROR
                or arg["status"] == ffmpeg.Status.EXCEPTION
            ):
                episode.etc_abort = 1
            elif arg["status"] == ffmpeg.Status.USER_STOP:
                episode.user_abort = True
                logger.debug("Status.USER_STOP received..")
            if arg["status"] == ffmpeg.Status.COMPLETED:
                episode.completed = True
                episode.end_time = datetime.now()
                episode.download_time = (episode.end_time - episode.start_time).seconds
                episode.completed_time = episode.end_time
                episode.filesize = arg["data"]["filesize"]
                episode.filename = arg["data"]["filename"]
                episode.filesize_str = arg["data"]["filesize_str"]
                episode.download_speed = arg["data"]["download_speed"]
                episode.status = "completed"
                logger.debug("Status.COMPLETED received..")
            elif arg["status"] == ffmpeg.Status.TIME_OVER:
                episode.etc_abort = 2
            elif arg["status"] == ffmpeg.Status.PF_STOP:
                episode.pf = int(arg["data"]["current_pf_count"])
                episode.pf_abort = 1
            elif arg["status"] == ffmpeg.Status.FORCE_STOP:
                episode.etc_abort = 3
            elif arg["status"] == ffmpeg.Status.HTTP_FORBIDDEN:
                episode.etc_abort = 4
            db.session.commit()
            logger.debug("LAST commit %s", arg["status"])
        elif arg["type"] == "log":
            pass
        elif arg["type"] == "normal":
            pass
        if refresh_type is not None:
            pass

        entity = QueueEntity.get_entity_by_entity_id(arg["plugin_id"])
        if entity is None:
            return
        entity.ffmpeg_arg = arg
        entity.ffmpeg_status = int(arg["status"])
        entity.ffmpeg_status_kor = str(arg["status"])
        entity.ffmpeg_percent = arg["data"]["percent"]
        entity.status = int(arg["status"])
        from . import plugin

        arg["status"] = str(arg["status"])
        plugin.socketio_callback("status", arg)

    # @staticmethod
    # def add_queue(info):
    #     try:
    #         entity = QueueEntity.create(info)
    #         if entity is not None:
    #             LogicQueue.download_queue.put(entity)
    #             return True
    #     except Exception as e:
    #         logger.error("Exception:%s", e)
    #         logger.error(traceback.format_exc())
    #     return False
    @staticmethod
    def add_queue(info):
        try:

            # Todo:
            # if is_exist(info):
            #     return 'queue_exist'
            # logger.debug("add_queue()::info >> %s", info)
            # logger.debug("info::", info["_id"])

            # episode[] code (episode_code)
            db_entity = ModelLinkkf.get_by_linkkf_id(info["code"])
            # logger.debug("add_queue:: db_entity >> %s", db_entity)

            if db_entity is None:
                entity = QueueEntity.create(info)

                # logger.debug("add_queue()::entity >> %s", entity)
                LogicQueue.download_queue.put(entity)
                return "enqueue_db_append"
            elif db_entity.status != "completed":
                entity = QueueEntity.create(info)
                # return "Debugging"
                LogicQueue.download_queue.put(entity)

                logger.debug("add_queue()::enqueue_db_exist")
                return "enqueue_db_exist"
            else:
                return "db_completed"

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
        return False

    @staticmethod
    def program_auto_command(req):
        try:
            from . import plugin

            command = req.form["command"]
            entity_id = int(req.form["entity_id"])
            logger.debug("command :%s %s", command, entity_id)
            entities = QueueEntity.get_entity_by_entity_id(entity_id)
            logger.debug("entity::> %s", entities)

            # logger.info('logic_queue:: entity', entity)

            ret = {}
            if command == "cancel":
                if entities.status == -1:
                    entities.cancel = True
                    entities.status_kor = "취소"
                    plugin.socketio_list_refresh()
                    ret["ret"] = "refresh"
                elif entities.status != 5:
                    ret["ret"] = "notify"
                    ret["log"] = "다운로드 중인 상태가 아닙니다."
                else:
                    idx = entities.ffmpeg_arg["data"]["idx"]
                    import ffmpeg

                    ffmpeg.Ffmpeg.stop_by_idx(idx)
                    plugin.socketio_list_refresh()
                    ret["ret"] = "refresh"
            elif command == "reset":
                if LogicQueue.download_queue is not None:
                    with LogicQueue.download_queue.mutex:
                        LogicQueue.download_queue.queue.clear()
                    for _ in QueueEntity.entity_list:
                        if _.ffmpeg_status == 5:
                            import ffmpeg

                            idx = _.ffmpeg_arg["data"]["idx"]
                            ffmpeg.Ffmpeg.stop_by_idx(idx)
                QueueEntity.entity_list = []
                plugin.socketio_list_refresh()
                ret["ret"] = "refresh"
            elif command == "delete_completed":
                new_list = []
                for _ in QueueEntity.entity_list:
                    if _.ffmpeg_status_kor in ["파일 있음", "취소"]:
                        continue
                    if _.ffmpeg_status != 7:
                        new_list.append(_)
                QueueEntity.entity_list = new_list
                plugin.socketio_list_refresh()
                ret["ret"] = "refresh"

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            ret["ret"] = "notify"
            ret["log"] = str(e)
        return ret
