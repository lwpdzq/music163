# -*- coding: utf-8 -*-
"""
aurhor:lorenliu
"""
import re
import os
import json
from new_api import Music163API


class DownSong(Music163API):
    def __init__(self):
        super().__init__()

    def one_song(self,song_name):
        try:
            song_list = self.search(song_name)
            song_id, song_name = song_list[0]['id'], song_list[0]['name']
            song_url, song_size = self.get_music_url(song_id)
            self.down_music(song_url, song_size,song_name)
        except:
            print("输入格式有误，请从新操作！")

    def playlist(self,playlist_name):
        try:
            playlists = self.search(playlist_name,search_type=1000)
            print("搜索结果如下(默认返回前五项结果)：")
            index = list()
            for i in range(5):
                playlist_id,playlist_name,playlist_description = playlists[i]['id'],playlists[i]['name'],playlists[i]['description']
                if playlist_description is not None:
                    playlist_description = playlist_description.replace("\n","")
                index.append(playlist_id)
                print("【{}】、[{}]  【歌单描述】{} 【对应网易云id】:{}".format(i+1, playlist_name,playlist_description,playlist_id))
            temp = input("你可以选择根据id值到网易云确认,在此输入以上序号将下载其中全部歌曲：")
            list_content = self.playlist_song(index[int(temp)-1])
            i = 0
            for content in list_content:
                song_id = content["id"]
                song_name = content["name"]
                song_url,song_size = self.get_music_url(song_id)
                if song_url is None:
                    print("【{}】此歌曲已找不到，原因可能是网易云已没有版权请到其他平台下载".format(song_name))
                else:
                    self.down_music(song_url,song_size,song_name)
                    i += 1
                
            print("歌单下载完成共{}首".format(i))
        except Exception:
            print("输入格式有误，请从新操作！")

    def artists(self,name):
        try:
            artists = self.search(name,search_type=100)
            print("以下是找到的结果:")
            index = list()
            for i in artists:
                artists_name,artists_id = i['name'],i['id']
                index.append(artists_id)
                print("【{}】、[{}]   【对应网易云id】:{}".format(artists.index(i)+1,artists_name,artists_id))
            temp = input("您可以输入以上序号来下载其热门歌曲：")
            song_list = self.artists_song(index[int(temp)-1])
            # print(song_list)
            i = 0
            for song in song_list:
                song_id = song['id']
                song_name = song['name']           
                song_url,song_size = self.get_music_url(song_id)
                if song_url is None:
                    print("【{}】此歌曲已找不到，原因可能是网易云已没有版权请到其他平台下载".format(song_name))
                else:
                    self.down_music(song_url,song_size,song_name)
                    i += 1
            
            print("歌单下载完成共{}首".format(i))
        except Exception:
            print("输入格式有误，请从新操作！")


