import time
from state import AgentState
import requests
from os import environ

BASE = "https://3090api.huannago.com"
CREATE_URL = f"{BASE}/api/v1/subtitle/tasks"
WAV_PATH = environ["AUDIO_FILE_PATH"]


def asr_node(state: AgentState):
    auth = ("nutc2504", "nutc2504")

    # 1) 建立任務
    with open(WAV_PATH, "rb") as f:
        r = requests.post(CREATE_URL, files={"audio": f}, timeout=60, auth=auth)
    r.raise_for_status()
    task_id = r.json()["id"]
    print("task_id:", task_id)
    print("等待轉文字...")
    txt_url = f"{BASE}/api/v1/subtitle/tasks/{task_id}/subtitle?type=TXT"
    srt_url = f"{BASE}/api/v1/subtitle/tasks/{task_id}/subtitle?type=SRT"

    def wait_download(url: str, max_tries=600):  # 等下載完成
        for _ in range(max_tries):
            try:
                resp = requests.get(url, timeout=(5, 60), auth=auth)
                if resp.status_code == 200:
                    return resp.text
                # 還沒好通常 404
                # 😡明明就會
            except requests.exceptions.ReadTimeout:
                pass
            time.sleep(2)
        return None

    # 2) 等 TXT(純文字)
    txt_text = wait_download(txt_url, max_tries=600)
    if txt_text is None:
        raise TimeoutError("轉錄逾時or錯誤")

    srt_text = wait_download(srt_url, max_tries=600)

    print("轉文字 end")
    return {
        "srt_text": srt_text,
        "txt_text": txt_text,
    }
