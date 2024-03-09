try:
    from beta.source.function import *
except:
    pass

RELEASE_VERSIONS = ["1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17", "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16", "1.15.2", "1.15.1", "1.15", "1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14", "1.13.2", "1.13.1", "1.13", "1.12.2", "1.12.1", "1.12", "1.11.2", "1.11.1", "1.11", "1.10.2", "1.10.1", "1.10", "1.9.4", "1.9.3", "1.9.2", "1.9.1", "1.9", "1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2", "1.8.1", "1.8", "1.7.10", "1.7.9", "1.7.8", "1.7.7", "1.7.6", "1.7.5", "1.7.4", "1.7.3", "1.7.2", "1.6.4", "1.6.2", "1.6.1", "1.5.2", "1.5.1", "1.4.7", "1.4.6", "1.4.5", "1.4.4", "1.4.2", "1.3.2", "1.3.1", "1.2.5", "1.2.4", "1.2.3", "1.2.2", "1.2.1", "1.1", "1.0"]
CURSEFORGE_API_KEY = {
    "Accept": "application/json",
    "x-api-key": "$2a$10$21wJppLHY6oZ4Fs/Jb85WuJdpWppY6RcX3o.G9.372hxeiec8Wy6m"
}
CURSEFORGE_POST_API_KEY = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-api-key": "$2a$10$21wJppLHY6oZ4Fs/Jb85WuJdpWppY6RcX3o.G9.372hxeiec8Wy6m"
}
CURSEFORGE_VERSION_TYPE = {
    1: "release",
    2: "beta",
    3: "alpha",
}
CURSEFORGE_LOADER_TYPE = {
    0: "any",
    1: "forge",
    2: "cauldron",
    3: "liteloader",
    4: "fabric",
    5: "quilt",
    6: "neoforge",
}


def getVersionList(version_type: str = "release"):
    """
    获取我的世界版本列表
    @param version_type: 版本类型：release 正式版，snapshot 测试版
    @return: 我的世界版本列表
    """
    global RELEASE_VERSIONS
    try:
        list = []
        response = f.requestGet("https://api.modrinth.com/v2/tag/game_version", program.REQUEST_HEADER)
        response = json.loads(response)
        for i in response:
            if i["version_type"] == version_type:
                list.append(i["version"])
        RELEASE_VERSIONS = list
        return list
    except:
        return RELEASE_VERSIONS


def searchMod(name: str, source: str = "CurseForge", version: str = "", page: int = 1) -> list:
    """
    搜索模组
    @param name: 名称
    @param source: 数据源
    @param version: 版本
    @param page: 页面编号（从1开始）
    @return: 模组列表
    """
    logging.debug(f"在{source}搜索应用{name}")
    list = []

    if source == "Modrinth":
        version = f',["versions:{version}"]' if version not in ["全部", "", None] else ""
        data = f.requestGet(f'https://api.modrinth.com/v2/search?query={name}&facets=[["project_type:mod"]{version}]&limit=50&offset={50 * (page - 1)}', program.REQUEST_HEADER)
        if "hits" in json.loads(data):
            data = json.loads(data)["hits"]
            for i in data:
                list.append({"id": i["project_id"],
                             "名称": i["title"],
                             "图标": i["icon_url"],
                             "介绍": i["description"],
                             "下载量": i["downloads"],
                             "游戏版本": f.sortVersion([j for j in i["versions"] if j in RELEASE_VERSIONS]),
                             "更新日期": i["date_modified"].split("T")[0],
                             "作者": i["author"],
                             "来源": "Modrinth",
                             })
    elif source == "CurseForge":
        version = f"&gameVersion={version}" if version != "全部" else ""
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/search?gameId=432&classId=6{version}&searchFilter={name}&pageSize=50&sortOrder=desc&index={50 * (page - 1)}", CURSEFORGE_API_KEY)
        if "data" in json.loads(data):
            data = json.loads(data)["data"]
            for i in data:
                list.append({"id": i["id"],
                             "名称": i["name"],
                             "图标": i["logo"]["url"],
                             "介绍": i["summary"],
                             "下载量": i["downloadCount"],
                             "游戏版本": f.sortVersion([j for j in [k["gameVersion"] for k in i["latestFilesIndexes"]] if j in RELEASE_VERSIONS]),
                             "更新日期": i["dateReleased"].split("T")[0],
                             "作者": i["authors"][0]["name"],
                             "来源": "CurseForge",
                             })
    return list


