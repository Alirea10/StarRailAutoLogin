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
        """
        检查游戏路径是否有效

        Args:
            path (str): 游戏路径
            path_type (str): 游戏类型 ("StarRail", "Starward"等)

        Returns:
            bool: 路径是否有效
        """
        if path_type == "Starward":
            logger.debug("使用 Starward 启动，无需路径校验")
            return True

        if path:
            # 提取文件名并检查是否匹配游戏类型
            filename = path.replace('\\', '/').split('/')[-1].split('.')[0]
            if filename != path_type:
                logger.warning("你尝试输入一个其他应用的路径")
                return False
            else:
                logger.debug(f"游戏路径校验通过{path}，类型为{path_type}")
                return True
        else:
            logger.warning("游戏路径为空")
            return False

    def launch_game(self, game_path, path_type="StarRail"):
        """
        启动游戏程序

        Args:
            game_path (str): 游戏可执行文件路径
            path_type (str): 游戏类型，默认为"StarRail"

        Returns:
            bool: 启动是否成功
        """
        # 检查游戏是否已经启动
        if find_window("崩坏：星穹铁道"):
            logger.info("游戏已经启动")
            return True

        # 启动游戏进程
        if not Popen(game_path):
            logger.error("启动失败")
            return False

        logger.info("等待游戏启动")
        time.sleep(2)

        # 等待游戏窗口出现（最多等待20秒）
        times = 0
        while True:
            if find_window("崩坏：星穹铁道") and check("res/img/12+.png", interval=0.5, max_time=20):
                logger.info("启动成功")
                return True
            else:
                time.sleep(0.5)
                times += 1
                if times == 40:  # 40 * 0.5 = 20秒
                    logger.error("启动时间过长，请尝试手动启动")
                    return False

    @staticmethod
    def launch_Starward(channel):
        """
        使用Starward启动游戏

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)

        Returns:
            bool: 启动是否成功
        """
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
        """
        检查游戏窗口状态和分辨率兼容性

        Returns:
            bool: 检查是否通过
        """
        window_title = "崩坏：星穹铁道"

        # 检查游戏窗口是否存在
        if not WindowsProcess.check_window(window_title):
            logger.warning(f"未找到窗口: {window_title} 或许你还没有运行游戏")
            return False

        # 检查游戏分辨率
        resolution = SRAOperator.resolution_detect()
        if resolution[1] / resolution[0] != 9 / 16:
            logger.warning("检测到游戏分辨率不为16:9, 自动登录可能无法按预期运行")

        return True

    def _launch_game_by_type(self, game_path, path_type, channel=0):
        """
        根据启动类型启动游戏

        Args:
            game_path (str): 游戏路径
            path_type (str): 启动类型 ("StarRail", "launcher", "Starward")
            channel (int): 服务器渠道 (0: 官服, 1: B服)

        Returns:
            bool: 启动是否成功
        """
        if find_window("崩坏：星穹铁道"):
            logger.info("游戏已经启动")
            return True

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
        else:
            logger.info("游戏已经启动")

        return True

    def _handle_login_process(self, channel, account, password):
        """
        处理登录流程

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)
            account (str): 账号
            password (str): 密码

        Returns:
            bool: 登录是否成功，True表示可以继续后续流程
        """
        if channel == 0:
            # 官服登录处理
            login_result = self.login_official(account, password)
            match login_result:
                case 0:
                    logger.warning("登录失败")
                    return False
                case 1 | 2:
                    logger.info("登录成功")
                    return True
                case 3:
                    logger.info("已进入游戏")
                    return True  # 直接返回True，跳过后续等待流程
                case _:
                    logger.error("未知登录状态")
                    return False

        elif channel == 1:
            # B服登录处理
            self.login_bilibili(account, password)
            if check("res/img/quit.png"):
                self.start_game_click()
                return True
            else:
                logger.warning("加载时间过长，请重试")
                return False
        else:
            logger.error(f"不支持的渠道: {channel}")
            return False

    def start_game(self, game_path, path_type, channel=0, login_flag=False, account="", password=""):
        """
        启动游戏的主流程

        Args:
            game_path (str): 游戏路径
            path_type (str): 启动类型
            channel (int): 服务器渠道
            login_flag (bool): 是否需要登录
            account (str): 账号
            password (str): 密码

        Returns:
            bool: 整个流程是否成功
        """
        logger.info("开始启动游戏流程")

        # 步骤1: 启动游戏
        if not self._launch_game_by_type(game_path, path_type, channel):
            return False

        # 步骤2: 处理登录（如果需要）
        if login_flag:
            logger.info("开始登录流程")
            if not self._handle_login_process(channel, account, password):
                return False

        # 步骤4: 等待游戏完全加载
        logger.info("等待游戏加载完成")
        return self.wait_game_load()

    def _detect_login_state(self, channel):
        """
        检测当前登录状态

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)

        Returns:
            int: 登录状态码
                官服: 0-未登录, 1-遇到用户协议, 2-已登录, 3-已进入游戏
                B服: 0-未登录, 1-遇到用户协议, 2-已登录, 3-已进入游戏
        """
        if channel == 0:
            # 官服登录状态检测
            result = check_any(
                ["res/img/login_page.png", "res/img/agree3.png", "res/img/quit.png", "res/img/chat_enter.png"],
                0.5,100)
            if result == 1:
                logger.info("检测到用户协议，同意中...")
                # 先check再click用户协议
                if check("res/img/agree3.png", interval=0.5, max_time=5):
                    if not click("res/img/agree3.png"):
                        logger.error("无法点击用户协议按钮")
                        return self._detect_login_state(channel)
                else:
                    logger.error("用户协议按钮已消失")
                    return 0
        else:
            # B服登录状态检测
            result = check_any(
                ["res/img/bilibili_login_page.png", "res/img/bilibili_agree3.png","res/img/quit.png", "res/img/chat_enter.png"],
                0.5,100)
            if result == 1:
                logger.info("检测到用户协议，同意中...")
                # 先check再click用户协议
                if check("res/img/bilibili_agree3.png", interval=0.5, max_time=5):
                    if not click("res/img/bilibili_agree3.png"):
                        logger.error("无法点击B服用户协议按钮")
                        return 0
                    result = 2
                else:
                    logger.error("B服用户协议按钮已消失")
                    return 0

        logger.info(f"检测到登录状态: {result}")
        return result

    @staticmethod
    def _check_resolution_compatibility():
        """
        检查游戏分辨率是否兼容
        """
        resolution = SRAOperator.resolution_detect()
        if resolution[1] / resolution[0] != 9 / 16:
            logger.warning("检测到游戏分辨率不为16:9, 自动登录可能无法按预期运行")

    def _handle_logout_process(self, channel):
        """
        处理登出流程

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)
        """
        logger.debug("开始登出流程")

        if check("res/img/logout.png", interval=0.5, max_time=30):
            click("res/img/logout.png")

        time.sleep(0.1)

        if channel == 0:
            # 官服登出流程
            if check("res/img/quit2.png", interval=0.5, max_time=5):
                if not click("res/img/quit2.png"):
                    logger.error("无法点击官服退出按钮")
                    return
            else:
                logger.error("官服退出按钮未找到")
                return

            time.sleep(0.1)

            if check("res/img/login_other.png", interval=0.5, max_time=5):
                if not click("res/img/login_other.png"):
                    logger.error("无法点击官服其他登录按钮")
            else:
                logger.error("官服其他登录按钮未找到")
        else:
            # B服登出流程
            if check("res/img/enter.png", interval=0.5, max_time=5):
                if not click("res/img/enter.png"):
                    logger.error("无法点击B服进入按钮")
                    return
            else:
                logger.error("B服进入按钮未找到")
                return

            time.sleep(0.5)

            if check("res/img/bilibili_login_other.png", interval=0.5, max_time=5):
                if not click("res/img/bilibili_login_other.png"):
                    logger.error("无法点击B服其他登录按钮")
            else:
                logger.error("B服其他登录按钮未找到")

    def _perform_account_login(self, channel, account, password):
        """
        执行账号密码登录

        Args:
            channel (int): 服务器渠道
            account (str): 账号
            password (str): 密码

        Returns:
            bool: 登录是否成功
        """
        if channel == 0:
            # 官服登录流程
            if check("res/img/login_with_account.png", interval=0.5, max_time=10):
                if not click("res/img/login_with_account.png"):
                    logger.error("发生错误，无法点击登录其他账号按钮，可能有未适配的界面")
                    return False
            else:
                logger.error("未找到官服登录其他账号按钮")
                return False

            logger.info("登录到" + account)

        else:
            # B服登录流程
            if check("res/img/bilibili_login_with_account.png", interval=0.5, max_time=10):
                if not click("res/img/bilibili_login_with_account.png"):
                    logger.error("发生错误，无法点击B服登录其他账号按钮，可能有未适配的界面")
                    return False
            else:
                logger.error("未找到B服登录其他账号按钮")
                return False

            logger.info("尝试登录到" + account[:3] + "****" + account[-2:])

            # B服需要先点击账号输入框
            if check("res/img/bilibili_account.png", interval=0.2, max_time=20):
                if not click("res/img/bilibili_account.png"):
                    logger.error("无法点击B服账号输入框")
                    return False

        return self._input_credentials(channel, account, password)

    def _input_credentials(self, channel, account, password):
        """
        输入登录凭据

        Args:
            channel (int): 服务器渠道
            account (str): 账号
            password (str): 密码

        Returns:
            bool: 输入是否成功
        """
        time.sleep(1)

        # 输入账号
        SRAOperator.copy(account)
        SRAOperator.paste()
        time.sleep(1)

        # 切换到密码框
        press_key("tab")
        time.sleep(0.2)

        # 输入密码
        SRAOperator.copy(password)
        SRAOperator.paste()

        # 处理登录时的用户协议同意
        if channel == 0:
            # 官服登录流程
            if check("res/img/agree.png", interval=0.5, max_time=5):
                if not click("res/img/agree.png", -158):
                    logger.error("无法点击官服用户协议同意按钮")
                    return False
            else:
                logger.error("官服用户协议同意按钮未找到")
                return False

            if check("res/img/enter_game.png", interval=0.5, max_time=5):
                return click("res/img/enter_game.png")
            else:
                logger.error("官服进入游戏按钮未找到")
                return False
        else:
            # B服登录流程
            if check("res/img/bilibili_agree2.png", interval=0.5, max_time=5):
                if not click("res/img/bilibili_agree2.png", -26):
                    logger.error("无法点击B服用户协议同意按钮")
                    return False

            if check("res/img/bilibili_enter_game.png", interval=0.5, max_time=5):
                if not click("res/img/bilibili_enter_game.png"):
                    logger.error("无法点击B服进入游戏按钮")
                    return False
            else:
                logger.error("B服进入游戏按钮未找到")
                return False

            return True

    def _wait_for_login_result(self, channel):
        """
        等待登录结果

        Args:
            channel (int): 服务器渠道

        Returns:
            int: 登录结果状态
        """

        if channel == 1:
            result =check_any(["res/img/welcome.png","res/img/bilibili_verify.png"], interval=0.2, max_time=20)
            # B服验证码处理
            if result==0:
                logger.info("登录成功")
                return 1
            else:
                return self._handle_bilibili_verification()
        else:
            logger.warning("长时间未成功登录，可能密码错误或需要新设备验证")
            return 0

    def _handle_bilibili_verification(self):
        """
        处理B站验证码

        Returns:
            int: 验证结果 (1: 成功, 0: 失败)
        """
        logger.warning("遇到b站验证码！请手动完成！")

        for wait_time in range(10):
            logger.warning(f"请手动完成b站验证码!剩余{10 - wait_time}秒")
            time.sleep(1)
            if check("res/img/welcome.png", interval=0.2, max_time=1):
                logger.info("登录成功")
                return 1

        logger.error("验证码超时，登录失败")
        return 0

    @staticmethod
    def login_official(account, password):
        """
        官服登录主流程

        Args:
            account (str): 账号
            password (str): 密码

        Returns:
            int: 登录状态码
        """
        logger.info("官服登录中")
        login_instance = Login("", "")  # 临时实例用于调用实例方法

        # 检测登录状态
        result = login_instance._detect_login_state(0)
        login_instance._check_resolution_compatibility()

        # 如果已经在游戏中，直接返回
        if result is not None and result == 3:
            return 3
        # 如果已经登录，先登出
        if result == 1:
            login_instance._handle_logout_process(0)
        else:
            # 先check再click其他登录方式
            if check("res/img/login_other.png", interval=0.5, max_time=5):
                if not click("res/img/login_other.png"):
                    logger.error("无法点击官服其他登录方式按钮")
                    return 0
            else:
                logger.error("官服其他登录方式按钮未找到")
                return 0

        # 执行登录流程
        if not login_instance._perform_account_login(0, account, password):
            logger.error("发生错误，找不到登录按钮，请检查页面是否有更新或用户协议是否已同意")
            return 0

        # 等待登录结果
        return login_instance._wait_for_login_result(0)

    @staticmethod
    def login_bilibili(account, password):
        """
        B服登录主流程

        Args:
            account (str): 账号
            password (str): 密码

        Returns:
            int: 登录状态码
        """
        logger.info("B服登录中")
        login_instance = Login("", "")  # 临时实例用于调用实例方法

        # 检测登录状态
        result = login_instance._detect_login_state(1)
        login_instance._check_resolution_compatibility()

        # 如果已经在游戏中，直接返回
        if result is not None and result == 3:
            return result

        # 处理已登录或用户协议情况
        if result == 2:
            login_instance._handle_logout_process(1)
        else:
            # 先check再click其他登录方式
            if check("res/img/bilibili_login_other.png", interval=0.5, max_time=5):
                if not click("res/img/bilibili_login_other.png"):
                    logger.error("无法点击B服其他登录方式按钮")
                    return 0
            else:
                logger.error("B服其他登录方式按钮未找到")
                return 0

        # 执行登录流程
        if not login_instance._perform_account_login(1, account, password):
            return 0

        # 等待登录结果
        return login_instance._wait_for_login_result(1)

    @staticmethod
    def start_game_click():
        """
        处理游戏启动时的点击操作
        检查是否处于登录页并登录
        """
        x, y = SRAOperator.get_screen_center()

        # 检查是否处于登录页(以12+标志为准)
        if SRAOperator.exist("res/img/12+.png"):
            click_point(x, y)
            time.sleep(3)

        logger.info("开始游戏")

        # 检查并点击退出按钮进入游戏
        if check("res/img/quit.png", interval=0.5):
            click_point(x, y)

    @staticmethod
    def wait_game_load():
        """
        等待游戏完全加载到大世界

        Returns:
            bool: 是否成功进入大世界
        """
        times = 0

        while True:
            # 处理月卡界面
            if click("res/img/train_supply.png"):
                time.sleep(4)
                # 向下移动鼠标并点击（领取月卡）
                SRAOperator.moveRel(0, +400)
                click()

            # 检查是否已进入大世界（聊天框或手机图标）
            res = SRAOperator.existAny(["res/img/chat_enter.png", "res/img/phone.png"])
            if res is not None:
                return True
            else:
                times += 1
                if times == 50:  # 50秒超时
                    logger.error("发生错误，可能进入游戏但未处于大世界")
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
    logger.debug(f"加载配置文件: {config_path}，使用第 {config_id} 配置")
    with open(config_path, "r", encoding="utf-8") as f:
        all_config = json.load(f)

    if config_id not in all_config:
        logger.error(f"未找到 id={config_id} 的配置，请检查 config.json")
        sys.exit(1)
    config = all_config[config_id]

    login = Login(
        game_path=config["game_path"],
        game_type=config["game_type"],
        enable_login=config.get("enable_login", False),
        server=config.get("server"),
        username=config.get("username"),
        password=config.get("password")
    )

    # 0 - 正在启动
    # 1 - 同意用户协议
    # 2.1 - 已登录,是正确的游戏账号登录
    # 2.2 - 已登录,但不是正确的账号,进行登出再登录
    # 2.3 - 未登录,进行登录

    # 串行任务执行 - 简化版
    if (login.path_check(login.game_path, login.game_type) and
        login.start_game(login.game_path, login.game_type, int(login.server), login.enable_login, login.username, login.password) and
        login.check_game()):
        logger.success("我滴任务，完成啦！")
    else:
        logger.warning("任务执行失败，终止后续操作")

    # 你真的需要它吗？它为什么在这里？我不知道，你得和一闪而过的控制台说去
    # input("按回车键退出...")
