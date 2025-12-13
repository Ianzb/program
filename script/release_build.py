from __future__ import annotations
import argparse
import os
import re
import sys
import json
import shutil
import subprocess
from pathlib import Path
import zipfile

config = {
    "log_index": "exe版",
}

ROOT = Path(__file__).resolve().parents[1]
PROG_PY = ROOT / "program" / "source" / "program" / "program.py"
SETUP_ISS = ROOT / "script" / "setup.iss"
INDEX_JSON = ROOT / "index.json"
INDEX_HTML = ROOT / "index.html"
REQS = ROOT / "requirements.txt"
BUILD_DIR = ROOT / "build"


def replace_version_in_program(version: str, version_code: int):
    text = PROG_PY.read_text(encoding="utf-8")
    pattern = re.compile(r"(\bVERSION\s*=\s*)([\"'])(.*?)(\2)", flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + m.group(2) + version + m.group(2), text, count=1)
    PROG_PY.write_text(new_text, encoding="utf-8")

    pattern = re.compile(r"(\bVERSION_CODE\s*=\s*)(\d+)", flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + str(version_code), text, count=1)
    PROG_PY.write_text(new_text, encoding="utf-8")
    print("已修改program.py版本号！")


def replace_version_in_setup(version: str):
    text = SETUP_ISS.read_text(encoding="utf-8")
    pattern = re.compile(r'(#define\s+MyAppVersion\s+")([^"]*)(\")', flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + version + m.group(3), text, count=1)
    SETUP_ISS.write_text(new_text, encoding="utf-8")
    print("已修改setup.iss版本号！")


def replace_index_json(version: str, version_code: int):
    data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    data["version"] = version
    data["version_code"] = version_code
    INDEX_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    print("已修改index.json版本号！")


def extract_release_notes():
    html = INDEX_HTML.read_text(encoding="utf-8")
    if config.get("log_index"):
        m = re.search(rf'<div\s+class="zb">\s*<h5>\s*{config.get("log_index")}\s*</h5>(.*?)</div>', html, flags=re.S)
    else:
        m = re.search(r'<div\s+class="zb">(.*?)</div>', html, flags=re.S)
    inner = m.group(1)
    parts = re.split(r"<br\s*/?>|\r|\n", inner)
    cleaned = [re.sub(r"<.*?>", "", p).strip() for p in parts]
    cleaned = [c for c in cleaned if c]
    last = cleaned[-1]
    last = re.sub(r"^\s*\d{4}-\d{2}-\d{2}：\s*[^：]+：\s*", "", last)
    last = re.sub(r"^\s*\d+(?:\.\d+){0,}：\s*", "", last).strip()
    print("已读取更新日志！")
    return last


def run_pyinstaller():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    add_data = os.pathsep.join([str(ROOT / "program" / "source" / "img"), "img"])
    cmd = [
        sys.executable, "-m", "PyInstaller", "-D", "-w", str(ROOT / "program" / "main.pyw"),
        "-i", str(ROOT / "program" / "source" / "img" / "program.ico"),
        "-n", "zbProgram", "--distpath", str(BUILD_DIR), "--workpath", str(BUILD_DIR / "build"),
        "--clean", "--contents-directory", "source", "--add-data", add_data, "-y"
    ]
    print("CMD:", " ".join(cmd))
    subprocess.check_call(cmd)
    print("打包完成")


def make_zip(version: str):
    zip_name = ROOT / f"zbProgram_{version}"
    print(f"正在压缩{zip_name}.zip...")
    zip_path = shutil.make_archive(str(zip_name), "zip", root_dir=BUILD_DIR / "zbProgram")
    print(f"压缩{zip_name}.zip完成！")
    return zip_path


def get_current_version_code():
    data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    return data.get("version_code", 0)


def get_current_version():
    data = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    return data.get("version", "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", required=True, help="版本号")
    parser.add_argument("--skip-pyinstaller", action="store_true")
    args = parser.parse_args()
    version = args.version

    release_notes = extract_release_notes()
    print("Release notes:", release_notes)

    # 获取当前版本和版本代码
    current_version = get_current_version()
    current_version_code = get_current_version_code()

    # 如果版本号发生变化，则增加版本代码
    if current_version != version:
        new_version_code = current_version_code + 1
        print(f"版本号从 {current_version} 变为 {version}, 增加版本代码到 {new_version_code}")
    else:
        new_version_code = current_version_code
        print(f"版本号未变化，保持版本代码为 {new_version_code}")

    replace_index_json(version, new_version_code)
    replace_version_in_program(version, new_version_code)
    replace_version_in_setup(version)

    run_pyinstaller()
    zip_path = make_zip(version)

    out = {
        "version": version,
        "version_code": new_version_code,
        "release_notes": release_notes,
        "zip": zip_path
    }

    out_path = ROOT / "script" / "release_output.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=4), encoding="utf-8")
