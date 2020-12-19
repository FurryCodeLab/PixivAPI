from flask import Flask,jsonify,request,make_response
import json
import requests
import os
import sys
from pixivpy3 import *

username = "1240188105@qq.com"
password = "kgs196983"

aapi = AppPixivAPI()
aapi.login(username, password)

papi = PixivAPI()
papi.login(username, password)

class mod:
    @staticmethod
    def add_two_dim_dict(dictionary,root,**value): 
        """新增修改二維字典\n
            dictionary  : 要新增修改的字典\n
            root        : 字典的字根(一維字典的鍵)\n
            value       : 傳入值 key=value 可複數，key為鍵 value為鍵值
        """
        dictionary[root] = {}
        for key in value.keys():
            dictionary[root][key] = value[key]
        return dictionary
    @staticmethod
    def datetransfer(date):
        return date[:4]+'-'+date[4:6]+'-'+date[6:]
    
class http:
    @staticmethod
    def status(message,status_code):
        return make_response(jsonify(message), status_code)

class illustDetailNotFound(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return "illustDetailNotFound ," + self.message

class illustListNotFound(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return "illustListNotFound ," + self.message

class PIXIV():
    """
    illustDetail(self,id)\n
    \t查詢 id 的作品詳細資料，id 為必須值\n
    illustList(userid,type='illust')\n
    \t查詢 userid 的作品列表詳細資料，userid 為必須值\n
    illustSearch(word,offset=None)\n
    \t搜尋 PIXIV 的作品中部分包含 word 的作品列表，word 為必須值\n\toffset 為可選
    """

    
    def illustDetail(self,illustid):
        """
        取得 id 的作品詳細資料\n
        illustDetail(illustid)\n
        如該 id 的作品已刪除或不存在該作品 id 直接回傳空json，http status code = 200
        """
        try:
            illustdetail = aapi.illust_detail(illustid)
            if 'error' in illustdetail:
                raise illustDetailNotFound(f'illust {illustid} not found')
            return http.status(illustdetail.illust, 200)
        except illustDetailNotFound as e:
            return http.status({ },200)
        except Exception as e:
            return Interal_Server_Error(str(e))

    def illustList(self,userid,type='illust'):
        """
        取得 userid 的作品列表詳細資料\n
        illustList(userid)\n
        如該 userid 無作品或不存在該使用者直接回傳空json，http status code = 200
        """
        try:
            illustlist = aapi.user_illusts(userid,type='illust')
            if not any(illustlist['illusts']):
                raise illustListNotFound(f'user {userid} not found illust ilst')
            return http.status(illustlist, 200)
        except illustListNotFound as e:
            return http.status({ },200)
        except Exception as e:
            return Interal_Server_Error(str(e))
    
    def illustSearch(self,word):
        """
        搜尋 word 的作品列表詳細資料\n
        illustSearch(word,offset=None)\n
        word 為必須搜尋關鍵字，offset 為可選預設0(None):顯示0~29筆 30:30~59筆依此類推\n
        """
        try:
            illust = aapi.search_illust(word, search_target='partial_match_for_tags')
            return http.status(illust, 200)
        except Exception as e:
            return Interal_Server_Error(str(e))

    def hottag(self):
        try:
            tag = aapi.trending_tags_illust()
            return http.status(tag, 200)
        except Exception as e:
            return Interal_Server_Error(str(e))

app = Flask(__name__)

class api:
    version = 'v1'

#GET / response 
@app.route(f"/{api.version}")
def home():
    return jsonify({'response':{'status':200,'message':'欢迎来到Pixiv API','version':'1.0'}})

#GET /illust/detail data:{illust id:id,}
@app.route(f'/{api.version}/illust/detail/<int:id>')
def illust_detail(id):
    pixiv = PIXIV()
    return pixiv.illustDetail(id)

#GET /illust/list data:{user id:id,}
@app.route(f'/{api.version}/illust/list/<int:id>')
def illust_list(id):
    pixiv = PIXIV()
    return pixiv.illustList(id)

#GET /illust/search data:{keyword:word,}
@app.route(f'/{api.version}/illust/search')
def illust_search():
    word = request.args.get('keyword')
    pixiv = PIXIV()
    return pixiv.illustSearch(word)

@app.route(f'/{api.version}/hottag')
def hot_tag():
    pixiv = PIXIV()
    return pixiv.hottag()

@app.errorhandler(404)
def Page_Not_Found(e):
    return http.status({'status_codde':404,'message':str(e)} , 404)

@app.errorhandler(500)
def Interal_Server_Error(e):
    if e is None:
        return http.status({'status_codde':500,'message':'500 Interal Server Error'} , 500)
    return http.status({'status_codde':500,'message':str(e)} , 500)



if __name__ == "__main__":
    app.run(host='0.0.0.0',port='5000')
