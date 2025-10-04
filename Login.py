import os
import sys
import ctypes
import json
import time
import webbrowser
import winreg

from SRACore.utils import WindowsProcess
from SRACore.utils.WindowsProcess import find_window, Popen
from SRACore.utils.Logger import logger, Level
from SRACore.utils.SRAOperator import SRAOperator


def set_log_level(level_str: str = "INFO"):
    """
    设置日志等级

    Args:
        level_str (str): 日志等级字符串，可选值: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, EXCEPTION
    """
    try:
        # 验证日志等级是否有效
        log_level = Level(level_str.upper())

        # 设置所有控制台处理器的日志等级
        for handler in logger.handlers:
            if hasattr(handler, 'console'):  # 控制台处理器
                handler.set_level(log_level)

        logger.info(f"日志等级已设置为: {log_level.value}")
        logger.debug(f"[set_log_level] 日志等级设置成功: {log_level.value}")

    except ValueError:
        logger.warning(f"无效的日志等级: {level_str}，使用默认等级 INFO")
        logger.debug(f"[set_log_level] 日志等级设置失败，使用默认值")
        # 设置为默认的INFO等级
        for handler in logger.handlers:
            if hasattr(handler, 'console'):
                handler.set_level(Level.INFO)


# 工具函数
def is_admin():
    logger.debug("[is_admin] 开始检查管理员权限")
    try:
        result = ctypes.windll.shell32.IsUserAnAdmin()
        logger.debug(f"[is_admin] 管理员权限检查结果: {result}")
        return result
    except Exception as e:
        logger.debug(f"[is_admin] 管理员权限检查异常: {e}")
        return False


def run_as_admin():
    logger.debug("[run_as_admin] 开始以管理员权限重启程序")
    if not is_admin():
        logger.info("尝试以管理员权限重启")
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        logger.debug(f"[run_as_admin] 重启参数: {params}")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1)
        logger.debug("[run_as_admin] 已发起管理员权限重启请求")
        sys.exit()
    else:
        logger.debug("[run_as_admin] 已具有管理员权限，无需重启")


def check_any(img_list: list, interval=0.5, max_time=40):
    logger.debug(f"[check_any] 开始检查图像列表: {img_list}, 间隔: {interval}s, 最大时间: {max_time}s")
    result = SRAOperator.checkAny(img_list, interval, max_time)
    logger.debug(f"[check_any] 检查结果: {result}")
    return result


def click(*args, **kwargs) -> bool:
    logger.debug(f"[click] 开始点击图像, 参数: {args}, 关键字参数: {kwargs}")
    result = SRAOperator.click_img(*args, **kwargs)
    logger.debug(f"[click] 点击结果: {result}")
    return result


def click_point(x: int = None, y: int = None) -> bool:
    logger.debug(f"[click_point] 开始点击坐标 ({x}, {y})")
    result = SRAOperator.click_point(x, y)
    logger.debug(f"[click_point] 点击结果: {result}")
    return result


def press_key(key: str, presses: int = 1, interval: float = 2, wait: float = 0) -> bool:
    logger.debug(f"[press_key] 开始按键操作: {key}, 次数: {presses}, 间隔: {interval}s, 等待: {wait}s")
    result = SRAOperator.press_key(key, presses, interval, wait)
    logger.debug(f"[press_key] 按键操作结果: {result}")
    return result


def exist(img_path, wait_time=0.3):
    logger.debug(f"[exist] 开始检查图像是否存在: {img_path}")
    result = SRAOperator.exist(img_path, wait_time)
    logger.debug(f"[exist] 检查结果: {result}")
    return result


def check(img_path, interval=0.5, max_time=40):
    logger.debug(f"[check] 开始检查图像: {img_path}, 间隔: {interval}s, 最大时间: {max_time}s")
    result = SRAOperator.check(img_path, interval, max_time)
    logger.debug(f"[check] 检查结果: {result}")
    return result


def write(content: str = "") -> bool:
    logger.debug(f"[write] 开始写入内容: {content[:20]}...")
    result = SRAOperator.write(content)
    logger.debug(f"[write] 写入结果: {result}")
    return result


# 检查Starward是否安装并注册了URL协议
def check_starward_URL(scheme) -> bool:
    logger.debug(f"[check_starward_URL] 开始检查Starward URL协议: {scheme}")
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, scheme)
        winreg.CloseKey(key)
        logger.debug(f"[check_starward_URL] URL协议检查成功: {scheme}")
        return True
    except FileNotFoundError:
        logger.debug(f"[check_starward_URL] URL协议未找到: {scheme}")
        return False


