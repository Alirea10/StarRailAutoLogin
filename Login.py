import os
import sys
import ctypes
import json
import time
import webbrowser
import winreg

from SRACore.utils import WindowsProcess
from SRACore.utils.WindowsProcess import find_window, Popen
from SRACore.utils.Logger import logger
from SRACore.utils.SRAOperator import SRAOperator

# 工具函数
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    if not is_admin():
        logger.info("尝试以管理员权限重启")
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1)
        sys.exit()

def check_any(img_list: list, interval=0.5, max_time=40):
    return SRAOperator.checkAny(img_list, interval, max_time)

def click(*args, **kwargs) -> bool:
    return SRAOperator.click_img(*args, **kwargs)

def click_point(x: int = None, y: int = None) -> bool:
    return SRAOperator.click_point(x, y)

def press_key(key: str, presses: int = 1, interval: float = 2, wait: float = 0) -> bool:
    return SRAOperator.press_key(key, presses, interval, wait)

def check(img_path, interval=0.5, max_time=40):
    return SRAOperator.check(img_path, interval, max_time)

def write(content: str = "") -> bool:
    return SRAOperator.write(content)
# 检查Starward是否安装并注册了URL协议
def check_starward_URL(scheme) -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, scheme)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


class Login:
    def __init__(self, game_path, game_type, enable_login=False, server=None, username=None, password=None):
        self.game_path = game_path
        self.game_type = game_type
        self.enable_login = enable_login
        self.username = username
        self.password = password
        self.server = server

    @staticmethod
    def path_check(path, path_type="StarRail"):
        if path:
            if path.replace('\\', '/').split('/')[-1].split('.')[0] != path_type:
                logger.warning("你尝试输入一个其他应用的路径")
                return False
            else:
                logger.debug(f"游戏路径校验通过{path}，类型为{path_type}")
                return True
        else:
            logger.warning("游戏路径为空")
            return False

    def launch_game(self, game_path, path_type="StarRail"):
        if find_window("崩坏：星穹铁道"):
            logger.info("游戏已经启动")
            return True
        if not self.path_check(game_path, path_type):
            logger.error("路径无效")
            return False
        if not Popen(game_path):
            logger.error("启动失败")
            return False
        logger.info("等待游戏启动")
        time.sleep(2)
        times = 0
        while True:
            if find_window("崩坏：星穹铁道"):
                logger.info("启动成功")
                return True
            else:
                time.sleep(0.5)
                times += 1
                if times == 40:
                    logger.error("启动时间过长，请尝试手动启动")
                    return False

    @staticmethod
    def launch_Starward(channel):
        if check_starward_URL:
            logger.info("准备启动游戏")
            if channel == 0:
                url = "starward://startgame/hkrpg_cn"
                webbrowser.open(url)
                return True
            elif channel == 1:
                url = "starward://startgame/hkrpg_bilibili"
                webbrowser.open(url)
                return True
            else:
                logger.error("暂不支持除了官服b服以外的其他渠道")
                return False
        else:
            logger.error("尚未启动Starward的URL协议，请打开Starward→设置→高级→URL协议 启动url协议")
            return False

    @staticmethod
    def check_game():
        window_title = "崩坏：星穹铁道"
        if not WindowsProcess.check_window(window_title):
            logger.warning(f"未找到窗口: {window_title} 或许你还没有运行游戏")
            return False
        resolution = SRAOperator.resolution_detect()
        if resolution[1] / resolution[0] != 9 / 16:
            logger.warning("检测到游戏分辨率不为16:9, 自动登录可能无法按预期运行")
        return True

    def start_game(self, game_path, path_type, channel=0, login_flag=False, account="", password=""):
        if path_type == "StarRail":
            if not self.launch_game(game_path, path_type):
                logger.warning("游戏启动失败")
                return False
        elif path_type == "launcher":
            logger.warning("暂未实现 launcher 启动")
            return False
        elif path_type == "Starward":
            logger.info("使用 Starward 启动")
            if not self.launch_Starward(channel):
                logger.warning("Starward 启动失败")
                return False

        # 打开游戏后进行登录
        if channel == 0:
            if login_flag:
                match self.login_official(account, password):
                    case 0:
                        logger.warning("登录失败")
                        return False
                    case 1 | 2:
                        logger.info("登录成功")
                    case 3:
                        logger.info("已进入游戏")
                        return True
                    case _:
                        logger.error("未知登录状态")
                        return False
            time.sleep(3)
            result = check_any(["res/img/quit.png","res/img/enter_game.png"], interval=0.5, max_time=30)
            if result==0:
                self.start_game_click()
            elif result==1:
                click("res/img/enter_game.png")
                self.start_game_click()
        elif channel == 1:
            self.login_bilibili(account, password)
            if check("res/img/quit.png"):
                self.start_game_click()
            else:
                logger.warning("加载时间过长，请重试")
                return False
        return self.wait_game_load()

    @staticmethod
    def login_official(account, password):
        logger.info("登录中")
        time.sleep(3)
        result = check_any(
            # 分别对应登录状态 0: 未登录, 1: 已有登录, 2: 已有登录, 3: 已进入游戏
            ["res/img/login_page.png", "res/img/welcome.png", "res/img/quit.png", "res/img/chat_enter.png"])

        logger.info(f"登录状态 {result}")
        resolution = SRAOperator.resolution_detect()
        if resolution[1] / resolution[0] != 9 / 16:
            logger.warning("检测到游戏分辨率不为16:9, 自动登录可能无法按预期运行")

        if result is not None and result == 3:
            return result
        # 若已经登录，则退出登录
        elif result == 1 or result == 2:
            # 等火车头...
            if check("res/img/logout.png",interval=0.5, max_time=30):
                click("res/img/logout.png")
            time.sleep(0.1)
            click("res/img/quit2.png")
            time.sleep(0.1)
            click("res/img/login_other.png")
        else:
            click("res/img/login_other.png")
        if not click("res/img/login_with_account.png"):
            logger.error("发生错误，错误编号10")
            return 0
        logger.info("登录到" + account)
        time.sleep(1)
        SRAOperator.copy(account)
        SRAOperator.paste()
        time.sleep(1)
        press_key("tab")
        time.sleep(0.2)
        SRAOperator.copy(password)
        SRAOperator.paste()
        click("res/img/agree.png", -158)
        if not click("res/img/enter_game.png"):
            logger.error("发生错误，错误编号9")
            return 0
        if check("res/img/welcome.png", interval=0.2, max_time=20):
            logger.info("登录成功")
            return 1
        else:
            logger.warning("长时间未成功登录，可能密码错误或需要新设备验证")
            return 0

    @staticmethod
    def login_bilibili(account, password):
        if not check("res/img/bilibili_login.png", interval=0.2, max_time=20):
            logger.error("检测超时，编号3")
            return False
        if click('res/img/bilibili_account.png'):
            logger.info("登录到" + account)
            time.sleep(0.5)
            write(account)
        if click('res/img/bilibili_pwd.png'):
            time.sleep(0.5)
            write(password)
        click('res/img/bilibili_remember.png')
        click("res/img/bilibili_read.png", x_add=-30)
        click("res/img/bilibili_login.png")
        return True

    @staticmethod
    def start_game_click():
        x, y = SRAOperator.get_screen_center()
        if SRAOperator.exist("res/img/12+.png"):
            click_point(x, y)
            time.sleep(3)
        logger.info("开始游戏")
        if check("res/img/quit.png", interval=0.5):
            click_point(x, y)

    @staticmethod
    def wait_game_load():
        times = 0
        while True:
            if click("res/img/train_supply.png"):
                time.sleep(4)
                SRAOperator.moveRel(0, +400)
                click()
            res = SRAOperator.existAny(["res/img/chat_enter.png", "res/img/phone.png"])
            if res is not None:
                return True
            else:
                times += 1
                if times == 50:
                    logger.error("发生错误，进入游戏但未处于大世界")
                    return False
            time.sleep(1)



