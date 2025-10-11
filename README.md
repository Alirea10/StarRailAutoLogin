# StarRailAutoLogin

基于OCR的星铁自动登录，拆分自[Shasnow/StarRailAssistant: 崩坏星穹铁道自动化助手](https://github.com/Shasnow/StarRailAssistant)，用于适配AUTO-MAA项目的通用配置，最终目的是实现星铁的多账号/多服务器登录和登出功能，以达到使用AUTO-MAA完全解放双手的终极目标

## 最佳应用

AUTO-MAA + 三月七小助手 + Starward（官服/b服）

前期的开发将优先适配以上内容

## 配置说明

默认配置如下

```json
{
  "1": {
    "game_name": "崩坏：星穹铁道",
    "game_path": "D:/Star Rail/Game/StarRail.exe",
    "game_type": "StarRail",
    "server": "0",
    "enable_login": true,
    "username": "user1@example.com",
    "password": "password1"
  },
}
```

"1"：代表唯一编号，可以在使用bat调用程序时选择当次进入的账号，如 python Login.py 1，即使用第一个内容进行登录操作，在下面添加2，3，4可配置多配置。

game_name：现阶段没啥用，接下来如果要适配原神、绝区零甚至其他更多游戏，可能会用上

game_path：星铁位置，用于启动星铁。**请注意，StarWard的硬链接用户不能直接使用此path，请使用StarWard启动器适配，当使用Starward时，此项可以不填**

game_type：上述path的类型，目前有StarRail和Starward两种，前者为直接打开游戏exe，后者是通过Starward的URL协议来打开。

server：0代表官服，1代表B服，如果真有人用的话未来在考虑国际服

enable_login：是否进行登录操作，如果为false，将直接登录当前账号

username/password：正如其名，账号和密码，**目前它是明文保存于本地json文件的，DEBUG日志当前会输出整个账号的一部分，请记得隐私保护，不要分享json配置**

## 使用方法

###  下载源码直接使用

1. 自行配置好AUTO-MAA的通用配置，请先了解AUTO_MAA项目并阅读[通用调度 | AUTO_MAA文档](https://doc.automaa.xyz/general-manager.html)或查看[AUTO_MAA_v4.4.1官方使用教程 45：40的通用脚本配置部分](https://www.bilibili.com/video/BV169hnzRE16?vd_source=1b23dbecbe67cf121377aea29d2373e7)，可选择从「AUTO_MAA配置分享中心」导入（推荐）或自行配置

2. 在下方的“下属配置”中，创建一个新配置，打开脚本前置任务并选择start.bat文件

3. 运行Script文件夹的init.bat，他会帮助你：检测Python版本（暂支持3.9~3.11，最好使用3.11），创建虚拟环境，安装必要的包在虚拟环境。
   
   *若你有python的开发经验，你可以自己精简一下requirements.txt*
   
4. 根据上面的配置说明填写config文件

5. 尝试启动start.bat，一般你使用此项目你一定有许多账号，你可以复制粘贴多个bat文件。查看是否正常运行，正常运行即可在AUTO-MAA中的“运行前运行脚本"中使用此脚本 

6. （推荐）使用taskkill.py作为“运行后运行脚本”，它会帮助你关闭残留的OCR进程，三月七和Starward，帮你在下一个账号代理前使崩铁进入登录界面（当前不支持在游戏内无缝登出并切换账号）

### Startward额外操作

如果你使用Starward，你需要先安装并打开Starward，在设置→高级→URL协议（测试版）中勾选注册URL协议，点击测试URL协议，出现Starward窗口即为正常，若在AUTO运行时出现“获取打开此'starward'链接的应用”说明......你没打开.....那你开开好不好？

### 三月七额外操作

如果你有以下情况：

当前AUTO-MAA，有概率出现杀死三月七进程后留下OCR进程在后台持续运行造成高占用。

你的三月七识别可能出错，导致崩铁在某个奇怪的界面没法退出（典型的例子：迷迷手机主题导致识别不到邮箱不小心进到设置导致后续脚本全部木大）

你可使用Script下的taskkill作为“运行后运行脚本”，它会：关闭所有崩铁（官 b 也许国际服也会）、Starward并关闭三月七杀不全导致的OCR进程残留。

## 当前测试

未列出为尚未测试，理论上SRA不需要本项目也能通过直接和AUTO-MAA配合登录使用，但尚未了解是否能无人值守切换账号/服务器。

当前B服尚已经进行登录适配，但小概率出现验证码，请不要输错密码导致重复登录进而出现验证码。

- [x] AUTO-MAA + 三月七小助手 +官服
- [x] AUTO-MAA + 三月七小助手 +B服
- [x] AUTO-MAA + 三月七小助手 +Starward（官服）
- [x] AUTO-MAA + 三月七小助手 +Starward（B服）

## TODO

- [x] 优化config逻辑，完善bat传参逻辑
- [x] 编写退出脚本，以适配AUTO-MAA的无缝换号链接
- [x] 适配b服登录
- [x] 适配Starward的识别，启动等
- [ ] 适配官方（b服）启动器（可能不再计划）（你知道吗Starward太好用了