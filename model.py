# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback
import json
from datetime import datetime

# third-party
from sqlalchemy import or_, and_, func, not_, desc

# sjva 공용
from framework.logger import get_logger
from framework import db, app, path_app_root
from framework.util import Util

# 패키지
# from .plugin import package_name, logger

package_name = __name__.split('.')[0]
logger = get_logger(package_name)
db_file = os.path.join(path_app_root, 'data', 'db', '%s.db' % package_name)
app.config['SQLALCHEMY_BINDS'][package_name] = 'sqlite:///%s' % (db_file)


class ModelSetting(db.Model):
    __tablename__ = 'plugin_%s_setting' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String, nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @staticmethod
    def get(key):
        try:
            return db.session.query(ModelSetting).filter_by(key=key).first().value.strip()
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())

    # @staticmethod
    # def get_bool(key):
    #     try:
    #         return (ModelSetting.get(key) == 'True')
    #     except Exception as exception:
    #         logger.error('Exception:%s %s', exception, key)
    #         logger.error(traceback.format_exc())


class ModelLinkkfProgram(db.Model):
    __tablename__ = 'plugin_%s_program' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    contents_json = db.Column(db.JSON)
    created_time = db.Column(db.DateTime)

    programcode = db.Column(db.String)

    save_folder = db.Column(db.String)
    season = db.Column(db.Integer)

    def __init__(self, data):
        self.created_time = datetime.now()
        self.programcode = data['code']
        self.save_folder = data['title']
        self.season = data['season']

    def __repr__(self):
        # return "<Episode(id:%s, episode_code:%s, quality:%s)>" % (self.id, self.episode_code, self.quality)
        return repr(self.as_dict())

    def as_dict(self):
        ret = {x.name: getattr(self, x.name) for x in self.__table__.columns}
        return ret

    def set_info(self, data):
        self.contents_json = data
        self.programcode = data['code']
        self.save_folder = data['save_folder']
        self.season = data['season']


class ModelLinkkf(db.Model):
    __tablename__ = 'plugin_%s_auto_episode' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    contents_json = db.Column(db.JSON)
    created_time = db.Column(db.DateTime)

    programcode = db.Column(db.String)
    episodecode = db.Column(db.String)
    filename = db.Column(db.String)
    duration = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    download_time = db.Column(db.Integer)
    completed = db.Column(db.Boolean)
    user_abort = db.Column(db.Boolean)
    pf_abort = db.Column(db.Boolean)
    etc_abort = db.Column(db.Integer)  # ffmpeg 원인 1, 채널, 프로그램
    ffmpeg_status = db.Column(db.Integer)
    temp_path = db.Column(db.String)
    save_path = db.Column(db.String)
    pf = db.Column(db.Integer)
    retry = db.Column(db.Integer)
    filesize = db.Column(db.Integer)
    filesize_str = db.Column(db.String)
    download_speed = db.Column(db.String)
    call = db.Column(db.String)

    def __init__(self, call, info):
        self.created_time = datetime.now()
        self.completed = False
        self.start_time = datetime.now()
        self.user_abort = False
        self.pf_abort = False
        self.etc_abort = 0
        self.ffmpeg_status = -1
        self.pf = 0
        self.retry = 0
        self.call = call
        self.set_info(info)
        # logger.info(str(self))

    def __repr__(self):
        # return "<Episode(id:%s, episode_code:%s, quality:%s)>" % (self.id, self.episode_code, self.quality)
        return repr(self.as_dict())

    def as_dict(self):
        ret = {x.name: getattr(self, x.name) for x in self.__table__.columns}
        return ret

    def set_info(self, data):
        self.contents_json = data
        self.programcode = data['program_code']
        self.episodecode = data['code']

    @classmethod
    def web_list(cls, req):
        ret = {}
        page = int(req.form['page']) if 'page' in req.form else 1
        page_size = 30
        job_id = ''
        search = req.form['search_word'] if 'search_word' in req.form else ''
        option = req.form['option'] if 'option' in req.form else 'all'
        order = req.form['order'] if 'order' in req.form else 'desc'
        query = cls.make_query(search=search, order=order, option=option)
        count = query.count()
        query = query.limit(page_size).offset((page-1)*page_size)
        lists = query.all()
        ret['list'] = [item.as_dict() for item in lists]
        ret['paging'] = Util.get_paging_info(count, page, page_size)
        return ret

    @classmethod
    def make_query(cls, search='', order='desc', option='all'):
        query = db.session.query(cls)
        if search is not None and search != '':
            if search.find('|') != -1:
                tmp = search.split('|')
                conditions = []
                for tt in tmp:
                    if tt != '':
                        conditions.append(cls.filename.like('%'+tt.strip()+'%') )
                query = query.filter(or_(*conditions))
            elif search.find(',') != -1:
                tmp = search.split(',')
                for tt in tmp:
                    if tt != '':
                        query = query.filter(cls.filename.like('%'+tt.strip()+'%'))
            else:
                query = query.filter(cls.filename.like('%'+search+'%'))
        if option == 'completed':
            query = query.filter(cls.status == 'completed')

        query = query.order_by(desc(cls.id)) if order == 'desc' else query.order_by(cls.id)
        return query
#########################################################
