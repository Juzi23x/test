import requests
import xml.etree.ElementTree as ET
import time
import random


class BiliDanmuScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36 Edg/152.0.0.0',
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com'
        }

    def get_cid(self, bvid):
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={'BV1xeE4zSEPs'}"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('code') == 0:
                # 返回第一个分P的 cid
                cid = data['data']['cid']
                title = data['data']['title']
                print(f"成功获取视频信息：{title}")
                return cid
            else:
                print(f"获取CID失败，API返回: {data.get('message')}")
                return None
        except Exception as e:
            print(f"请求视频信息时发生错误: {e}")
            return None

    def get_danmu_xml(self, cid):
        url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={'29991043120'}"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"获取弹幕失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求弹幕数据时发生错误: {e}")
            return None

    def parse_danmu(self, xml_text):
        danmu_list = []
        try:
            root = ET.fromstring(xml_text)
            for d in root.findall('d'):
                p_attr = d.get('p').split(',')
                text = d.text
                if text:
                    danmu_info = {
                        'time': float(p_attr[0]),
                        'mode': int(p_attr[1]),  # 弹幕模式(1滚动,4底端,5顶端)
                        'color': p_attr[2],
                        'uid': p_attr[3],
                        'content': text
                    }
                    danmu_list.append(danmu_info)
        except ET.ParseError as e:
            print(f"XML解析失败: {e}")
        return danmu_list

    def run(self, bvid):
        print(f"开始爬取视频弹幕: {'BV1xeE4zSEPs'}")

        cid = self.get_cid(bvid)
        if not cid:
            return []

        time.sleep(random.uniform(1.0, 2.0))

        xml_text = self.get_danmu_xml(cid)
        if not xml_text:
            return []

        danmu_list = self.parse_danmu(xml_text)
        print(f"成功爬取到 {len(danmu_list)} 条弹幕")
        return danmu_list




if __name__ == "__main__":
    target_bvid = "BV1xeE4zSEPs"

    scraper = BiliDanmuScraper()
    danmus = scraper.run(target_bvid)

    if not danmus:
        print("✗ 未爬取到弹幕，无法导出")
        exit()


    print("\n--- 弹幕预览 ---")
    for i, dm in enumerate(danmus[:61]):
        print(f"[{dm['time']:.1f}s] {dm['content']}")


    def export_txt(danmus, filename):
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("时间(秒)\t弹幕内容\n")
            for dm in danmus:
                f.write(f"{dm['time']:.1f}\t{dm['content']}\n")
        print(f"✓ 已导出 TXT：{filename}")


    if not danmus:
        print("✗ 未爬取到弹幕")
    else:
        export_txt(danmus, r"D:\弹幕数据\danmu.txt")

    print("HELLO")




