import time
import subprocess
import os
import shutil
import json
import shlex
import sys
import codecs
import threading

try:
    import pil
    import helpers
    import logger
    from constants import Constants
except ImportError:
    from . import pil
    from . import helpers
    from . import logger
    from .constants import Constants

def strdatetime():
    return time.strftime('%m-%d-%Y %I:%M:%S %p')


def strtime():
    return time.strftime('%I:%M:%S %p')


def strdate():
    return time.strftime('%m-%d-%Y')


def strepochtime():
    return str(int(time.time()))


def strdatetime_compat():
    return time.strftime('%Y%m%d')


def command_exists(command):
    try:
        fnull = open(os.devnull, 'w')
        subprocess.call([command], stdout=fnull, stderr=subprocess.STDOUT)
        return True
    except OSError:
        return False


def run_command(command):
    try:
        fnull = open(os.devnull, 'w')
        subprocess.Popen(shlex.split(command), stdout=fnull, stderr=sys.stdout)
        return False
    except Exception as e:
        return str(e)


def bool_str_parse(bool_str):
    if bool_str.lower() in ["true", "yes", "y", "1"]:
        return True
    elif bool_str.lower() in ["false", "no", "n", "0"]:
        return False
    else:
        return "Invalid"

def clean_download_dir():
    dir_delcount = 0
    file_delcount = 0
    error_count = 0
    lock_count = 0
    try:
        logger.info('Cleaning up temporary files and folders.')
        if Constants.PYTHON_VER[0] == "2":
            directories = (os.walk(pil.dl_path).next()[1])
            files = (os.walk(pil.dl_path).next()[2])
        else:
            directories = (os.walk(pil.dl_path).__next__()[1])
            files = (os.walk(pil.dl_path).__next__()[2])

        for directory in directories:
            if directory.endswith('_downloads'):
                if not any(filename.endswith('.lock') for filename in
                           os.listdir(os.path.join(pil.dl_path, directory))):
                    try:
                        shutil.rmtree(os.path.join(pil.dl_path, directory))
                        dir_delcount += 1
                    except Exception as e:
                        logger.error("Could not remove folder: {:s}".format(str(e)))
                        error_count += 1
                else:
                    lock_count += 1
        logger.separator()
        for file in files:
            if file.endswith('_downloads.json'):
                if not any(filename.endswith('.lock') for filename in
                           os.listdir(os.path.join(pil.dl_path))):
                    try:
                        os.remove(os.path.join(pil.dl_path, file))
                        file_delcount += 1
                    except Exception as e:
                        logger.error("Could not remove file: {:s}".format(str(e)))
                        error_count += 1
                else:
                    lock_count += 1
        if dir_delcount == 0 and file_delcount == 0 and error_count == 0 and lock_count == 0:
            logger.info('The cleanup has finished. No items were removed.')
            logger.separator()
            return
        logger.info('The cleanup has finished.')
        logger.info('Folders removed:     {:d}'.format(dir_delcount))
        logger.info('Files removed:       {:d}'.format(file_delcount))
        logger.info('Locked items:        {:d}'.format(lock_count))
        logger.info('Errors:              {:d}'.format(error_count))
        logger.separator()
    except KeyboardInterrupt as e:
        logger.separator()
        logger.warn("The cleanup was aborted by the user.")
        if dir_delcount == 0 and file_delcount == 0 and error_count == 0 and lock_count == 0:
            logger.info('No items were removed.')
            logger.separator()
            return
        logger.info('Folders removed:     {:d}'.format(dir_delcount))
        logger.info('Files removed:       {:d}'.format(file_delcount))
        logger.info('Locked items  :      {:d}'.format(lock_count))
        logger.info('Errors:              {:d}'.format(error_count))
        logger.separator()