class GetComment(Music163API):
    def __init__(self):
        super().__init__()
        self.path = './Comment'
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def save_hot_comment(self,song_id,song_name,file_path):
        hot_comment = self.get_comment(song_id)
        if not os.path.exists(file_path):
            with open(file_path,'a') as f:
                f.write('song name,nickname,content')
                f.write('\n')
        with open(file_path,'a') as f:
            for i in hot_comment:
                content = i['content']
                content = re.sub(r'\r|\n','',content)
                nickname = i['user']['nickname']
                replied = i['beReplied']
                # print('{}:{}'.format(nickname,content))
                f.write('{},{},{}'.format(song_name,nickname,content))
                f.write('\n')
                if replied:
                    replied_content, replied_user= replied[0]['content'],replied[0]['user']['nickname']
                    replied_content = re.sub(r'\n|\r','',replied_content)
                    # print('回复:{}:{}'.format(replied_user,replied_content))
                    f.write('{},回复:{},{}'.format(song_name,replied_user,replied_content))
                    f.write('\n')

    def save_all_comment(self,song_id,song_name,file_path):
        page = 1
        comment_all,pages = self.get_comment(song_id,page,1)
        if not os.path.exists(file_path):
            with open(file_path,'a') as f:
                f.write('song name,nickname,content')
                f.write('\n')
        while page<pages+1:
            print('正在获取第{}页共{}'.format(page,pages))
            with open(file_path,'a') as f:
                for i in comment_all:
                    content = i['content']
                    content = re.sub(r'\r|\n','',content)
                    nickname = i['user']['nickname']
                    replied = i['beReplied']
                    # print('第{}页{}:{}'.format(page,nickname,content))
                    f.write('{}第{}页 共{},{},{}'.format(song_name,page,pages,nickname,content))
                    f.write('\n')
                    if replied:
                        replied_content, replied_user= replied[0]['content'],replied[0]['user']['nickname']
                        if replied_content is not None:
                            replied_content = re.sub(r'\n|\r','',replied_content)
                        # print('回复:{}:{}'.format(replied_user,replied_content))
                        f.write('{},回复:{},{}'.format(song_name,replied_user,replied_content))
                        f.write('\n')
                page += 1
                comment_all = self.get_comment(song_id,page,1)

    def one_song(self,song_name):
        search_result = self.search(song_name)
        try:
            song_id, song_name = search_result[0]['id'], search_result[0]['name']
            tip = input('提示：输入2程序将获取歌曲的全部评论，不输入将获取热门评论【ps】:由于评论数量庞大这需要花费很长时间：')
            if str(tip) == '2':
                file_path = os.path.join(self.path,str(song_name) + '.csv')
                self.save_all_comment(song_id,song_name,file_path)
            else:
                file_path = os.path.join(self.path,str(song_name) + '-hot.csv')
                self.save_hot_comment(song_id,song_name,file_path)
        except:
            print('输入格式有误，请从新操作！')

    def playlist(self,playlist_name):
        playlists = self.search(playlist_name,search_type=1000)
        try:
            print("搜索结果如下(返回前五项结果)：")
            index = list()
            for i in range(5):
                playlist_id,playlist_name,playlist_description = playlists[i]['id'],playlists[i]['name'],playlists[i]['description']
                if playlist_description is not None:
                    playlist_description = playlist_description.replace("\n","")
                index.append(playlist_id)
                print("【{}】、[{}]  【歌单描述】{} 【对应网易云id】:{}".format(i+1, playlist_name,playlist_description,playlist_id))
            temp = input("你可以选择根据id值到网易云确认,在此输入以上序号将下载其中全部歌曲的评论：")
            list_content = self.playlist_song(index[int(temp)-1])
            print('输入2下载每首歌曲的全部评论 不输入默认只下载热门评论\n【ps】:由于评论数量庞大这需要花费很长时间')
            select_type = input('请选择：')
            if str(select_type) == '2':
                file_path = os.path.join(self.path,str(playlist_name) + '-playlist-all.csv')
                for content in list_content:
                    song_id = content['id']
                    song_name = content['name']
                    self.save_all_comment(song_id,song_name,file_path)
            else:
                file_path = os.path.join(self.path,str(playlist_name) + '-playlist-hot.csv')
                i = 0
                for content in list_content:
                    song_id = content["id"]
                    song_name = content["name"]
                    print("正在获取[{}]热评".format(song_name))
                    self.save_hot_comment(song_id,song_name,file_path)
                    i += 1
                print("歌单评论下载完成共{}首".format(i))
        except Exception as result:
            print("输入格式有误，请从新操作！{}".format(result))


class MakeChart(Music163API):
    def __init__(self):
        super().__init__()
        self.header = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <script type="text/javascript" src="http://api.map.baidu.com/api?v=2.0&ak=此处填写自己申请的ak"></script>
    <script type="text/javascript" src="http://api.map.baidu.com/library/Heatmap/2.0/src/Heatmap_min.js"></script>
    <title>热力图</title>
    <style type="text/css">
        ul,li{list-style: none;margin:0;padding:0;float:left;}
        html{height:100%}
        body{height:100%;margin:0px;padding:0px;font-family:"微软雅黑";}
        #container{height:850px;width:100%;}
        #r-result{width:100%;}
    </style>	
