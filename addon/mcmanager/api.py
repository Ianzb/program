import sys, os

sys.path = [os.path.dirname(sys.argv[0])] + sys.path
from source.custom import *

os.chdir(os.path.dirname(__file__))

try:
    from program.source.custom import *
except:
    pass

RELEASE_VERSIONS = ["1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17", "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16", "1.15.2", "1.15.1", "1.15", "1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14", "1.13.2", "1.13.1", "1.13", "1.12.2", "1.12.1", "1.12", "1.11.2", "1.11.1", "1.11", "1.10.2", "1.10.1", "1.10", "1.9.4", "1.9.3", "1.9.2", "1.9.1", "1.9", "1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2", "1.8.1", "1.8", "1.7.10", "1.7.9", "1.7.8", "1.7.7", "1.7.6", "1.7.5", "1.7.4", "1.7.3", "1.7.2", "1.6.4", "1.6.2", "1.6.1", "1.5.2", "1.5.1", "1.4.7", "1.4.6", "1.4.5", "1.4.4", "1.4.2", "1.3.2", "1.3.1", "1.2.5", "1.2.4", "1.2.3", "1.2.2", "1.2.1", "1.1", "1.0"]
CURSEFORGE_API_KEY = {
    "Accept": "application/json",
    "x-api-key": "$2a$10$P1NwR9RKf.xei0ApvtH.0u9JxczxbgvWzHsyTbRiaEXS2tMqC6Bgy"
}
CURSEFORGE_POST_API_KEY = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-api-key": "$2a$10$P1NwR9RKf.xei0ApvtH.0u9JxczxbgvWzHsyTbRiaEXS2tMqC6Bgy"
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
CURSEFORGE_LOADER_TYPE_REVERSE = dict([val, key] for key, val in CURSEFORGE_LOADER_TYPE.items())
LOADER_TYPE = {
    "Forge": "forge",
    "Cauldron": "cauldron",
    "LiteLoader": "liteloader",
    "Fabric": "fabric",
    "Quilt": "quilt",
    "NeoForge": "neoforge",
    "DataPack": "datapack",
    "Bukkit": "bukkit",
    "Folia": "folia",
    "Paper": "paper",
    "Purpur": "purpur",
    "Spigot": "spigot",
    "Iris": "iris",
    "Optifine": "optifine",
    "Sponge": "sponge",
    "Minecraft": "minecraft",
    "Canvas": "canvas",
    "Vanilla": "vanilla",
    "Rift": "rift",
    "Risugami's ModLoader": "modloader",
}
LOADER_TYPE_REVERSE = dict([val, key] for key, val in LOADER_TYPE.items())
MODRINTH_TYPE = {
    "模组": "mod",
    "整合包": "modpack",
    "资源包": "resourcepack",
    "光影": "shader",
    "数据包": "datapack",
    "插件": "plugin",
}
CURSEFORGE_TYPE = {
    "模组": 6,
    "整合包": 4471,
    "资源包": 12,
    "光影": 6552,
    "数据包": 6945,
    "插件": 5,
    "地图": 17,
    "Addon": 4559,
    "定制": 4546,

}