def show_info():
    session_files = []
    session_from_config = ''
    try:
        for file in os.listdir(os.getcwd()):
            if file.endswith(".dat"):
                session_files.append(file)
            if pil.ig_user == file.replace(".dat", ''):
                session_from_config = file
    except Exception as e:
        logger.warn("Could not list login session files: {:s}".format(str(e)))
        logger.whiteline()
    logger.info("To see all the available arguments, use the -h argument.")
    logger.whiteline()
    logger.info("PyInstaLive version:        {:s}".format(Constants.SCRIPT_VER))
    logger.info("Python version:             {:s}".format(Constants.PYTHON_VER))
    if not command_exists("ffmpeg"):
        logger.error("FFmpeg framework:           Not found")
    else:
        logger.info("FFmpeg framework:           Available")

    if len(session_from_config) > 0:
        logger.info("Login session files:        {:s} ({:s} matches config user)".format(str(len(session_files)),
                                                                                         session_from_config))
    elif len(session_files) > 0:
        logger.info("Login session files:        {:s}".format(str(len(session_files))))
    else:
        logger.warn("Login session files:        None found")

    logger.info("CLI supports color:         {:s}".format("No" if not logger.supports_color() else "Yes"))
    logger.info(
        "Command to run at start:    {:s}".format("None" if not pil.cmd_on_started else pil.cmd_on_started))
    logger.info(
        "Command to run at finish:   {:s}".format("None" if not pil.cmd_on_ended else pil.cmd_on_ended))

    if os.path.exists(pil.config_path):
        logger.info("Config file contents:")
        logger.whiteline()
        with open(pil.config_path) as f:
            for line in f:
                logger.plain("    {:s}".format(line.rstrip()))
    else:
        logger.error("Config file:         Not found")
    logger.whiteline()
    logger.info("End of PyInstaLive information screen.")
    logger.separator()


def check_if_guesting():
    try:

        livestream_guest =  pil.livestream_downloaded_obj.get('cobroadcasters', {})[0].get('username')
    except Exception:
        livestream_guest = None
    if livestream_guest and not pil.has_guest:
        logger.separator()
        pil.has_guest = livestream_guest
        logger.binfo('The livestream host has started guesting with user: {}'.format(pil.has_guest))
    if not livestream_guest and pil.has_guest:
        logger.separator()
        logger.binfo('The livestream host has stopped guesting with user: {}'.format(pil.has_guest))
        if pil.has_guest == pil.dl_user:
            pil.livestream_downloader.stop()
        pil.has_guest = None
        

def get_stream_duration(duration_type):
    try:
        if not pil.livestream_downloaded_obj:
            if duration_type == 0: # Airtime duration
                stream_started_mins, stream_started_secs = divmod((int(time.time()) - pil.initial_livestream_obj.get("broadcast_dict").get("published_time")), 60)
            if duration_type == 1: # Download duration
                stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(pil.epochtime)), 60)
            if duration_type == 2: # Missing duration
                if (int(pil.epochtime) - pil.livestream_downloaded_obj.get("published_time")) <= 0:
                    stream_started_mins, stream_started_secs = 0, 0 # Download started 'earlier' than actual broadcast, assume started at the same time instead
                else:
                    stream_started_mins, stream_started_secs = divmod((int(pil.epochtime) - pil.initial_livestream_obj.get("broadcast_dict").get("published_time")), 60)
        else:
            if duration_type == 0: # Airtime duration
                stream_started_mins, stream_started_secs = divmod((int(time.time()) - pil.livestream_downloaded_obj.get("published_time")), 60)
            if duration_type == 1: # Download duration
                stream_started_mins, stream_started_secs = divmod((int(time.time()) - int(pil.epochtime)), 60)
            if duration_type == 2: # Missing duration
                if (int(pil.epochtime) - pil.livestream_downloaded_obj.get("published_time")) <= 0:
                    stream_started_mins, stream_started_secs = 0, 0 # Download started 'earlier' than actual broadcast, assume started at the same time instead
                else:
                    stream_started_mins, stream_started_secs = divmod((int(pil.epochtime) - pil.livestream_downloaded_obj.get("published_time")), 60)
        if stream_started_mins < 0:
            stream_started_mins = 0
        if stream_started_secs < 0:
            stream_started_secs = 0
        stream_duration_str = '%d minutes' % stream_started_mins
        if stream_started_secs:
            stream_duration_str += ' and %d seconds' % stream_started_secs
        return stream_duration_str
    except Exception:
        return "Not available"

