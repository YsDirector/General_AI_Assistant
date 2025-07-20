import os
import json
import webview
from multiprocessing import Process
import plyer
import logging
import sys
import platform
import time
import urllib.request  # 新增导入用于URL检查

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 全局变量
settings_window_process = None
settings_window_active = False

# 加载翻译文件的函数
def load_translations(lang):
    current_dir = os.path.dirname(__file__)
    translations_path = os.path.join(current_dir, '..', 'frontend', 'locales', f'{lang}.json')
    
    if os.path.exists(translations_path):
        with open(translations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 获取当前语言设置
def get_current_language():
    settings_path = os.path.join(os.getenv('APPDATA'), 'general-assistant-2', 'settings.json')
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        if isinstance(settings, list) and len(settings) > 0:
            return settings[0].get('language', 'zh-CN')
        return 'zh-CN'
    return 'zh-CN'

def run_settings_webview():
    global settings_window
    # 添加启动前的等待确保服务器就绪
    time.sleep(1)  # 等待服务器启动
    
    current_dir = os.path.dirname(__file__)
    icon_path = os.path.join(current_dir, '..', 'frontend', 'favicon.ico')

    general_path = "http://localhost:54900/general.html"
    print(f"Opening general settings window: {general_path}")
    
    # 新增：检查URL是否可达
    try:
        response = urllib.request.urlopen(general_path)
        if response.status != 200:
            logging.error(f"URL {general_path} returned status: {response.status}")
    except Exception as e:
        logging.error(f"Failed to access URL {general_path}: {str(e)}")

    # 添加调试信息
    logging.debug("Creating webview window")
    logging.debug(f"Icon path exists: {os.path.exists(icon_path) if icon_path else 'No icon path'}")
    
    width, height = 800, 600

    settings_window = webview.create_window(
        'Settings',
        url=general_path,
        width=width,
        height=height
    )
    settings_window.events.closed += on_settings_window_closed

    start_args = {'debug': False}  # 强制启用调试模式
    if os.path.exists(icon_path):  # 只有图标存在时才设置
        start_args['icon'] = icon_path
    else:
        logging.warning(f"Icon file not found: {icon_path}")

    try:
        logging.debug("Starting webview with args: %s", start_args)
        webview.start(**start_args)
    except Exception as e:
        logging.error("Failed to start webview: %s", str(e), exc_info=True)

def on_settings_window_closed():
    global settings_window_active
    settings_window_active = False
    print("Settings window closed", flush=True)
    return

def close_settings_window():
    global settings_window_process, settings_window_active
    if settings_window_process and settings_window_process.is_alive():
        settings_window_process.terminate()
        settings_window_active = False

def start_settings_webview_process():
    global settings_window_process, settings_window_active
    if settings_window_active:
        close_settings_window()
    settings_window_process = Process(target=run_settings_webview)
    settings_window_process.start()
    settings_window_active = True
    return

if __name__ == '__main__':
    # 加载翻译
    current_language = get_current_language()
    translations = load_translations(current_language)
    
    # 启动webview
    start_settings_webview_process()