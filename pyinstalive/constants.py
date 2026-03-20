import sys


class Constants:
    SCRIPT_VERSION = "4.1.0"
    PYTHON_VERSION = sys.version.split(" ")[0]
    CONFIG_TEMPLATE = """
[pyinstalive]
username = johndoe
password = grapefruits
download_path = {:s}
download_comments = True
clear_temp_files = True
cmd_on_started =
cmd_on_ended =
ffmpeg_path = 
log_to_file = True
no_assemble = False
use_locks = True
send_heartbeat = True
proxy =
cookie_file =
    """



    BASE_HEADERS =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7478.45 Safari/537.36', "x-ig-app-id": '936619743392459', "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="148", "Google Chrome";v="148"', "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"', "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "none", "sec-fetch-user": "?1", "upgrade-insecure-requests": "1", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8", "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9"}
    BASE_WEB = "https://www.instagram.com/"
    BASE_API = "https://i.instagram.com/api/v1/"

    LOGIN_PAGE = BASE_WEB + "accounts/login/"
    LOGIN_AJAX = BASE_WEB + "accounts/login/ajax/"

    REELS_TRAY = BASE_API + "live/reels_tray_broadcasts/"
    USER_INFO = BASE_API + "users/web_profile_info/?username={:s}"
    LIVE_STATE_USER = BASE_API + "live/web_info/?target_user_id={:s}"
    LIVE_HEARTBEAT = BASE_API + "live/{:s}/heartbeat_and_get_viewer_count/"
    LIVE_COMMENT = BASE_API + "live/{:s}/get_comment/?last_comment_ts={:s}"