def generate_json_files():
    if not pil.kill_threads:
        try:
            live_json_file = '{}{}_{}_{}_{}_live_downloads.json'.format(pil.dl_path, pil.datetime_compat, pil.dl_user,
                                                        pil.initial_livestream_obj.get('broadcast_id'), pil.epochtime)
            pil.initial_livestream_obj['segments'] = pil.livestream_downloader.segment_meta

            if pil.dl_comments:
                comments_collected = pil.comments
                before_count = len(comments_collected)
                comments_response = pil.ig_api.get(Constants.BROADCAST_COMMENTS_URL.format(pil.initial_livestream_obj.get('broadcast_id'), str(pil.comments_last_ts)))
                comments_json = json.loads(comments_response.text)
                new_comments = comments_json.get("comments", [])
                for i, comment in enumerate(new_comments):
                    elapsed = int(time.time()) - int(pil.epochtime)
                    new_comments[i].update({"total_elapsed": elapsed})
                pil.comments_last_ts = (new_comments[0]['created_at_utc'] if new_comments else int(time.time()))
                comments_collected.extend(new_comments)
                after_count = len(comments_collected)

                if after_count > before_count:
                    pil.initial_livestream_obj['comments'] = comments_collected
                pil.comments = comments_collected
            try:
                with open(live_json_file, 'w') as json_file:
                    json.dump(pil.initial_livestream_obj, json_file, indent=2)
            except Exception as e:
                logger.warn(str(e))
        except Exception as e:
            logger.warn(str(e))

def print_durations(download_ended=False):
        logger.info('Airing time  : {}'.format(get_stream_duration(0)))
        if download_ended:
            logger.info('Downloaded   : {}'.format(get_stream_duration(1)))
            logger.info('Missing      : {}'.format(get_stream_duration(2)))

def print_heartbeat(from_thread=False):
    if not pil.kill_threads:
        if not pil.livestream_downloaded_obj:
            previous_state = pil.initial_livestream_obj.get("broadcast_dict").get("broadcast_status")
        else:
            previous_state = pil.livestream_downloaded_obj.get("broadcast_status")
        heartbeat_response = pil.ig_api.get(Constants.BROADCAST_HEALTH_URL.format(pil.initial_livestream_obj.get('broadcast_id')))
        pil.ig_api.post(Constants.BROADCAST_HEALTH2_URL.format(pil.initial_livestream_obj.get('broadcast_id')))
        response_json = json.loads(heartbeat_response.text)
        pil.livestream_downloaded_obj = response_json
        if from_thread:
            check_if_guesting()
        if not from_thread or (previous_state != pil.livestream_downloaded_obj.get("broadcast_status")):
            if from_thread:
                logger.separator()
                print_durations()
            logger.info('Status       : {}'.format( pil.livestream_downloaded_obj.get("broadcast_status").capitalize()))
            logger.info('Viewers      : {}'.format(int( pil.livestream_downloaded_obj.get("viewer_count"))))
        return pil.livestream_downloaded_obj.get('broadcast_status') not in ['available', 'interrupted']

def do_json_generation():
    while True:
        generate_json_files()
        if pil.kill_threads:
            break
        else:
            time.sleep(2.5)

def do_heartbeat():
    while True:
        print_heartbeat(True)
        if pil.kill_threads:
            break
        else:
            time.sleep(5)

def new_config():
    try:
        if os.path.exists(pil.config_path):
            logger.info("A configuration file is already present:")
            logger.whiteline()
            with open(pil.config_path) as f:
                for line in f:
                    logger.plain("    {:s}".format(line.rstrip()))
            logger.whiteline()
            logger.info("To create a default configuration file, delete the existing file and run PyInstaLive again.")
            logger.separator()
        else:
            try:
                logger.warn("Could not find configuration file, creating a default one.")
                config_file = open(pil.config_path, "w")
                config_file.write(Constants.CONFIG_TEMPLATE.format(os.getcwd()).strip())
                config_file.close()
                logger.info("A new configuration file has been created.")
                logger.separator()
                return
            except Exception as e:
                logger.error("Could not create default configuration file: {:s}".format(str(e)))
                logger.warn("Please manually create one using the following template: ")
                logger.whiteline()
                for line in Constants.CONFIG_TEMPLATE.strip().splitlines():
                    logger.plain("    {:s}".format(line.rstrip()))
                logger.whiteline()
                logger.warn("Save it as 'pyinstalive.ini' and run this script again.")
                logger.separator()
    except Exception as e:
        logger.error("d: {:s}".format(str(e)))
        logger.warn(
            "If you don't have a configuration file, manually create one using the following template:")
        logger.whiteline()
        logger.plain(Constants.CONFIG_TEMPLATE)
        logger.whiteline()
        logger.warn("Save it as 'pyinstalive.ini' and run this script again.")
        logger.separator()


