"""
c相关结构体
"""
from ctypes import Structure

from camera.hik_vision.type_map import h_CHAR, h_BYTE, h_WORD, h_VOID_P, h_BOOL, h_LONG, h_DWORD, h_HWND


# noinspection PyPep8Naming
class NET_DVR_USER_LOGIN_INFO(Structure):
    """
    登录参数结构体
    """
    _fields_ = [
        ("sDeviceAddress", h_CHAR * 129),  # 设备地址，ip或者普通域名
        ("byUseTransport", h_BYTE),  # 是否启用能力集透传：0- 不启用透传，默认；1- 启用透传
        ("wPort", h_WORD),  # 设备端口号，例如：8000
        ("sUserName", h_CHAR * 64),  # 登录用户名，例如：admin
        ("sPassword", h_CHAR * 64),  # 登录密码，例如：12345
        # ("cbLoginResult", h_VOID_P),  # 登录状态回调函数，bUseAsynLogin 为1时有效
        ("pUser", h_VOID_P),  # 用户数据
        ("bUseAsynLogin", h_BOOL),  # 是否异步登录：0-否，1-是
        ("byProxyType", h_BYTE),  # 代理服务器类型：0- 不使用代理，1- 使用标准代理，2- 使用EHome代理
        ("byUseUTCTime", h_BYTE),  # 是否使用UTC时间：0- 不进行转换，默认；1- 输入输出UTC时间，SDK进行与设备时区的转换；2- 输入输出平台本地时间，SDK进行与设备时区的转换
        ("byLoginMode", h_BYTE),  # 登录模式(不同模式具体含义详见“Remarks”说明)：0- SDK私有协议，1- ISAPI协议，2- 自适应（设备支持协议类型未知时使用，一般不建议）
        ("byHttps", h_BYTE),
        # ISAPI协议或海康私有协议登录时是否启用TLS(即byLoginMode为0或1均有效)：0-不使用TLS，1-使用TLS
        # 2-自适应（自适应登录时，会对性能有较大影响，自适应时要同时发起HTTP和HTTPS，设备支持协议类型未知时使用，一般不建议。）
        ("iProxyID", h_LONG),  # 代理服务器序号，添加代理服务器信息时相对应的服务器数组下表值
        ("byVerifyMode", h_LONG),
        # 认证方式， 0-不认证，1-双向认证（暂不支持），2-单向认证；使用海康私有协议登录且使用TLS链路时有效（即SDK Over
        # TLS，byLoginMode为0且byHttps为1）;选择0时，无需加载CA证书；选择2时，需要调用接口NET_DVR_SetSDKLocalCfg加载CA
        # 证书，枚举值为NET_SDK_LOCAL_CFG_CERTIFICATION。
        ("byRes3", h_BYTE * 119)  # 保留，置为0
    ]