FILE_PATH = {
    "模组": "mods",
    "光影": "shaderpacks",
    "资源包": "resourcepacks",
    "存档": "saves"
}
FILE_SUFFIX = {
    "模组": [".jar", ".zip", ".disabled"],
    "光影": [".zip"],
    "资源包": [".zip"],
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


def searchMod(name: str, source: str = "CurseForge", version: str = "", page: int = 1, type: str = "模组") -> list:
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
        data = f.requestGet(f'https://api.modrinth.com/v2/search?query={name}&facets=[["project_type:{MODRINTH_TYPE[type]}"]{version}]&limit=50&offset={50 * (page - 1)}', program.REQUEST_HEADER)
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
                             "发布日期": i["date_created"].split("T")[0],
                             "类型": type,
                             })
    elif source == "CurseForge":
        version = f"&gameVersion={version}" if version != "全部" else ""
        name = f"&searchFilter={name}" if name else ""
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/search?gameId=432&classId={CURSEFORGE_TYPE[type]}{version}{name}&pageSize=50&sortOrder=desc&index={50 * (page - 1)}", CURSEFORGE_API_KEY)
        if "data" in json.loads(data):
            data = json.loads(data)["data"]
            for i in data:
                list.append({"id": i["id"],
                             "名称": i["name"],
                             "图标": i["logo"]["url"] if i["logo"] else "",
                             "介绍": i["summary"],
                             "下载量": i["downloadCount"],
                             "游戏版本": f.sortVersion([j for j in [k["gameVersion"] for k in i["latestFilesIndexes"]] if j in RELEASE_VERSIONS]),
                             "更新日期": i["dateReleased"].split("T")[0],
                             "作者": i["authors"][0]["name"],
                             "来源": "CurseForge",
                             "发布日期": i["dateCreated"].split("T")[0],
                             "类型": type,
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

        dict.update({
            "id": data["id"],
            "名称": data["title"],
            "图标": data["icon_url"],
            "介绍": data["description"],
            "下载量": data["downloads"],
            "游戏版本": f.sortVersion([j for j in data["game_versions"] if j in RELEASE_VERSIONS]),
            "更新日期": data["updated"].split("T")[0],
            "来源": "Modrinth",
            "源代码链接": data["source_url"],
            "加载器": [(LOADER_TYPE_REVERSE[i] if i in LOADER_TYPE_REVERSE.keys() else i) for i in data["loaders"]],
            "发布日期": data["published"].split("T")[0],
            "网站链接": f"https://modrinth.com/mod/{data['slug']}",
        })
    elif source == "CurseForge":
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/{mod_id}", CURSEFORGE_API_KEY)
        data = json.loads(data)["data"]

        loader = []
        for i in data["latestFilesIndexes"]:
            if "modLoader" in i.keys():
                loader.append(i["modLoader"])
        loader = list(set(loader))
        loader = [(LOADER_TYPE_REVERSE[CURSEFORGE_LOADER_TYPE[i]] if i in CURSEFORGE_LOADER_TYPE else str(i)) for i in loader]

        dict.update({
            "id": data["id"],
            "名称": data["name"],
            "图标": data["logo"]["url"] if data["logo"] else "",
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


def getModsInfo(mod_ids, source: str = "CurseForge") -> dict:
    """
    获得模组信息
    @param mod_ids: 模组id
    @param source: 数据源
    @return: 模组信息
    """
    data = []
    if source == "Modrinth":
        mod_ids = [mod_ids[i:i + 150] for i in range(0, len(mod_ids), 150)]
        for id in mod_ids:
            id = str(id).replace("'", '"')
            response = f.requestGet(f"https://api.modrinth.com/v2/projects?ids={id}", program.REQUEST_HEADER)
            response = json.loads(response)
            for i in response:
                data.append({
                    "id": i["id"],
                    "名称": i["title"],
                    "图标": i["icon_url"],
                    "介绍": i["description"],
                    "下载量": i["downloads"],
                    "游戏版本": f.sortVersion([j for j in i["game_versions"] if j in RELEASE_VERSIONS]),
                    "更新日期": i["updated"].split("T")[0],
                    "来源": "Modrinth",
                    "源代码链接": i["source_url"],
                    "加载器": [(LOADER_TYPE_REVERSE[j] if j in LOADER_TYPE_REVERSE.keys() else j) for j in i["loaders"]],
                    "发布日期": i["published"].split("T")[0],
                    "网站链接": f"https://modrinth.com/mod/{i['slug']}",
                })
    elif source == "CurseForge":
        post_info = {
            "modIds": mod_ids,
            "filterPcOnly": True
        }
        response = f.requestPost(f"https://api.curseforge.com/v1/mods", post_info, CURSEFORGE_POST_API_KEY)
        try:
            response = response.json()["data"]
        except:
            return None
        for i in response:
            loader = []
            for k in i["latestFilesIndexes"]:
                if "modLoader" in k.keys():
                    loader.append(k["modLoader"])
            loader = list(set(loader))
            loader = [(LOADER_TYPE_REVERSE[CURSEFORGE_LOADER_TYPE[i]] if i in CURSEFORGE_LOADER_TYPE else str(i)) for i in loader]

            data.append({
                "id": i["id"],
                "名称": i["name"],
                "图标": i["logo"]["url"] if i["logo"] else "",
                "介绍": i["summary"],
                "下载量": i["downloadCount"],
                "游戏版本": f.sortVersion([j for j in [k["gameVersion"] for k in i["latestFilesIndexes"]] if j in RELEASE_VERSIONS]),
                "更新日期": i["dateReleased"].split("T")[0],
                "作者": i["authors"][0]["name"],
                "来源": "CurseForge",
                "源代码链接": i["links"]["sourceUrl"],
                "加载器": loader,
                "发布日期": i["dateCreated"].split("T")[0],
                "网站链接": i["links"]["websiteUrl"],
            })
    return data


def getModFile(id, version: str = "", loader: str = "", source: str = "CurseForge") -> dict:
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
        loader = f'&loaders=["{LOADER_TYPE[loader] if loader in LOADER_TYPE.keys() else loader.lower()}"]' if loader not in ["全部", "", None] else ""
        data = f.requestGet(f"https://api.modrinth.com/v2/project/{id}/version?a=0{version}{loader}", program.REQUEST_HEADER)
        data = json.loads(data)
        for i in data:
            list1.append({
                "id": i["id"],
                "模组id": i["project_id"],
                "名称": i["name"],
                "版本号": i["version_number"],
                "前置": [j["project_id"] for j in i["dependencies"] if j["dependency_type"] == "required"],
                "游戏版本": f.sortVersion([j for j in i["game_versions"] if j in RELEASE_VERSIONS]),
                "版本类型": i["version_type"],
                "加载器": [(LOADER_TYPE_REVERSE[i] if i in LOADER_TYPE_REVERSE.keys() else i) for i in i["loaders"]],
                "下载量": i["downloads"],
                "更新日期": i["date_published"].split("T")[0],
                "来源": "Modrinth",
                "哈希值": i["files"][0]["hashes"]["sha1"],
                "下载链接": i["files"][0]["url"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if i["files"][0]["url"] else i["files"][0]["url"],
                "文件名称": i["files"][0]["filename"],
                "文件大小": i["files"][0]["size"],
            })
    elif source == "CurseForge":
        version = f"&gameVersion={version}" if version not in ["全部", "", None] else ""
        if (LOADER_TYPE[loader] if loader in LOADER_TYPE.keys() else loader) in list(CURSEFORGE_LOADER_TYPE_REVERSE.keys()) + ["全部", "", None]:
            loader = f"&modLoaderType={CURSEFORGE_LOADER_TYPE_REVERSE[LOADER_TYPE[loader]]}" if loader not in ["全部", "", None] else ""
        else:
            loader = ""
        data = f.requestGet(f"https://api.curseforge.com/v1/mods/{id}/files?a=0{version}{loader}", CURSEFORGE_API_KEY)
        data = json.loads(data)["data"]

        for i in data:
            list1.append({
                "id": i["id"],
                "模组id": i["modId"],
                "名称": i["displayName"],
                # "版本号": i["version_number"],
                "前置": [j["modId"] for j in i["dependencies"] if j["relationType"] == 3],
                "游戏版本": f.sortVersion([j for j in i["gameVersions"] if j in RELEASE_VERSIONS]),
                "版本类型": CURSEFORGE_VERSION_TYPE[i["releaseType"]],
                "加载器": [(LOADER_TYPE_REVERSE[j.lower()] if j.lower() in LOADER_TYPE_REVERSE.keys() else j.lower()) for j in i["gameVersions"] if j.lower() in CURSEFORGE_LOADER_TYPE.values()],
                "下载量": i["downloadCount"],
                "更新日期": i["fileDate"].split("T")[0],
                "来源": "CurseForge",
                "哈希值": i["fileFingerprint"],
                "下载链接": i["downloadUrl"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if i["downloadUrl"] else i["downloadUrl"],
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


def CurseForgeHash(file: str):
    from murmurhash2 import murmurhash2
    with open(file, 'rb') as file:
        filtered_bytes = bytearray()
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            for byte in chunk:
                if byte not in (0x09, 0x0A, 0x0D, 0x20):
                    filtered_bytes.append(byte)
        data = murmurhash2(bytes(filtered_bytes), seed=1) & 0xFFFFFFFF
    return data


def getInfoFromHash(path, source: str = "CurseForge"):
    """
    从本地文件获得模组信息
    @param path: 文件
    @param source: 数据源
    """
    if source == "Modrinth":
        if f.isDir(path):
            path = f.walkFile(path, 1)
        elif f.isFile(path):
            path = [path]
        elif type(path) == list:
            pass
        else:
            return False
        path = [i for i in path if not i.endswith(".old")]
        hash = {}
        for i in path:
            hash[f.splitPath(i)] = f.getSha1(i)
        post_info = {
            "hashes": list(hash.values()),
            "algorithm": "sha1"
        }
        hash_reverse = dict([val, key] for key, val in hash.items())
        response = f.requestPost(f"https://api.modrinth.com/v2/version_files", post_info, CURSEFORGE_POST_API_KEY)
        try:
            response = response.json()
        except:
            return None
        data = []
        for i in list(response.values()):
            data.append({
                "id": i["id"],
                "模组id": i["project_id"],
                "名称": i["name"],
                "版本号": i["version_number"],
                "前置": [j["project_id"] for j in i["dependencies"] if j["dependency_type"] == "required"],
                "游戏版本": f.sortVersion([j for j in i["game_versions"] if j in RELEASE_VERSIONS]),
                "版本类型": i["version_type"],
                "加载器": [(LOADER_TYPE_REVERSE[j] if j in LOADER_TYPE_REVERSE.keys() else j) for j in i["loaders"]],
                "下载量": i["downloads"],
                "更新日期": i["date_published"].split("T")[0],
                "来源": "Modrinth",
                "哈希值": i["files"][0]["hashes"]["sha1"],
                "下载链接": i["files"][0]["url"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if i["files"][0]["url"] else i["files"][0]["url"],
                "文件名称": i["files"][0]["filename"],
                "文件大小": i["files"][0]["size"],
                "源文件名称": hash_reverse[i["files"][0]["hashes"]["sha1"]],
            })
    elif source == "CurseForge":
        if f.isDir(path):
            path = f.walkFile(path, 1)
        elif f.isFile(path):
            path = [path]
        elif type(path) == list:
            pass
        else:
            return False
        path = [i for i in path if not i.endswith(".old")]
        hash = {}
        for i in path:
            hash[f.splitPath(i)] = CurseForgeHash(i)
        post_info = {
            "fingerprints": list(hash.values())
        }
        hash_reverse = dict([val, key] for key, val in hash.items())
        response = f.requestPost("https://api.curseforge.com/v1/fingerprints/432", post_info, CURSEFORGE_POST_API_KEY)
        response = response.json()["data"]["exactMatches"]  # [0]["file"]
        data = []
        for i in response:
            i = i["file"]
            data.append({
                "id": i["id"],
                "模组id": i["modId"],
                "名称": i["displayName"],
                # "版本号": i["version_number"],
                "前置": [j["modId"] for j in i["dependencies"] if j["relationType"] == 3],
                "游戏版本": f.sortVersion([j for j in i["gameVersions"] if j in RELEASE_VERSIONS]),
                "版本类型": CURSEFORGE_VERSION_TYPE[i["releaseType"]],
                "加载器": [(LOADER_TYPE_REVERSE[j.lower()] if j.lower() in LOADER_TYPE_REVERSE.keys() else j.lower()) for j in i["gameVersions"] if j.lower() in CURSEFORGE_LOADER_TYPE.values()],
                "下载量": i["downloadCount"],
                "更新日期": i["fileDate"].split("T")[0],
                "来源": "CurseForge",
                "哈希值": i["fileFingerprint"],
                "下载链接": i["downloadUrl"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if i["downloadUrl"] else i["downloadUrl"],
                "文件名称": i["fileName"],
                "文件大小": i["fileLength"],
                "源文件名称": hash_reverse[i["fileFingerprint"]],
            })

    return data


def getNewestFromHash(path, version: str, loader: str, source: str = "CurseForge"):
    """
    从本地文件获得模组最新版本
    @param path: 文件
    @param version: 版本
    @param loader: 加载器
    @param source: 数据源
    """
    if source == "Modrinth":
        if f.isDir(path):
            path = f.walkFile(path, 1)
        elif f.isFile(path):
            path = [path]
        elif type(path) == list:
            pass
        else:
            return False
        path = [i for i in path if not i.endswith(".old")]
        hash = {}
        for i in path:
            hash[f.splitPath(i)] = f.getSha1(i)
        post_info = {
            "hashes": list(hash.values()),
            "algorithm": "sha1",
            "loaders": [
                LOADER_TYPE[loader] if loader in LOADER_TYPE.keys() else loader.lower(),
            ],
            "game_versions": [
                version,
            ]
        }
        hash_reverse = dict([val, key] for key, val in hash.items())
        response = f.requestPost(f"https://api.modrinth.com/v2/version_files/update", post_info, CURSEFORGE_POST_API_KEY)
        try:
            response = response.json()
        except:
            return None
        data = []
        for i in list(response.values()):
            data.append({
                "id": i["id"],
                "模组id": i["project_id"],
                "名称": i["name"],
                "版本号": i["version_number"],
                "前置": [j["project_id"] for j in i["dependencies"] if j["dependency_type"] == "required"],
                "游戏版本": f.sortVersion([j for j in i["game_versions"] if j in RELEASE_VERSIONS]),
                "版本类型": i["version_type"],
                "加载器": [(LOADER_TYPE_REVERSE[j] if j in LOADER_TYPE_REVERSE.keys() else j) for j in i["loaders"]],
                "下载量": i["downloads"],
                "更新日期": i["date_published"].split("T")[0],
                "来源": "Modrinth",
                "哈希值": i["files"][0]["hashes"]["sha1"],
                "下载链接": i["files"][0]["url"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if i["files"][0]["url"] else i["files"][0]["url"],
                "文件名称": i["files"][0]["filename"],
                "文件大小": i["files"][0]["size"],
            })
    elif source == "CurseForge":
        response = getInfoFromHash(path, source)
        data = []
        for i in response:
            data.append(getModFile(i["模组id"], version, loader, source))

    return data
