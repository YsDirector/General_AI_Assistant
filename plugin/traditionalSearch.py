import json
import webbrowser
import urllib.parse
import requests
import plyer

def main():
    translations = {}  # 初始化translations为空字典
    try:
        # 获取当前语言设置
        settings_response = requests.get('http://localhost:54900/getConfig/settings.json', timeout=10)
        settings_response.raise_for_status()
        settings = settings_response.json()
        
        # 处理settings可能为列表的情况
        if isinstance(settings, list):
            if len(settings) > 0:
                settings = settings[0]
            else:
                settings = {}
        
        lang = settings.get('language', 'en-US')
        
        # 获取对应语言的翻译文件
        translations_response = requests.get(f'http://localhost:54900/locales/{lang}.json', timeout=10)
        translations_response.raise_for_status()
        translations = translations_response.json()
        
        # 获取配置文件
        config_response = requests.get('http://localhost:54900/getConfig/input.json', timeout=10)
        config_response.raise_for_status()
        config = config_response.json()
        
        if isinstance(config, list) and len(config) > 0:
            base_url = config[0].get("Prompt", "")
            search_term = config[0].get("Clipboard", "")
        else:
            base_url = config.get("Prompt", "")
            search_term = config.get("Clipboard", "")
        
        encoded_term = urllib.parse.quote(search_term)
        full_url = f"{base_url}{encoded_term}"
        print(f"Constructed URL: {full_url}")
        #plyer.notification.notify(
            #title=translations.get('notification_title', 'Traditional Search'),
            #message=translations.get('notification_message', 'Searching') +f"{full_url}: {str(search_term)}",
            #app_name='traditionalSearch'
        #)
        webbrowser.open(full_url)
        
    except requests.exceptions.RequestException as e:
        error_msg = translations.get('error_http_request_failed', 'HTTP request failed')
        print(f"{error_msg}: {str(e)}")
        plyer.notification.notify(
            title=translations.get('error_title', 'Error'),
            message=f"{error_msg}: {str(e)}",
            app_name='traditionalSearch'
        )
    except json.JSONDecodeError as e:
        error_msg = translations.get('error_json_decode', 'JSON decode failed')
        print(f"{error_msg}: {str(e)}")
        plyer.notification.notify(
            title=translations.get('error_title', 'Error'),
            message=f"{error_msg}: {str(e)}",
            app_name='traditionalSearch'
        )
    except Exception as e:
        error_msg = translations.get('error_unknown', 'Unknown error occurred')
        print(f"{error_msg}: {str(e)}")
        plyer.notification.notify(
            title=translations.get('error_title', 'Error'),
            message=f"{error_msg}: {str(e)}",
            app_name='traditionalSearch'
        )

if __name__ == "__main__":
    main()