# noinspection PyPep8Naming
class NET_DVR_DEVICEINFO_V30(Structure):
    """
    设备参数结构体
    """
    _fields_ = [
        ("sSerialNumber", h_BYTE * 48),  # 序列号
        ("byAlarmInPortNum", h_BYTE),  # 模拟报警输入个数
        ("byAlarmOutPortNum", h_BYTE),  # 模拟报警输出个数
        ("byDiskNum", h_BYTE),  # 硬盘个数
        ("byDVRType", h_BYTE),  # 设备类型，详见下文列表
        ("byChanNum", h_BYTE),  # 设备模拟通道个数，数字(IP)通道最大个数为byIPChanNum + byHighDChanNum*256
        ("byStartChan", h_BYTE),  # 模拟通道的起始通道号，从1开始。数字通道的起始通道号见下面参数byStartDChan
        ("byAudioChanNum", h_BYTE),  # 设备语音对讲通道数
        ("byIPChanNum", h_BYTE),
        # 设备最大数字通道个数，低8位，搞8位见byHighDChanNum. 可以根据ip通道个数是否调用NET_DVR_GetDVRConfig (
        # 配置命令NET_DVR_GET_IPPARACFG_V40)获得模拟和数字通道的相关参数
        ("byZeroChanNum", h_BYTE),  # 零通道编码个数
        ("byMainProto", h_BYTE),  # 主码流传输协议类型： 0 - private, 1 - rtsp, 2- 同时支持私有协议和rtsp协议去留（默认采用私有协议取流）
        ("bySubProto", h_BYTE),  # 字码流传输协议类型： 0 - private , 1 - rtsp , 2 - 同时支持私有协议和rtsp协议取流 （默认采用私有协议取流）

        # 能力，位与结果为0表示不支持，1
        # 表示支持
        # bySupport & 0x1，表示是否支持智能搜索
        # bySupport & 0x2，表示是否支持备份
        # bySupport & 0x4，表示是否支持压缩参数能力获取
        # bySupport & 0x8, 表示是否支持双网卡
        # bySupport & 0x10, 表示支持远程SADP
        # bySupport & 0x20, 表示支持Raid卡功能
        # bySupport & 0x40, 表示支持IPSAN目录查找
        # bySupport & 0x80, 表示支持rtp over rtsp
        ("bySupport", h_BYTE),
        # 能力集扩充，位与结果为0表示不支持，1
        # 表示支持
        # bySupport1 & 0x1, 表示是否支持snmp
        # v30
        # bySupport1 & 0x2, 表示是否支持区分回放和下载
        # bySupport1 & 0x4, 表示是否支持布防优先级
        # bySupport1 & 0x8, 表示智能设备是否支持布防时间段扩展
        # bySupport1 & 0x10, 表示是否支持多磁盘数（超过33个）
        # bySupport1 & 0x20, 表示是否支持rtsp over http
        # bySupport1 & 0x80, 表示是否支持车牌新报警信息，且还表示是否支持NET_DVR_IPPARACFG_V40配置
        ("bySupport1", h_BYTE),
        # 能力集扩充，位与结果为0表示不支持，1
        # 表示支持
        # bySupport2 & 0x1, 表示解码器是否支持通过URL取流解码
        # bySupport2 & 0x2, 表示是否支持FTPV40
        # bySupport2 & 0x4, 表示是否支持ANR(断网录像)
        # bySupport2 & 0x20, 表示是否支持单独获取设备状态子项
        # bySupport2 & 0x40, 表示是否是码流加密设备
        ("bySupport2", h_BYTE),
        ("wDevType", h_WORD),  # 设备型号，详见下文列表
        # 能力集扩展，位与结果：0 - 不支持，1 - 支持
        # bySupport3 & 0x1, 表示是否支持多码流
        # bySupport3 & 0x4, 表示是否支持按组配置，具体包含通道图像参数、报警输入参数、IP报警输入 / 输出接入参数、用户参数、设备工作状态、JPEG抓图、定时和时间抓图、硬盘盘组管理等
        # bySupport3 & 0x20,表示是否支持通过DDNS域名解析取流
        ("bySupport3", h_BYTE),
        # 是否支持多码流，按位表示，位与结果：0 - 不支持，1 - 支持
        # byMultiStreamProto & 0x1, 表示是否支持码流3
        # byMultiStreamProto & 0x2, 表示是否支持码流4
        # byMultiStreamProto & 0x40, 表示是否支持主码流
        # byMultiStreamProto & 0x80, 表示是否支持子码流
        ("byMultiStreamProto", h_BYTE),
        ("byStartDChan", h_BYTE),  # 起始数字通道号，0表示无数字通道，比如DVR或IPC
        ("byStartDTalkChan", h_BYTE),  # 起始数字对讲通道号，区别于模拟对讲通道号，0表示无数字对讲通道
        ("byHighDChanNum", h_BYTE),  # 数字通道个数，高8位

        # 能力集扩展，按位表示，位与结果：0 - 不支持，1 - 支持
        # bySupport4 & 0x01, 表示是否所有码流类型同时支持RTSP和私有协议
        # bySupport4 & 0x10, 表示是否支持域名方式挂载网络硬盘
        ("bySupport4", h_BYTE),
        # 支持语种能力，按位表示，位与结果：0 - 不支持，1 - 支持
        # byLanguageType == 0，表示老设备，不支持该字段
        # byLanguageType & 0x1，表示是否支持中文
        # byLanguageType & 0x2，表示是否支持英文
        ("byLanguageType", h_BYTE),

        ("byVoiceInChanNum", h_BYTE),  # 音频输入通道数
        ("byStartVoiceInChanNo", h_BYTE),  # 音频输入起始通道号，0表示无效
        ("byRes3", h_BYTE * 2),  # 保留，置为0
        ("byMirrorChanNum", h_BYTE),  # 镜像通道个数，录播主机中用于表示导播通道
        ("wStartMirrorChanNo", h_WORD),  # 起始镜像通道号
        ("byRes2", h_BYTE * 2)]  # 保留，置为0


