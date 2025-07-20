import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

import sys
import os
import json
from PIL import Image
from pystray import Icon, Menu, MenuItem
from threading import Thread, Timer
from pynput import keyboard
import pyperclip
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import plyer
import subprocess  # 新增导入
import webbrowser  # 新增导入：用于打开帮助文档

# 全局变量初始化

# 新增：加载翻译文件的函数
def load_translations(lang):
    translations_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'locales', f'{lang}.json')
    
    if os.path.exists(translations_path):
        with open(translations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
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

# 新增：打开帮助文档的函数
def open_help():
    lang = get_current_language()
    if lang == 'zh-CN':
        webbrowser.open('http://localhost:54900/help_zh-CN.html')
    else:
        webbrowser.open('http://localhost:54900/help_en-US.html')

# 修改：创建托盘菜单时使用翻译内容
def create_tray_menu():
    lang = get_current_language()
    translations = load_translations(lang)
    
    return Menu(
        MenuItem(translations.get('showToolbar','显示工具栏'),show_tool_bar),
        Menu.SEPARATOR,
        # 修改：使用PowerShell运行Settings.py
        MenuItem(translations.get('settings', '设置'), run_settings_with_powershell),
        # 修改：点击帮助时打开对应语言的帮助文档
        MenuItem(translations.get('help', '帮助'), lambda icon, item: open_help()),  # 修改这一行
        Menu.SEPARATOR,
        MenuItem(translations.get('restart', '重启应用'), restart_main),  
        MenuItem(translations.get('exit', '退出'), lambda icon, item: icon.stop())
    )

def show_tool_bar():
    try:    
        from tool_bar import create_tool_bar_menu
        create_tool_bar_menu()
    except:
        script_path = os.path.join(os.path.dirname(__file__), 'tool_bar.py')
        python_embed_path = os.path.join(os.path.dirname(__file__), '..', 'python_embed', 'python.exe')
        subprocess.run([python_embed_path, script_path], check=True)

# 新增：重启 main.py 的函数
def restart_main():
    import sys
    import os
    import time
    print("Restarting main.py...")
    plyer.notification.notify(
        title=translations.get('GeneralAssistant', 'General Assistant 2'),
        message=translations.get('restarting', 'restarting'),
    )
    # 修复：确保原应用完全退出
    icon.stop()  # 停止托盘图标主循环
    time.sleep(0.5)  # 短暂延迟确保资源释放
    
    # 修复：使用 subprocess 正确处理带空格的路径
    subprocess.Popen([sys.executable] + sys.argv, shell=True)
    sys.exit(0)  # 确保当前进程退出

def run_settings_with_powershell():
    script_path = os.path.join(os.path.dirname(__file__), 'Settings.py')
    python_embed_path = os.path.join(os.path.dirname(__file__), '..', 'python_embed', 'python.exe')
    
    # 添加调试日志
    logging.debug(f"Running Settings.py with: {python_embed_path} {script_path}")
    
    # 直接执行
    subprocess.Popen([python_embed_path, script_path])

def ensure_config_files_exist():
    app_data_dir = os.path.join(os.getenv('APPDATA'), 'general-assistant-2')
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)

    toolbar_path = os.path.join(app_data_dir, 'toolbar.json')
    models_path = os.path.join(app_data_dir, 'models.json')
    settings_path = os.path.join(app_data_dir, 'settings.json')
    # 新增：chatBot所需配置文件路径
    input_path = os.path.join(app_data_dir, 'input.json')
    call_openai_path = os.path.join(app_data_dir, 'callOpenAI.json')

    default_toolbar = [
        {
            "Toolname": "Translate to English",
            "Plugin": "callOpenAI.py",
            "Prompt": "You are an AI assistant, please translate the following content into English and keep it professional and concise.",
            "Model": "gpt-3.5-turbo",
        },
        {
            "Toolname": "Chat Bot",
            "Plugin": "chatBot.py",
            "Prompt": "You are an AI assistant, please answer the questions according to the requirements.",
            "Model": "gpt-3.5-turbo",
        },
        {
            "Toolname": "Traditional Search",
            "Plugin": "traditionalSearch.py",
            "Prompt": "https://global.bing.com/search?q=",
            "Model": "gpt-3.5-turbo",
        }
    ]

    default_models = [
        {
        "API_URL": "https://api.openai.com/v1/chat/completions",
        "Model": "gpt-3.5-turbo",
        "API_Key": ""
        }
    ]

    default_settings = [
        {
            "language": "en-US"  # 修改：将默认语言改为英文
        }
    ]  # 新增: 默认 settings 内容

    # 新增：chatBot插件的默认配置
    default_input = [
        {
        "Model": "gpt-3.5-turbo",
        "Prompt": "You are an AI assistant, please answer the questions according to the requirements.",
        "Plugin": "chatBot.py",
        "Replace": True,
        "API_URL": "https://api.openai.com/v1/chat/completions",
        "API_Key": "",
        "Clipboard": ""
    }
    ]

    default_call_openai = {
        "temperature": 0.7,
        "top_p": 1.0,
        "n": 1,
        "stream": False,
        "stop": None,
        "max_tokens": 4096,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "logit_bias": {},
        "replace": True
    }
    

    # 新增配置文件初始化
    if not os.path.exists(input_path):
        with open(input_path, 'w') as f:
            json.dump(default_input, f, indent=4)
        print(f"Created {input_path}")

    if not os.path.exists(call_openai_path):
        with open(call_openai_path, 'w') as f:
            json.dump(default_call_openai, f, indent=4)
        print(f"Created {call_openai_path}")

    if not os.path.exists(toolbar_path):
        with open(toolbar_path, 'w') as f:
            json.dump(default_toolbar, f, indent=4)
        print(f"Created {toolbar_path}")

    if not os.path.exists(models_path):
        with open(models_path, 'w') as f:
            json.dump(default_models, f, indent=4)
        print(f"Created {models_path}")

    if not os.path.exists(settings_path):  # 新增: 检查并创建 settings.json
        with open(settings_path, 'w') as f:
            json.dump(default_settings, f, indent=4)
        print(f"Created {settings_path}")

