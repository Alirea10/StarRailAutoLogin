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

game_path：星铁位置，用于启动星铁。**请注意，StarWard的硬链接用户不能直接使用此path，请使用StarWard启动器适配，当使用Starward时**

game_type：上述path的类型，目前有StarRail和Starward两种，前者为直接打开游戏exe，后者是通过Starward的URL协议来打开。SRA（但是现在此项目还不）支持官，B的启动器，通过启动器进行启动更新等操作。

server：0代表官服，1代表B服，如果真有人用的话未来在考虑国际服

enable_login：是否进行登录操作，如果为false，将直接登录当前账号

username/password：正如其名，账号和密码，**目前它是明文保存的，DEBUG日志当前会输出整个config，请记得隐私保护**

## 使用方法

###  直接使用

1. 自行配置好AUTO-MAA的通用配置，请先了解AUTO_MAA项目并阅读[通用调度 | AUTO_MAA文档](https://doc.automaa.xyz/general-manager.html)或查看[AUTO_MAA_v4.4.1官方使用教程 45：40的通用脚本配置部分](https://www.bilibili.com/video/BV169hnzRE16?vd_source=1b23dbecbe67cf121377aea29d2373e7)，可选择从「AUTO_MAA配置分享中心」导入（推荐）或自行配置
2. 在下方的“下属配置”中，创建一个新配置，打开脚本前置任务并选择start.bat文件
3. 安装python（3.9至3.11（推荐））环境，并安装requirements.txt。
   *若你有python的开发经验，你可以创造一个虚拟环境以供使用（推荐但非必须）*
4. 根据上面的配置说明填写config文件
5. 尝试启动start.bat，查看是否正常运行，正常运行即可在AUTO-MAA中使用 

### Startward额外操作

如果你使用Starward，你需要先安装并打开Starward，在设置→高级→URL协议（测试版）中勾选注册URL协议，点击测试URL协议，出现Starward窗口即为正常，若出现“获取打开此'starward'链接的应用”说明......你没打开.....那你开开好不好？

## 当前测试

未列出为尚未测试，理论上SRA不需要本项目也能通过直接和AUTO-MAA配合登录使用，但尚未了解是否能无人值守切换账号/服务器。

当前B服尚未进行登录适配

- [x] AUTO-MAA + 三月七小助手 +官服
- [ ] AUTO-MAA + 三月七小助手 +B服
- [x] AUTO-MAA + 三月七小助手 +Starward（官服）
- [ ] AUTO-MAA + 三月七小助手 +B服

## TODO

- [ ] 优化config逻辑，完善bat传参逻辑
- [ ] 编写退出脚本，以适配AUTO-MAA的无缝换号链接
- [ ] 适配b服登录
- [x] 适配Starward的识别，启动等
- [ ] 适配官方（b服）启动器