# noinspection PyPep8Naming
class NET_DVR_DEVICEINFO_V40(Structure):
    """
    设备参数结构体
    """
    _fields_ = [
        ("struDeviceV30", NET_DVR_DEVICEINFO_V30),  # 设备参数
        ("bySupportLock", h_BYTE),  # 设备是否支持锁定功能，bySuportLock 为1时，dwSurplusLockTime和byRetryLoginTime有效
        ("byRetryLoginTime", h_BYTE),  # 剩余可尝试登陆的次数，用户名，密码错误时，此参数有效

        # 密码安全等级： 0-无效，1-默认密码，2-有效密码，3-风险较高的密码，
        # 当管理员用户的密码为出厂默认密码（12345）或者风险较高的密码时，建议上层客户端提示用户名更改密码
        ("byPasswordLevel", h_BYTE),

        ("byProxyType", h_BYTE),  # 代理服务器类型，0-不使用代理，1-使用标准代理，2-使用EHome代理
        # 剩余时间，单位：秒，用户锁定时次参数有效。在锁定期间，用户尝试登陆，不算用户名密码输入对错
        # 设备锁定剩余时间重新恢复到30分钟
        ("dwSurplusLockTime", h_DWORD),
        # 字符编码类型（SDK所有接口返回的字符串编码类型，透传接口除外）：
        # 0 - 无字符编码信息（老设备）
        # 1 - GB2312
        ("byCharEncodeType", h_BYTE),
        # 支持v50版本的设备参数获取，设备名称和设备类型名称长度扩展为64字节
        ("bySupportDev5", h_BYTE),
        # 登录模式（不同的模式具体含义详见"Remarks"说明：0- SDK私有协议，1- ISAPI协议）
        ("byLoginMode", h_BYTE),
        # 保留，置为0
        ("byRes2", h_BYTE * 253),
    ]


# noinspection PyPep8Naming
class NET_DVR_Login_V40(Structure):
    """
    用户注册设备
    """
    _fields_ = [
        ("pLoginInfo", NET_DVR_USER_LOGIN_INFO),
        ("lpDeviceInfo", NET_DVR_DEVICEINFO_V40)
    ]


# noinspection PyPep8Naming
class NET_DVR_PREVIEWINFO(Structure):
    """
    预览参数结构体
    """
    _fields_ = [
        # 通道号，目前设备模拟通道号从1开始，数字通道的起始通道号通过
        # NET_DVR_GetDVRConfig(配置命令NET_DVR_GET_IPPARACFG_V40)获取（dwStartDChan）
        ('lChannel', h_LONG),
        # 码流类型：0-主码流，1-子码流，2-三码流，3-虚拟码流，以此类推
        ('dwStreamType', h_DWORD),
        # 连接方式：0-TCP方式，1-UDP方式，2-多播方式，3-RTP方式，4-RTP/RTSP，5-RTP/HTTP,6-HRUDP（可靠传输）
        ('dwLinkMode', h_DWORD),
        # 播放窗口的句柄，为NULL表示不解码显示
        ('hPlayWnd', h_HWND),
        # 0-非阻塞取流，1- 阻塞取流
        # 若设为不阻塞，表示发起与设备的连接就认为连接成功，如果发生码流接收失败、播放失败等
        # 情况以预览异常的方式通知上层。在循环播放的时候可以减短停顿的时间，与NET_DVR_RealPlay
        # 处理一致。
        # 若设为阻塞，表示直到播放操作完成才返回成功与否，网络异常时SDK内部connect失败将会有5s
        # 的超时才能够返回，不适合于轮询取流操作。
        ('bBlocked', h_BOOL),
        # 是否启用录像回传： 0-不启用录像回传，1-启用录像回传。ANR断网补录功能，
        # 客户端和设备之间网络异常恢复之后自动将前端数据同步过来，需要设备支持。
        ('bPassbackRecord', h_BOOL),
        # 延迟预览模式：0-正常预览，1-延迟预览
        ('byPreviewMode', h_BYTE),
        # 流ID，为字母、数字和"_"的组合，IChannel为0xffffffff时启用此参数
        ('byStreamID', h_BYTE * 32),
        # 应用层取流协议：0-私有协议，1-RTSP协议。
        # 主子码流支持的取流协议通过登录返回结构参数NET_DVR_DEVICEINFO_V30的byMainProto、bySubProto值得知。
        # 设备同时支持私协议和RTSP协议时，该参数才有效，默认使用私有协议，可选RTSP协议。
        ('byProtoType', h_BYTE),
        # 保留，置为0
        ('byRes1', h_BYTE),
        # 码流数据编解码类型：0-通用编码数据，1-热成像探测器产生的原始数据
        # （温度数据的加密信息，通过去加密运算，将原始数据算出真实的温度值）
        ('byVideoCodingType', h_BYTE),
        # 播放库播放缓冲区最大缓冲帧数，取值范围：1、6（默认，自适应播放模式）   15:置0时默认为1
        ('dwDisplayBufNum', h_DWORD),
        # NPQ模式：0- 直连模式，1-过流媒体模式
        ('byNPQMode', h_BYTE),
        # 保留，置为0
        ('byRes', h_BYTE * 215),
    ]