class ClipboardMonitor:
    def __init__(self):
        self.last_clipboard_content = ""
        self.clipboard_changed_time = None
        self.hotkey_listener = None
        self.timer = None
        self.running = True  # 新增运行状态标志

    def monitor_clipboard(self):
        while self.running:  # 修改循环判断条件
            try:
                current_clipboard_content = pyperclip.paste()
                if current_clipboard_content != self.last_clipboard_content:
                    self.last_clipboard_content = current_clipboard_content
                    print("Clipboard updated")
                    self.clipboard_changed_time = time.time()
                    self.setup_hotkey_listener()
                time.sleep(0.2)
            except Exception as e:
                logging.error(f"剪切板监控异常: {str(e)}")
                time.sleep(1)  # 异常后稍作等待

    def setup_hotkey_listener(self):
        print("Setting up hotkey listener")
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.timer:
            self.timer.cancel()

        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+c': self.on_ctrl_c
        })
        self.hotkey_listener.start()

        # 设置一个2秒后停止热键监听器的定时器
        self.timer = Timer(2, self.stop_hotkey_listener)
        self.timer.start()

    def stop_hotkey_listener(self):
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            print("Hotkey listener stopped due to timeout")

    def on_ctrl_c(self):
        print("Ctrl+C detected")
        if self.clipboard_changed_time and time.time() - self.clipboard_changed_time < 2:
            print("Ctrl+C detected within 2 seconds of clipboard change")
            show_tool_bar()

    def stop(self):
        self.running = False  # 新增停止方法
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.timer:
            self.timer.cancel()

    def start(self):
        thread = Thread(target=self.monitor_clipboard, daemon=True)
        thread.start()

class PluginHTTPServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        # 修改：动态获取资源路径（支持打包环境）
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            frontend_dir = os.path.join(base_path, 'frontend')
            plugin_dir = os.path.join(base_path, 'plugin')
        else:
            project_root = os.path.abspath(os.path.dirname(__file__))
            frontend_dir = os.path.join(project_root, '..', 'frontend')
            plugin_dir = os.path.join(project_root, '..', 'plugin')

        # 新增marked.min.js的请求处理
        if self.path == '/marked.min.js':
            file_path = os.path.join(frontend_dir, 'marked.min.js')
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/javascript')
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File Not Found: marked.min.js")
            return

        # 新增: 处理 /getPluginFiles 请求
        if self.path == '/getPluginFiles':
            try:
                # 获取 plugin 目录下的 .py 文件列表
                if not os.path.exists(plugin_dir):
                    self.send_error(404, "Plugin directory not found")
                    return
                
                # 获取所有 .py 文件的文件名（不带扩展名）
                files = [f[:-3] for f in os.listdir(plugin_dir) if f.endswith('.py')]
                
                # 返回 JSON 格式的文件列表
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(files).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return

        if self.path == '/plugins':
            print(f"Attempting to access plugin directory: {plugin_dir}")  
            if not os.path.exists(plugin_dir):
                self.send_error(404, "Plugin directory not found")
                return
            files = [f[:-5] for f in os.listdir(plugin_dir) if f.endswith('.html')]  # Remove .html extension
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(files).encode('utf-8'))
        elif self.path.startswith('/plugin/'):
            filename = self.path[len('/plugin/'):] + '.html'
            file_path = os.path.join(plugin_dir, filename)
            if os.path.isfile(file_path) and file_path.endswith('.html'):
                with open(file_path, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File Not Found: %s" % filename)
        elif self.path == '/favicon.ico':
            # 修改：使用动态获取的前端目录路径
            file_path = os.path.join(frontend_dir, 'favicon.ico')
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/x-icon')
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File Not Found: %s" % self.path)
        elif self.path.startswith('/getConfig/'):  # 合并后的配置获取接口
            config_name = self.path.split('/getConfig/')[-1]
            app_data_dir = os.path.join(os.getenv('APPDATA'), 'general-assistant-2')
            config_path = os.path.join(app_data_dir, config_name)

            logging.debug(f"尝试访问配置文件: {config_path}")

            # 修改后路径安全检查（保留目录遍历防护，移除白名单限制）
            if '..' in config_name or not config_name.endswith('.json'):
                self.send_error(400, "Invalid config file name")
                logging.warning(f"非法配置文件请求: {config_name}")
                return

            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(config_data).encode('utf-8'))
                logging.debug(f"成功加载配置文件: {config_name}")
            else:
                self.send_error(404, f"配置文件未找到: {config_name}")
                logging.debug(f"配置文件未找到: {config_name}")

        elif self.path == '/openPluginFolder':
            # 新增：处理打开 plugin 文件夹的请求
            try:
                # 使用系统命令打开文件夹
                if os.name == 'nt':  # Windows
                    os.startfile(plugin_dir)
                elif os.name == 'posix':  # macOS 和 Linux
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', plugin_dir])
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Plugin folder opened successfully")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Failed to open plugin folder: {str(e)}".encode('utf-8'))
        elif self.path.startswith('/locales/'):
            # 处理语言文件请求
            lang = self.path.split('/')[-1]
            if lang in ['en-US.json', 'zh-CN.json']:
                # 修改：使用动态获取的路径
                if getattr(sys, 'frozen', False):
                    base_path = sys._MEIPASS
                    file_path = os.path.join(base_path, 'frontend', 'locales', lang)
                else:
                    file_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'locales', lang)
                
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(file.read().encode('utf-8'))
                else:
                    self.send_error(404, f"Locale file not found: {lang}")
            else:
                self.send_error(404, "Invalid locale file requested")
        else:
            # Serve files from the frontend directory
            if self.path == '/':
                self.path = '/plugin.html'
            file_path = os.path.join(frontend_dir, self.path.lstrip('/'))
            if os.path.isfile(file_path) and file_path.endswith(('.html', '.css', '.js')):
                with open(file_path, 'rb') as file:
                    self.send_response(200)
                    content_type = 'text/html' if file_path.endswith('.html') else ('text/css' if file_path.endswith('.css') else 'application/javascript')
                    self.send_header('Content-type', content_type)
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File Not Found: %s" % self.path)

    def do_POST(self):
        if self.path.startswith('/savePluginConfig/'):  # 新增插件专用配置保存接口
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                config_data = json.loads(post_data)
                
                # 解析配置文件名
                config_name = self.path.split('/savePluginConfig/')[-1]
                
                # 路径安全检查
                if '..' in config_name or not config_name.endswith('.json'):
                    self.send_error(400, "Invalid config file name")
                    logging.warning(f"非法插件配置文件请求: {config_name}")
                    return

                # 获取配置文件路径
                app_data_dir = os.path.join(os.getenv('APPDATA'), 'general-assistant-2')
                config_path = os.path.join(app_data_dir, config_name)
                
                # 确保目录存在
                if not os.path.exists(app_data_dir):
                    os.makedirs(app_data_dir)

                # 直接保存完整配置数据
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                logging.debug(f"成功保存插件配置文件: {config_name}")

            except json.JSONDecodeError as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'无效的JSON格式: {str(e)}'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'服务器错误: {str(e)}'}).encode('utf-8'))

        elif self.path.startswith('/saveConfig/'):  # 保留原有接口
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                config_data = json.loads(post_data)
                
                # 动态解析配置文件名和操作类型
                # 修复路径拼接问题：正确提取配置文件名并自动补全.json后缀
                config_name = self.path.split('/saveConfig/')[-1]
                action = config_data.get('action', 'add')
                index = config_data.get('index', -1)

                # 路径安全检查（防止遍历攻击与操作非json文件）
                if '..' in config_name or not config_name.endswith('.json'):
                    self.send_error(400, "Invalid config file name")
                    logging.warning(f"非法配置文件请求: {config_name}")
                    return

                # 获取配置文件路径
                app_data_dir = os.path.join(os.getenv('APPDATA'), 'general-assistant-2')
                config_path = os.path.join(app_data_dir, config_name)
                
                # 确保目录存在
                if not os.path.exists(app_data_dir):
                    os.makedirs(app_data_dir)

                # 读取现有配置数据
                existing_data = []
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)

                # 新增：特殊处理 settings.json 的保存逻辑
                if config_name == 'settings.json':
                    # 直接更新 language 字段
                    if existing_data and isinstance(existing_data, list):
                        existing_data[0]['language'] = config_data.get('language', 'zh-CN')
                    else:
                        existing_data = [{'language': config_data.get('language', 'zh-CN')}]
                else:
                    # 原有处理其他配置文件的逻辑
                    if action == 'add':
                        existing_data.append(config_data.get('model', config_data.get('tool', {})))
                    elif action == 'update' and index >= 0:
                        if 0 <= index < len(existing_data):
                            if 'model' in config_data:
                                existing_data[index] = config_data['model']
                            elif 'tool' in config_data:
                                existing_data[index] = config_data['tool']

                # 保存更新后的配置数据
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                logging.debug(f"成功保存配置文件: {config_name}")

            except json.JSONDecodeError as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'无效的JSON格式: {str(e)}'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'服务器错误: {str(e)}'}).encode('utf-8'))

    def do_DELETE(self):
        if self.path.startswith('/deleteConfig/'):  # 合并后的统一删除接口
            try:
                # 从路径中解析配置文件名和索引
                path_parts = self.path.split('/')[2:]  # 示例路径：/deleteConfig/models.json/1
                if len(path_parts) != 2:
                    self.send_error(400, "Invalid delete path format")
                    return
                
                config_name, index_str = path_parts
                index = int(index_str)

                # 修改后路径安全检查（保留目录遍历防护）
                if '..' in config_name or not config_name.endswith('.json'):
                    self.send_error(400, "Invalid config file name")
                    logging.warning(f"非法配置文件请求: {config_name}")
                    return

                # 获取配置文件路径
                app_data_dir = os.path.join(os.getenv('APPDATA'), 'general-assistant-2')
                config_path = os.path.join(app_data_dir, config_name)
                
                # 确保目录存在
                if not os.path.exists(app_data_dir):
                    os.makedirs(app_data_dir)
                
                # 读取现有配置数据
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                else:
                    config_data = []
                
                # 检查索引是否有效并删除配置项
                if 0 <= index < len(config_data):
                    del config_data[index]
                    
                    # 保存更新后的配置数据
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=4)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid index'}).encode('utf-8'))
            except ValueError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid index format'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Server error: {str(e)}'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()



