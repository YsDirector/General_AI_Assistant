import requests
import json
import webview
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

class ChatBot:
    def __init__(self):
        self.api_url = None
        self.api_key = None
        self.model = None
        self.temperature = 0.7
        self.max_tokens = 150
        self.stream = False  # 新增流式控制属性

    def load_config(self):
        
            # 通过 HTTP 请求获取配置信息
            try:
                # 获取 input.json 配置
                input_response = requests.get('http://localhost:54900/getConfig/input.json')
                input_config = input_response.json()[0]  # 假设只有一个配置项
                print(f"原始input配置内容: {json.dumps(input_config, indent=2)}")  # 新增调试信息
                
                # 使用带默认值的get方法获取配置项
                self.api_url = input_config.get("API_URL", "https://api.openai.com/v1/chat/completions")
                self.api_key = input_config.get("API_Key", "")
                self.model = input_config.get("Model", "gpt-3.5-turbo")
                # 新增：读取Prompt配置
                self.system_prompt = input_config.get("Prompt", "请展示完整的思考过程，然后给出最终答案：")
                
                # 获取 callOpenAI.json 配置
                call_openai_response = requests.get('http://localhost:54900/getConfig/callOpenAI.json')
                call_openai_config = call_openai_response.json()
                print(f"原始callOpenAI配置内容: {json.dumps(call_openai_config, indent=2)}")  # 新增调试信息
                
                # 使用带类型检查的配置获取
                self.temperature = float(call_openai_config.get("temperature", 0.7))
                self.max_tokens = int(call_openai_config.get("max_tokens", 150))
                
                # 新增流式配置读取
                self.stream = bool(call_openai_config.get("stream", False))
                print(f"流式模式: {'启用' if self.stream else '禁用'}")
                
                # 修改配置检查逻辑：仅检查必要字段
                missing_fields = []
                if not self.api_url:
                    missing_fields.append("API_URL")
                if not self.model:
                    missing_fields.append("Model")
                    
                if missing_fields:
                    print(f"警告: 配置缺失关键字段 {missing_fields}，当前配置 API_URL={self.api_url}, Model={self.model}")
                else:
                    print("配置检查通过，必要字段完整")

            except Exception as e:
                print(f"配置加载异常: {str(e)}，使用默认配置继续运行")
                # 设置安全默认值
                self.api_url = "https://api.openai.com/v1/chat/completions"
                self.api_key = ""
                self.model = "gpt-3.5-turbo"
                self.temperature = 0.7
                self.max_tokens = 150

    def get_clipboard_content(self):
        """读取 input.json 中的 Clipboard 内容"""
        try:
            input_response = requests.get('http://localhost:54900/getConfig/input.json')
            input_config = input_response.json()[0]
            clipboard_content = input_config.get("Clipboard", "")
            return clipboard_content.strip()  # 去除可能的多余空格
        except Exception as e:
            print(f"读取 Clipboard 内容失败: {str(e)}")
            return ""

    def _generate_stream_response(self, messages):
        """流式响应专用方法（返回生成器）"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model,
                "messages": messages,  # 使用完整对话历史
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    #print(f"原始响应行: {decoded_line}")  # 新增调试信息
                    
                    if decoded_line.startswith('data:'):
                        try:
                            chunk = json.loads(decoded_line[5:])
                            #print(f"解析后的chunk: {json.dumps(chunk, indent=2)}")  # 新增调试信息
                            
                            if 'choices' in chunk and chunk['choices']:
                                # 修改：优先检查reasoning_content字段
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('reasoning_content')  # 优先使用reasoning_content
                                if content is None:  # 如果reasoning_content不存在则回退到content
                                    content = delta.get('content', '')
                                
                                # 处理换行符并过滤空内容
                                if content:
                                    content = content.replace('\n', '<br>')
                                    print(f"流式数据块 - 内容: {content}")
                                    yield f"data:{content}\n\n"
                                #else:
                                    #print("收到空内容，继续等待后续数据")
                            else:
                                print(f"未找到有效数据结构: {decoded_line}")
                                
                        except json.JSONDecodeError as je:
                            print(f"JSON解析失败: {str(je)}，原始数据: {decoded_line}")
                    elif decoded_line.startswith('[DONE]'):
                        print("收到[DONE]信号，结束流式传输")
                        yield "\ndata: [END]\n\n"
                        break
                        
            print("流式传输完成 - 发送结束标识")
        except Exception as e:
            error_msg = f"流式生成异常: {str(e)}"
            print(f"异常信息: {error_msg}")
            yield f"data: [ERROR: {str(e)}]\n\n"
        finally:
            print("流式传输会话结束")

    def generate_response(self, messages):
        """统一响应入口，根据流式标志返回不同类型"""
        if self.stream:
            return self._generate_stream_response(messages)
        else:
            # 非流式模式保持字典返回
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                data = {
                    "model": self.model,
                    "messages": messages,  # 使用完整对话历史
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": False
                }
                
                response = requests.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                response_data = response.json()
                
                if response_data.get('choices'):
                    content = response_data['choices'][0]['message']['content']
                    # 将换行符替换为<br>标签
                    content = content.replace('\n', '<br>')
                    return content  # 修改：直接返回内容字符串
                return "未收到有效回复"
                
            except requests.exceptions.RequestException as e:
                return f"网络错误: {str(e)}"
            except Exception as e:
                return f"处理错误: {str(e)}"

    def open_webview(self):
        """
        启动 GUI 界面
        """
        try:
            # 创建窗口并加载 HTML 文件
            webview.create_window(
                "ChatBot",  # 窗口标题
                "http://localhost:54900/plugin/chatBot",  # HTML 文件路径
                resizable=False,
                min_size=(600, 710),
                text_select=True,
            )
            webview.start(debug=False)  # 启动 GUI 主循环
        except Exception as e:
            print(f"启动 GUI 失败: {str(e)}")
            sys.exit(1)

# 新增：定义 Flask 接口
@app.route('/plugin/chatBot', methods=['GET', 'POST', 'OPTIONS'])
def handle_chatbot_request():
    try:
        # 处理预检请求
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'preflight accepted'})
            response.headers.add('Access-Control-Allow-Origin', '*')  # 修改: 允许所有来源
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            return response, 200

        print("\n=== 收到新请求 ===")
        
        # 修改：支持GET请求参数解析（messages参数）
        if request.method == 'GET':
            messages_json = request.args.get('messages')
            if messages_json:
                try:
                    messages = json.loads(messages_json)
                    # 修改：使用配置中的系统提示词
                    bot = ChatBot()
                    bot.load_config()
                    messages.insert(0, {"role": "system", "content": bot.system_prompt})
                except json.JSONDecodeError:
                    return jsonify({'error': 'Invalid messages format'}), 400
            else:
                # 兼容旧逻辑
                message = request.args.get('message')
                if not message:
                    # 获取 Clipboard 内容并返回
                    bot = ChatBot()
                    clipboard_content = bot.get_clipboard_content()
                    response = jsonify({'message': clipboard_content})
                    response.headers.add('Access-Control-Allow-Origin', '*')  # 修改: 添加CORS头
                    return response, 200
                # 构造单条消息格式
                bot = ChatBot()
                bot.load_config()
                messages = [
                    {"role": "system", "content": bot.system_prompt},  # 修改：使用配置中的系统提示词
                    {"role": "user", "content": message}
                ]
        else:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({'error': 'Invalid request data'}), 400
            else:
                # 优先尝试获取messages字段
                if 'messages' in data:
                    messages = data['messages']
                    # 确保messages是列表
                    if not isinstance(messages, list):
                        return jsonify({'error': 'messages must be a list'}), 400
                    # 修改：使用配置中的系统提示词
                    bot = ChatBot()
                    bot.load_config()
                    messages.insert(0, {"role": "system", "content": bot.system_prompt})
                else:
                    # 构造单条消息格式
                    bot = ChatBot()
                    bot.load_config()
                    messages = [
                        {"role": "system", "content": bot.system_prompt},  # 修改：使用配置中的系统提示词
                        {"role": "user", "content": data['message']}
                    ]

        bot = ChatBot()
        bot.load_config()
        
        # 确保只在有效数据时打印日志
        print(f"生成回复内容: {messages[-1]['content'] if messages else '无内容'}")
        
        response_content = bot.generate_response(messages)  # 传递完整上下文
        
        if bot.stream:
            def stream():
                try:
                    for content in response_content:
                        if content.strip() != '':
                            # 内容已包含<br>标签，直接转发
                            yield f"data: {content}\n\n"
                    yield "data: [END]\n\n"
                except Exception as e:
                    yield f"data: [ERROR: {str(e)}]\n\n"
                finally:
                    print("流式传输结束")

            response = app.response_class(
                stream(),
                mimetype='text/event-stream',
                headers={
                    'Access-Control-Allow-Origin': '*',  # 修改: 添加CORS头
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive'
                }
            )
            return response
        else:
            print(f"返回非流式响应，包装为流式响应: {response_content}")
                
            def generate():
                try:
                    if response_content:
                        # 直接发送已处理的内容（已包含<br>标签）
                        yield f"data: {response_content}\n\n"
                        yield "data: [END]\n\n"
                except Exception as e:
                    yield f"data: [ERROR: {str(e)}]\n\n"
                finally:
                    print("非流式响应传输结束")
            
            response = app.response_class(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Access-Control-Allow-Origin': '*',  # 修改: 添加CORS头
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive'
                }
            )
            return response

    except Exception as e:
        print(f"处理请求时发生错误: {str(e)}")
        response = app.response_class(
            response=f"Error: {str(e)}",
            status=500,
            mimetype='text/plain',
            headers={'Access-Control-Allow-Origin': '*'}  # 修改: 添加CORS头
        )
        return response

if __name__ == "__main__":
    bot = ChatBot()
    bot.load_config()
    print("ChatBot initialized with configuration:")
    print(f"API URL: {bot.api_url}")
    print(f"Model: {bot.model}")
    print(f"Temperature: {bot.temperature}")
    print(f"Max Tokens: {bot.max_tokens}")
    
    # 修改线程启动顺序：Flask在后台线程，webview在主线程
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='localhost', port=54901, debug=False, use_reloader=False))
    flask_thread.daemon = True  # 新增：设置为守护线程
    flask_thread.start()
    
    # 新增：等待服务器启动
    import time
    time.sleep(1)
    
    bot.open_webview()  # 主线程直接调用