class Login:
    def __init__(self, game_path, game_type, enable_login=False, server=None, username=None, password=None):
        logger.debug(
            f"[Login.__init__] 初始化Login实例, 游戏路径: {game_path}, 游戏类型: {game_type}, 启用登录: {enable_login}, 服务器: {server}")
        self.game_path = game_path
        self.game_type = game_type
        self.enable_login = enable_login
        self.username = username
        self.password = password
        self.server = server
        logger.debug("[Login.__init__] Login实例初始化完成")

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
        logger.debug(f"[path_check] 开始检查游戏路径: {path}, 类型: {path_type}")

        if path_type == "Starward":
            logger.debug("使用 Starward 启动，无需路径校验")
            logger.debug("[path_check] Starward路径校验通过")
            return True

        if path:
            # 提取文件名并检查是否匹配游戏类型
            filename = path.replace('\\', '/').split('/')[-1].split('.')[0]
            logger.debug(f"[path_check] 提取的文件名: {filename}")

            if filename != path_type:
                logger.warning("你尝试输入一个其他应用的路径")
                logger.debug(f"[path_check] 路径校验失败: 文件名({filename}) != 游戏类型({path_type})")
                return False
            else:
                logger.debug(f"游戏路径校验通过{path}，类型为{path_type}")
                logger.debug("[path_check] 路径校验成功")
                return True
        else:
            logger.warning("游戏路径为空")
            logger.debug("[path_check] 路径校验失败: 路径为空")
            return False

    @staticmethod
    def _wait_for_game_startup():
        """
        等待游戏窗口出现并检查启动是否成功

        Returns:
            bool: 游戏是否成功启动
        """
        logger.debug("[_wait_for_game_startup] 开始等待游戏启动")

        # 直接使用 check 方法等待 12+ 图标出现，该方法内部已经有循环逻辑
        # 12+ 图标出现意味着游戏已经启动并且窗口已经存在
        if check("res/img/12+.png", interval=1, max_time=60):
            logger.info("启动成功")
            logger.debug("[_wait_for_game_startup] 游戏启动成功")
            return True
        else:
            logger.error("启动时间过长，请尝试手动启动")
            logger.debug("[_wait_for_game_startup] 启动超时，未检测到12+图标")
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
        logger.debug(f"[launch_game] 开始启动游戏: {game_path}, 类型: {path_type}")
        # TODO 游戏已经启动还得检查是不是已经登进游戏里面了
        # 检查游戏是否已经启动
        if find_window("崩坏：星穹铁道"):
            logger.info("游戏已经启动")
            logger.debug("[launch_game] 检测到游戏已启动")
            return True

        # 启动游戏进程
        logger.debug("[launch_game] 尝试启动游戏进程")
        if not Popen(game_path):
            logger.error("启动失败")
            logger.debug("[launch_game] 游戏进程启动失败")
            return False

        logger.info("等待游戏启动")
        logger.debug("[launch_game] 游戏进程已启动，等待2秒后检查启动状态")
        time.sleep(2)

        result = self._wait_for_game_startup()
        logger.debug(f"[launch_game] 游戏启动结果: {result}")
        return result

    @staticmethod
    def launch_Starward(channel):
        """
        使用Starward启动游戏

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)

        Returns:
            bool: 启动是否成功
        """
        logger.debug(f"[launch_Starward] 开始使用Starward启动游戏, 渠道: {channel}")

        if check_starward_URL:
            logger.info("准备启动游戏")
            if channel == 0:
                url = "starward://startgame/hkrpg_cn"
                logger.debug(f"[launch_Starward] 官服启动URL: {url}")
                webbrowser.open(url)
            elif channel == 1:
                url = "starward://startgame/hkrpg_bilibili"
                logger.debug(f"[launch_Starward] B服启动URL: {url}")
                webbrowser.open(url)
            else:
                logger.error("暂不支持除了官服b服以外的其他渠道")
                logger.debug(f"[launch_Starward] 不支持的渠道: {channel}")
                return False

            logger.debug("[launch_Starward] URL已发送，等待游戏启动")
            result = Login._wait_for_game_startup()
            logger.debug(f"[launch_Starward] Starward启动结果: {result}")
            return result
        else:
            logger.error("尚未启动Starward的URL协议，请打开Starward→设置→高级→URL协议 启动url协议")
            logger.debug("[launch_Starward] Starward URL协议未启用")
            return False

    @staticmethod
    def check_game():
        """
        检查游戏窗口状态和分辨率兼容性

        Returns:
            bool: 检查是否通过
        """
        logger.debug("[check_game] 开始检查游戏窗口状态")
        window_title = "崩坏：星穹铁道"

        # 检查游戏窗口是否存在
        logger.debug(f"[check_game] 检查窗口是否存在: {window_title}")
        if not WindowsProcess.check_window(window_title):
            logger.warning(f"未找到窗口: {window_title} 或许你还没有运行游戏")
            logger.debug("[check_game] 游戏窗口未找到")
            return False

        # 检查游戏分辨率
        logger.debug("[check_game] 检查游戏分辨率")
        resolution = SRAOperator.resolution_detect()
        logger.debug(f"[check_game] 检测到分辨率: {resolution}")

        if resolution[1] / resolution[0] != 9 / 16:
            logger.warning("检测到游戏分辨率不为16:9, 自动登录可能无法按预期运行")
            logger.debug(f"[check_game] 分辨率不兼容，当前比例: {resolution[1] / resolution[0]}")

        logger.debug("[check_game] 游戏检查完成")
        return True

    def _launch_game_by_type(self, game_path, path_type, channel):
        """
        根据启动类型启动游戏

        Args:
            game_path (str): 游戏路径
            path_type (str): 启动类型 ("StarRail", "Starward")
            channel (int): 服务器渠道 (0: 官服, 1: B服)

        Returns:
            bool: 启动是否成功
        """
        logger.debug(f"[_launch_game_by_type] 开始根据类型启动游戏: 路径={game_path}, 类型={path_type}, 渠道={channel}")

        if find_window("崩坏：星穹铁道"):
            logger.info("游戏已经启动")
            logger.debug("[_launch_game_by_type] 检测到游戏已启动")
            return True

        if path_type == "StarRail":
            logger.debug("[_launch_game_by_type] 使用StarRail方式启动")
            if not self.launch_game(game_path, path_type):
                logger.warning("游戏启动失败")
                logger.debug("[_launch_game_by_type] StarRail启动失败")
                return False
            logger.debug("[_launch_game_by_type] StarRail启动成功")
            return True  # StarRail 启动成功
        elif path_type == "Starward":
            logger.info("使用 Starward 启动")
            logger.debug("[_launch_game_by_type] 使用Starward方式启动")
            if not self.launch_Starward(channel):
                logger.warning("Starward 启动失败")
                logger.debug("[_launch_game_by_type] Starward启动失败")
                return False
            logger.debug("[_launch_game_by_type] Starward启动成功")
            return True  # Starward 启动成功
        else:
            logger.info("非法参数，请检查启动类型")
            logger.debug(f"[_launch_game_by_type] 非法启动类型: {path_type}")
            return False

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
        logger.debug(
            f"[_handle_login_process] 开始处理登录流程: 渠道={channel}, 账号={account[:3]}***{account[-2:] if len(account) > 5 else '***'}")

        if channel == 0:
            # 官服登录处理
            logger.debug("[_handle_login_process] 处理官服登录")
            result = self.login_official(account, password)
            logger.debug(f"[_handle_login_process] 官服登录结果: {result}")
            return result

        elif channel == 1:
            # B服登录处理
            logger.debug("[_handle_login_process] 处理B服登录")
            self.login_bilibili(account, password)
            if check("res/img/quit.png"):
                # 移除对不存在的start_game_click方法的调用
                logger.debug("[_handle_login_process] B服登录成功，检测到quit.png")
                return True
            else:
                logger.warning("加载时间过长，请重试")
                logger.debug("[_handle_login_process] B服登录失败，未检测到quit.png")
                return False
        else:
            logger.error(f"不支持的渠道: {channel}")
            logger.debug(f"[_handle_login_process] 不支持的渠道: {channel}")
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
        logger.debug(f"[start_game] 启动参数: 路径={game_path}, 类型={path_type}, 渠道={channel}, 登录={login_flag}")

        # 步骤1: 启动游戏
        logger.debug("[start_game] 步骤1: 启动游戏")
        if not self._launch_game_by_type(game_path, path_type, channel):
            logger.debug("[start_game] 步骤1失败: 游戏启动失败")
            return False

        # 步骤2: 检测用户协议（无论是否需要登录都先检测）
        logger.info("检测用户协议")
        logger.debug("[start_game] 步骤2: 检测用户协议")
        if not self._detect_user_agreement(channel):
            logger.error("用户协议处理失败")
            logger.debug("[start_game] 步骤2失败: 用户协议处理失败")
            return False

        # 步骤3: 处理登录（如果需要）
        if login_flag:
            logger.info("开始登录流程")
            logger.debug("[start_game] 步骤3: 处理登录")
            if not self._handle_login_process(channel, account, password):
                logger.debug("[start_game] 步骤3失败: 登录流程失败")
                return False
        else:
            logger.info("跳过登录流程，开始检测登录状态")
            logger.debug("[start_game] 步骤3: 跳过登录，检测登录状态")
            # 即使不需要登录，也要检测当前状态
            login_state = self._detect_login_state(channel)
            if login_state is None:
                logger.error("登录状态检测失败")
                logger.debug("[start_game] 步骤3失败: 登录状态检测失败")
                return False
            # 检测到未登录，强制使用账密登录
            if login_state == 0:
                if not self._handle_login_process(channel, account, password):
                    logger.debug("[start_game] 步骤3失败: 检测到未登录，且强制登录失败")
                    return False
            # 检测到已经登录
            if login_state == 2:
                if check("res/img/click_start.png", interval=0.4, max_time=60):
                    logger.debug("[_wait_for_login_result] 检测到开始按钮，进入游戏")
                    click("res/img/click_start.png")
                    return True

        # 步骤4: 等待游戏完全加载
        logger.info("等待游戏加载完成")
        logger.debug("[start_game] 步骤4: 等待游戏完全加载")
        result = self.wait_game_load()
        logger.debug(f"[start_game] 游戏启动流程完成，结果: {result}")
        return result

    def _detect_user_agreement(self, channel):
        """
        检测并处理用户协议

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)

        Returns:
            bool: 是否成功处理用户协议
        """
        logger.info("开始检测用户协议")
        logger.debug(f"[_detect_user_agreement] 开始检测用户协议，渠道: {channel}")

        if channel == 0:
            # 官服用户协议检测
            logger.debug("[_detect_user_agreement] 检测官服用户协议")
            if check("res/img/agree3.png", interval=0.5, max_time=10):
                logger.info("检测到官服用户协议，同意中...")
                logger.debug("[_detect_user_agreement] 检测到官服用户协议，准备点击")
                if not click("res/img/agree3.png"):
                    logger.error("无法点击官服用户协议按钮")
                    logger.debug("[_detect_user_agreement] 官服用户协议点击失败")
                    return False
                logger.info("已同意官服用户协议")
                logger.debug("[_detect_user_agreement] 官服用户协议处理成功")
                return True
            else:
                logger.info("未检测到官服用户协议")
                logger.debug("[_detect_user_agreement] 未检测到官服用户协议")
                return True
        else:
            # B服用户协议检测
            logger.debug("[_detect_user_agreement] 检测B服用户协议")
            if check("res/img/bilibili_agree3.png", interval=0.5, max_time=10):
                logger.info("检测到B服用户协议，同意中...")
                logger.debug("[_detect_user_agreement] 检测到B服用户协议，准备点击")
                if not click("res/img/bilibili_agree3.png"):
                    logger.error("无法点击B服用户协议按钮")
                    logger.debug("[_detect_user_agreement] B服用户协议点击失败")
                    return False
                logger.info("已同意B服用户协议")
                logger.debug("[_detect_user_agreement] B服用户协议处理成功")
                return True
            else:
                logger.info("未检测到B服用户协议")
                logger.debug("[_detect_user_agreement] 未检测到B服用户协议")
                return True

    def _detect_login_state(self, channel):
        """
        检测当前登录状态（不包含用户协议检测）

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)

        Returns:
            int: 登录状态码
                官服: 0-未登录, 2-已登录, 3-已进入游戏
                B服: 0-未登录, 2-已登录, 3-已进入游戏
        """
        logger.debug(f"[_detect_login_state] 开始检测登录状态，渠道: {channel}")

        if channel == 0:
            # 官服登录状态检测（移除用户协议检测）
            logger.debug("[_detect_login_state] 检测官服登录状态")
            result = check_any(
                ["res/img/login_page.png", "res/img/quit.png", "res/img/chat_enter.png"],
                0.5, 100)
            # 重新映射结果：0-未登录, 1-已登录, 2-已进入游戏
            if result == 0:  # login_page.png
                result = 0  # 未登录
                logger.debug("[_detect_login_state] 官服状态: 未登录")
            elif result == 1:  # quit.png
                result = 2  # 已登录
                logger.debug("[_detect_login_state] 官服状态: 已登录")
            elif result == 2:  # chat_enter.png
                result = 3  # 已进入游戏
                logger.debug("[_detect_login_state] 官服状态: 已进入游戏")
        else:
            # B服登录状态检测（移除用户协议检测）
            logger.debug("[_detect_login_state] 检测B服登录状态")
            result = check_any(
                ["res/img/bilibili_login_page.png", "res/img/quit.png", "res/img/chat_enter.png"],
                0.5, 100)
            # 重新映射结果：0-未登录, 1-已登录, 2-已进入游戏
            if result == 0:  # bilibili_login_page.png
                result = 0  # 未登录
                logger.debug("[_detect_login_state] B服状态: 未登录")
            elif result == 1:  # quit.png
                result = 2  # 已登录
                logger.debug("[_detect_login_state] B服状态: 已登录")
            elif result == 2:  # chat_enter.png
                result = 3  # 已进入游戏
                logger.debug("[_detect_login_state] B服状态: 已进入游戏")

        logger.info(f"检测到登录状态: {result}")
        logger.debug(f"[_detect_login_state] 登录状态检测完成: {result}")
        return result

    @staticmethod
    def _check_resolution_compatibility():
        """
        检查游戏分辨率是否兼容
        """
        logger.debug("[_check_resolution_compatibility] 开始检查分辨率兼容性")
        resolution = SRAOperator.resolution_detect()
        logger.debug(f"[_check_resolution_compatibility] 检测到分辨率: {resolution}")

        if resolution[1] / resolution[0] != 9 / 16:
            logger.warning("检测到游戏分辨率不为16:9, 自动登录可能无法按预期运行")
            logger.debug(f"[_check_resolution_compatibility] 分辨率不兼容，当前比例: {resolution[1] / resolution[0]}")
        else:
            logger.debug("[_check_resolution_compatibility] 分辨率兼容检查通过")

    def _handle_logout_process(self, channel):
        """
        处理登出流程

        Args:
            channel (int): 服务器渠道 (0: 官服, 1: B服)
        """
        logger.debug("开始登出流程")
        logger.debug(f"[_handle_logout_process] 开始登出流程，渠道: {channel}")

        logger.debug("[_handle_logout_process] 检查登出按钮")
        if check("res/img/logout.png", interval=0.5, max_time=30):
            logger.debug("[_handle_logout_process] 找到登出按钮，点击中")
            click("res/img/logout.png")
        else:
            logger.debug("[_handle_logout_process] 未找到登出按钮")

        time.sleep(1)

        if channel == 0:
            # 官服登出流程
            logger.debug("[_handle_logout_process] 处理官服登出流程")
            if check("res/img/quit2.png", interval=0.5, max_time=25):
                logger.debug("[_handle_logout_process] 找到官服退出按钮")
                if not click("res/img/quit2.png"):
                    logger.error("无法点击官服退出按钮")
                    logger.debug("[_handle_logout_process] 官服退出按钮点击失败")
                    return
                else:
                    logger.debug("[_handle_logout_process] 官服退出按钮点击成功")
            else:
                logger.error("官服退出按钮未找到")
                logger.debug("[_handle_logout_process] 官服退出按钮未找到")
                return

            time.sleep(0.1)

            logger.debug("[_handle_logout_process] 检查官服其他登录按钮")
            if check("res/img/login_other.png", interval=0.5, max_time=25):
                if not click("res/img/login_other.png"):
                    logger.error("无法点击官服其他登录按钮")
                    logger.debug("[_handle_logout_process] 官服其他登录按钮点击失败")
                else:
                    logger.debug("[_handle_logout_process] 官服其他登录按钮点击成功")
            else:
                logger.error("官服其他登录按钮未找到")
                logger.debug("[_handle_logout_process] 官服其他登录按钮未找到")
        else:
            # B服登出流程
            logger.debug("[_handle_logout_process] 处理B服登出流程")
            if check("res/img/enter.png", interval=0.5, max_time=5):
                logger.debug("[_handle_logout_process] 找到B服进入按钮")
                if not click("res/img/enter.png"):
                    logger.error("无法点击B服进入按钮")
                    logger.debug("[_handle_logout_process] B服进入按钮点击失败")
                    return
                else:
                    logger.debug("[_handle_logout_process] B服进入按钮点击成功")
            else:
                logger.error("B服进入按钮未找到")
                logger.debug("[_handle_logout_process] B服进入按钮未找到")
                return

            time.sleep(0.5)

            logger.debug("[_handle_logout_process] 检查B服其他登录按钮")
            if check("res/img/bilibili_login_other.png", interval=0.5, max_time=5):
                if not click("res/img/bilibili_login_other.png"):
                    logger.error("无法点击B服其他登录按钮")
                    logger.debug("[_handle_logout_process] B服其他登录按钮点击失败")
                else:
                    logger.debug("[_handle_logout_process] B服其他登录按钮点击成功")
            else:
                logger.error("B服其他登录按钮未找到")
                logger.debug("[_handle_logout_process] B服其他登录按钮未找到")

        logger.debug("[_handle_logout_process] 登出流程完成")

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
        logger.debug(f"[_perform_account_login] 开始执行账号登录，渠道: {channel}")

        if channel == 0:
            # 官服登录流程
            logger.debug("[_perform_account_login] 处理官服登录流程")
            if check("res/img/login_with_account.png", interval=0.5, max_time=10):
                logger.debug("[_perform_account_login] 找到官服登录其他账号按钮")
                if not click("res/img/login_with_account.png"):
                    logger.error("发生错误，无法点击登录其他账号按钮，可能有未适配的界面")
                    logger.debug("[_perform_account_login] 官服登录其他账号按钮点击失败")
                    return False
                else:
                    logger.debug("[_perform_account_login] 官服登录其他账号按钮点击成功")
            else:
                logger.error("未找到官服登录其他账号按钮")
                logger.debug("[_perform_account_login] 官服登录其他账号按钮未找到")
                return False

            logger.info("登录到" + account)

        else:
            # B服登录流程
            logger.debug("[_perform_account_login] 处理B服登录流程")
            if check("res/img/bilibili_login_with_account.png", interval=0.5, max_time=10):
                logger.debug("[_perform_account_login] 找到B服登录其他账号按钮")
                if not click("res/img/bilibili_login_with_account.png"):
                    logger.error("发生错误，无法点击B服登录其他账号按钮，可能有未适配的界面")
                    logger.debug("[_perform_account_login] B服登录其他账号按钮点击失败")
                    return False
                else:
                    logger.debug("[_perform_account_login] B服登录其他账号按钮点击成功")
            else:
                logger.error("未找到B服登录其他账号按钮")
                logger.debug("[_perform_account_login] B服登录其他账号按钮未找到")
                return False

            logger.info("尝试登录到" + account[:3] + "****" + account[-2:])

            # B服需要先点击账号输入框
            logger.debug("[_perform_account_login] B服点击账号输入框")
            if check("res/img/bilibili_account.png", interval=0.2, max_time=20):
                if not click("res/img/bilibili_account.png"):
                    logger.error("无法点击B服账号输入框")
                    logger.debug("[_perform_account_login] B服账号输入框点击失败")
                    return False
                else:
                    logger.debug("[_perform_account_login] B服账号输入框点击成功")

        result = self._input_credentials(channel, account, password)
        logger.debug(f"[_perform_account_login] 账号登录流程完成，结果: {result}")
        return result

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
        logger.debug(f"[_input_credentials] 开始输入登录凭据，渠道: {channel}")
        time.sleep(1)

        # 输入账号
        logger.debug("[_input_credentials] 输入账号")
        SRAOperator.copy(account)
        SRAOperator.paste()
        time.sleep(1)

        # 切换到密码框
        logger.debug("[_input_credentials] 切换到密码框")
        press_key("tab")
        time.sleep(0.2)

        # 输入密码
        logger.debug("[_input_credentials] 输入密码")
        SRAOperator.copy(password)
        SRAOperator.paste()

        # 处理登录时的用户协议同意
        if channel == 0:
            # 官服登录流程
            logger.debug("[_input_credentials] 处理官服登录协议和进入按钮")
            if check("res/img/agree.png", interval=0.5, max_time=5):
                logger.debug("[_input_credentials] 找到官服用户协议同意按钮")
                if not click("res/img/agree.png", -158):
                    logger.error("无法点击官服用户协议同意按钮")
                    logger.debug("[_input_credentials] 官服用户协议同意按钮点击失败")
                    return False
                else:
                    logger.debug("[_input_credentials] 官服用户协议同意按钮点击成功")
            else:
                logger.error("官服用户协议同意按钮未找到")
                logger.debug("[_input_credentials] 官服用户协议同意按钮未找到")
                return False

            if check("res/img/enter_game.png", interval=0.5, max_time=5):
                logger.debug("[_input_credentials] 找到官服进入游戏按钮")
                result = click("res/img/enter_game.png")
                logger.debug(f"[_input_credentials] 官服进入游戏按钮点击结果: {result}")
                return True
            else:
                logger.error("官服进入游戏按钮未找到")
                logger.debug("[_input_credentials] 官服进入游戏按钮未找到")
                return False
        else:
            # B服登录流程
            logger.debug("[_input_credentials] 处理B服登录协议和进入按钮")
            if check("res/img/bilibili_agree2.png", interval=0.5, max_time=5):
                logger.debug("[_input_credentials] 找到B服用户协议同意按钮")
                if not click("res/img/bilibili_agree2.png", -26):
                    logger.error("无法点击B服用户协议同意按钮")
                    logger.debug("[_input_credentials] B服用户协议同意按钮点击失败")
                    return False
                else:
                    logger.debug("[_input_credentials] B服用户协议同意按钮点击成功")

            if check("res/img/bilibili_enter_game.png", interval=0.5, max_time=5):
                logger.debug("[_input_credentials] 找到B服进入游戏按钮")
                if not click("res/img/bilibili_enter_game.png"):
                    logger.error("无法点击B服进入游戏按钮")
                    logger.debug("[_input_credentials] B服进入游戏按钮点击失败")
                    return False
                else:
                    logger.debug("[_input_credentials] B服进入游戏按钮点击成功")
            else:
                logger.error("B服进入游戏按钮未找到")
                logger.debug("[_input_credentials] B服进入游戏按钮未找到")
                return False

            logger.debug("[_input_credentials] 登录凭据输入完成")

            # 获取屏幕中心点坐标
            x, y = SRAOperator.get_screen_center()

            # 检查是否处于登录页(以12+标志为准)，进入火车头界面
            if check("res/img/12+.png", 0.5, 10):
                click_point(x, y)
                time.sleep(3)

            logger.info("[_input_credentials] 点击开始游戏，即将进入火车头")
            return True

    def _wait_for_login_result(self, channel):
        """
        执行登录后操作，等待登录结果

        Args:
            channel (int): 服务器渠道

        Returns:
            Bool: 登录结果状态
        """
        logger.debug(f"[_wait_for_login_result] 开始等待登录结果，渠道: {channel}")

        if channel == 0:
            logger.debug("[_wait_for_login_result] 等待官服登录结果")
            if check("res/img/click_start.png", interval=0.4, max_time=60):
                logger.debug("[_wait_for_login_result] 检测到官服点击开始按钮")
                click("res/img/click_start.png")
                logger.success("已成功登入游戏")
                logger.debug("[_wait_for_login_result] 官服登录成功")
                return True
            else:
                logger.warning("长时间未成功登录，可能密码错误或需要新设备验证")
                logger.debug("[_wait_for_login_result] 官服登录超时失败")
                return False

        elif channel == 1:
            logger.debug("[_wait_for_login_result] 等待B服登录结果")
            result = check_any(["res/img/click_start.png", "res/img/bilibili_verify.png"], interval=0.4, max_time=60)
            logger.debug("[_wait_for_login_result] 检测到官服点击开始按钮")
            click("res/img/click_start.png")
            logger.success("已成功登入游戏")
            logger.debug("[_wait_for_login_result] 官服登录成功")
            # B服验证码处理
            if result == 0:
                logger.info("登录成功")
                logger.debug("[_wait_for_login_result] B服登录成功")
                return True
            else:
                logger.warning("遇到B站验证码")
                logger.debug("[_wait_for_login_result] B服遇到验证码")
                return self._handle_bilibili_verification()
        else:
            logger.warning("非法参数，请检查服务器渠道")
            logger.debug(f"[_wait_for_login_result] 非法渠道参数: {channel}")
            return False

    def _handle_bilibili_verification(self):
        """
        处理B站验证码

        Returns:
            Bool: 验证结果 (True: 成功, False: 失败)
        """
        logger.debug("[_handle_bilibili_verification] 开始处理B站验证码")
        logger.warning("遇到b站验证码！请手动完成！")

        for wait_time in range(20):
            logger.warning(f"请手动完成b站验证码!剩余{10 - wait_time}秒")
            logger.debug(f"[_handle_bilibili_verification] 验证码等待第{wait_time + 1}秒")
            time.sleep(1)
            if check("res/img/bilibili_welcome.png", interval=0.2, max_time=1):
                logger.info("登录成功")
                logger.debug("[_handle_bilibili_verification] B站验证码处理成功")
                return True

        logger.error("验证码超时，登录失败")
        logger.debug("[_handle_bilibili_verification] B站验证码处理超时失败")
        return False

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
        logger.debug(
            f"[login_official] 开始官服登录流程，账号: {account[:3]}***{account[-2:] if len(account) > 5 else '***'}")
        login_instance = Login("", "")  # 临时实例用于调用实例方法

        # 检测登录状态
        # 0-未登录, 2-已登录, 3-已进入游戏
        logger.debug("[login_official] 检测登录状态")
        result = login_instance._detect_login_state(0)
        login_instance._check_resolution_compatibility()

        # 如果已经在游戏中，直接返回
        if result == 3:
            logger.debug("[login_official] 已在游戏中，直接返回")
            return True
        # 如果已经登录，先登出
        if result == 2:
            logger.debug("[login_official] 已登录，执行登出流程")
            login_instance._handle_logout_process(0)
        # 如果从未登录，点击一次使用账号密码登录再进行登录
        else:
            logger.debug("[login_official] 点击使用账号登录")
            if check("res/img/login_with_account.png", interval=0.5, max_time=5):
                if not click("res/img/login_with_account.png"):
                    logger.error("无法点击使用账号登录")
                    logger.debug("[login_official] 官服点击使用账号登录失败")
                    return False
                else:
                    logger.debug("[login_official] 官服点击使用账号登录成功")
            else:
                logger.error("官服使用账号登录按钮未找到")
                logger.debug("[login_official] 官服使用账号登录按钮未找到")
                return False

        # 执行登录流程
        logger.debug("[login_official] 执行账号密码登录")
        if not login_instance._perform_account_login(0, account, password):
            logger.error("发生错误，找不到登录按钮，请检查页面是否有更新或用户协议是否已同意")
            logger.debug("[login_official] 账号密码登录失败")
            return False

        # 等待登录结果
        logger.debug("[login_official] 等待登录结果")
        result = login_instance._wait_for_login_result(0)
        logger.debug(f"[login_official] 官服登录流程完成，结果: {result}")
        return result

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
        logger.debug(
            f"[login_bilibili] 开始B服登录流程，账号: {account[:3]}***{account[-2:] if len(account) > 5 else '***'}")
        login_instance = Login("", "")  # 临时实例用于调用实例方法

        # 检测登录状态
        logger.debug("[login_bilibili] 检测登录状态")
        result = login_instance._detect_login_state(1)
        login_instance._check_resolution_compatibility()

        # 如果已经在游戏中，直接返回
        if result is not None and result == 3:
            logger.debug(f"[login_bilibili] 已在游戏中，直接返回: {result}")
            return result

        # 处理已登录或用户协议情况
        if result == 2:
            logger.debug("[login_bilibili] 已登录，执行登出流程")
            login_instance._handle_logout_process(1)
        else:
            # 先check再click其他登录方式
            logger.debug("[login_bilibili] 点击使用账密登录")
            if check("res/img/bilibili_login_with_account.png", interval=0.5, max_time=5):
                if not click("res/img/bilibili_login_with_account.png"):
                    logger.error("无法点击B服使用账密登录")
                    logger.debug("[login_bilibili] B服点击使用账密登录点击失败")
                    return 0
                else:
                    logger.debug("[login_bilibili] B服点击使用账密登录点击成功")
            else:
                logger.error("B服使用账密登录未找到")
                logger.debug("[login_bilibili] B服使用账密登录未找到")
                return 0

        # 执行登录流程
        logger.debug("[login_bilibili] 执行账号密码登录")
        if not login_instance._perform_account_login(1, account, password):
            logger.debug("[login_bilibili] 账号密码登录失败")
            return 0

        # 等待登录结果
        logger.debug("[login_bilibili] 等待登录结果")
        result = login_instance._wait_for_login_result(1)
        logger.debug(f"[login_bilibili] B服登录流程完成，结果: {result}")
        return result

    @staticmethod
    def wait_game_load():
        """
        等待游戏完全加载到大世界

        Returns:
            bool: 是否成功进入大世界
        """
        logger.debug("[wait_game_load] 开始等待游戏加载到大世界")
        times = 0

        while True:
            logger.debug(f"[wait_game_load] 第{times + 1}次检查游戏加载状态")

            # 处理月卡界面
            logger.debug("[wait_game_load] 检查月卡界面")
            res = check_any(["res/img/train_supply.png", "res/img/chat_enter.png", "res/img/phone.png"])
            if res is not None and res == 0:
                logger.debug("[wait_game_load] 检测到月卡界面，处理中")
                click("res/img/train_supply.png")
                time.sleep(4)
                # 向下移动鼠标并点击（领取月卡）
                logger.debug("[wait_game_load] 移动鼠标并点击领取月卡")
                SRAOperator.moveRel(0, +400)
                click()
                logger.debug("[wait_game_load] 月卡处理完成")
                return True
            elif res == 1 or res == 2:
                logger.info("成功进入大世界")
                logger.debug("[wait_game_load] 游戏加载完成，已进入大世界")
                return True
            else:
                times += 1
                if times == 30:  # 30秒超时
                    logger.error("发生错误，可能进入游戏但未处于大世界")
                    logger.debug(f"[wait_game_load] 等待超时，已等待{times}秒")
                    return False
                logger.debug(f"[wait_game_load] 未检测到大世界，继续等待 ({times}/30)")
            time.sleep(1)


