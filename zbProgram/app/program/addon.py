from .manager import *

import shutil
import importlib.metadata as importlib_metadata

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion, parse as parse_version
from packaging.tags import sys_tags


class AddonManager:
    ADDON_OBJECT = {}  # 导入的插件的对象
    ADDON_MAIN_PAGE = {}

    # 常见“发行名 != 导入名”映射，用于导入可用性检查
    IMPORT_ALIASES = {
        "pillow": "PIL",
        "pycryptodome": "Crypto",
        "beautifulsoup4": "bs4",
        "pyyaml": "yaml",
        "opencv-python": "cv2",
        "scikit-learn": "sklearn",
        "python-dateutil": "dateutil",
    }

    def _try_import(self, package: str) -> bool:
        """尝试按发行名导入对应的模块，成功返回 True"""
        module_name = self.IMPORT_ALIASES.get(package.lower(), package.replace("-", "_"))
        try:
            importlib.import_module(module_name)
            return True
        except Exception:
            return False

    def _compatible_tag_set(self) -> set:
        """当前解释器可用的 (python tag, abi tag, platform tag) 集合"""
        try:
            return {(t.interpreter, t.abi, t.platform) for t in sys_tags()}
        except Exception:
            logging.warning(f"获取当前平台兼容标签失败：{traceback.format_exc()}")
            return set()

    def _is_compatible_wheel(self, filename: str) -> bool:
        """根据 wheel 文件名判断是否兼容当前平台与 Python 版本"""
        try:
            stem = os.path.basename(str(filename))
            if not stem.endswith(".whl"):
                return False
            parts = stem[:-4].split("-")
            # wheel 文件名从尾部取三段标签：...-{python tag}-{abi tag}-{platform tag}.whl
            # （distribution-version 之间可能存在可选 build tag，故不能从头部定索引）
            if len(parts) < 5:
                return False
            compatible = self._compatible_tag_set()
            if not compatible:
                return False
            for py in parts[-3].split("."):
                for abi in parts[-2].split("."):
                    for plat in parts[-1].split("."):
                        if (py, abi, plat) in compatible:
                            return True
            return False
        except Exception:
            return False

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
            return {}

    def downloadAddonFromInfo(self, data: dict, progress=None):
        """
        通过插件自述文件数据链接获取指定插件信息
        @param data: 插件信息
        @param general_data: 基础链接（addon.json链接，仅文件为相对路径的时候需要）
        @param progress: 可选回调 progress(str)，用于向任务中心等上报安装阶段
        """

        def report(text):
            if progress:
                try:
                    progress(text)
                except Exception:
                    pass

        try:
            logging.info(f"正在下载插件{data.get("name", "")}！")
            report(f"正在下载插件包...")
            dir_path = zb.joinPath(program.ADDON_PATH, data.get("id", ""))
            zb.createDir(dir_path)
            with open(zb.joinPath(dir_path, "addon.json"), "w+", encoding="utf-8") as file:
                file.write(json.dumps(data, indent=2, ensure_ascii=False))
            result = zb.singleDownload(data.get("file", ""), dir_path, True, True)
            # packages can be like ["name==1.2","name>=1.0","name"]
            for package in data.get("packages", []):
                self.installPackage(package, progress=progress)
            if result:
                report("正在解压插件文件...")
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
                    try:
                        with open(zb.joinPath(i, "addon.json"), encoding="utf-8") as file:
                            addon_data = json.load(file)
                            key = addon_data.get("id", "")
                            if key:
                                data[key] = addon_data
                    except:
                        pass
            return data
        except:
            logging.error(f"获取本地插件信息失败，报错信息：{traceback.format_exc()}！")

    def _normalize_name(self, name: str) -> str:
        return name.replace("_", "-").lower()

    def _remove_installed_from_dir(self, name: str, target_dir: str):
        """在 target_dir 下尝试删除与 name 相关的 .dist-info / .egg-info / 包目录 / 文件"""
        try:
            if not os.path.isdir(target_dir):
                return
            normalized = self._normalize_name(name)
            for entry in os.listdir(target_dir):
                low = entry.lower()
                # 如果包含包名或者以包名开头，并且是 dist-info / egg-info 或包目录
                if normalized in low:
                    path = os.path.join(target_dir, entry)
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                            logging.info(f"删除已安装包: {path}")
                        else:
                            os.remove(path)
                            logging.info(f"删除已安装文件: {path}")
                    except Exception:
                        logging.warning(f"删除已安装包时出错: {traceback.format_exc()}")
        except Exception:
            logging.warning(f"清理已安装包时出错: {traceback.format_exc()}")

    def _read_version_from_distinfo(self, distinfo_path: str) -> tuple:
        """从 .dist-info 目录读取 Name 和 Version，如果找不到返回 (None, None)"""
        metadata_files = [os.path.join(distinfo_path, "METADATA"), os.path.join(distinfo_path, "PKG-INFO")]
        name = None
        version = None
        for mf in metadata_files:
            if os.path.isfile(mf):
                try:
                    with open(mf, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Name:"):
                                name = line.split(":", 1)[1].strip()
                            elif line.startswith("Version:"):
                                version = line.split(":", 1)[1].strip()
                            if name and version:
                                return name, version
                except Exception:
                    continue
        return None, None

    def installPackage(self, package: str, target_dir: str = program.PACKAGE_PATH, progress=None):
        """
        安装包到 target_dir；支持 requirement 风格的 version specifier（例如 "pkg>=1.2" 或参数 version=">=1.2"），
        若已安装的版本满足 specifier 则跳过，否则删除 target_dir 下相关文件并重新下载 wheel 并解压到 target_dir。
        @param progress: 可选回调 progress(str)，用于向任务中心等上报安装阶段
        返回 True/False
        """

        def report(text):
            if progress:
                try:
                    progress(text)
                except Exception:
                    pass

        zb.createDir(target_dir)
        if target_dir not in sys.path:
            sys.path.insert(0, target_dir)

        spec = None

        if package and Requirement is not None:
            try:
                req = Requirement(package)
                package = req.name
                spec = req.specifier  # SpecifierSet
            except Exception:
                # 解析失败，回退为简单解析
                spec = None
                if "==" in package:
                    package, v = package.split("==", 1)
                    spec = SpecifierSet(f"=={v}") if SpecifierSet is not None else None
        elif package and Requirement is None:
            # packaging 不可用时，简单解析只支持 ==
            if "==" in package:
                package, v = package.split("==", 1)
                spec = None
                if SpecifierSet is not None:
                    spec = SpecifierSet(f"=={v}")
            else:
                # 无法解析复杂 specifier，则当作普通包名处理
                package = package
                spec = None

        # 先尝试通过 import 检查是否已安装（全环境），并通过 importlib.metadata 获取版本
        installed_version = None
        try:
            # 优先使用 importlib_metadata 获取分发包版本
            if importlib_metadata is not None:
                try:
                    installed_version = importlib_metadata.version(package)
                except Exception:
                    installed_version = None
            # 如果没有通过 importlib_metadata 获取到，则从 target_dir 的 .dist-info 中读取
            if installed_version is None and os.path.isdir(target_dir):
                for entry in os.listdir(target_dir):
                    if entry.lower().endswith(".dist-info"):
                        dist_path = os.path.join(target_dir, entry)
                        pkg_name, pkg_version = self._read_version_from_distinfo(dist_path)
                        if pkg_name and pkg_version:
                            # 规范化包名比较
                            if pkg_name.replace("_", "-").lower() == package.replace("_", "-").lower() or \
                                    package.replace("_", "-").lower() in entry.lower():
                                installed_version = pkg_version
                                break
                    # 备选：如果目录名看起来像 package-version.dist-info，则尝试解析版本
                    if entry.lower().endswith(".dist-info") and installed_version is None:
                        parts = entry.rsplit("-", 2)
                        if len(parts) >= 2 and parts[-1].endswith(".dist-info"):
                            maybe_ver = parts[-2]
                            # 简单验证 maybe_ver 是否像版本
                            if maybe_ver and any(c.isdigit() for c in maybe_ver):
                                installed_version = maybe_ver
                                break
        except Exception:
            installed_version = None

        # 检查是否满足 specifier
        if spec and installed_version:
            try:
                inst_v_raw = str(installed_version).strip()
                try:
                    v_inst = parse_version(inst_v_raw)
                    if spec.contains(v_inst, prereleases=True):
                        # 版本满足之外还要求可导入：防止平台上装了错误 wheel（如跨平台/跨解释器）
                        # 后版本号满足却被永久跳过的自锁问题
                        if self._try_import(package):
                            logging.info(f"包{package}已安装且满足版本要求{spec}！")
                            report(f"运行库 {package} 已就绪")
                            return True
                        logging.warning(f"包{package}版本{inst_v_raw}满足{spec}但导入失败，将移除并重新安装！")
                except InvalidVersion:
                    # 解析失败时回退为字符串匹配
                    if inst_v_raw in str(spec):
                        logging.info(f"包{package}已安装且满足版本要求{spec}！")
                        return True
            except Exception:
                pass
        else:
            # 如果没有 spec，且能 import，则认为已存在
            if self._try_import(package):
                logging.info(f"包{package}已存在！")
                report(f"运行库 {package} 已就绪")
                # 如果没有 spec，直接返回 True
                if not spec:
                    return True

        logging.info(f"正在安装{package}... 目标目录：{target_dir}")
        report(f"正在安装运行库 {package}...")

        # 如果安装存在但不满足版本，则尝试删除 target_dir 下的相关文件，然后重新安装
        if installed_version and spec:
            self._remove_installed_from_dir(package, target_dir)
            logging.info(f"检测到已安装包版本{installed_version}不满足{spec}，将尝试移除并重新安装！")

        # 使用 pypi_simple 找到合适的 wheel 链接
        from pypi_simple import PyPISimple
        class NewPyPISimple(PyPISimple):
            def __init__(self):
                super().__init__()

            def get_project_url(self, project: str) -> str:
                return super().get_project_url(project).replace("https://pypi.org/simple/", "https://mirrors.aliyun.com/pypi/simple/")

        with NewPyPISimple() as client:
            try:
                requests_page = client.get_project_page(package)
            except Exception:
                logging.error(f"无法获取包{package}的项目页面！")
                return False
        packages = requests_page.packages

        candidate_url = None
        best_ver = None
        # 遍历所有 wheel：先按当前平台/Python 版本过滤，再在兼容项中选取满足 specifier 的最高版本
        # 注意：循环变量不能沿用 package（外部 package 是包名字符串，后面日志与删除逻辑还要用）
        for dist in packages:
            if dist.package_type != "wheel":
                continue
            if not self._is_compatible_wheel(dist.filename):
                continue
            try:
                ver = parse_version(str(dist.version).strip())
            except Exception:
                ver = None
            if spec and ver is not None:
                try:
                    if not spec.contains(ver, prereleases=True):
                        continue
                except Exception:
                    if str(dist.version) not in str(spec):
                        continue
            if best_ver is None or (ver is not None and (best_ver is None or ver > best_ver)):
                best_ver = ver
                candidate_url = dist.url

        if not candidate_url:
            logging.error(f"未找到与当前平台和 Python 版本兼容的包{package}的 wheel（将跳过安装）！")
            return False

        result = zb.singleDownload(candidate_url, target_dir, True, True)
        if not result:
            logging.error(f"下载包{package}失败！")
            return False
        zb.extractZip(result, target_dir, True)
        logging.info(f"包{package}安装成功：{candidate_url.rsplit('/', 1)[-1]}")
        report(f"运行库 {package} 安装完成")
        return True


addonManager = AddonManager()