if __name__ == '__main__':
    ensure_config_files_exist()

    # 清空剪切板
    pyperclip.copy('')
    print("Clipboard cleared on startup.")

    # 启动剪切板监听器
    clipboard_monitor = ClipboardMonitor()
    clipboard_monitor.start()

    # 修改：动态获取图标路径（支持打包环境）
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        icon_path = os.path.join(base_path, 'frontend', 'favicon.ico')
    else:
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
        icon_path = os.path.join(frontend_dir, 'favicon.ico')
    
    # 确保图标文件存在
    if not os.path.exists(icon_path):
        logging.error(f"图标文件不存在: {icon_path}")
        # 创建空图像作为后备
        image = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    else:
        image = Image.open(icon_path)

    # 使用新的创建菜单函数
    menu = create_tray_menu()
    
    icon = Icon('GeneralAIAssistant', image, 'General Assistant 2', menu=menu)

    # Start HTTP server for serving plugin list
    httpd = HTTPServer(('localhost', 54900), PluginHTTPServer)
    http_thread = Thread(target=httpd.serve_forever, daemon=True)
    http_thread.start()

    # 打印服务器启动信息
    print("HTTP Server started at http://localhost:54900")

    #显示软件启动成功通知
    plyer.notification.notify(
        title=translations.get('GeneralAssistant', 'General Assistant 2'),
        message=translations.get('startup_message', 'General Assistant 2 has started successfully.'),
        app_name=translations.get('GeneralAssistant', 'General Assistant 2'),
        app_icon=icon_path,
        timeout=1
    )

    icon.run()  # 阻塞主线程

    # 程序退出时清理
    clipboard_monitor.stop()
    httpd.shutdown()



