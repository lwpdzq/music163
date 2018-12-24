# -*- coding: utf-8 -*-
"""
实现网易云音乐主要功能接口
"""

import json
import math
import os
import re
import sys
import requests
from lxml import etree
from urllib.parse import quote
from encryped import Encryped


class Music163API(object):
    def __init__(self):
        self.encryped = Encryped()
        self.pattern = re.compile(r'<span>所在地区：.*?\s-\s(.*?)</span>|<span>所在地区：(.*?)\s</span>')
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Origin': 'https://music.163.com',
            'Referer': 'https://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }

    def request_post(self, url, params):
        data = self.encryped.encrypted_request(params)
        resp = requests.post(url, headers=self.headers, data=data)
        result = resp.json()
        if result['code'] != 200:
            print('request failed')
        else:
            return result

    def search(self, search_name, search_type=1):
        """
        search_type:value=1 return song,value=10 return albums,
        value=100 return artists,value=1000 return playlists
        """
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        params = {'s': search_name, 'type': search_type, 'limit': '30'}
        result = self.request_post(url, params)
        if str(search_type) == '1':
            # return song_id
            try:
                song_list = result['result']['songs']
                return song_list
            except Exception as result:
                print(result)
        if str(search_type) == '10':
            # reutrn albums
            try:
                albums = result['result']['albums']
                return albums
            except Exception as result:
                print(result)
        if str(search_type) == '100':
            # return artists
            try:
                artists = result['result']['artists']
                return artists
            except Exception as result:
                print(result)
        if str(search_type) == '1000':
            # return playlists
            try:
                playlists = result['result']['playlists']
                return playlists
            except Exception as result:
                print(result)

    def get_music_url(self, song_id):
        """
        get a music url
        """
        url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
        params = {'ids':[song_id],'br':320000,'csrf_token':''}
        result = self.request_post(url,params)
        song_url = result['data'][0]['url']
        song_size = result['data'][0]['size']
        return song_url,song_size

    def down_music(self,url,size,name):
        """
        save music
        """
        path = './Music'
        if not os.path.exists(path):
            os.mkdir(path)
        response = requests.get(url)
        file_path = os.path.join(path,str(name) + '.mp3')
        try:
            with open(file_path,'wb') as f:
                f.write(response.content)
                print(" %s 下载完成 共 %.2f M" % (name, size/1024 ** 2))
        except:
            print("{}下载出错".format(name))

    def playlist_song(self,playlist_id, description = False):
        """
        Get a song list of playlsit pages
        description: Returns the description of the current song list when the value is true, default false
        """
        url = 'https://music.163.com/playlist?id={}'.format(playlist_id)
        response = requests.get(url,headers=self.headers)
        text_html = response.content.decode()
        html = etree.HTML(text_html)
        playlist_description = html.xpath("//meta[@name='description']/@content")[0]
        playlist_description = re.sub("\r|\n","",playlist_description)
        ul_list = html.xpath("//ul[@class='f-hide']//li")
        content_list = list()
        for li in ul_list:
            item = dict()
            test_id = li.xpath("./a/@href")
            item["id"] = test_id[0].split("=")[1]
            item["name"] = li.xpath("./a/text()")[0]
            content_list.append(item)
        if description is True:
            return content_list,playlist_description
        return content_list

    def artists_song(self,artists_id):
        """
        Get a song list of artists pages
        """
        url = 'https://music.163.com/artist?id={}'.format(artists_id)
        response = requests.get(url, headers=self.headers)
        html = etree.HTML(response.content.decode())
        ul_list = html.xpath("//ul[@class='f-hide']//li")
        content_list = list()
        for li in ul_list:
            item = dict()
            song_id = li.xpath("./a/@href")
            item['id'] = song_id[0].split("=")[1]
            item['name'] = li.xpath("./a/text()")[0]
            content_list.append(item)
        return content_list


    def get_comment(self, song_id, current_page = 1,comment_type=0):
        """
        song_id:The unique ID corresponding to the song，
        comment_type:value=0 return a list of hotcomment, value=1 return a list of all comment
        """
        url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token='.format(song_id)
        params = {'offset': str((current_page-1) * 20), 'limit': '20', 'csrf_token': ''}
        comment = self.request_post(url, params)
        if str(comment_type) == '0':
            hot_comment = comment['hotComments']
            return hot_comment
        if str(comment_type) == '1':
            total = comment['total']
            pages = math.ceil(total / 20)
            comment = comment['comments']
            if str(current_page) == '1':
                return comment,pages
            return comment

    def get_fans(self,user_id,current_page=1):
        """
        get the fans region by artists
        """
        url = 'https://music.163.com/weapi/user/getfolloweds?csrf_token='
        params = {'offset':str((current_page-1) * 20),'limit': '20','total':'true','csrf_token':'','userId':str(user_id)}
        result = self.request_post(url,params)
        return result

    def get_fans_region(self,user_id):
        url = 'https://music.163.com/user/home?id={}'.format(user_id)
        response = requests.get(url,headers=self.headers)
        html = response.content.decode()
        city_list = self.pattern.findall(html)
        city = city_list[0][0] if len(city_list) > 0 else None
        if city == '':
            city = city_list[0][1]
        if city is not None:
            return city

    def location(self,city):
        ak = 'aXY90PUGEe2xXzDD2o3m2GGW14BssNoY'
        address = quote(city)
        url = 'http://api.map.baidu.com/geocoder/v2/?address={}&output=json&ak={}'.format(address,ak)
        response = requests.get(url)
        data = response.content.decode()
        data = json.loads(data)
        return data


def main():
    """
    主要逻辑
    """
    content = Music163API()
    song_id = 97137413
    more = True
    while more:
        result = content.get_fans(song_id,current_page=1)
        followeds_list = result['followeds']
        more = result['more']
        for i in followeds_list:
            user_id = i['userId']
            city = content.get_fans_region(user_id)
            print(city)
            data = content.location(city)
            print(data)
    # print(followeds_list)
    # print(more)

    # content.get_fans_region(1706704295)

    # comment.playlist_song(song_id)


    # song_name = input("please input the song name:")

    # music_url,music_size = comment.get_music_url(song_id)
    # comment.down_music(music_url,music_size,song_name)

    # hot_comment = comment.get_comment(song_id)
    # for i in hot_comment:
    #     content = i['content']
    #     content = re.sub(r'\r|\n','',content)
    #     nickname = i['user']['nickname']
    #     replied = i['beReplied']
    #     print('{}:{}'.format(nickname,content))
    #     if replied:
    #         replied_content, replied_user= replied[0]['content'],replied[0]['user']['nickname']
    #         print('回复:{}:{}'.format(replied_user,replied_content))


    # page = 1
    # comment_all,pages = comment.get_comment(song_id,page,1)
    # print(pages)
    # while page<pages:
    #     for i in comment_all:
    #         content = i['content']
    #         content = re.sub(r'\r|\n','',content)
    #         nickname = i['user']['nickname']
    #         replied = i['beReplied']
    #         print('第{}页{}:{}'.format(page,nickname,content))
    #         if replied:
    #             replied_content, replied_user= replied[0]['content'],replied[0]['user']['nickname']
    #             print('回复:{}:{}'.format(replied_user,replied_content))
    #     page += 1
    #     comment_all = comment.get_comment(song_id,page,1)



if __name__ == "__main__":
    main()