</head>
<body>
    <div id="container"></div>
    <div id="r-result">
        <input type="button"  onclick="openHeatmap();" value="显示热力图"/><input type="button"  onclick="closeHeatmap();" value="关闭热力图"/>
    </div>
</body>
</html>
<script type="text/javascript">
    var map = new BMap.Map("container");          // 创建地图实例

    var point = new BMap.Point(116.418261, 39.921984);
    map.centerAndZoom(point, 15);             // 初始化地图，设置中心点坐标和地图级别
    map.enableScrollWheelZoom(); // 允许滚轮缩放

    var points =["""
        self.footer = """];

    if(!isSupportCanvas()){
        alert('热力图目前只支持有canvas支持的浏览器,您所使用的浏览器不能使用热力图功能~')
    }
    //详细的参数,可以查看heatmap.js的文档 https://github.com/pa7/heatmap.js/blob/master/README.md
    //参数说明如下:
    /* visible 热力图是否显示,默认为true
    * opacity 热力的透明度,1-100
    * radius 势力图的每个点的半径大小   
    * gradient  {JSON} 热力图的渐变区间 . gradient如下所示
    *	{
            .2:'rgb(0, 255, 255)',
            .5:'rgb(0, 110, 255)',
            .8:'rgb(100, 0, 255)'
        }
        其中 key 表示插值的位置, 0~1. 
            value 为颜色值. 
    */
    heatmapOverlay = new BMapLib.HeatmapOverlay({"radius":20});
    map.addOverlay(heatmapOverlay);
    heatmapOverlay.setDataSet({data:points,max:100});
    //是否显示热力图
    function openHeatmap(){
        heatmapOverlay.show();
    }
    function closeHeatmap(){
        heatmapOverlay.hide();
    }
    closeHeatmap();
    function setGradient(){
        /*格式如下所示:
        {
            0:'rgb(102, 255, 0)',
            .5:'rgb(255, 170, 0)',
            1:'rgb(255, 0, 0)'
        }*/
        var gradient = {};
        var colors = document.querySelectorAll("input[type='color']");
        colors = [].slice.call(colors,0);
        colors.forEach(function(ele){
            gradient[ele.getAttribute("data-key")] = ele.value; 
        });
        heatmapOverlay.setOptions({"gradient":gradient});
    }
    //判断浏览区是否支持canvas
    function isSupportCanvas(){
        var elem = document.createElement('canvas');
        return !!(elem.getContext && elem.getContext('2d'));
    }