def getModInfo(mod_id, source: str = "CurseForge") -> dict:
    """
    获得模组信息
    @param mod_id: 模组id
    @param source: 数据源
    @return: 模组信息
    """
    dict = {}
    if source == "Modrinth":
        data = f.requestGet(f"https://api.modrinth.com/v2/project/{mod_id}", program.REQUEST_HEADER)
        data = json.loads(data)
        data2 = f.requestGet(f"https://api.modrinth.com/v2/project/{mod_id}/members", program.REQUEST_HEADER)
        data2 = json.loads(data2)

        dict.update({
            "id": data["id"],
            "名称": data["title"],
            "图标": data["icon_url"],
            "介绍": data["description"],
            "下载量": data["downloads"],
            "游戏版本": f.sortVersion([j for j in data["versions"] if j in RELEASE_VERSIONS]),
            "更新日期": data["updated"].split("T")[0],
            "作者": [i["user"]["username"] for i in data2 if i["role"] == "Owner"][0],
            "来源": "Modrinth",
            "源代码链接": data["source_url"],
            "加载器": data["loaders"],
            "发布日期": data["published"].split("T")[0],
            "网站链接": f"https://modrinth.com/mod/{data["slug"]}",
        })
    elif source == "CurseForge":
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/{mod_id}", CURSEFORGE_API_KEY)
        data = json.loads(data)["data"]

        data2 = f.requestGet(f"https://api.curseforge.com/v1/mods/{mod_id}/files", CURSEFORGE_API_KEY)
        data2 = json.loads(data2)["data"]

        loader = []
        for i in data2:
            loader += [j.lower() for j in i["gameVersions"] if j.lower() in CURSEFORGE_LOADER_TYPE.values()]
        loader = list(set(loader))

        dict.update({
            "id": data["id"],
            "名称": data["name"],
            "图标": data["logo"]["url"],
            "介绍": data["summary"],
            "下载量": data["downloadCount"],
            "游戏版本": f.sortVersion([j for j in [k["gameVersion"] for k in data["latestFilesIndexes"]] if j in RELEASE_VERSIONS]),
            "更新日期": data["dateReleased"].split("T")[0],
            "作者": data["authors"][0]["name"],
            "来源": "CurseForge",
            "源代码链接": data["links"]["sourceUrl"],
            "加载器": loader,
            "发布日期": data["dateCreated"].split("T")[0],
            "网站链接": data["links"]["websiteUrl"],
        })
    return dict


def getModFile(id, source: str = "CurseForge", version: str = "", loader: str = "") -> dict:
    """
    获得模组文件
    @param id: 模组id
    @param source: 数据源
    @param version: 版本
    @param loader: 加载器（全小写）
    @return:
    """
    list1 = []
    if source == "Modrinth":
        version = f'&game_versions=["{version}"]' if version not in ["全部", "", None] else ""
        loader = f'&loaders=["{loader}"]' if loader not in ["全部", "", None] else ""
        data = f.requestGet(f"https://api.modrinth.com/v2/project/{id}/version?a=0{version}{loader}", program.REQUEST_HEADER)
        data = json.loads(data)
        for i in data:
            list1.append({
                "id": i["id"],
                "模组id": i["project_id"],
                "名称": i["name"],
                "版本号": i["version_number"],
                "前置": i["dependencies"],
                "游戏版本": f.sortVersion([j for j in i["game_versions"] if j in RELEASE_VERSIONS]),
                "版本类型": i["version_type"],
                "加载器": i["loaders"],
                "下载量": i["downloads"],
                "更新日期": i["date_published"].split("T")[0],
                "来源": "Modrinth",
                "哈希值": i["files"][0]["hashes"]["sha1"],
                "下载链接": i["files"][0]["url"],
                "文件名称": i["files"][0]["filename"],
                "文件大小": i["files"][0]["size"],
            })
    elif source == "CurseForge":
        version = f"&gameVersion={version}" if version not in ["全部", "", None] else ""
        for k, v in CURSEFORGE_LOADER_TYPE.items():
            if v == loader:
                loader = k
        loader = f"&modLoaderType={loader}" if loader not in ["全部", "", None] else ""
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/{id}/files?a=0{version}{loader}", CURSEFORGE_API_KEY)
        data = json.loads(data)["data"]

        for i in data:
            list1.append({
                "id": i["id"],
                "模组id": i["modId"],
                "名称": i["displayName"],
                # "版本号": i["version_number"],
                "前置": i["dependencies"],
                "游戏版本": f.sortVersion([j for j in i["gameVersions"] if j in RELEASE_VERSIONS]),
                "版本类型": CURSEFORGE_VERSION_TYPE[i["releaseType"]],
                "加载器": [j.lower() for j in i["gameVersions"] if j.lower() in CURSEFORGE_LOADER_TYPE.values()],
                "下载量": i["downloadCount"],
                "更新日期": i["fileDate"].split("T")[0],
                "来源": "CurseForge",
                "哈希值": i["hashes"][0]["value"],
                "下载链接": i["downloadUrl"],
                "文件名称": i["fileName"],
                "文件大小": i["fileLength"],
            })

    dict = {}
    for i in RELEASE_VERSIONS:
        for j in list1:
            if i in j["游戏版本"]:
                if i not in dict.keys():
                    dict[i] = [j]
                else:
                    dict[i].append(j)
    for i in dict.keys():
        dict[i].sort(key=lambda x: x["更新日期"], reverse=True)
    return dict