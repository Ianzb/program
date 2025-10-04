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


def ensure_requirements():
    if not REQS.exists():
        print('WARN: requirements.txt 不存在，跳过依赖安装')
        return True
    print('Installing requirements...')
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(REQS)])
        return True
    except subprocess.CalledProcessError as e:
        print('安装依赖失败:', e)
        return False


def is_pyinstaller_available():
    # Check if PyInstaller module can be imported
    try:
        import importlib
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
    zip_name = ROOT / f'zbProgram_{version}.zip'
    print(f'Creating zip {zip_name} ...')
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        if BUILD_DIR.exists():
            for root, dirs, files in os.walk(BUILD_DIR):
                for f in files:
                    full = Path(root) / f
                    rel = full.relative_to(BUILD_DIR.parent)
                    zf.write(full, arcname=str(rel))
    print('Zip created:', zip_name)
    return zip_name


def run_inno_setup():
    inno = os.environ.get('INNO_SETUP_PATH', r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe')
    if not Path(inno).exists():
        print(f'INNO Setup (ISCC.exe) not found at {inno}, skipping installer build')
        return None
    print('Running Inno Setup:', inno)
    cmd = [inno, str(SETUP_ISS)]
    subprocess.check_call(cmd)
    out_exe = BUILD_DIR / 'zbProgram_setup.exe'
    if out_exe.exists():
        print('Inno Setup produced:', out_exe)
        return out_exe
    alt = BUILD_DIR / 'zbProgram' / 'zbProgram_setup.exe'
    if alt.exists():
        return alt
    print('WARN: 未找到生成的安装包，可能 ISCC 的 OutputDir 与 setup.iss 不一致')
    return None


def git_commit_and_push(version: str):
    try:
        subprocess.check_call(['git', 'add', str(PROG_PY), str(SETUP_ISS), str(INDEX_JSON)])
        subprocess.check_call(['git', 'commit', '-m', f'Bump version to {version} [ci skip]'])
        subprocess.check_call(['git', 'push', 'origin', 'HEAD:main'])
        print('Pushed version changes to main')
    except subprocess.CalledProcessError as e:
        print('Git push failed or no changes to commit:', e)


def upload_webdav(webdav_url, user, password, zip_path: Path, installer_path: Path):
    try:
        import requests
    except Exception:
        print('requests not available, skip webdav upload')
        return
    webdav_url = webdav_url.rstrip('/')
    targets = [
        (INDEX_JSON, f'{webdav_url}/Code/program/index.json'),
        (zip_path, f'{webdav_url}/Code/program/zbProgram.zip'),
    ]
    if installer_path:
        targets.append((installer_path, f'{webdav_url}/Code/program/zbProgram_setup.exe'))
    for src, dest in targets:
        try:
            print(f'Uploading {src} -> {dest}')
            with open(src, 'rb') as f:
                r = requests.put(dest, data=f, auth=(user, password), timeout=60)
            if r.status_code in (200, 201, 204):
                print('Uploaded', dest)
            else:
                print('Upload failed', dest, r.status_code, r.text)
        except Exception as e:
            print('Upload error', e)


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
    # print in a safe way; release_notes may contain non-ASCII
    print('Release notes:', release_notes)

    replace_version_in_program(version)
    replace_version_in_setup(version)
    replace_index_json(version)

    if not args.skip_requirements:
        req_ok = ensure_requirements()
    else:
        req_ok = True

    installer_path = None
    zip_path = None
    # Decide whether to run pyinstaller: skip if user requested or if requirements failed or PyInstaller missing
    should_run_pyinstaller = not args.skip_pyinstaller and req_ok
    if should_run_pyinstaller:
        if not is_pyinstaller_available():
            print('PyInstaller 未安装或不可用，跳过打包')
            should_run_pyinstaller = False

    if should_run_pyinstaller:
        try:
            run_pyinstaller()
        except Exception as e:
            print('PyInstaller 失败:', e)
            # don't abort; continue to write output
            should_run_pyinstaller = False
        try:
            zip_path = make_zip(version)
        except Exception as e:
            print('打包 zip 失败:', e)
        if not args.no_inno and should_run_pyinstaller:
            try:
                installer_path = run_inno_setup()
            except Exception as e:
                print('Inno Setup 失败:', e)
    else:
        print('已跳过 PyInstaller 步骤')

    # 尝试提交版本变更
    try:
        git_commit_and_push(version)
    except Exception as e:
        print('git 提交或推送出错:', e)

    out = {
        'version': version,
        'release_notes': release_notes,
        'zip': str((ROOT / f'zbProgram_{version}.zip').resolve())
    }
    if installer_path:
        out['installer'] = str(Path(installer_path).resolve())

    out_path = ROOT / 'script' / 'release_output.json'
    try:
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
        print('\n=== BUILD OUTPUT ===')
        print(json.dumps(out, ensure_ascii=False, indent=2))
    except Exception as e:
        print('写出 release_output.json 失败:', e)

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
