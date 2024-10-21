import requests

class YandexDisk:
    def __init__(self, token):
        self.token = token
        self.api_base_url = 'https://cloud-api.yandex.net/v1/disk'
    
    def get_headers(self):
        return {'Authorization': f'OAuth {self.token}'}
    
    def upload_file(self, data, path):
        upload_url = f'{self.api_base_url}/resources/upload?path={path}&overwrite=true'
        headers = self.get_headers()
        response = requests.get(upload_url, headers=headers)
        if response.status_code == 200:
            upload_link = response.json()['href']
            upload_response = requests.put(upload_link, files={'file': data})
            upload_response.raise_for_status()
        else:
            response.raise_for_status()
    
    def download_file(self, path):
        download_url = f'{self.api_base_url}/resources/download?path={path}'
        headers = self.get_headers()
        response = requests.get(download_url, headers=headers)
        if response.status_code == 200:
            download_link = response.json()['href']
            file_response = requests.get(download_link)
            file_response.raise_for_status()
            return file_response
        else:
            response.raise_for_status()
