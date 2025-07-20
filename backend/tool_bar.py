# -*- coding: utf-8 -*-
import json
import os
import win32api
import win32con
import win32gui
import win32clipboard
import threading
from functools import partial
import subprocess
import plyer
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def app_data_dir():
    """应用数据目录"""
    path = os.path.join(os.getenv('APPDATA'), 'general-assistant-2')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def config_path(filename):
    """配置文件路径"""
    return os.path.join(app_data_dir(), filename)

def init_config():
    """初始化配置文件"""
    tool_path = config_path('toolbar.json')
    models_path = config_path('models.json')
    input_path = config_path('input.json')
    settings_path = config_path('settings.json')  # 新增: 添加 settings.json 路径

    if not os.path.exists(tool_path):
        with open(tool_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

    if not os.path.exists(models_path):
        with open(models_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

    if not os.path.exists(input_path):
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

    if not os.path.exists(settings_path):  # 新增: 检查并创建 settings.json
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump({"language": "zh-CN"}, f)  # 默认语言设置为中文

# 新增：加载翻译文件的函数
def load_translations(lang):
    """加载翻译文件"""
    try:
        # 尝试使用 __file__（标准环境）
        base_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # 嵌入式环境回退方案
        base_dir = sys.path[0]
    
    translations_path = os.path.join(
        base_dir, '..', '..', 'frontend', 'locales', f'{lang}.json'
    )
    
    # 规范化路径处理跨平台问题
    translations_path = os.path.normpath(translations_path)
    
    if os.path.exists(translations_path):
        with open(translations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    logging.error(f"Translation file not found: {translations_path}")
    return {}

# 新增：获取当前语言设置的函数
def get_current_language():
    settings_path = os.path.join(os.getenv('APPDATA'), 'general-assistant-2', 'settings.json')
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        # 修复：处理 settings 作为列表的情况，并添加默认值处理
        if isinstance(settings, list) and len(settings) > 0:
            return settings[0].get('language', 'zh-CN')
        return 'zh-CN'  # 如果文件格式不正确则返回默认值
    return 'zh-CN'

current_language = get_current_language()
translations = load_translations(current_language)
def get_tool_names():
    """获取工具列表"""
    try:
        with open(config_path('toolbar.json'), 'r', encoding='utf-8') as f:
            tools = json.load(f)
        return [tool.get('Toolname', '未命名工具') for tool in tools], tools
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"配置加载错误: {e}")
        plyer.notification.notify(
            title=translations.get("error", "Error"),
            message=translations.get("error_config_load", "配置加载错误: {e}"),
            app_name=translations.get('GeneralAssistant', 'General Assistant 2'),
            )
        return [], []


def create_temp_window():
    """创建临时窗口"""
    return win32gui.CreateWindowEx(
        0,
        "STATIC",
        "",
        win32con.WS_POPUP,
        0, 0, 0, 0,
        0, 0,
        win32api.GetModuleHandle(None),
        None
    )

def create_native_menu(tool_names, translations):
    """创建原生Windows菜单并返回句柄"""
    hmenu = win32gui.CreatePopupMenu()
    for idx, name in enumerate(tool_names):
        translated_name = translations.get(name, name)  # 使用翻译后的名称
        win32gui.AppendMenu(hmenu, win32con.MF_STRING, idx+1, translated_name)
    win32gui.AppendMenu(hmenu, win32con.MF_SEPARATOR, 0, "")
    win32gui.AppendMenu(hmenu, win32con.MF_STRING, len(tool_names)+1, translations.get("cancel", "取消"))  # 确保“取消”使用翻译后的值
    return hmenu

def show_menu(hwnd, hmenu):
    """显示菜单并处理选择"""
    x, y = win32api.GetCursorPos()
    selected = win32gui.TrackPopupMenu(
        hmenu,
        win32con.TPM_RETURNCMD | win32con.TPM_NONOTIFY,
        x,
        y,
        0,  # 必须保留此参数
        hwnd,
        None
    )
    win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)  # 发送空消息以结束消息循环
    return selected

def save_selected_text(selected_tool, all_tools):
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            clipboard_data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
            clipboard_data = win32clipboard.GetClipboardData(win32con.CF_TEXT)
            if isinstance(clipboard_data, bytes):
                clipboard_data = clipboard_data.decode('utf-8')
        else:
            clipboard_data = ""
        
        model_name = selected_tool['Model']
        prompt = selected_tool['Prompt']
        plugin = selected_tool['Plugin']
        replace = selected_tool['Replace']

        with open(config_path('models.json'), 'r', encoding='utf-8') as f:
            models = json.load(f)
        
        model_info = next((model for model in models if model['Model'] == model_name), {})
        api_url = model_info.get('API_URL', '')
        api_key = model_info.get('API_Key', '')

        input_data = [{
            "Model": model_name,
            "Prompt": prompt,
            "Plugin": plugin,
            "Replace": replace,
            "API_URL": api_url,
            "API_Key": api_key,
            "Clipboard": clipboard_data
        }]
        
        with open(config_path('input.json'), 'w', encoding='utf-8') as f:
            json.dump(input_data, f, ensure_ascii=False, indent=4)

        print("plugin called")
        run_plugin(plugin)

    except Exception as e:
        pass  # 忽略所有异常，包括 pywintypes.error
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass  # 忽略关闭剪贴板时的异常

def run_plugin(plugin):
    """运行指定的插件脚本"""
    try:
        base_dir = sys.path[0]
        script_path = os.path.join(base_dir, '..', '..', 'plugin', plugin)
        python_embed_path = os.path.join(base_dir, '..', 'python.exe')
        
        logging.debug(f"Running {plugin} with: {python_embed_path} {script_path}")
        subprocess.run([python_embed_path, script_path], check=True)
    except FileNotFoundError as e:
        logging.error(f"Plugin {plugin} not found: {str(e)}")
        plyer.notification.notify(
            title=translations.get("error", "Error"),
            message=translations.get("error_plugin_notfound", "插件{plugin} 未找到"),
            app_name=translations.get('GeneralAssistant', 'General Assistant 2'),
            )
    except Exception as e:
        logging.error(f"Error running plugin {plugin}: {str(e)}")
        plyer.notification.notify(
            title=translations.get("error", "Error"),
            message=translations.get("error_plugin_run", "插件运行错误: {e}"),
            app_name=translations.get('GeneralAssistant', 'General Assistant 2'),
            )

def menu_loop():
    """主菜单循环"""
    global menu_thread_id
    tool_names, all_tools = get_tool_names()
    if not tool_names:
        logging.debug("未找到可用工具")
        return

    # 加载语言设置
    settings_path = config_path('settings.json')
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        lang = settings[0].get('language', 'zh-CN') if isinstance(settings, list) else settings.get('language', 'zh-CN')
        logging.debug(f"加载语言设置: {lang}")
    else:
        lang = 'zh-CN'
        logging.debug("未找到 settings.json，使用默认语言: zh-CN")

    # 加载翻译文件
    translations = load_translations(lang)

    hwnd = create_temp_window()
    hmenu = create_native_menu(tool_names, translations)
    try:
        selected = show_menu(hwnd, hmenu)
        
        if 0 < selected <= len(tool_names):
            selected_tool = all_tools[selected-1]
            logging.debug(f"已选择工具: {selected_tool['Toolname']}")
            save_selected_text(selected_tool, all_tools)
        elif selected == len(tool_names) + 1:
            logging.debug("取消操作")
    finally:
        win32gui.DestroyMenu(hmenu)
        win32gui.DestroyWindow(hwnd)
        menu_thread_id = None  # 清除线程ID

def create_tool_bar_menu():
    """创建工具条菜单"""
    global menu_thread_id
    menu_thread = threading.Thread(target=menu_loop)
    menu_thread.start()
    menu_thread_id = menu_thread.ident

if __name__ == "__main__":
    init_config()
    create_tool_bar_menu()