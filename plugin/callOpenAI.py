# -*- coding: utf-8 -*-
import json
import os
import requests
import pyautogui
import win32clipboard
import win32con
import plyer

def app_data_dir():
    """应用数据目录"""
    path = os.path.join(os.getenv('APPDATA'), 'general-assistant-2')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def config_path(filename):
    """配置文件路径"""
    return os.path.join(app_data_dir(), filename)

def init_call_openai_config():
    """初始化 callOpenAI.json 配置文件"""
    default_config ={
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
    
    call_openai_path = config_path('callOpenAI.json')
    if not os.path.exists(call_openai_path):
        with open(call_openai_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)

def get_current_language():
    """获取当前语言配置"""
    try:
        response = requests.get('http://localhost:54900/getConfig/settings.json')
        response.raise_for_status()
        config = response.json()
        
        # 增加类型检查和多重解析逻辑
        if isinstance(config, dict):
            # 直接从字典中获取
            return config.get('language', 'zh-CN')
        elif isinstance(config, list):
            # 遍历列表寻找字典类型的语言配置
            for item in config:
                if isinstance(item, dict) and 'language' in item:
                    return item['language']
            return 'zh-CN'
        else:
            # 兜底处理非字典/列表返回值
            if hasattr(config, 'language'):
                return config.language
            return 'zh-CN'
    except (requests.RequestException, ValueError):
        return 'zh-CN'

def load_translations(lang):
    """加载对应语言的翻译文件"""
    try:
        response = requests.get(f'http://localhost:54900/locales/{lang}.json')
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        # 回退到中文
        if lang != 'zh-CN':
            response = requests.get('http://localhost:54900/locales/zh-CN.json')
            response.raise_for_status()
            return response.json()
        return {}

def truncate_message(message, max_length=256):
    """截取消息为指定最大长度"""
    if len(message) > max_length:
        return message[:max_length] + "..."
    return message

# 获取当前语言和翻译字典
current_language = get_current_language()
translations = load_translations(current_language)

def read_input_json():
    """读取 input.json 文件"""
    input_path = config_path('input.json')
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[0] if data else {}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"读取 input.json 错误: {e}")
        plyer.notification.notify(
            title=translations.get("notification_title_error", "Error"),
            message=truncate_message(translations.get("error_reading_input_json", "Failed to read input.json: {e}").format(e=e)),
            app_name='traditionalSearch'
        )
        return {}

def read_call_openai_config():
    """读取 callOpenAI.json 文件"""
    call_openai_path = config_path('callOpenAI.json')
    try:
        with open(call_openai_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"读取 callOpenAI.json 错误: {e}")
        plyer.notification.notify(
            title=translations.get("notification_title_error", "Error"),
            message=truncate_message(translations.get("error_reading_call_openai", "Failed to read callOpenAI.json: {e}").format(e=e)),
            app_name='traditionalSearch'
        )
        return {}

def replace_check(params):
    """检查是否需要替换"""
    if params.get("replace", False):
        return
    else:
        pyautogui.press('right')
        return

