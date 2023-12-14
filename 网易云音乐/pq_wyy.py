import requests
import execjs
import re
from bs4 import BeautifulSoup


class Wyy(object):
    def __init__(self):
        self.all_id = []
        self.all_url = []
        self.headers = {
            'authority': 'music.163.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            # 'cookie': 'NTES_P_UTID=QhsJHDHa47f7As51etOssMiGoTfULmZH|1702373410; P_INFO=chengt19980421@163.com|1702373410|0|mail163|00&99|CN&1698396345&mail163#US&null#10#0#0|&0|mail163|chengt19980421@163.com; NMTID=00Ok3CKauiJeQ0VnkqbrDh040dVURAAAAGMYk4o-Q; JSESSIONID-WYYY=1o%2BQOs51IJIwCjK%5CKbv9Ps%5CT8npzZgk6DEdIWRWFuCRotVQ6bW08lnj%2B06YuUHg99gpPQZf1FZ8OamoJ6n7Ez606Rw2ETyS2E%2FE1nkqf%2FAhM697%2BgTFrZfxQfR859A87ITQbPonUzSrtAT9hqlmJxKX6f9c3Spbxfi%2BYjaVOvKTT7Ax0%3A1702458142867; _iuqxldmzr_=32; _ntes_nnid=4382659be36ed0c86d22e6947eac78de,1702456342877; _ntes_nuid=4382659be36ed0c86d22e6947eac78de; WEVNSM=1.0.0; WNMCID=qtzelq.1702456348495.01.0; WM_NI=0v5q4YunPjKhnUPh9FEDA4Dep2DbCfSC3hffBZbahiny6NUCfU5B1mOaj60%2FwcKZs4IZ%2B0GDyaEB%2FX2h3DSusC2FTXM%2BjhSJZjBatwla6D%2BmgmG0R78GcRc50TEXluqVUmY%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed5db42a793fca8ec60a69e8eb3d15a979b8b86c57988a887aee864f286aaa6eb2af0fea7c3b92af4aafb92b753b7b2a08bca64ae8ba089bc4e879c8fd5c76fb4ee8c83c26e919dfd89e56e8286ae82eb63aea7faafd849a68bfba3b4678dbfa6d7b325b5bd85bbf2408b86e5d1c650bbbf8ba3ae54f2b8fda5d27fb19dfea7d7548ff5a689d2429ab68e82f77db0bffaa5aa67a5b389d1d13dfc99adb3e23ff48c8bb9ef7fb38a9b8edc37e2a3; WM_TID=IM9uv8UHiMNEAEVUEVKB8CgNIKhnNLEl; ntes_utid=tid._.ty%252FRpB%252BAvxZEBgFQEAOE4TkJYLlnKHqO._.0; sDeviceId=YD-Q9xGt8%2BEKdlFF1VRRFaV5G0JNa1mfH%2Bh; playerid=24807904',
            'origin': 'https://music.163.com',
            'pragma': 'no-cache',
            'referer': 'https://music.163.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.params = {
            'csrf_token': '',
        }

        self.data = {
            'params': '',
            'encSecKey': ''
        }

    def get_all_id(self):
        """第一次获取每一个音乐的id"""
        response = requests.get('https://music.163.com/discover/toplist', headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        li = soup.find('ul', class_='f-hide').find_all('li')
        href = [(i.find('a')['href'], i.find('a').text) for i in li]
        pattern = r"id=(\d+)"
        res = list(map(lambda x: (re.findall(pattern, x[0])[0], x[1]), href))
        return res

    def get_all_url(self):
        """将每一个音乐的id做请求 并拿到所有对应的url链接"""
        id_name = self.get_all_id()
        X8P = '/api/song/enhance/player/url/v1'
        e7d_all = [self.get_e7d_c(i[0]) for i in id_name]
        with open('canshu.js', 'r', encoding='utf8') as f:
            content = f.read()
        params_all = [execjs.compile(content).call('get_res', X8P, e7d) for e7d in e7d_all]
        for params, secrey in params_all:
            try:
                self.data['params'] = params
                self.data['encSecKey'] = secrey
                response = requests.post(
                    'https://music.163.com/weapi/song/enhance/player/url/v1',
                    params=self.params,
                    cookies='',
                    headers=self.headers,
                    data=self.data,
                    verify=False)
                self.all_url.append(response.json()['data'][0]['url'])
            except:
                print(params, '\n', secrey, '失效')
                continue
        # return self.all_url

    @staticmethod
    def get_e7d_c(i):
        e7d = {
            "type": "json",
            "query": {
                "ids": f"[{i}]",
                "level": "standard",
                "encodeType": "aac"
            }
        }
        return e7d

    def get_save(self):
        """将url链接全都作出请求得到对应的mp4值并保存"""
        self.all_url = [i for i in self.all_url if i != None]
        for id, url in enumerate(self.all_url):
            resp = requests.get(url, headers=self.headers)
            with open(f'{id}.mp4', 'wb') as f:
                f.write(resp.content)
            print(id, 'ok')
        print('all ok')


if __name__ == '__main__':
    aa = Wyy()
    aa.get_all_url()
    aa.get_save()
