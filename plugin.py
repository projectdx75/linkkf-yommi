# -*- coding: utf-8 -*-
#########################################################
# 고정영역
#########################################################
# python
import os
import sys
import traceback
import json

# third-party
from flask import (
    Blueprint,
    request,
    Response,
    render_template,
    redirect,
    jsonify,
    url_for,
    send_from_directory,
)
from flask_login import login_required
from flask_socketio import SocketIO, emit, send

# sjva 공용
from framework.logger import get_logger
from framework import app, db, scheduler, socketio, path_app_root
from framework.util import Util, AlchemyEncoder
from system.logic import SystemLogic

# 패키지

from .logic import Logic
from .logic_linkkfyommi import LogicLinkkfYommi
from .logic_queue import QueueEntity, LogicQueue
from .model import ModelSetting, ModelLinkkf

# blueprint = Blueprint(package_name,
#                       package_name,
#                       url_prefix='/%s' % package_name,
#                       template_folder=os.path.join(os.path.dirname(__file__),
#                                                    'templates'))

package_name = __name__.split(".")[0]
logger = get_logger(package_name)

#########################################################
# 플러그인 공용
#########################################################
blueprint = Blueprint(
    package_name,
    package_name,
    url_prefix="/%s" % package_name,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)


def plugin_load():
    Logic.plugin_load()


def plugin_unload():
    Logic.plugin_unload()


# 메뉴 구성.
menu = {
    "main": [package_name, "linkkf-yommi"],
    "sub": [
        ["setting", "설정"],
        ["request", "요청"],
        ["category", "검색"],
        ["queue", "큐"],
        ["list", "목록"],
        ["log", "로그"],
    ],
    "category": "vod",
    # 'sub2': {
    #     'linkkf-yommi': [
    #             ['setting', u'설정'], ['request', u'요청'], ['queue', u'큐'], ['list', u'목록']
    #         ],
    # }
}

plugin_info = {
    "version": "0.3.0.0",
    "name": "linkkf-yommi",
    "category_name": "vod",
    "icon": "",
    "developer": "projectdx && persuade",
    "description": "linkkf 사이트에서 애니 다운로드",
    "home": "https://github.com/projectdx75/linkkf-yommi",
    "more": "",
}


#########################################################


# def plugin_load():
#     Logic.plugin_load()
#     #
#     # LogicQueue.queue_load()
#
#
# def plugin_unload():
#     Logic.plugin_unload()


#########################################################
# WEB Menu
#########################################################
@blueprint.route("/")
def home():
    # return redirect('/%s/setting' % package_name)
    return redirect("/%s/category" % package_name)


@blueprint.route("/<sub>")
@login_required
def detail(sub):
    if sub == "setting":
        setting_list = db.session.query(ModelSetting).all()
        arg = Util.db_list_to_dict(setting_list)
        arg["package_name"] = package_name
        arg["sub"] = "setting"
        arg["scheduler"] = str(scheduler.is_include(package_name))
        arg["is_running"] = str(scheduler.is_running(package_name))
        return render_template("%s_%s.html" % (package_name, sub), arg=arg)
    elif sub in ["request", "queue", "list"]:
        setting_list = db.session.query(ModelSetting).all()
        arg = Util.db_list_to_dict(setting_list)
        arg["package_name"] = package_name
        arg["current_code"] = (
            LogicLinkkfYommi.current_data["code"]
            if LogicLinkkfYommi.current_data is not None
            else ""
        )
        return render_template("%s_%s.html" % (package_name, sub), arg=arg)
    elif sub == "category":
        setting_list = db.session.query(ModelSetting).all()
        arg = Util.db_list_to_dict(setting_list)
        arg["package_name"] = package_name
        return render_template("%s_%s.html" % (package_name, sub), arg=arg)
    elif sub == "log":
        return render_template("log.html", package=package_name)
    return render_template("sample.html", title="%s - %s" % (package_name, sub))


