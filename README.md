# ChaoXing_Sign
超星学习通自动签到脚本，本项目是基于作者[一碗炒饭啊](https://space.bilibili.com/85497962)在基本源码上面进行修改的，只在上面增加了签到后自动发送邮件功能。

# 大致原理
隔一段时间(自定义)对于所有课程查看近期的活动，若有需要签到的就会去签到。

# 存在的问题
1. 若新增课程需要打卡需要重启程序(因为所有课程是服务器启动时候解析的,这是作者一开始就是这样设计的，后面我会考虑隔一段时间也从新获取下课程列表)
2. 24小时运行可能出现异常`Expecting value: line 1 column 1 (char 0)`导致程序被中止,待排查...
3. cookie过期，无法正常运行，解决办法是手动删除cookie.txt文件，再运行使得重新获取cookie
4. 24小时运行可能会出现程序没正常打卡的情况，待排查....

# 功能
- 支持普通签到、拍照签到、位置签到、手势签到。
- 支持全自动运行检测并签到。
- **目前只支持单人，不支持多人**


# 使用方法
1. 修改emailUtil.py文件，配置文件最上面的三个变量，即发件人邮箱、发件人密码、收件人邮箱。
2. 修改main.py文件，配置最上面setting里面的内容，即账号、密码、签到设置等。
3. 运行main.py