def create_lock_user():
    try:
        if not os.path.isfile(os.path.join(pil.dl_path, pil.dl_user + '.lock')):
            if pil.use_locks:
                open(os.path.join(pil.dl_path, pil.dl_user + '.lock'), 'a').close()
                return True
        else:
            return False
    except Exception:
        logger.warn("Could not create lock file.")
        return True


def create_lock_folder():
    try:
        if not os.path.isfile(os.path.join(pil.live_folder_path, 'folder.lock')):
            if pil.use_locks:
                open(os.path.join(pil.live_folder_path, 'folder.lock'), 'a').close()
                return True
        else:
            return False
    except Exception:
        logger.warn("Could not create lock file.")
        return True


def remove_lock():
    download_folder_lock = os.path.join(pil.dl_path, pil.dl_user + '.lock')
    temp_folder_lock = os.path.join(pil.live_folder_path, 'folder.lock')
    lock_paths = [download_folder_lock, temp_folder_lock]
    for lock in lock_paths:
        try:
            os.remove(lock)
        except Exception:
            pass


def remove_temp_folder():
    try:
        shutil.rmtree(pil.live_folder_path)
    except Exception as e:
        logger.error("Could not remove segment folder: {:s}".format(str(e)))


def download_folder_has_lockfile():
    return os.path.isfile(os.path.join(pil.dl_path, pil.dl_user + '.lock'))

def winbuild_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    elif __file__:
        return None

def generate_log(comments={}, log_file="", gen_from_arg=False):
    try:
        if gen_from_arg:
            with open(pil.gencomments_arg, 'r') as comments_json:
                comments = json.load(comments_json).get("comments", None)
            if comments:
                log_file = os.path.join(
                    pil.dl_path, os.path.basename(pil.gencomments_arg.replace(".json", ".log")))
                logger.info("Generating comments file from input.")
            else:
                logger.warn("The input file does not contain any comments.")
                logger.separator()
                return None
        comments_timeline = {}
        for c in comments:
            if 'offset' in c:
                for k in list(c.get('comment')):
                    c[k] = c.get('comment', {}).get(k)
                c['created_at_utc'] = c.get('offset')
            created_at_utc = str(2 * (c.get('created_at_utc') // 2))
            comment_list = comments_timeline.get(created_at_utc) or []
            comment_list.append(c)
            comments_timeline[created_at_utc] = comment_list

        if comments_timeline:
            comment_errors = 0
            total_comments = 0
            timestamps = sorted(list(comments_timeline))
            subs = []
            for tc in timestamps:
                t = comments_timeline[tc]

                comments_log = ''
                for c in t:
                    try:
                        comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(c.get("total_elapsed"))), '{}: {}'.format(c.get('user', {}).get('username'),c.get('text')))
                    except Exception:
                        comment_errors += 1
                        try:
                            comments_log += '{}{}\n\n'.format(time.strftime('%H:%M:%S\n', time.gmtime(c.get("total_elapsed"))), '{}: {}'.format(c.get('user', {}).get('username'),c.get('text').encode('ascii', 'ignore')))
                        except Exception:
                            pass
                    total_comments += 1
                subs.append(comments_log)

            with codecs.open(log_file, 'w', 'utf-8-sig') as log_outfile:
                log_outfile.write(''.join(subs))
            if gen_from_arg:
                if comment_errors:
                    logger.warn(
                        "Successfully saved {:s} comments. {:s} comments might be (partially) incomplete.".format(
                            str(total_comments), str(comment_errors)))
                else:
                    logger.info("Successfully saved {:s} comments.".format(
                        str(total_comments)))
                logger.separator()
            return comment_errors, total_comments
        else:
            return 0, 0
    except Exception as e:
        logger.error("Could not save comments: {:s}".format(str(e)))
        logger.separator()