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
- 尝试调用 Inno Setup 编译 script/setup.iss 生成安装包
- 提示产物路径以便 workflow 上传到 Release
- 将版本号修改以 GitHub Actions 身份提交到 main 分支（workflow 已使用 actions/checkout 持久凭据）

注意：
- 若希望 Inno Setup 生效，请在 runner 中确保 ISCC.exe 可用或配置环境变量 INNO_SETUP_PATH 指向 ISCC.exe
"""

import argparse
import os
import re
import sys
import json
import shutil
import subprocess
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROG_PY = ROOT / 'program' / 'source' / 'program' / 'program.py'
SETUP_ISS = ROOT / 'script' / 'setup.iss'
INDEX_JSON = ROOT / 'index.json'
INDEX_HTML = ROOT / 'index.html'
REQS = ROOT / 'requirements.txt'
BUILD_DIR = ROOT / 'build'


def replace_version_in_program(version: str):
    text = PROG_PY.read_text(encoding='utf-8')
    # Match only the VERSION assignment (avoid CORE_VERSION). Preserve original quote char.
    pattern = re.compile(r'(\bVERSION\s*=\s*)(["\'])(.*?)(\2)', flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + m.group(2) + version + m.group(2), text, count=1)
    if n == 0:
        print('WARN: 未在 program.py 中找到 VERSION 字段，跳过替换')
    else:
        PROG_PY.write_text(new_text, encoding='utf-8')
        print(f'Updated {PROG_PY} VERSION -> {version}')


def replace_version_in_setup(version: str):
    text = SETUP_ISS.read_text(encoding='utf-8')
    # First try match with quotes: (#define MyAppVersion "...")
    pattern = re.compile(r'(#define\s+MyAppVersion\s+")([^"]*)(\")', flags=re.M)
    new_text, n = pattern.subn(lambda m: m.group(1) + version + m.group(3), text, count=1)
    if n == 0:
        # Fallback: match without surrounding quotes and replace with quoted version
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


def extract_release_notes():
    # 解析 index.html 中 exe 版块最后一行文本（去掉日期/版本号）
    html = INDEX_HTML.read_text(encoding='utf-8')
    # 找到含有 <h5>exe版</h5> 的 div 块
    m = re.search(r'<div\s+class="zb">\s*<h5>\s*exe版\s*</h5>(.*?)</div>', html, flags=re.S)
    if not m:
        print('WARN: 未找到 exe版 区块，Release 描述将为空')
        return ''
    inner = m.group(1)
    # 去掉标签，按 <br> 或换行切分，取最后一个非空行
    parts = re.split(r'<br\s*/?>|\r|\n', inner)
    cleaned = [re.sub(r'<.*?>', '', p).strip() for p in parts]
    cleaned = [c for c in cleaned if c]
    if not cleaned:
        return ''
    last = cleaned[-1]
    # 去掉开头的日期和版本号，例如：2024-05-02：4.0.0：...
    last = re.sub(r'^\s*\d{4}-\d{2}-\d{2}：\s*[^：]+：\s*', '', last)
    # 另外去掉以版本号开头的模式：例如 5.4.0：文本
    last = re.sub(r'^\s*\d+(?:\.\d+){0,}：\s*', '', last)
    return last.strip()


def ensure_requirements():
    if not REQS.exists():
        print('WARN: requirements.txt 不存在，跳过依赖安装')
        return
    print('Installing requirements...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(REQS)])


def run_pyinstaller():
    # 构建参数参考 script/exe.bat
    print('Running PyInstaller...')
    # 清理旧的 build 目录
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
    zip_name = ROOT / f'zbProgram_{version}.zip'
    print(f'Creating zip {zip_name} ...')
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 将 build 目录下的所有文件打包到 zip
        if BUILD_DIR.exists():
            for root, dirs, files in os.walk(BUILD_DIR):
                for f in files:
                    full = Path(root) / f
                    rel = full.relative_to(BUILD_DIR.parent)
                    zf.write(full, arcname=str(rel))
    print('Zip created:', zip_name)
    return zip_name


def run_inno_setup():
    # 通过环境变量 INNO_SETUP_PATH 指定 ISCC.exe 的路径
    inno = os.environ.get('INNO_SETUP_PATH', r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe')
    if not Path(inno).exists():
        print(f'INNO Setup (ISCC.exe) not found at {inno}, skipping installer build')
        return None
    print('Running Inno Setup:', inno)
    # ISCC support relative path
    cmd = [inno, str(SETUP_ISS)]
    subprocess.check_call(cmd)
    # 输出默认在 setup.iss 中设置 OutputDir=..\build\zbProgram and OutputBaseFilename=zbProgram_setup
    out_exe = BUILD_DIR / 'zbProgram_setup.exe'
    if out_exe.exists():
        print('Inno Setup produced:', out_exe)
        return out_exe
    # sometimes placed in build\zbProgram\zbProgram_setup.exe
    alt = BUILD_DIR / 'zbProgram' / 'zbProgram_setup.exe'
    if alt.exists():
        return alt
    print('WARN: 未找到生成的安装包，可能 ISCC 的 OutputDir 与 setup.iss 不一致')
    return None


def git_commit_and_push(version: str):
    # 假设 actions/checkout 已经配置为允许推送
    try:
        subprocess.check_call(['git', 'add', str(PROG_PY), str(SETUP_ISS), str(INDEX_JSON)])
        subprocess.check_call(['git', 'commit', '-m', f'Bump version to {version} [ci skip]'])
        subprocess.check_call(['git', 'push', 'origin', 'HEAD:main'])
        print('Pushed version changes to main')
    except subprocess.CalledProcessError as e:
        print('Git push failed or no changes to commit:', e)


def upload_webdav(webdav_url, user, password, zip_path: Path, installer_path: Path):
    # 使用简单的 PUT 上传覆盖目标文件
    import requests
    # 确保 url 无结尾斜杠
    webdav_url = webdav_url.rstrip('/')
    targets = [
        (INDEX_JSON, f'{webdav_url}/Code/program/index.json'),
        (zip_path, f'{webdav_url}/Code/program/zbProgram.zip'),
    ]
    if installer_path:
        targets.append((installer_path, f'{webdav_url}/Code/program/zbProgram_setup.exe'))
    for src, dest in targets:
        print(f'Uploading {src} -> {dest}')
        with open(src, 'rb') as f:
            r = requests.put(dest, data=f, auth=(user, password))
            if r.status_code in (200, 201, 204):
                print('Uploaded', dest)
            else:
                print('Upload failed', dest, r.status_code, r.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', required=True, help='版本号，例如 5.4.1')
    parser.add_argument('--skip-requirements', action='store_true')
    parser.add_argument('--skip-pyinstaller', action='store_true')
    parser.add_argument('--no-inno', action='store_true')
    parser.add_argument('--upload-webdav', action='store_true', help='上传生成的 zip 和安装包到 WebDAV，需在环境变量中设置 WEB_DAV_URL/WEB_DAV_USER/WEB_DAV_PASSWORD')
    args = parser.parse_args()
    version = args.version

    release_notes = extract_release_notes()
    print('Release notes:', release_notes)

    replace_version_in_program(version)
    replace_version_in_setup(version)
    replace_index_json(version)

    if not args.skip_requirements:
        try:
            ensure_requirements()
        except Exception as e:
            print('安装依赖失败:', e)

    installer_path = None
    if not args.skip_pyinstaller:
        try:
            run_pyinstaller()
        except Exception as e:
            print('PyInstaller 失败:', e)
            sys.exit(2)
        zip_path = make_zip(version)
        if not args.no_inno:
            try:
                installer_path = run_inno_setup()
            except Exception as e:
                print('Inno Setup 失败:', e)

    # 尝试提交版本变更
    try:
        git_commit_and_push(version)
    except Exception as e:
        print('git 提交或推送出错:', e)

    # 输出构建产物路径，供 workflow 使用
    out = {
        'version': version,
        'release_notes': release_notes,
        'zip': str((ROOT / f'zbProgram_{version}.zip').resolve())
    }
    if installer_path:
        out['installer'] = str(Path(installer_path).resolve())

    # Write machine-readable output for CI usage
    out_path = ROOT / 'script' / 'release_output.json'
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n=== BUILD OUTPUT ===')
    print(json.dumps(out, ensure_ascii=False, indent=2))

    # Optional: upload to webdav when environment variables present or flag provided
    if getattr(args, 'upload_webdav', False):
        webdav_url = os.environ.get('WEB_DAV_URL')
        webdav_user = os.environ.get('WEB_DAV_USER')
        webdav_password = os.environ.get('WEB_DAV_PASSWORD')
        if webdav_url and webdav_user and webdav_password:
            try:
                upload_webdav(webdav_url, webdav_user, webdav_password, Path(out['zip']), Path(out.get('installer')) if out.get('installer') else None)
            except Exception as e:
                print('WebDAV 上传失败:', e)
        else:
            print('WEB_DAV_URL/WEB_DAV_USER/WEB_DAV_PASSWORD 未全部设置，跳过 WebDAV 上传')

    print('Done')
