import sys, os

sys.path.append(os.path.dirname(sys.argv[0]))
from source.custom import *

try:
    from program.source.custom import *
except:
    pass

setting.add("minecraftJavaPath", f.pathJoin(program.USER_PATH, r"AppData\Roaming\.minecraft"))


class MinecraftFunctions(QWidget):
    """
    Minecraft函数
    """
    versionUpdateSignal = pyqtSignal()
    FILE_DOWNLOAD_PATH = setting.read("minecraftJavaPath")  # 游戏文件下载根路径
    FILE_PATH = {
        "模组": "mods",
        "光影包": "shaderpacks",
        "资源包": "resourcepacks",
        "存档": "saves",
        "截图": "screenshots",
    }  # 文件类型-文件夹名称映射表
    FILE_SUFFIX = {
        "模组": [".jar", ".zip", ".disabled"],
        "光影包": [".zip"],
        "资源包": [".zip"],
    }  # 文件类型-文件格式映射表

    RELEASE_VERSIONS = ["1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
                        "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19",
                        "1.18.2", "1.18.1", "1.18",
                        "1.17.1", "1.17",
                        "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16",
                        "1.15.2", "1.15.1", "1.15",
                        "1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14",
                        "1.13.2", "1.13.1", "1.13",
                        "1.12.2", "1.12.1", "1.12",
                        "1.11.2", "1.11.1", "1.11",
                        "1.10.2", "1.10.1", "1.10",
                        "1.9.4", "1.9.3", "1.9.2", "1.9.1", "1.9",
                        "1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2", "1.8.1", "1.8",
                        "1.7.10", "1.7.9", "1.7.8", "1.7.7", "1.7.6", "1.7.5", "1.7.4", "1.7.3", "1.7.2",
                        "1.6.4", "1.6.2", "1.6.1", "1.5.2", "1.5.1",
                        "1.4.7", "1.4.6", "1.4.5", "1.4.4", "1.4.2",
                        "1.3.2", "1.3.1",
                        "1.2.5", "1.2.4", "1.2.3", "1.2.2", "1.2.1",
                        "1.1", "1.0"]  # Minecraft正式版
    MOD_LOADER_LIST = ["Forge", "Fabric", "Quilt", "NeoForge"]

    CURSEFORGE_HEADER = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": "$2a$10$P1NwR9RKf.xei0ApvtH.0u9JxczxbgvWzHsyTbRiaEXS2tMqC6Bgy"
    }  # CurseForge网络请求API
    CURSEFORGE_VERSION_TYPE = {
        1: "release",
        2: "beta",
        3: "alpha",
    }  # CurseForge文件版本类型映射表
    CURSEFORGE_LOADER = {
        "全部": 0,
        "Forge": 1,
        "Cauldron": 2,
        "LiteLoader": 3,
        "Fabric": 4,
        "Quilt": 5,
        "NeoForge": 6,
    }  # CurseForge模组加载器映射表-全称为键
    CURSEFORGE_LOADER_REVERSE = dict([val, key] for key, val in CURSEFORGE_LOADER.items())  # CurseForge模组加载器映射表-id为键
    CURSEFORGE_TYPE = {
        "模组": 6,
        "整合包": 4471,
        "资源包": 12,
        "光影包": 6552,
        "数据包": 6945,
        "插件": 5,
        "地图": 17,
        "Addon": 4559,
        "定制": 4546,
    }  # CurseForge资源类型映射表

    MODRINTH_TYPE = {
        "模组": "mod",
        "整合包": "modpack",
        "资源包": "resourcepack",
        "光影包": "shader",
        "数据包": "datapack",
        "插件": "plugin",
    }  # Modrinth资源类型映射表
    MODRINTH_LOADER = {
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
        "BungeeCord": "bungeecord",
        "Velocity": "velocity",
        "Waterfall": "waterfall",
    }  # 通用模组加载器全称简称映射表-全称为键
    MODRINTH_LOADER_REVERSE = dict([val, key] for key, val in MODRINTH_LOADER.items())  # 通用模组加载器全称简称映射表-id为键

    def __init__(self):
        super().__init__()

    def getVersionList(self, version_type: str = "release"):
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

    def searchMod(self, name: str, source: str = "CurseForge", version: str = "", page: int = 1,
                  type: str = "模组") -> list:
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
            data = f.requestGet(
                f'https://api.modrinth.com/v2/search?query={name}&facets=[["project_type:{self.MODRINTH_TYPE[type]}"]{version}]&limit=50&offset={50 * (page - 1)}',
                program.REQUEST_HEADER)
            if "hits" in json.loads(data):
                data = json.loads(data)["hits"]
                for i in data:
                    list.append({"id": i["project_id"],
                                 "名称": i["title"],
                                 "图标": i["icon_url"],
                                 "介绍": i["description"],
                                 "下载量": i["downloads"],
                                 "游戏版本": f.sortVersion([j for j in i["versions"] if self.isRelease(j)]),
                                 "更新日期": i["date_modified"].split("T")[0],
                                 "作者": i["author"],
                                 "来源": "Modrinth",
                                 "发布日期": i["date_created"].split("T")[0],
                                 "类型": type,
                                 })
        elif source == "CurseForge":
            version = f"&gameVersion={version}" if version != "全部" else ""
            name = f"&searchFilter={name}" if name else ""
            data = f.requestGet(
                f"https://api.curseforge.com/v1/mods/search?gameId=432&classId={self.CURSEFORGE_TYPE[type]}{version}{name}&pageSize=50&sortOrder=desc&index={50 * (page - 1)}",
                self.CURSEFORGE_HEADER)
            if "data" in json.loads(data):
                data = json.loads(data)["data"]
                for i in data:
                    list.append({"id": i["id"],
                                 "名称": i["name"],
                                 "图标": i["logo"]["url"] if i["logo"] else "",
                                 "介绍": i["summary"],
                                 "下载量": i["downloadCount"],
                                 "游戏版本": f.sortVersion(
                                     [j for j in [k["gameVersion"] for k in i["latestFilesIndexes"]] if
                                      self.isRelease(j)]),
                                 "更新日期": i["dateReleased"].split("T")[0],
                                 "作者": i["authors"][0]["name"],
                                 "来源": "CurseForge",
                                 "发布日期": i["dateCreated"].split("T")[0],
                                 "类型": type,
                                 })
        return list

    def getModInfo(self, mod_id, source: str = "CurseForge") -> dict:
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
                "游戏版本": f.sortVersion([j for j in data["game_versions"] if self.isRelease(j)]),
                "更新日期": data["updated"].split("T")[0],
                "来源": "Modrinth",
                "源代码链接": data["source_url"],
                "加载器": [(self.MODRINTH_LOADER_REVERSE[i] if i in self.MODRINTH_LOADER.values() else i) for i in
                           data["loaders"]],
                "发布日期": data["published"].split("T")[0],
                "网站链接": f"https://modrinth.com/mod/{data["slug"]}",
            })
        elif source == "CurseForge":
            data = f.requestGet(f"https://api.curseforge.com/v1/mods/{mod_id}", self.CURSEFORGE_HEADER)
            data = json.loads(data)["data"]

            loader = []
            for i in data["latestFilesIndexes"]:
                if "modLoader" in i.keys():
                    loader.append(i["modLoader"])
            loader = list(set(loader))
            loader = [(self.CURSEFORGE_LOADER_REVERSE[i] if i in self.CURSEFORGE_LOADER.values() else i) for i in
                      loader]

            dict.update({
                "id": data["id"],
                "名称": data["name"],
                "图标": data["logo"]["url"] if data["logo"] else "",
                "介绍": data["summary"],
                "下载量": data["downloadCount"],
                "游戏版本": f.sortVersion(
                    [j for j in [k["gameVersion"] for k in data["latestFilesIndexes"]] if self.isRelease(j)]),
                "更新日期": data["dateReleased"].split("T")[0],
                "作者": data["authors"][0]["name"],
                "来源": "CurseForge",
                "源代码链接": data["links"]["sourceUrl"],
                "加载器": loader,
                "发布日期": data["dateCreated"].split("T")[0],
                "网站链接": data["links"]["websiteUrl"],
            })
        return dict

    def getModsInfo(self, mod_ids, source: str = "CurseForge") -> dict:
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
                        "游戏版本": f.sortVersion([j for j in i["game_versions"] if self.isRelease(j)]),
                        "更新日期": i["updated"].split("T")[0],
                        "来源": "Modrinth",
                        "源代码链接": i["source_url"],
                        "加载器": [(self.MODRINTH_LOADER_REVERSE[j] if j in self.MODRINTH_LOADER.values() else j) for j
                                   in i["loaders"]],
                        "发布日期": i["published"].split("T")[0],
                        "网站链接": f"https://modrinth.com/mod/{i["slug"]}",
                    })
        elif source == "CurseForge":
            post_info = {
                "modIds": mod_ids,
                "filterPcOnly": True
            }
            response = f.requestPost(f"https://api.curseforge.com/v1/mods", post_info, self.CURSEFORGE_HEADER)
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
                loader = [(self.CURSEFORGE_LOADER_REVERSE[i] if i in self.CURSEFORGE_LOADER.values() else i) for i in
                          loader]

                data.append({
                    "id": i["id"],
                    "名称": i["name"],
                    "图标": i["logo"]["url"] if i["logo"] else "",
                    "介绍": i["summary"],
                    "下载量": i["downloadCount"],
                    "游戏版本": f.sortVersion(
                        [j for j in [k["gameVersion"] for k in i["latestFilesIndexes"]] if self.isRelease(j)]),
                    "更新日期": i["dateReleased"].split("T")[0],
                    "作者": i["authors"][0]["name"],
                    "来源": "CurseForge",
                    "源代码链接": i["links"]["sourceUrl"],
                    "加载器": loader,
                    "发布日期": i["dateCreated"].split("T")[0],
                    "网站链接": i["links"]["websiteUrl"],
                })
        return data

    def getModFile(self, id, version: str = "", loader: str | list = "", source: str = "CurseForge") -> dict:
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
            loader = f'&loaders=["{self.MODRINTH_LOADER[loader] if loader in self.MODRINTH_LOADER.keys() else loader.lower()}"]' if loader not in [
                "全部", "", None] else ""
            data = f.requestGet(f"https://api.modrinth.com/v2/project/{id}/version?a=0{version}{loader}",
                                program.REQUEST_HEADER)
            data = json.loads(data)
            for i in data:
                list1.append({
                    "id": i["id"],
                    "模组id": i["project_id"],
                    "名称": i["name"],
                    "版本号": i["version_number"],
                    "前置": [j["project_id"] for j in i["dependencies"] if j["dependency_type"] == "required"],
                    "游戏版本": f.sortVersion([j for j in i["game_versions"] if self.isRelease(j)]),
                    "版本类型": i["version_type"],
                    "加载器": [(self.MODRINTH_LOADER_REVERSE[i] if i in self.MODRINTH_LOADER.values() else i) for i in
                               i["loaders"]],
                    "下载量": i["downloads"],
                    "更新日期": i["date_published"].split("T")[0],
                    "来源": "Modrinth",
                    "哈希值": i["files"][0]["hashes"]["sha1"],
                    "下载链接": i["files"][0]["url"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if
                    i["files"][0]["url"] else i["files"][0]["url"],
                    "文件名称": i["files"][0]["filename"],
                    "文件大小": i["files"][0]["size"],
                })
        elif source == "CurseForge":
            version = f"&gameVersion={version}" if version not in ["全部", "", None] else ""
            if type(loader) == list:
                loader = ""
            else:
                loader = f"&modLoaderType={self.CURSEFORGE_LOADER[loader]}" if loader in self.CURSEFORGE_LOADER.keys() and loader not in [
                    "全部", "", None] else ""
            data = f.requestGet(f"https://api.curseforge.com/v1/mods/{id}/files?a=0{version}{loader}",
                                self.CURSEFORGE_HEADER)
            data = json.loads(data)["data"]

            for i in data:
                list1.append({
                    "id": i["id"],
                    "模组id": i["modId"],
                    "名称": i["displayName"],
                    # "版本号": i["version_number"],
                    "前置": [j["modId"] for j in i["dependencies"] if j["relationType"] == 3],
                    "游戏版本": f.sortVersion([j for j in i["gameVersions"] if self.isRelease(j)]),
                    "版本类型": self.CURSEFORGE_VERSION_TYPE[i["releaseType"]],
                    "加载器": [(self.MODRINTH_LOADER_REVERSE[
                                    j.lower()] if j.lower() in self.MODRINTH_LOADER.values() else j.lower()) for j in
                               i["gameVersions"] if j in self.CURSEFORGE_LOADER.keys()],
                    "下载量": i["downloadCount"],
                    "更新日期": i["fileDate"].split("T")[0],
                    "来源": "CurseForge",
                    "哈希值": i["fileFingerprint"],
                    "下载链接": i["downloadUrl"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if i[
                        "downloadUrl"] else i["downloadUrl"],
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

    def CurseForgeHash(self, file: str):
        from .murmurhash2 import murmurhash2
        with open(file, "rb") as file:
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

    def getInfoFromHash(self, path, source: str = "CurseForge"):
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
            response = f.requestPost(f"https://api.modrinth.com/v2/version_files", post_info, self.CURSEFORGE_HEADER)
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
                    "游戏版本": f.sortVersion([j for j in i["game_versions"] if self.isRelease(j)]),
                    "版本类型": i["version_type"],
                    "加载器": [(self.MODRINTH_LOADER_REVERSE[j] if j in self.MODRINTH_LOADER.values() else j) for j in
                               i["loaders"]],
                    "下载量": i["downloads"],
                    "更新日期": i["date_published"].split("T")[0],
                    "来源": "Modrinth",
                    "哈希值": i["files"][0]["hashes"]["sha1"],
                    "下载链接": i["files"][0]["url"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if
                    i["files"][0]["url"] else i["files"][0]["url"],
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
                hash[f.splitPath(i)] = self.CurseForgeHash(i)
            post_info = {
                "fingerprints": list(hash.values())
            }
            hash_reverse = dict([val, key] for key, val in hash.items())
            response = f.requestPost("https://api.curseforge.com/v1/fingerprints/432", post_info,
                                     self.CURSEFORGE_HEADER)
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
                    "游戏版本": f.sortVersion([j for j in i["gameVersions"] if self.isRelease(j)]),
                    "版本类型": self.CURSEFORGE_VERSION_TYPE[i["releaseType"]],
                    "加载器": [(self.MODRINTH_LOADER_REVERSE[
                                    j.lower()] if j.lower() in self.MODRINTH_LOADER.values() else j.lower()) for j in
                               i["gameVersions"] if j in self.CURSEFORGE_LOADER.keys()],
                    "下载量": i["downloadCount"],
                    "更新日期": i["fileDate"].split("T")[0],
                    "来源": "CurseForge",
                    "哈希值": i["fileFingerprint"],
                    "下载链接": i["downloadUrl"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if i[
                        "downloadUrl"] else i["downloadUrl"],
                    "文件名称": i["fileName"],
                    "文件大小": i["fileLength"],
                    "源文件名称": hash_reverse[i["fileFingerprint"]],
                })

        return data

    def getNewestFromHash(self, path, version: str, loader: str | list, source: str = "CurseForge"):
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
            if type(loader) == str:
                loader = [loader]
            path = [i for i in path if not i.endswith(".old")]
            hash = {}
            for i in path:
                hash[f.splitPath(i)] = f.getSha1(i)
            post_info = {
                "hashes": list(hash.values()),
                "algorithm": "sha1",
                "loaders": [self.MODRINTH_LOADER[i] for i in loader if i in self.MODRINTH_LOADER.keys()],
                "game_versions": [
                    version,
                ]
            }
            hash_reverse = dict([val, key] for key, val in hash.items())
            response = f.requestPost(f"https://api.modrinth.com/v2/version_files/update", post_info,
                                     self.CURSEFORGE_HEADER)
            try:
                response = response.json()
            except:
                return None
            data = []
            for k, i in response.items():
                data.append({
                    "id": i["id"],
                    "模组id": i["project_id"],
                    "名称": i["name"],
                    "版本号": i["version_number"],
                    "前置": [j["project_id"] for j in i["dependencies"] if j["dependency_type"] == "required"],
                    "游戏版本": f.sortVersion([j for j in i["game_versions"] if self.isRelease(j)]),
                    "版本类型": i["version_type"],
                    "加载器": [(self.MODRINTH_LOADER_REVERSE[j] if j in self.MODRINTH_LOADER.values() else j) for j in
                               i["loaders"]],
                    "下载量": i["downloads"],
                    "更新日期": i["date_published"].split("T")[0],
                    "来源": "Modrinth",
                    "哈希值": i["files"][0]["hashes"]["sha1"],
                    "下载链接": i["files"][0]["url"].replace("edge.forgecdn.net", "mediafilez.forgecdn.net") if
                    i["files"][0]["url"] else i["files"][0]["url"],
                    "文件名称": i["files"][0]["filename"],
                    "文件大小": i["files"][0]["size"],
                    "源文件名称": hash_reverse[k],
                })
        elif source == "CurseForge":
            response = self.getInfoFromHash(path, source)
            data = []
            for i in response:
                data.append(self.getModFile(i["模组id"], version, loader, source))

        return data

    def getPathGameInfo(self, path: str):
        """
        获得游戏版本和加载器信息
        @param path: 游戏版本路径
        @return: 数据
        """
        result = {"路径": path, "id": "", "游戏版本": "", "加载器": []}
        json_path = f.pathJoin(path, f.splitPath(path) + ".json")
        if f.existPath(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as file:
                    data = json.loads(file.read())
                result["id"] = data["id"]
                if "jar" in data.keys() and not result["游戏版本"]:
                    result["游戏版本"] = data["jar"]
                if "clientVersion" in data.keys() and not result["游戏版本"]:
                    result["游戏版本"] = data["clientVersion"]
                if "assets" in data.keys() and not result["游戏版本"]:
                    result["游戏版本"] = data["assets"]
                if "patches" in data.keys():
                    for i in data["patches"]:
                        if i["id"] != "game" and "version" in i.keys():
                            result["加载器"].append(
                                [i["id"], i["version"].replace(result["游戏版本"], "").strip("-_ ")])
                        if i["id"] == "game":
                            result["游戏版本"] = i["version"]
                if "libraries" in data.keys() and not result["加载器"]:
                    def findVersionCode(lst):
                        import re
                        strings_with_numbers = [s for s in lst if re.search(r"\d", s)]
                        last_string_with_number = strings_with_numbers[-1] if strings_with_numbers else None
                        return last_string_with_number.replace(result["游戏版本"], "").strip("-_ ")

                    forge = False
                    fabric = False
                    optifine = False
                    liteloader = False

                    for i in data["libraries"]:
                        if "net.minecraftforge:forge:" in i["name"] and not forge:
                            result["加载器"].append(["forge", findVersionCode(i["name"].split(":"))])
                            forge = True
                        elif "optifine:OptiFine" in i["name"] and not optifine:
                            result["加载器"].append(["optifine", findVersionCode(i["name"].split(":"))])
                            optifine = True
                        elif "com.mumfrey:liteloader" in i["name"] and not liteloader:
                            result["加载器"].append(["liteloader", findVersionCode(i["name"].split(":"))])
                            liteloader = True
                        elif "net.fabricmc:fabric-loader:" in i["name"] and not fabric:
                            result["加载器"].append(["fabric", findVersionCode(i["name"].split(":"))])
                            fabric = True

                for i in range(len(result["加载器"])):
                    if result["加载器"][i][0] in self.MODRINTH_LOADER.values():
                        result["加载器"][i][0] = self.MODRINTH_LOADER_REVERSE[result["加载器"][i][0]]
                return result
            except Exception as ex:
                logging.warning(f"读取{path}下的游戏数据失败，报错信息为{ex}")
                return False

    def getSaveInfo(self, path: str):
        """
        获得存档信息
        @param path: 存档文件夹路径
        @return: 数据
        """
        from .python_nbt import read_from_nbt_file
        from datetime import datetime
        data = read_from_nbt_file(f.pathJoin(path, "level.dat")).json_obj(True)["value"]["Data"]["value"]
        data = {"名称": data["LevelName"]["value"],
                "种子": data["WorldGenSettings"]["value"]["seed"]["value"],
                "游戏模式": {0: "生存模式", 1: "创造模式", 2: "冒险模式", 3: "旁观模式"}[data["GameType"]["value"]],
                "游戏难度": {0: "和平", 1: "简单", 2: "普通", 3: "困难"}[data["Difficulty"]["value"]],
                "最近游玩": datetime.fromtimestamp(data["LastPlayed"]["value"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                "封面": f.pathJoin(path, "icon.png") if f.existPath(f.pathJoin(path, "icon.png")) else None,
                "路径": path,
                }
        return data

    def isMinecraftPath(self, path: str):
        """
        判断路径是否为Minecraft路径
        @param path: 路径
        @return: 是否
        """
        if f.isDir(path):
            if f.existPath(f.pathJoin(path, f.splitPath(path) + ".json")):
                return "version"
            elif f.existPath(f.pathJoin(path, "versions")) and f.existPath(f.pathJoin(path, "assets")) and f.existPath(
                    f.pathJoin(path, "libraries")):
                return "minecraft"

    def isRelease(self, version: str):
        """
        判断是否为正式版
        @param version: 版本
        @return: 是否
        """
        return not any(c.isalpha() for c in version)

    def getVersionImg(self, version: str):
        """
        获得正式版/测试版版本图标
        @param version: 版本
        @return: 图片链接
        """
        if self.isRelease(version):
            return "grass_block.png", "https://patchwiki.biligame.com/images/mc/d/d0/jsva4b20p50dyilh54o7jnzmt5eytt4.png"
        else:
            return "dirt_block.png", "https://patchwiki.biligame.com/images/mc/a/af/7js1n1i51sg8z5j6phsci4sr7pc83u8.png"

    def getNewestVersion(self) -> str:
        """
        获取Minecraft最新版本
        @return: 字符串
        """

        def changeList(data: list, index: dict):
            """
            批量替换元素
            @param data: 数据列表
            @param index: 替换字典{键值替换键名}
            @return:
            """
            for i in range(len(data)):
                for k, v in index.items():
                    data[i] = data[i].replace(k, v)
            return data

        useful = ["{{v|java}}",
                  "{{v|java-experimental}}",
                  "{{v|java-snap}}",
                  "{{v|bedrock}}",
                  "{{v|bedrock-beta}}",
                  "{{v|bedrock-preview}}",
                  "{{v|dungeons}}",
                  "{{v|legends-win}}",
                  "{{v|launcher}}",
                  "{{v|launcher-beta}}",
                  "{{v|education}}",
                  "{{v|education-beta}}",
                  "{{v|education-preview}}",
                  "{{v|china-win}}",
                  "{{v|china-android}}",
                  ]
        try:
            response = f.requestGet("https://zh.minecraft.wiki/w/Template:Version", timeout=(5, 10))
        except Exception as ex:
            logging.warning(f"无法连接至Minecraft Wiki服务器{ex}")
            return "无法连接至服务器"
        soup = bs4.BeautifulSoup(response, "lxml")
        data = soup.find_all(name="td")
        l1 = [n.text.replace("\n", "") for n in data]
        v1 = l1[::3]
        v2 = l1[1::3]
        v3 = l1[2::3]
        str1 = ""
        v1 = changeList(v1, {"（": "", "）": ""})
        for i in range(len(v1)):
            if v1[i][-1] == "版":
                v1[i] = v1[i] + "正式版"
            if v3[i] == "{{v|china-win}}":
                v1[i] = "中国版端游"
            elif v3[i] == "{{v|china-android}}":
                v1[i] = "中国版手游"
            elif v3[i] == "{{v|legends-win}}":
                v1[i] = "我的世界：传奇"
            elif v3[i] == "{{v|dungeons}}":
                v1[i] = "我的世界：地下城"
            if v3[i] in useful and v2[i] != "":
                str1 += v1[i] + "版本：" + v2[i] + "\n"
        logging.debug("成功获取我的世界最新版本")
        return str1


mc = MinecraftFunctions()