#########################################################
# For UI (보통 웹에서 요청하는 정보에 대한 결과를 리턴한다.)
#########################################################
@blueprint.route("/ajax/<sub>", methods=["GET", "POST"])
def ajax(sub):
    logger.debug("AJAX %s %s", package_name, sub)
    if sub == "setting_save":
        try:
            ret = Logic.setting_save(request)
            return jsonify(ret)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "scheduler":
        go = request.form["scheduler"]
        logger.debug("scheduler :%s", go)
        if go == "true":
            Logic.scheduler_start()
        else:
            Logic.scheduler_stop()
        return jsonify(go)
    # 요청
    elif sub == "analysis":
        try:

            code = request.form["code"]
            data = LogicLinkkfYommi.get_title_info(code)
            # logger.debug("data::> %s", data)
            # current_data = data

            # return jsonify(data)
            if data["ret"] == "error":
                return jsonify(data)
            else:
                return jsonify({"ret": "success", "data": data})
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            # except IndexError as e:
            #     logger.error("Exception:%s", e)
            #     logger.error(traceback.format_exc())
            return jsonify({"ret": "error", "log": e})
    elif sub == "search":
        try:
            query = request.form["query"]
            logger.debug("query::>> %s", query)
            data = LogicLinkkfYommi.get_search_result(str(query))

            return jsonify(data)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "anime_list":
        try:
            # logger.debug(request.form)
            page = request.form["page"]
            cate = request.form["type"]
            # data = LogicLinkkfYommi.get_screen_movie_info(page)
            data = LogicLinkkfYommi.get_anime_list_info(cate, page)
            dummy_data = {"ret": "success", "data": data}
            return jsonify(data)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "airing_list":
        try:
            data = LogicLinkkfYommi.get_airing_info()
            # dummy_data = {"ret": "success", "data": data}
            logger.debug(f"airing_list:: {data}")
            return jsonify(data)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    elif sub == "screen_movie_list":
        try:
            logger.debug("request:::> %s", request.form["page"])
            page = request.form["page"]
            data = LogicLinkkfYommi.get_screen_movie_info(page)
            dummy_data = {"ret": "success", "data": data}
            return jsonify(data)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "complete_anilist":
        try:
            logger.debug("request:::> %s", request.form["page"])
            page = request.form["page"]
            data = LogicLinkkfYommi.get_complete_anilist_info(page)
            dummy_data = {"ret": "success", "data": data}
            return jsonify(data)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "apply_new_title":
        try:
            new_title = request.form["new_title"]
            ret = LogicLinkkfYommi.apply_new_title(new_title)
            return jsonify(ret)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "apply_new_season":
        try:
            new_season = request.form["new_season"]
            ret = LogicLinkkfYommi.apply_new_season(new_season)
            return jsonify(ret)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "add_whitelist":
        try:
            # params = request.get_data()
            # logger.debug(f"params: {params}")
            # data_code = request.args.get("data_code")
            params = request.get_json()
            logger.debug(params)
            if params is not None:
                code = params["data_code"]
                logger.debug(f"params: {code}")
                ret = LogicLinkkfYommi.add_whitelist(code)
            else:
                ret = LogicLinkkfYommi.add_whitelist()
            return jsonify(ret)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
    elif sub == "add_queue":
        try:
            ret = {}
            # info = json.loads(request.form["data"])
            # logger.info("test::", info)
            # logger.info("_id", info["_id"])
            # return False

            code = request.form["code"]
            # 해당 code로 db조회후 info 변수에 담는다
            info = LogicLinkkfYommi.get_info_by_code(code)
            # info = LogicLinkkfYommi.get_info_by_code(info)
            # logger.debug(info)
            # return False

            logger.debug(f"info::> {info}")

            # ret["ret"] = "debugging"

            if info is not None:
                from .logic_queue import LogicQueue

                tmp = LogicQueue.add_queue(info)
                logger.debug("add_queue : tmp >> %s", tmp)
                # ret["ret"] = "success" if tmp else "fail"
                ret["ret"] = tmp
            else:
                ret["ret"] = "no_data"
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            ret["ret"] = "fail"
            ret["log"] = str(e)
        return jsonify(ret)
    elif sub == "add_queue_checked_list":
        ret = {}
        try:
            from .logic_queue import LogicQueue

            code = request.form["code"]
            code_list = code.split(",")
            count = 0
            for c in code_list:
                info = LogicLinkkfYommi.get_info_by_code(c)
                if info is not None:
                    tmp = LogicQueue.add_queue(info)
                    count += 1
            ret["ret"] = "success"
            ret["log"] = str(count)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            ret["ret"] = "fail"
            ret["log"] = str(e)
        return jsonify(ret)
    # 큐
    elif sub == "program_auto_command":
        try:
            from .logic_queue import LogicQueue

            ret = LogicQueue.program_auto_command(request)
            return jsonify(ret)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    elif sub == "web_list":
        try:
            logger.info(request)
            data = []
            logger.info("db :::>", ModelLinkkf.web_list(request))
            data = [{}]
            dummy_data = {"ret": "success", "method": "web_list", "data": data}
            return jsonify(ModelLinkkf.web_list(request))
            # return jsonify(dummy_data)
        except Exception as e:
            logger.error("Exception: %s", e)
            logger.error(traceback.format_exc())
    elif sub == "db_remove":
        return jsonify(ModelLinkkf.delete_by_id(request.form["id"]))
    # reset_db
    elif sub == "reset_db":
        ret = {}
        res = False
        try:
            res = LogicLinkkfYommi.reset_db()
            if res:
                ret["ret"] = "success"

            return jsonify(ret)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())


#########################################################
# API
#########################################################
@blueprint.route("/api/<sub>", methods=["GET", "POST"])
def api(sub):
    logger.debug("api %s %s", package_name, sub)


#########################################################
# socketio
#########################################################
sid_list = []


@socketio.on("connect", namespace="/%s" % package_name)
def connect():
    try:
        sid_list.append(request.sid)
        tmp = None
        from .logic_queue import QueueEntity

        data = [_.__dict__ for _ in QueueEntity.entity_list]
        tmp = json.dumps(data, cls=AlchemyEncoder)
        tmp = json.loads(tmp)
        emit("on_connect", tmp, namespace="/%s" % package_name)
    except Exception as e:
        logger.error("Exception:%s", e)
        logger.error(traceback.format_exc())


@socketio.on("disconnect", namespace="/%s" % package_name)
def disconnect():
    try:
        sid_list.remove(request.sid)
    except Exception as e:
        logger.error("Exception:%s", e)
        logger.error(traceback.format_exc())


def socketio_callback(cmd, data):
    if sid_list:
        tmp = json.dumps(data, cls=AlchemyEncoder)
        tmp = json.loads(tmp)
        socketio.emit(cmd, tmp, namespace="/%s" % package_name, broadcast=True)


def socketio_list_refresh():
    data = [_.__dict__ for _ in QueueEntity.entity_list]
    tmp = json.dumps(data, cls=AlchemyEncoder)
    tmp = json.loads(tmp)
    socketio_callback("list_refresh", tmp)