# noinspection SpellCheckingInspection
class NET_DVR_VIDEOEFFECT(Structure):
    """
    视频参数结构体
    """
    _fields_ = [
        # byBrightnessLevel
        # 亮度，取值范围[0, 100]
        ("byBrightnessLevel", h_BYTE),
        # byContrastLevel
        # 对比度，取值范围[0, 100]
        ("byContrastLevel", h_BYTE),
        # bySharpnessLevel
        # 锐度，取值范围[0, 100]
        ("bySharpnessLevel", h_BYTE),
        # bySaturationLevel
        # 饱和度，取值范围[0, 100]
        ("bySaturationLevel", h_BYTE),
        # byHueLevel
        # 色度，取值范围[0, 100]，保留
        ("byHueLevel", h_BYTE),
        # byEnableFunc
        # 使能，按位表示。bit0 - SMART
        # IR(防过曝)，bit1 - 低照度，bit2 - 强光抑制使能，值：0 - 否，1 - 是，例如byEnableFunc & 0x2 == 1
        # 表示使能低照度功能； bit3 - 锐度类型，值：0 - 自动，1 - 手动。
        ("byEnableFunc", h_BYTE),
        # byLightInhibitLevel
        # 强光抑制等级，取值范围：[1, 3]
        ("byLightInhibitLevel", h_BYTE),
        # byGrayLevel
        # 灰度值域:0 - [0, 255]，1 - [16, 235]
        ("byGrayLevel", h_BYTE)
    ]


class NET_DVR_GAIN(Structure):
    """
    增益参数结构体
    """
    _fields_ = [
        # byGainLevel
        # 增益，单位dB，取值范围[0, 100]
        ("byGainLevel", h_BYTE),
        ("byGainUserSet", h_BYTE),
        ("byRes", h_BYTE * 2),
        ("dwMaxGainValue", h_DWORD)
    ]


class NET_DVR_WHITEBALANCE(Structure):
    _fields_ = [
        ("byWhiteBalanceMode", h_BYTE),
        ("byWhiteBalanceModeRGain", h_BYTE),
        ("byWhiteBalanceModeBGain", h_BYTE),
        ("byRes", h_BYTE * 5)
    ]


class NET_DVR_EXPOSURE(Structure):
    _fields_ = [
        ("byExposureMode", h_BYTE),
        ("byAutoApertureLevel", h_BYTE),
        ("byRes", h_BYTE * 2),
        ("dwVideoExposureSet", h_WORD),
        ("dwExposureUserSet", h_WORD),
        ("dwRes", h_WORD),
    ]


class NET_DVR_GAMMACORRECT(Structure):
    _fields_ = [
        ("byGammaCorrectionEnabled", h_BYTE),
        ("byGammaCorrectionLevel", h_BYTE),
        ("byRes", h_BYTE * 6),
    ]


class NET_DVR_WDR(Structure):
    _fields_ = [
        ("byWDREnabled", h_BYTE),
        ("byWDRLevel1", h_BYTE),
        ("byWDRLevel2", h_BYTE),
        ("byWDRContrastLevel", h_BYTE),
        ("byRes", h_BYTE * 16),
    ]


