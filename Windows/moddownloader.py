version = "0.0.5"
import requests, json, os, hashlib

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36"}


# 路径拼接
def join(*data):
    path = ""
    for i in data:
        path = os.path.join(path, i)
    path = path.replace("//", r"\ "[:-1]).replace(r"\\ "[:-1], r"\ "[:-1]).replace("\/", r"\ "[:-1]).replace("/\ "[:-1], r"\ "[:-1]).replace("/", r"\ "[:-1])
    return path


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


# 搜索模组
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
    index = changeList(index, ["相关性", "下载次数", "关注数", "发布时间", "更新时间"], ["relevance", "downloads", "downloads", "newest", "updated"])
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
        dict1 = {"名称": i["title"],  "类型：": i["project_type"], "ID": i["slug"], "介绍": i["description"], "标签": i["categories"], "适配版本": i["versions"], "适配版本范围": i["versions2"][0] + "-" + i["versions2"][-1], "下载次数": str(i["downloads"]), "图标": i["icon_url"], "发布日期": i["date_created"], "更新日期": i["date_modified"], "客户端": i["client_side"], "服务端": i["server_side"]}
        list.append(dict1)
    return list


# 获取模组详细信息
def getModData(data: list):
    for i in range(len(data)):
        data[i] = data[i]["ID"]
    response = requests.get(joinUrl("https://api.modrinth.com/v2/projects", {"ids": data}), headers=header, timeout=600).text
    response = load(response)
    list = []
    for i in response:
        i["game_versions2"] = [item for item in i["game_versions"] if "-" not in item and "w" not in item]
        dict1 = {"名称": i["title"], "类型：": i["project_type"], "ID": i["slug"], "介绍": i["description"], "标签": i["categories"], "适配版本": i["game_versions"], "适配版本范围": i["game_versions2"][0] + "-" + i["game_versions2"][-1], "下载次数": str(i["downloads"]), "图标": i["icon_url"], "发布日期": i["approved"], "更新日期": i["updated"], "客户端": i["client_side"], "服务端": i["server_side"], "加载器": i["loaders"], "模组版本": i["versions"], "源代码链接": i["source_url"]}
        list.append(dict1)
    return list


# 分析模组信息
def modVersionsInf(data: list):
    list = []
    for i in data:
        dict1 = {"名称": i["name"], "版本号": i["version_number"], "加载器": i["loaders"], "游戏版本": i["game_versions"], "版本类型": i["version_type"], "ID": i["project_id"], "版本ID": i["id"], "下载次数": i["downloads"], "文件": i["files"], "sha1": i["files"][0]["hashes"]["sha1"]}
        list.append(dict1)
    return list


# 获取某模组的版本列表
def getModVersions(data: dict):
    list = []
    for i in data["模组版本"]:
        list.append(i)
    response = requests.get(joinUrl("https://api.modrinth.com/v2/versions", {"ids": list}), headers=header, timeout=600).text
    response = load(response)
    list = modVersionsInf(response)
    return list


# 获取sha1对应版本
def getShaVersions(data: list):
    list = []
    for i in data:
        try:
            response = requests.get("https://api.modrinth.com/v2/version_file/" + i, headers=header, timeout=600).text
            response = load(response)
            list.append(response)
        except:
            return
    list = modVersionsInf(list)
    return list


# 版本文件整理
def sortVersionsFiles(data: list):
    dict = {}
    for i in data:
        for j in i["游戏版本"]:
            if "-" not in j and "w" not in j:
                dict[j] = []
    for i in data:
        for j in i["游戏版本"]:
            for k in i["文件"]:
                if "-" not in j and "w" not in j:
                    dict[j].append({"文件名": k["filename"], "版本号": i["版本号"], "加载器": i["加载器"], "版本类型": i["版本类型"], "sha1": i["sha1"], "下载链接": k["url"]})
    return dict


# 获取前置模组
def getModDepends(data):
    response = requests.get("https://api.modrinth.com/v2/project/" + data["ID"] + "/dependencies", headers=header, timeout=600).text
    response = load(response)
    list = response["projects"]
    list = modVersionsInf(list)
    return list


# 获取mc版本列表
def getGameVersions():
    list = []
    response = requests.get("https://api.modrinth.com/v2/tag/game_version", headers=header, timeout=600).text
    response = load(response)
    for i in response:
        if i["version_type"] == "release":
            list.append(i["version"])
    return list


# 获取文件夹里面所有文件的sha1，格式{"文件名":"sha1值"}
def getShaList(data):
    dict = {}
    list = []
    list2 = []
    for i in os.walk(data):
        list.append(i)
    list = list[0][2]
    list = [join(data, i) for i in list]
    for i in range(len(list)):
        with open(list[i], "rb") as file:
            list2.append(hashlib.sha1(file.read()).hexdigest())
    for i in range(len(list)):
        dict[list[i]] = list2[i]

    return dict


# 检查sha1对应模组有无更新
def checkShaUpdate(data, needVersion: str, needLoader: str):
    needLoader.lower()
    data = getShaList(data)
    export = []
    for k, i in data.items():
        print("开始检查更新", k)
        list = getShaVersions([i])
        if not list:
            print("未找到模组", k)
            continue
        print("找到文件信息", list[0]["名称"])
        list = getModData(list)
        if not list:
            print("这个文件对应的模组无了")
            continue
        print("找到对应模组了", list[0]["名称"])
        list = getModVersions(list[0])
        if not list:
            print("这个模组的文件无了")
            continue
        print("正在翻找模组版本")
        list = sortVersionsFiles(list)
        if needVersion not in list:
            print("该模组没有", needVersion, "版本")
            continue
        list = list[needVersion]
        list2 = []
        for j in list[::-1]:
            if needLoader in j["加载器"]:
                list2.append(j)
        if not list2:
            print("模组更新了", needVersion, "但没有更新", needLoader, "加载器的这个版本")
            continue
        list2 = list2[0]
        if list2["sha1"] == i:
            print("当前模组已经是最新的了")
        elif list2["sha1"] != i:
            print("当前模组有新版本", list2["文件名"])
            export.append({"路径": os.path.dirname(k), "旧名称": os.path.basename(k), "新名称": list2["文件名"], "链接": list2["下载链接"]})
    return export


# 承接上面直接更新模组
def modUpdate(data):
    for i in data:
        try:
            response = requests.get(i["链接"], headers=header, timeout=600).content
            with open(join(i["路径"], i["新名称"]), "wb") as file:
                file.write(response)
            os.rename(join(i["路径"], i["旧名称"]), join(i["路径"], i["旧名称"]) + ".old")
            print(f"{i['新名称']}下载成功")
        except:
            print(f"{i['新名称']}下载失败")


data = checkShaUpdate(input("请输入模组目录："), "1.20.1", "fabric")
print(data)
if input("是否更新？"):
    modUpdate(data)

'''
2023年9月24日：0.0.1：添加搜索api接入
2023年9月25日：0.0.2：完善搜索功能，丰富可操控参数，修复Bug，添加简易的搜索使用
2023年9月26日：0.0.3：添加获取模组页面信息，获取版本列表，sha1对应版本
2023年9月27日：0.0.4：添加模组版本按照游戏版本整理并提供链接功能，添加获取前置模组，简易版检查模组更新功能
2023年9月28日：0.0.5：完美完成检查指定文件夹模组更新的功能，添加获取mc正式版列表功能
'''
