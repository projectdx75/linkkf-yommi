# -*- coding: utf-8 -*-
#########################################################
# python
import os
import sys
import traceback
import logging
import threading
import time
import re
import random
# import urlparse
from urllib.parse import urlparse
import json
# third-party
import requests
from lxml import html

# sjva 공용
from framework import db, scheduler, path_data
from framework.job import Job
from framework.util import Util
from framework.logger import get_logger

# 패키지
# from .plugin import package_name, logger
# from anime_downloader.logic_ohli24 import ModelOhli24Item
from .model import ModelSetting, ModelLinkkf, ModelLinkkfProgram
from .logic_queue import LogicQueue

#########################################################
package_name = __name__.split('.')[0]
logger = get_logger(package_name)


class LogicLinkkfYommi(object):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 '
            'Safari/537.36',
        'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    session = None
    referer = None
    current_data = None

    @staticmethod
    def get_html(url):
        try:
            if LogicLinkkfYommi.session is None:
                LogicLinkkfYommi.session = requests.Session()
            LogicLinkkfYommi.headers['referer'] = LogicLinkkfYommi.referer
            LogicLinkkfYommi.referer = url
            page = LogicLinkkfYommi.session.get(
                url, headers=LogicLinkkfYommi.headers)
            # logger.info("page", page)

            return page.content.decode('utf8')
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_video_url_from_url(url, url2):
        video_url = None
        referer_url = None
        vtt_url = None
        LogicLinkkfYommi.referer = url
        # logger.info("dx: url", url)
        # logger.info("dx: urls2", url2)

        # logger.info("dx download url : %s , url2 : %s" % (url, url2))
        try:
            if 'kfani' in url2:
                # kfani 계열 처리 => 방문해서 m3u8을 받아온다.

                data = LogicLinkkfYommi.get_html(url2)
                # print(data)
                # logger.info("dx: data", data)
                regex2 = r'"([^\"]*m3u8)"|<source[^>]+src=\"([^"]+)'

                temp_url = re.findall(regex2, data)[0]
                video_url = ''
                ref = 'https://kfani.me'
                for i in temp_url:
                    # print(i)
                    if i is None:
                        continue
                    video_url = i
                    # video_url = '{1} -headers \'Referer: "{0}"\' -user_agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.0 Safari/537.36"'.format(ref, video_url)

                match = re.compile(r'<track.+src\=\"(?P<vtt_url>.*?.vtt)').search(data)
                # logger.info("match group: %s", match.group('vtt_url'))
                vtt_url = match.group('vtt_url')
                # logger.info("vtt_url: %s", vtt_url)
                referer_url = LogicLinkkfYommi.referer

            elif 'kftv' in url2:
                # kftv 계열 처리 => url의 id로 https://yt.kftv.live/getLinkStreamMd5/df6960891d226e24b117b850b44a2290 페이지
                # 접속해서 json 받아오고, json에서 url을 추출해야함
                if '=' in url2:
                    md5 = urlparse.urlparse(url2).query.split('=')[1]
                elif 'embedplay' in url2:
                    md5 = url2.split('/')[-1]
                url3 = 'https://yt.kftv.live/getLinkStreamMd5/' + md5
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                data3 = LogicLinkkfYommi.get_html(url3)
                data3dict = json.loads(data3)
                # print(data3dict)
                video_url = data3dict[0]['file']

            elif ('linkkf' in url2):
                # linkkf 계열 처리 => URL 리스트를 받아오고, 하나 골라 방문해서 m3u8을 받아온다.
                referer_url = url
                data2 = LogicLinkkfYommi.get_html(url2)
                # print(data2)
                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                # logger.info("cat: %s", cat)
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("url3: %s", url3)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                if 'kftv' in url3:
                    return LogicLinkkfYommi.get_video_url_from_url(url2, url3)
                elif url3.startswith('/'):
                    url3 = urlparse.urljoin(url2, url3)
                    print('url3 = ', url3)
                    LogicLinkkfYommi.referer = url2
                    data3 = LogicLinkkfYommi.get_html(url3)
                    # print(data3)
                    # logger.info('data3: %s', data3)
                    # regex2 = r'"([^\"]*m3u8)"'
                    regex2 = r'"([^\"]*mp4|m3u8)"'
                    video_url = re.findall(regex2, data3)[0]
                    # logger.info('video_url: %s', video_url)
                    referer_url = url3

                else:
                    logger.error("새로운 유형의 url 발생! %s %s %s" %
                                 (url, url2, url3))
            elif 'kakao' in url2:
                # kakao 계열 처리, 외부 API 이용
                payload = {'inputUrl': url2}
                kakaoUrl = 'http://webtool.cusis.net/wp-pages/download-kakaotv-video/video.php'
                data2 = requests.post(
                    kakaoUrl,
                    json=payload,
                    headers={
                        'referer':
                            'http://webtool.cusis.net/download-kakaotv-video/'
                    }).content
                time.sleep(3)  # 서버 부하 방지를 위해 단시간에 너무 많은 URL전송을 하면 IP를 차단합니다.
                url3 = json.loads(data2)
                # logger.info("download url2 : %s , url3 : %s" % (url2, url3))
                video_url = url3
            elif '#V' in url2:  # V 패턴 추가
                print('#v routine')

                data2 = LogicLinkkfYommi.get_html(url2)
                # print(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                if 'kftv' in url3:
                    return LogicLinkkfYommi.get_video_url_from_url(url2, url3)
                elif url3.startswith('/'):
                    url3 = urlparse.urljoin(url2, url3)
                    LogicLinkkfYommi.referer = url2
                    data3 = LogicLinkkfYommi.get_html(url3)
                    # print("내용: %s", data3)
                    # logger.info("movie content: %s", data3)
                    # print(data)
                    # regex2 = r'"([^\"]*m3u8)"'
                    regex2 = r'"([^\"]*mp4)"'
                    video_url = re.findall(regex2, data3)[0]
                else:
                    logger.error("새로운 유형의 url 발생! %s %s %s" %
                                 (url, url2, url3))

            elif '#M2' in url2:
                LogicLinkkfYommi.referer = url
                data2 = LogicLinkkfYommi.get_html(url2)
                # print(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                if 'kftv' in url3:
                    return LogicLinkkfYommi.get_video_url_from_url(url2, url3)
                elif url3.startswith('/'):
                    url3 = urlparse.urljoin(url2, url3)
                    LogicLinkkfYommi.referer = url2
                    data3 = LogicLinkkfYommi.get_html(url3)
                    # print("내용: %s", data3)
                    # logger.info("movie content: %s", data3)
                    # regex2 = r'"([^\"]*m3u8)"'
                    regex2 = r'"([^\"]*mp4)"'
                    video_url = re.findall(regex2, data3)[0]
                else:
                    logger.error("새로운 유형의 url 발생! %s %s %s" %
                                 (url, url2, url3))
            elif '😀#i' in url2:
                LogicLinkkfYommi.referer = url
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))

            elif '#k' in url2:
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))

            elif '#k2' in url2:
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
            elif 'mopipi' in url2:
                LogicLinkkfYommi.referer = url
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)
                match = re.compile(
                    r'src\=\"(?P<video_url>http.*?\.mp4)').search(data2)
                video_url = match.group('video_url')

                match = re.compile(
                    r'src\=\"(?P<vtt_url>http.*?.vtt').search(data2)
                logger.info("match group: %s", match.group('video_url'))
                vtt_url = match.group('vtt_url')

                # logger.info("download url : %s , url3 : %s" % (url, url3))

            else:
                logger.error("새로운 유형의 url 발생! %s %s" % (url, url2))
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

        return [video_url, referer_url, vtt_url]

    @staticmethod
    def get_video_url(episode_id):
        try:
            # url = urlparse.urljoin(ModelSetting.get('linkkf_url'), episode_id)
            url = episode_id
            # logger.info("url: %s" % url)
            data = LogicLinkkfYommi.get_html(url)
            # logger.info(data)
            tree = html.fromstring(data)
            url2s = [
                tag.attrib['value'] for tag in tree.xpath(
                    '//*[@id="body"]/div/span/center/select/option')
            ]
            # url2s = filter(lambda url:
            #         ('kfani' in url) |
            #         ('linkkf' in url) |
            #         ('kftv' in url), url2s)
            # url2 = random.choice(url2s)

            # logger.info('dx: url', url)
            # logger.info('dx: urls2', url2s)

            video_url = None
            referer_url = None  # dx

            for url2 in url2s:
                try:
                    if video_url is not None:
                        continue
                    ret = LogicLinkkfYommi.get_video_url_from_url(url, url2)
                    # print(f'ret::::> {ret}')

                    if ret is not None:
                        video_url = ret
                        referer_url = url2
                except Exception as e:
                    logger.error('Exception:%s', e)
                    logger.error(traceback.format_exc())

            logger.info(video_url)

            # return [video_url, referer_url]
            return video_url
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def apply_new_title(new_title):
        try:
            ret = {}
            if LogicLinkkfYommi.current_data is not None:
                program = db.session.query(ModelLinkkfProgram) \
                    .filter_by(programcode=LogicLinkkfYommi.current_data['code']) \
                    .first()
                new_title = Util.change_text_for_use_filename(new_title)
                LogicLinkkfYommi.current_data['save_folder'] = new_title
                program.save_folder = new_title
                db.session.commit()

                for entity in LogicLinkkfYommi.current_data['episode']:
                    entity['save_folder'] = new_title
                    entity['filename'] = LogicLinkkfYommi.get_filename(
                        LogicLinkkfYommi.current_data['save_folder'],
                        LogicLinkkfYommi.current_data['season'],
                        entity['title'])
                #    tmp = data['filename'].split('.')
                #    tmp[0] = new_title
                #    data['filename'] = '.'.join(tmp)
                return LogicLinkkfYommi.current_data
            else:
                ret['ret'] = False
                ret['log'] = 'No current data!!'
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            ret['ret'] = False
            ret['log'] = str(e)
        return ret

    @staticmethod
    def apply_new_season(new_season):
        try:
            ret = {}
            season = int(new_season)
            if LogicLinkkfYommi.current_data is not None:
                program = db.session.query(ModelLinkkfProgram) \
                    .filter_by(programcode=LogicLinkkfYommi.current_data['code']) \
                    .first()
                LogicLinkkfYommi.current_data['season'] = season
                program.season = season
                db.session.commit()

                for entity in LogicLinkkfYommi.current_data['episode']:
                    entity['filename'] = LogicLinkkfYommi.get_filename(
                        LogicLinkkfYommi.current_data['save_folder'],
                        LogicLinkkfYommi.current_data['season'],
                        entity['title'])
                return LogicLinkkfYommi.current_data
            else:
                ret['ret'] = False
                ret['log'] = 'No current data!!'
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            ret['ret'] = False
            ret['log'] = str(e)
        return ret

    @staticmethod
    def add_whitelist():
        ret = {}
        try:
            code = str(LogicLinkkfYommi.current_data['code'])
            whitelist_program = ModelSetting.get('whitelist_program')
            whitelist_programs = [
                str(x.strip().replace(' ', ''))
                for x in whitelist_program.replace('\n', ',').split(',')
            ]
            if (code not in whitelist_programs):
                whitelist_programs.append(code)
                whitelist_programs = filter(
                    lambda x: x != '', whitelist_programs)  # remove blank code
                whitelist_program = ','.join(whitelist_programs)
                entity = db.session.query(ModelSetting).filter_by(
                    key='whitelist_program').with_for_update().first()
                entity.value = whitelist_program
                db.session.commit()
                return LogicLinkkfYommi.current_data
            else:
                ret['ret'] = False
                ret['log'] = "이미 추가되어 있습니다."
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            ret['ret'] = False
            ret['log'] = str(e)
        return ret

    @staticmethod
    def get_airing_info():
        try:
            url = f"{ModelSetting.get('linkkf_url')}/airing"
            html_content = LogicLinkkfYommi.get_html(url)
            tree = html.fromstring(html_content)
            tmp_items = tree.xpath('//div[@class="item"]')
            logger.info('tmp_items:::', tmp_items)

            data = {'ret': 'success'}

            data['episode_count'] = len(tmp_items)
            data['episode'] = []


            for item in tmp_items:
                entity = {}
                entity['link'] = item.xpath('.//a/@href')[0]
                entity['code'] = re.search(r'[0-9]+', entity['link']).group()
                entity['title'] = item.xpath('.//span[@class="name-film"]//text()')[0].strip()
                logger.info('entity:::', entity['title'])
                data['episode'].append(entity)

            return data

        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_title_info(code):
        try:
            if LogicLinkkfYommi.current_data is not None and LogicLinkkfYommi.current_data['code'] == code and \
                    LogicLinkkfYommi.current_data['ret']:
                return LogicLinkkfYommi.current_data
            url = '%s/%s' % (ModelSetting.get('linkkf_url'), code)
            # logger.info(url)
            html_content = LogicLinkkfYommi.get_html(url)
            # logger.info(html_content)
            tree = html.fromstring(
                html_content)
            # logger.info(tree)

            data = {'code': code, 'ret': False}
            # //*[@id="body"]/div/div[1]/article/center/strong
            # tmp = tree.xpath('/html/body/div[2]/div/div/article/center/strong'
            #                  )[0].text_content().strip().encode('utf8')
            # tmp = tree.xpath('//*[@id="body"]/div/div[1]/article/center/strong')[0].text_content().strip()
            logger.info('tmp::>', tree.xpath('//div[@class="hrecipe"]/article/center/strong'))

            tmp = tree.xpath('//div[@class="hrecipe"]/article/center/strong')[0].text_content().strip()

            # print(tmp)
            # logger.info(tmp)
            match = re.compile(r'(?P<season>\d+)기').search(tmp)
            if match:
                data['season'] = match.group('season')
            else:
                data['season'] = '1'
            data['title'] = tmp.replace(data['season'] + u'기', '').strip()
            data['title'] = Util.change_text_for_use_filename(
                data['title']).replace('OVA', '').strip()
            try:
                # data['poster_url'] = tree.xpath(
                #     '//*[@id="body"]/div/div/div[1]/center/img'
                # )[0].attrib['data-src']

                data['poster_url'] = tree.xpath(
                    '//*[@id="body"]/div/div[1]/div[1]/center/img'
                )[0].attrib['data-lazy-src']
                data['detail'] = [{
                    'info':
                        tree.xpath('/html/body/div[2]/div/div[1]/div[1]')
                        [0].text_content().strip()
                }]
            except:
                data['detail'] = [{'정보없음': ''}]
                data['poster_url'] = None

            # tmp = tree.xpath('//*[@id="relatedpost"]/ul/li')
            # tmp = tree.xpath('//article/a')
            # 수정된
            tmp = tree.xpath('//ul/a')

            # logger.info(tmp)
            if tmp is not None:
                data['episode_count'] = len(tmp)
            else:
                data['episode_count'] = '0'

            data['episode'] = []
            # tags = tree.xpath(
            #     '//*[@id="syno-nsc-ext-gen3"]/article/div[1]/article/a')
            tags = tree.xpath('//ul/a')

            # logger.info("tags", tags)
            # re1 = re.compile(r'\/(?P<code>\d+)')
            re1 = re.compile(r'\-([^-])+\.')

            data['save_folder'] = data['title']

            program = db.session.query(ModelLinkkfProgram) \
                .filter_by(programcode=code) \
                .first()

            if program is None:
                program = ModelLinkkfProgram(data)
                db.session.add(program)
                db.session.commit()
            else:
                data['save_folder'] = program.save_folder
                data['season'] = program.season

            idx = 1
            for t in tags:
                entity = {}
                entity['program_code'] = data['code']
                entity['program_title'] = data['title']
                entity['save_folder'] = Util.change_text_for_use_filename(
                    data['save_folder'])
                # entity['code'] = re1.search(t.attrib['href']).group('code')
                entity['code'] = data['code'] + str(idx)
                entity['url'] = t.attrib['href']
                entity['season'] = data['season']
                data['episode'].append(entity)
                entity['image'] = data['poster_url']

                # entity['title'] = t.text_content().strip().encode('utf8')
                entity['title'] = t.text_content().strip()
                # entity['season'] = data['season']
                entity['filename'] = LogicLinkkfYommi.get_filename(
                    data['save_folder'], data['season'], entity['title'])
                idx = idx + 1
            data['ret'] = True
            # logger.info('data', data)
            LogicLinkkfYommi.current_data = data

            # srt 파일 처리

            return data
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            data['log'] = str(e)
            return data

    @staticmethod
    def get_filename(maintitle, season, title):
        try:
            match = re.compile(
                r'(?P<title>.*?)\s?((?P<season>\d+)기)?\s?((?P<epi_no>\d+)화)'
            ).search(title)
            if match:
                epi_no = int(match.group('epi_no'))
                if epi_no < 10:
                    epi_no = '0%s' % epi_no
                else:
                    epi_no = '%s' % epi_no

                if int(season) < 10:
                    season = '0%s' % season
                else:
                    season = '%s' % season

                # title_part = match.group('title').strip()
                # ret = '%s.S%sE%s%s.720p-SA.mp4' % (maintitle, season, epi_no, date_str)
                ret = '%s.S%sE%s.720p-LK.mp4' % (maintitle, season, epi_no)
            else:
                logger.debug('NOT MATCH')
                ret = '%s.720p-SA.mp4' % title

            return Util.change_text_for_use_filename(ret)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_info_by_code(code):
        try:
            if LogicLinkkfYommi.current_data is not None:
                for t in LogicLinkkfYommi.current_data['episode']:
                    if t['code'] == code:
                        return t
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_function():
        try:
            logger.debug('Linkkf scheduler_function start..')

            whitelist_program = ModelSetting.get('whitelist_program')
            whitelist_programs = [
                x.strip().replace(' ', '')
                for x in whitelist_program.replace('\n', ',').split(',')
            ]

            for code in whitelist_programs:
                logger.info('auto download start : %s', code)
                downloaded = db.session.query(ModelLinkkf) \
                    .filter(ModelLinkkf.completed.is_(True)) \
                    .filter_by(programcode=code) \
                    .with_for_update().all()
                dl_codes = [dl.episodecode for dl in downloaded]
                logger.info('downloaded codes :%s', dl_codes)
                data = LogicLinkkfYommi.get_title_info(code)
                for episode in data['episode']:
                    e_code = episode['code']
                    if e_code not in dl_codes:
                        logger.info('Logic Queue added :%s', e_code)
                        LogicQueue.add_queue(episode)

            logger.debug('========================================')
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def reset_db() -> bool:
        db.session.query(ModelLinkkf).delete()
        db.session.commit()
        return True