def send_request_to_api(params):
    """发送请求到 OpenAI API"""
    api_url = params["API_URL"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {params['API_Key']}"
    }
    payload = {
        "model": params["Model"],
        "messages": [
            {"role": "system", "content": params["Prompt"]},
            {"role": "user", "content": params["Clipboard"]}
        ],
        "temperature": params.get("temperature", 0.7),
        "top_p": params.get("top_p", 1.0),
        "n": params.get("n", 1),
        "stream": params.get("stream", False),
        "stop": params.get("stop"),
        "max_tokens": params.get("max_tokens", 150),
        "presence_penalty": params.get("presence_penalty", 0.0),
        "frequency_penalty": params.get("frequency_penalty", 0.0),
        "logit_bias": params.get("logit_bias", {}),
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, stream=params.get("stream", False), verify=False)
    except requests.RequestException as e:
        print(f"API 请求失败: {e}")
        plyer.notification.notify(
            title=translations.get("notification_title_openai_error", "OpenAI API Error"),
            message=truncate_message(translations.get("error_sending_request", "Failed to send API request").format(e=e))
        )
        return

    if response.status_code != 200:
        print(f"API 请求失败: {response.status_code} - {response.text}")
        plyer.notification.notify(
            title=translations.get("notification_title_openai_error", "OpenAI API Error"),
            message=truncate_message(translations.get("error_api_response", "API request failed with status code").format(
                code=response.status_code, text=response.text
            ))
        )
        return

    # 检查响应内容是否为空
    if not response.text.strip():
        error_msg = "API 返回了空响应"
        print(error_msg)
        plyer.notification.notify(
            title=translations.get("notification_title_openai_error", "OpenAI API Error"),
            message=truncate_message(translations.get("error_empty_response", "API returned an empty response"))
        )
        return

    if params.get("stream", False):
        content = ""
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data:'):
                    chunk = line[len('data:'):].strip()
                    if chunk == '[DONE]':
                        break
                    try:
                        # 打印原始字节数据
                        #print(f"原始字节数据: {line.encode('utf-8')}")  # 新增调试信息
                        
                        json_chunk = json.loads(chunk)
                        if 'choices' in json_chunk and json_chunk['choices']:
                            delta_content = json_chunk['choices'][0]['delta'].get('content', '')
                            if delta_content:
                                # 增强编码处理逻辑
                                if isinstance(delta_content, bytes):
                                    decoded_content = delta_content.decode('utf-8', 'replace')
                                else:
                                    try:
                                        # 尝试通过 latin-1 -> utf-8 的二次编码解码修复乱码
                                        decoded_content = delta_content.encode('latin-1').decode('utf-8', 'replace')
                                    except Exception as e:
                                        decoded_content = delta_content
                                        print(f"编码修复失败: {e}")
                                        plyer.notification.notify(title='Encoding repair failed', message=truncate_message(str(e)))
                                
                                # 改进调试信息输出格式
                                print(f"解析后 token: {decoded_content} (原始长度:{len(delta_content)}, 解码后长度:{len(decoded_content)})")  # 改进长度显示
                                
                                content += decoded_content
                                set_clipboard_and_paste(decoded_content)  # 立即更新剪贴板和执行粘贴
                    except Exception as e:
                        print(f"流式请求处理错误: {e}")

        finally:
            pass  # 不需要在这里更新剪贴板，已经在每次接收token时更新过了
    else:
        try:
            # 添加响应内容有效性检查
            if not response.text.strip():
                raise ValueError("API 返回了空响应")
                
            response_json = response.json()
            content = response_json['choices'][0]['message']['content']
            set_clipboard_and_paste(content)
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            print(f"解析 JSON 数据错误: {e}")
            # 添加详细的响应内容日志输出
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")  # 只打印前500个字符
            
            plyer.notification.notify(
                title=translations.get("notification_title_error", "Error"),
                message=truncate_message(translations.get("error_parsing_response", "Failed to parse response JSON: {e}").format(e=e))
            )

def set_clipboard_and_paste(text):
    """设置剪贴板内容并执行粘贴操作"""
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        pyautogui.hotkey('ctrl', 'v')
    except Exception as e:
        print(f"设置剪贴板和粘贴操作失败: {e}")
        plyer.notification.notify(
            title=translations.get("notification_title_error", "Error"),
            message=translations.get("clipboard_paste_failed", "Failed to set clipboard and paste: {e}").format(e=e)
        )

if __name__ == "__main__":
    init_call_openai_config()
    input_params = read_input_json()
    call_openai_config = read_call_openai_config()

    if not input_params:
        print("未找到有效的 input.json 内容")
        plyer.notification.notify(
            title=translations.get("notification_title_error", "Error"),
            message=translations.get("error_required_content", "Please enter valid content")
        )
    else:
        combined_params = {**input_params, **call_openai_config}
        replace_check(combined_params)  # 传入合并后的参数
        send_request_to_api(combined_params)