# 主程序入口
if __name__ == "__main__":
    logger.info("程序开始")
    logger.debug("[main] 程序启动，开始初始化")

    if is_admin():
        logger.info("以管理员权限运行")
        logger.debug("[main] 管理员权限检查通过")
    else:
        logger.error("请以管理员权限运行本程序")
        logger.debug("[main] 管理员权限检查失败，尝试重启")
        run_as_admin()

    # 读取 id 参数
    logger.debug("[main] 开始解析命令行参数")
    if len(sys.argv) < 2:
        logger.warning("未给定参数 id，默认为1，请给定参数设置例如: python Login.py 1")
        logger.debug("[main] 未提供配置ID参数，使用默认值1")
    config_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    logger.debug(f"[main] 使用配置ID: {config_id}")

    # 如果没有给定参数，默认使用第一个配置
    config_path = os.path.join(os.path.dirname(__file__), "config/config.json")
    logger.debug(f"[main] 配置文件路径: {config_path}")
    logger.debug(f"加载配置文件: {config_path}，使用第 {config_id} 配置")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            all_config = json.load(f)
        logger.debug(f"[main] 配置文件加载成功，共有{len(all_config)}个配置")
    except Exception as e:
        logger.error(f"配置文件加载失败: {e}")
        logger.debug(f"[main] 配置文件加载异常: {e}")
        sys.exit(1)

    if config_id not in all_config:
        logger.error(f"未找到 id={config_id} 的配置，请检查 config.json")
        logger.debug(f"[main] 配置ID {config_id} 不存在，可用配置: {list(all_config.keys())}")
        sys.exit(1)

    config = all_config[config_id]
    logger.debug(f"[main] 成功加载配置: {config_id}")

    # 设置日志等级
    log_level = config.get("log_level", "INFO")
    logger.debug(f"[main] 从配置读取到日志等级: {log_level}")
    set_log_level(log_level)

    logger.debug("[main] 开始初始化Login实例")
    login = Login(
        game_path=config["game_path"],
        game_type=config["game_type"],
        enable_login=config.get("enable_login", False),
        server=config.get("server"),
        username=config.get("username"),
        password=config.get("password")
    )

    # 串行任务执行 - 简化版
    logger.debug("[main] 开始执行主任务流程")
    logger.debug("[main] 任务1: 检查游戏路径")
    path_check_result = login.path_check(login.game_path, login.game_type)
    logger.debug(f"[main] 路径检查结果: {path_check_result}")

    if path_check_result:
        logger.debug("[main] 任务2: 启动游戏并处理登录")
        start_game_result = login.start_game(
            login.game_path,
            login.game_type,
            int(login.server),
            login.enable_login,
            login.username,
            login.password
        )
        logger.debug(f"[main] 游戏启动结果: {start_game_result}")

        if start_game_result:
            logger.debug("[main] 任务3: 最终游戏检查")
            final_check_result = login.wait_game_load()
            logger.debug(f"[main] 最终检查结果: {final_check_result}")

            if final_check_result:
                logger.success("我滴任务，完成啦！")
                logger.debug("[main] 所有任务执行成功")
            else:
                logger.warning("任务执行失败，终止后续操作")
                logger.debug("[main] 最终检查失败")
        else:
            logger.warning("任务执行失败，终止后续操作")
            logger.debug("[main] 游戏启动失败")
    else:
        logger.warning("任务执行失败，终止后续操作")
        logger.debug("[main] 路径检查失败")

    logger.debug("[main] 程序执行完成")
