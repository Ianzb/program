from .web_api import *

setting.add("minecraftJavaPath", f.pathJoin(program.USER_PATH, r"AppData\Roaming\.minecraft"))

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


def getPathGameInfo(path: str):
    """
    获得游戏版本和加载器信息
    @param path: 游戏版本路径
    @return: 数据
    """
    result = {"id": "", "游戏版本": "", "加载器": []}
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
                        result["加载器"].append([i["id"], i["version"].replace(result["游戏版本"], "").strip("-_ ")])
            if "libraries" in data.keys() and not result["加载器"]:
                for i in data["libraries"]:
                    if "net.minecraftforge:forge:" in i["name"]:
                        result["加载器"].append(["forge", i["name"].split(":")[-1].replace(result["游戏版本"], "").strip("-").split("-")[-1].strip("-_ ")])
                    elif "optifine:OptiFine" in i["name"]:
                        result["加载器"].append(["optifine", i["name"].replace(":installer", "").split(":")[-1].replace(result["游戏版本"], "").strip("-").split("-")[-1].strip("-_ ")])
                    elif "com.mumfrey:liteloader" in i["name"]:
                        result["加载器"].append(["liteloader", i["name"].split(":")[-1].strip("-").split("-")[-1].replace(result["游戏版本"], "").strip("-_ ")])
            for i in range(len(result["加载器"])):
                if result["加载器"][i][0] in LOADER_TYPE.values():
                    result["加载器"][i][0] = LOADER_TYPE_REVERSE[result["加载器"][i][0]]
            return result
        except Exception as ex:
            logging.warning(f"读取{path}下的游戏数据失败，报错信息为{ex}")
            return False


def getSaveInfo(path: str):
    """
    获得存档信息
    @param path: 存档文件夹路径
    @return: 数据
    """

    import python_nbt
    from datetime import datetime
    data = python_nbt.nbt.read_from_nbt_file(f.pathJoin(path, "level.dat")).json_obj(True)["value"]["Data"]["value"]
    data = {"名称": data["LevelName"]["value"],
            "种子": data["WorldGenSettings"]["value"]["seed"]["value"],
            "游戏模式": {0: "生存模式", 1: "创造模式", 2: "冒险模式", 3: "旁观模式"}[data["GameType"]["value"]],
            "游戏难度": {0: "和平", 1: "简单", 2: "普通", 3: "困难"}[data["Difficulty"]["value"]],
            "最近游玩": datetime.fromtimestamp(data["LastPlayed"]["value"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            "封面": f.pathJoin(path, "icon.png") if f.existPath(f.pathJoin(path, "icon.png")) else None,
            }
    return data