</script>"""
        self.path = './HeatMap'
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def heatmap_data(self, artists):
        try:
            artists_list = self.search(artists,search_type=100)
            print('【ps】有部分歌手在网易云并没有个人主页，这意味着搜索不到其账户')
            print('搜索到以下歌手：')
            index = list()
            for artist in artists_list:
                artist_id = artist.get('accountId')
                if artist_id:
                    artist_name = artist['name']
                    index.append(artist_id)
                    print("【{}】、[{}]   【对应网易云id】:{}".format(artists_list.index(artist)+1,artist_name,artist_id))
            temp = input("您可以输入以上序号来生成其粉丝地域分布热力图【ps】这可能需要一段时间！ 请输入：")
            more = True
            current_page = 1
            item = dict()
            while more:
                result = self.get_fans(index[int(temp)-1],current_page=current_page)
                followeds_list = result['followeds']
                more = result['more']
                for i in followeds_list:    
                    user_id = i['userId']
                    user_city = self.get_fans_region(user_id)
                    if user_city is not None:
                        if user_city not in item:
                            item[user_city] =1
                        else:
                            item[user_city] = item[user_city] + 1
                print(str(item))
                current_page += 1
            file_path = os.path.join(self.path, 'swap' + '.json')
            json.dump(item,open(file_path,'a'),ensure_ascii=False)
        except Exception as result:
            print("输入格式有误，请从新操作！{}".format(result))

    def heatmap_make(self,file_name):
        if not os.path.exists(self.path+'/swap.json'):
            print("未检测到'swap.json'文件,请先执行第一步！")
        else:
            data = json.load(open(self.path+'/swap.json'))
            file_path = os.path.join(self.path,file_name+'粉丝分布热力图.html')
            with open(file_path,'a') as f:
                f.write(self.header)
                for key in data.keys():
                    print(key)
                    location = self.location(key)
                    if location.get('result') is not None:
                        lng,lat = location['result']['location']['lng'],location['result']['location']['lat']
                        point = '{"lat":%s,"lng":%s,"count":%s},' % (str(lat),str(lng),str(data[key]))
                        f.write(point)
                        f.write('\n')
                f.write(self.footer)
                print("热力图生成完成请在'HeatMap'文件夹中查看！")


class Menu(object):
    def __init__(self):
        self.down_song = DownSong()
        self.get_comment = GetComment()
        self.make_chart = MakeChart()

    def region(self):
        while True:
            print('######################################################')
            print('#                   热力图生成功能                   #')
            print('#    【ps】此功能需要根据歌手的粉丝地区来实现，所以需#')
            print("# 要分成两步完成，第一步完成后会在'HeatMap'文件夹中生#")
            print("# 成 'swap.json' 数据文件,进行第二步之前请确保数据文 #")
            print('# 件的存在，您需要输入歌手的名称                     #')
            print('#       1. 获得歌手粉丝数据                          #')
            print('#       2. 生成图表文件                              #')
            print('#       3. 返回                                      #')
            print('######################################################')
            function = input('请输入功能编号或歌手名字：')            
            if str(function) == '3':
                os.system('clear')
                break
            elif str(function) == '2':
                file_name = input("您需要输入生成热力图的文件名：")
                self.make_chart.heatmap_make(file_name)
            self.make_chart.heatmap_data(function)

    def comment(self):
        while True:
            print('######################################################')
            print('#                    获取评论功能                    #')
            print('#       1. 单曲评论                                  #')
            print('#       2. 歌单评论                                  #')
            print('#       3. 返回                                      #')
            print('######################################################')
            function = input('请输入正确的功能编号：')
            if str(function) == '1':
                song_name = input('请输入歌曲的名字')
                self.get_comment.one_song(song_name)
            if str(function) == '2':
                playlist_name = input('请输入歌单名')
                self.get_comment.playlist(playlist_name)
            if str(function) == '3':
                os.system('clear')
                break
    
    def download(self):
        while True:
            print('######################################################')
            print('#                      下载功能                      #')
            print('#       1. 下载单曲                                  #')
            print('#       2. 下载歌单                                  #')
            print('#       3. 下载歌手                                  #')
            print('#       4. 返回                                      #')
            print('######################################################')
            function = input('请输入正确的功能编号：')
            if str(function) == '1':
                song_name = input("请输入歌曲名：")
                self.down_song.one_song(song_name)
            if str(function) == '2':
                playlist_name = input("请输入歌单名:")
                self.down_song.playlist(playlist_name)

            if str(function) == '3':
                artists_name = input("请输入要寻找的歌手:")
                self.down_song.artists(artists_name)
            if str(function) == '4':
                os.system('clear')
                break


def main():
    # 主功能区
    menu = Menu()
    while True:
        print('######################################################')
        print('#                  欢迎来到xxx平台                   #')
        print('#                 你可以使用以下功能                 #')
        print('#       1. 下载歌曲                                  #')
        print('#       2. 获取评论                                  #')
        print('#       3. 粉丝地域分布热力图                        #')
        print('#       4. 退出                                      #')
        print('######################################################')
        function = input('请输入正确的功能编号：')
        if str(function) == '1':
            os.system('clear')            
            menu.download()
        elif str(function) == '2':
            os.system('clear')
            menu.comment()
        elif str(function) == '3':
            os.system('clear')
            menu.region()            
        elif str(function) == '4':
            break
        else:
            print('输入有误,请重新输入')


if __name__ == "__main__":
    main()