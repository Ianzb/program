#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
release_build.py

用法:
  python script\release_build.py -v <version>

功能：
- 更新 program/source/program/program.py 中的 VERSION
- 更新 script/setup.iss 中的 MyAppVersion
- 更新 index.json 中的 version
- 解析 index.html 中 exe 版块获取最后一行作为 Release 描述（去掉日期/版本）
- 安装 requirements.txt 中的依赖（用于打包）
- 使用 PyInstaller 构建 exe（行为参考 script/exe.bat）
- 将 build 目录打包为 zbProgram_<version>.zip
- 尝试调用 Inno Setup 编译 script/setup.iss 生成安装包（可由 workflow 的 Inno action 代替）
- 提示产物路径以便 workflow 上传到 Release
- 将版本号修改以 GitHub Actions 身份提交到 main 分支（workflow 已使用 actions/checkout 持久凭据）

注意：
- 若希望 Inno Setup 生效，请在 runner 中确保 ISCC.exe 可用或配置环境变量 INNO_SETUP_PATH 指向 ISCC.exe
"""

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

# Ensure stdout/stderr use UTF-8 to avoid UnicodeEncodeError on Windows consoles
try:
    if hasattr(sys, 'stdout') and sys.stdout and (sys.stdout.encoding or '').lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            import io

            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
PROG_PY = ROOT / 'program' / 'source' / 'program' / 'program.py'
SETUP_ISS = ROOT / 'script' / 'setup.iss'
INDEX_JSON = ROOT / 'index.json'
INDEX_HTML = ROOT / 'index.html'
REQS = ROOT / 'requirements.txt'
BUILD_DIR = ROOT / 'build'


def replace_version_in_program(version: str):
    if not PROG_PY.exists():
        print(f'WARN: {PROG_PY} not found, skip')
        return
    text = PROG_PY.read_text(encoding='utf-8')
    # Match only the VERSION assignment (avoid CORE_VERSION). Preserve original quote char.
    pattern = re.compile(r"(\bVERSION\s*=\s*)([\"'])(.*?)(\2)", flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + m.group(2) + version + m.group(2), text, count=1)
    if n == 0:
        print('WARN: 未在 program.py 中找到 VERSION 字段，跳过替换')
    else:
        PROG_PY.write_text(new_text, encoding='utf-8')
        print(f'Updated {PROG_PY} VERSION -> {version}')


def replace_version_code_in_program(version_code: int):
    if not PROG_PY.exists():
        print(f'WARN: {PROG_PY} not found, skip')
        return
    text = PROG_PY.read_text(encoding='utf-8')
    # Match VERSION_CODE assignment
    pattern = re.compile(r"(\bVERSION_CODE\s*=\s*)(\d+)", flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + str(version_code), text, count=1)
    if n == 0:
        print('WARN: 未在 program.py 中找到 VERSION_CODE 字段，跳过替换')
    else:
        PROG_PY.write_text(new_text, encoding='utf-8')
        print(f'Updated {PROG_PY} VERSION_CODE -> {version_code}')


def replace_version_in_setup(version: str):
    if not SETUP_ISS.exists():
        print(f'WARN: {SETUP_ISS} not found, skip')
        return
    text = SETUP_ISS.read_text(encoding='utf-8')
    # Try match with quotes
    pattern = re.compile(r'(#define\s+MyAppVersion\s+")([^"]*)(\")', flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + version + m.group(3), text, count=1)
    if n == 0:
        # Fallback: match without surrounding quotes
        pattern2 = re.compile(r'(#define\s+MyAppVersion\s+)["\']?([^\n\r]*)', flags=re.M)
        new_text, n = pattern2.subn(lambda m: m.group(1) + '"' + version + '"', text, count=1)
    if n == 0:
        print('WARN: 未在 setup.iss 中找到 MyAppVersion，跳过替换')
    else:
        SETUP_ISS.write_text(new_text, encoding='utf-8')
        print(f'Updated {SETUP_ISS} MyAppVersion -> {version}')


def replace_index_json(version: str):
    data = {}
    if INDEX_JSON.exists():
        try:
            data = json.loads(INDEX_JSON.read_text(encoding='utf-8'))
        except Exception:
            print('WARN: 解析 index.json 失败，尝试覆盖写入')
    data['version'] = version
    INDEX_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Updated {INDEX_JSON} version -> {version}')


def replace_version_code_in_index(version_code: int):
    data = {}
    if INDEX_JSON.exists():
        try:
            data = json.loads(INDEX_JSON.read_text(encoding='utf-8'))
        except Exception:
            print('WARN: 解析 index.json 失败，尝试覆盖写入')
    data['version_code'] = version_code
    INDEX_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Updated {INDEX_JSON} version_code -> {version_code}')


def extract_release_notes():
    if not INDEX_HTML.exists():
        return ''
    html = INDEX_HTML.read_text(encoding='utf-8')
    m = re.search(r'<div\s+class="zb">\s*<h5>\s*exe版\s*</h5>(.*?)</div>', html, flags=re.S)
    if not m:
        return ''
    inner = m.group(1)
    parts = re.split(r'<br\s*/?>|\r|\n', inner)
    cleaned = [re.sub(r'<.*?>', '', p).strip() for p in parts]
    cleaned = [c for c in cleaned if c]
    if not cleaned:
        return ''
    last = cleaned[-1]
    last = re.sub(r'^\s*\d{4}-\d{2}-\d{2}：\s*[^：]+：\s*', '', last)
    last = re.sub(r'^\s*\d+(?:\.\d+){0,}：\s*', '', last)
    return last.strip()


def is_pyinstaller_available():
    # Check if PyInstaller module can be imported
    try:
        import importlib.util
        if importlib.util.find_spec('PyInstaller') is not None:
            return True
    except Exception:
        pass
    # Fallback: try 'pyinstaller' command
    try:
        subprocess.check_call([sys.executable, '-m', 'PyInstaller', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def run_pyinstaller():
    print('Running PyInstaller...')
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    add_data = os.pathsep.join([str(ROOT / 'program' / 'source' / 'img'), 'img'])
    cmd = [
        sys.executable, '-m', 'PyInstaller', '-D', '-w', str(ROOT / 'program' / 'main.pyw'),
        '-i', str(ROOT / 'program' / 'source' / 'img' / 'program.ico'),
        '-n', 'zbProgram', '--distpath', str(BUILD_DIR), '--workpath', str(BUILD_DIR / 'build'),
        '--clean', '--contents-directory', 'source', '--add-data', add_data, '-y'
    ]
    print('CMD:', ' '.join(cmd))
    subprocess.check_call(cmd)
    print('PyInstaller finished')


def make_zip(version: str):
    zip_name = ROOT / f'zbProgram_{version}'
    print(f'Creating zip {zip_name}.zip ...')
    # shutil.make_archive 的第一个参数是输出文件路径（不带扩展名）
    # 第二个参数是格式，这里用 'zip'
    # 第三个参数是要压缩的目录
    zip_path = shutil.make_archive(str(zip_name), 'zip', root_dir=BUILD_DIR / "zbProgram")
    print('Zip created:', zip_path)
    return zip_path


def get_current_version_code():
    """获取当前的版本代码"""
    if INDEX_JSON.exists():
        try:
            data = json.loads(INDEX_JSON.read_text(encoding='utf-8'))
            return data.get('version_code', 0)
        except Exception:
            pass
    return 0


def get_current_version():
    """获取当前的版本号"""
    if INDEX_JSON.exists():
        try:
            data = json.loads(INDEX_JSON.read_text(encoding='utf-8'))
            return data.get('version', '')
        except Exception:
            pass
    return ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', required=True, help='版本号，例如 5.4.1')
    parser.add_argument('--skip-pyinstaller', action='store_true')
    args = parser.parse_args()
    version = args.version

    release_notes = extract_release_notes()
    # print in a safe way; release_notes may contain non-ASCII
    print('Release notes:', release_notes)

    # 获取当前版本和版本代码
    current_version = get_current_version()
    current_version_code = get_current_version_code()

    # 如果版本号发生变化，则增加版本代码
    if current_version != version:
        new_version_code = current_version_code + 1
        print(f'版本号从 {current_version} 变为 {version}, 增加版本代码到 {new_version_code}')
    else:
        new_version_code = current_version_code
        print(f'版本号未变化，保持版本代码为 {new_version_code}')

    replace_version_in_program(version)
    replace_version_code_in_program(new_version_code)
    replace_version_in_setup(version)
    replace_index_json(version)
    replace_version_code_in_index(new_version_code)

    installer_path = None
    zip_path = None

    try:
        run_pyinstaller()
    except Exception as e:
        print('PyInstaller 失败:', e)
        # don't abort; continue to write output
    try:
        zip_path = make_zip(version)
    except Exception as e:
        print('打包 zip 失败:', e)

    out = {
        'version': version,
        'version_code': new_version_code,
        'release_notes': release_notes,
        'zip': ''
    }
    if zip_path:
        zipp = Path(zip_path)
        if zipp.exists():
            out['zip'] = str(zipp.resolve())
    if installer_path:
        instp = Path(installer_path)
        if instp.exists():
            out['installer'] = str(instp.resolve())

    out_path = ROOT / 'script' / 'release_output.json'
    try:
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
        print('\n=== BUILD OUTPUT ===')
        print(json.dumps(out, ensure_ascii=False, indent=2))
    except Exception as e:
        print('写出 release_output.json 失败:', e)

    print('Done')