# 主程序入口
if __name__ == "__main__":
    logger.info("程序开始")
    if is_admin():
        logger.info("以管理员权限运行")
    else:
        logger.error("请以管理员权限运行本程序")
        run_as_admin()

    # 读取 id 参数
    if len(sys.argv) < 2:
        logger.warning("未给定参数 id，默认为1，请给定参数设置例如: python Login.py 1")
    config_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    # 如果没有给定参数，默认使用第一个配置
    config_path = os.path.join(os.path.dirname(__file__), "config/config.json")
    logger.info(f"加载配置文件: {config_path}，使用第 {config_id} 配置")
    with open(config_path, "r", encoding="utf-8") as f:
        all_config = json.load(f)

    if config_id not in all_config:
        logger.error(f"未找到 id={config_id} 的配置，请检查 config.json")
        sys.exit(1)
    config = all_config[config_id]
    logger.debug(f"配置内容：{config}")

    login = Login(
        game_path=config["game_path"],
        game_type=config["game_type"],
        enable_login=config.get("enable_login", False),
        server=config.get("server"),
        username=config.get("username"),
        password=config.get("password")
)

    # 串行任务队列
    tasks = [
        (login.path_check, (login.game_path, login.game_type)),
        (login.start_game, (login.game_path, login.game_type, int(login.server), login.enable_login, login.username, login.password)),
        (login.check_game, ()),
    ]
    for func, args in tasks:
        result = func(*args)
        if not result:
            logger.warning(f"任务 {func.__name__} 失败，终止后续操作")
            break
    else:
        logger.info("我滴任务，完成啦！")

    # 你真的需要它吗？它为什么在这里？我不知道，你得和一闪而过的控制台说去
    # input("按回车键退出...")