class NET_DVR_DAYNIGHT(Structure):
    _fields_ = [
        ("byDayNightFilterType", h_BYTE),
        ("bySwitchScheduleEnabled", h_BYTE),
        ("byBeginTime", h_BYTE),
        ("byEndTime", h_BYTE),
        ("byDayToNightFilterLevel", h_BYTE),
        ("byNightToDayFilterLevel", h_BYTE),
        ("byDayNightFilterTime", h_BYTE),
        ("byBeginTimeMin", h_BYTE),
        ("byBeginTimeSec", h_BYTE),
        ("byEndTimeMin", h_BYTE),
        ("byEndTimeSec", h_BYTE),
        ("byAlarmTrigState", h_BYTE),
    ]


class NET_DVR_NOISEREMOVE(Structure):
    _fields_ = [
        ("byDigitalNoiseRemoveEnable", h_BYTE),
        ("byDigitalNoiseRemoveLevel", h_BYTE),
        ("bySpectralLevel", h_BYTE),
        ("byTemporalLevel", h_BYTE),
        ("byDigitalNoiseRemove2DEnable", h_BYTE),
        ("byDigitalNoiseRemove2DLevel", h_BYTE),
        ("byRes", h_BYTE * 2),
    ]


class NET_DVR_CMOSMODECFG(Structure):
    _fields_ = [
        ("byCaptureMod", h_BYTE),
        ("byBrightnessGate", h_BYTE),
        ("byCaptureGain1", h_BYTE),
        ("byCaptureGain2", h_BYTE),
        ("dwCaptureShutterSpeed1", h_WORD),
        ("dwCaptureShutterSpeed2", h_WORD),
        ("byRes", h_BYTE * 4),
    ]


class NET_DVR_BACKLIGHT(Structure):
    _fields_ = [
        ("byBacklightMode", h_BYTE),
        ("byBacklightLevel", h_BYTE),
        ("byRes1", h_BYTE * 2),
        ("dwPositionX1", h_DWORD),
        ("dwPositionY1", h_DWORD),
        ("dwPositionX2", h_DWORD),
        ("dwPositionY2", h_DWORD),
        ("byRes2", h_BYTE * 4),
    ]


# noinspection SpellCheckingInspection
class NET_DVR_CAMERAPARAMCFG(Structure):
    """
    前端参数配置结构体
    """
    _fields_ = [
        ("dwSize", h_DWORD),
        ("struVideoEffect", NET_DVR_VIDEOEFFECT),
        ("struGain", NET_DVR_GAIN),
        ("struWhiteBalance", NET_DVR_WHITEBALANCE),
        ("struExposure", NET_DVR_EXPOSURE),
        ("struGammaCorrect", NET_DVR_GAMMACORRECT),
        ("struWdr", NET_DVR_WDR),
        ("struDayNight", NET_DVR_DAYNIGHT),
        ("struBackLight", NET_DVR_BACKLIGHT),
        ("struNoiseRemove", NET_DVR_NOISEREMOVE),
        ("byPowerLineFrequencyMode", h_BYTE),
        ("byIrisMode", h_BYTE),
        ("byMirror", h_BYTE),
        ("byDigitalZoom", h_BYTE),
        ("byDeadPixelDetect", h_BYTE),
        ("byBlackPwl", h_BYTE),
        ("byEptzGate", h_BYTE),
        ("byLocalOutputGate", h_BYTE),
        ("byCoderOutputMode", h_BYTE),
        ("byLineCoding", h_BYTE),
        ("byDimmerMode", h_BYTE),
        ("byPaletteMode", h_BYTE),
        ("byEnhancedMode", h_BYTE),
        ("byDynamicContrastEN", h_BYTE),
        ("byDynamicContrast", h_BYTE),
        ("byJPEGQuality", h_BYTE),
        ("struCmosModeCfg", NET_DVR_CMOSMODECFG),
        ("byFilterSwitch", h_BYTE),
        ("byFocusSpeed", h_BYTE),
        ("byAutoCompensationInterval", h_BYTE),
        ("bySceneMode", h_BYTE),
    ]


class NET_DVR_TIME(Structure):
    _fields_ = [
        ("dwYear", h_DWORD),
        ("dwMonth", h_DWORD),
        ("dwDay", h_DWORD),
        ("dwHour", h_DWORD),
        ("dwMinute", h_DWORD),
        ("dwSecond", h_DWORD),
    ]
