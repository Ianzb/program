version = "0.0.2"
import requests, json

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36"}


# str转json
def load(data: str):
    return json.loads(data)


# 批量替换
def changeList(data: str, a: list, b: list):
    if data in a:
        data = b[a.index(data)]
    return data


# 拼接链接，需要头链接+字典形式参数
def joinUrl(first: str, end: dict):
    if first[-1] == "?":
        first = first[:-1]
    list = []
    for k, v in end.items():
        if v:
            list.append(k + "=" + str(v))
    string = "&".join(list)
    string = first + "?" + string
    if string[-1] == "?":
        string = string[:-1]
    string = string.replace("'", '"')
    return string


# 拼接搜索facets模组信息参数
def facetsEdit(type, versions, categories):
    facets = []
    if type:
        facets.append(["project_type:" + type])
    elif versions:
        facets.append(["versions:" + versions])
    elif categories:
        facets.append(["categories:" + categories])
    return facets


# 搜索文件
def search(data=None, type="mod", versions=None, index="相关性", limit=10, page=1, categories=None):
    if not data:
        data = None
    if not type:
        type = "mod"
    if not versions:
        versions = None
    if not index:
        index = "相关性"
    if not limit:
        limit = 10
    if not page:
        page = 1
    if not categories:
        categories = None
    limit = int(limit)
    page = int(page)
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100
    index = changeList(index, ["相关性", "下载量", "关注数", "发布时间", "更新时间"], ["relevance", "downloads", "downloads", "newest", "updated"])
    page = limit * (page - 1)
    facets = facetsEdit(type, versions, categories)
    response = requests.get(joinUrl("https://api.modrinth.com/v2/search", {"query": data, "facets": facets, "limit": limit, "index": index, "offset": page}), headers=header, stream=True).text
    response = load(response)
    return response


# 处理搜索结果
def searchInf(data):
    dict1 = {"当前页面展示数量": str(len(data["hits"])), "总结果数量": str(data["total_hits"])}
    return dict1


# 处理搜索的模组结果
def searchModInf(data):
    string = data["hits"]
    list = []
    for i in string:
        i["versions2"] = [item for item in i["versions"] if "-" not in item and "w" not in item]
        dict1 = {"名称": i["title"], "作者": i["author"], "类型：": i["project_type"], "ID": i["slug"], "介绍": i["description"], "标签": i["categories"], "适配版本": i["versions"], "适配版本范围": i["versions2"][0] + "-" + i["versions2"][-1], "下载次数": str(i["downloads"]), "图标": i["icon_url"], "发布日期": i["date_created"], "更新日期": i["date_modified"], "客户端": i["client_side"], "服务端": i["server_side"]}
        list.append(dict1)
    return list


# 获取模组详细信息
def getModData(data: list):
    data2 = []
    for i in range(len(data)):
        data2.append(data[i]["ID"])
    print(joinUrl("https://api.modrinth.com/v2/projects", {"ids": data2}))
    response = requests.get(joinUrl("https://api.modrinth.com/v2/projects", {"ids": data2}), headers=header, stream=True).text
    response = load(response)
    list = []
    for i in response:
        i["versions2"] = [item for item in i["versions"] if "-" not in item and "w" not in item]
        dict1 = {"名称": i["title"], "类型：": i["project_type"], "ID": i["slug"], "介绍": i["description"], "标签": i["categories"], "适配版本": i["versions"], "适配版本范围": i["versions2"][0] + "-" + i["versions2"][-1], "下载次数": str(i["downloads"]), "图标": i["icon_url"], "发布日期": i["approved"], "更新日期": i["updated"], "客户端": i["client_side"], "服务端": i["server_side"], "加载器": i["loaders"], "模组版本": i["versions"], "源代码链接": i["source_url"]}
        list.append(dict1)
    for i in range(len(data)):
        list[i].update(data[i])
    return list


data = input("搜索名称：")
version = input("版本：")
page = input("页面数：")
limit = input("每页数量：")
index = input("排列顺序：")
str1 = search(data, page=page, limit=limit, versions=version, index=index)
print(searchModInf(str1)[0])
mod = getModData(searchModInf(str1))
print(mod[0])
'''
2023年9月24日：0.0.1：添加搜索api接入
2023年9月25日：0.0.2：完善搜索功能，丰富可操控参数，修复Bug，添加简易的搜索使用
'''
