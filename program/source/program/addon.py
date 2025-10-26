from .setting import *


class AddonManager:
    ADDON_OBJECT = {}  # 导入的插件的对象
    ADDON_MAINPAGE = {}

    def getOnlineAddonDict(self):
        """
        获取插件字典
        @return: 字典
        """
        try:
            response = zb.getUrl(program.ADDON_URL, headers=zb.REQUEST_HEADER)
            data = json.loads(response.text)
            logging.info("插件信息获取成功！")
            return data
        except:
            logging.warning(f"插件信息获取失败，报错信息：{traceback.format_exc()}！")

    def getAddonInfoFromUrl(self, url: str):
        """
        通过自述文件链接获取指定插件信息
        @param url: 自述文件链接
        @return: 信息
        """
        try:
            response = zb.getUrl(url, headers=zb.REQUEST_HEADER)
            data = json.loads(response.text)
            data["url"] = url
            logging.info(f"插件{data.get("name", "")}信息获取成功")
            return data
        except:
            logging.error(f"插件{url}信息获取失败，报错信息：{traceback.format_exc()}！")
            return False

    def downloadAddonFromInfo(self, data: dict):
        """
        通过插件自述文件数据链接获取指定插件信息
        @param data: 插件信息
        @param general_data: 基础链接（addon.json链接，仅文件为相对路径的时候需要）
        """

        try:
            logging.info(f"正在下载插件{data.get("name", "")}！")
            dir_path = zb.joinPath(program.ADDON_PATH, data.get("id", ""))
            zb.createDir(dir_path)
            with open(zb.joinPath(dir_path, "addon.json"), "w+", encoding="utf-8") as file:
                file.write(json.dumps(data, indent=2, ensure_ascii=False))
            result = zb.singleDownload(data.get("file", ""), dir_path, True, True)
            for package in data.get("packages", []):
                if "==" in package:
                    name, version = package.split("==")
                    self.installPackage(name, version)
                else:
                    self.installPackage(package)
            if result:
                zb.extractZip(result, dir_path, True)
                logging.info(f"插件{data.get("name", "")}下载成功！")
                return True
            else:
                logging.error(f"插件{data.get("name", "")}下载失败！")
                return False
        except:
            logging.error(f"插件{data.get("name", "")}在下载与解压过程中发生错误，报错信息：{traceback.format_exc()}！")
            return False

    def getInstalledAddonInfo(self):
        """
        获取本地插件信息，格式为 {“插件id”:{自述文件字典数据}...}
        @return: 信息
        """
        try:
            data = {}
            for i in zb.walkDir(program.ADDON_PATH, True):
                if zb.isFile(zb.joinPath(i, "addon.json")):
                    with open(zb.joinPath(i, "addon.json"), encoding="utf-8") as file:
                        addon_data = json.load(file)
                        key = addon_data.get("id", "")
                        if key:
                            data[key] = addon_data
            return data
        except:
            logging.error(f"获取本地插件信息失败，报错信息：{traceback.format_exc()}！")

    def installPackage(self, package_name: str | list, version: str = None, target_dir: str = program.PACKAGE_PATH):
        zb.createDir(target_dir)
        if target_dir not in sys.path:
            sys.path.insert(0, target_dir)

        try:
            # 尝试导入，如果已经存在则直接返回
            importlib.import_module(package_name.replace('-', '_'))
            logging.info(f"{package_name} 已存在")
            return True
        except ImportError:
            logging.info(f"正在安装 {package_name}...")

        from pypi_simple import PyPISimple
        class NewPyPISimple(PyPISimple):
            def __init__(self):
                super().__init__()

            def get_project_url(self, project: str) -> str:
                return super().get_project_url(project).replace("https://pypi.org/simple/", "https://mirrors.aliyun.com/pypi/simple/")

        with NewPyPISimple() as client:
            requests_page = client.get_project_page(package_name)
        packages = requests_page.packages
        if not version:
            url = None
            for package in packages:
                if package.package_type == "wheel":
                    url = package.url
        else:
            url = None
            for package in packages:
                if package.version == version and package.package_type == "wheel":
                    url = package.url
            if not url:
                url = None
                for package in packages:
                    if package.package_type == "wheel":
                        url = package.url
        if not url:
            logging.error(f"未找到{package_name}的安装包！")
            return False
        result = zb.singleDownload(url, target_dir, True, True)
        zb.extractZip(result, target_dir, True)


addonManager = AddonManager()
