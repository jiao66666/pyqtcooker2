########电路板通用配置#########
BOARDTYPE_FEEDER = 1     # 加料板
BOARDTYPE_FIVE_AXIS = 2  # 五轴板
BOARDTYPE_DC = 3         # 直流板

BOARDLIST =[
    {"name":"stepmotor","port":"COM2","baudrate":19200,"timeout":1.0,"board_id":BOARDTYPE_FIVE_AXIS},
    {"name":"feedermotor","port":"COM3","baudrate":19200,"timeout":1.0,"board_id":BOARDTYPE_FEEDER},
    {"name":"spinmotor","port":"COM4","baudrate":19200,"timeout":1.0,"board_id":BOARDTYPE_DC}
]

#######步进板配置######
POT_BACKUP_MOTOR= 0  # 1号锅移动电机编号
POT1_MOVE_MOTOR = 2  # 1号锅移动电机编号
POT1_FLIP_MOTOR = 1  # 1号锅翻转电机编号
POT2_MOVE_MOTOR = 4  # 2号锅移动电机编号
POT2_FLIP_MOTOR = 3  # 2号锅翻转电机编号

MOTOR_LIST = [POT_BACKUP_MOTOR,POT1_MOVE_MOTOR,POT1_FLIP_MOTOR,POT2_MOVE_MOTOR,POT2_FLIP_MOTOR]

POT1_POS_OUTFOOD_FLIP  = 10  # 1号锅外倒菜位,翻转位
POT1_POS_OUTFOOD_LEVEL = 4.16  # 1号锅外倒菜位，水平位
POT1_POS_INFOOD_FLIP  = 4.60  # 1号锅内倒菜位,翻转位
POT1_POS_INFOOD_LEVEL = 4.16  # 1号锅内倒菜位，水平位
POT1_POS_WASHPOT_FLIP  = -11.5  # 1号锅洗锅位,翻转位
POT1_POS_WASHPOT_LEVEL = 4.16  # 1号锅洗锅位，水平位
POT1_POS_FIREPOT_FLIP  = 0  # 1号锅烧菜位,翻转位
POT1_POS_FIREPOT_LEVEL = 0  # 1号锅烧菜位，水平位
POT1_POS_DROPFOOD_FLIP  = 20.2 # 号锅最终倒菜位置
POT_POS_SAFE_FLIP1 = 4.60  # 锅移动安全位,翻转位

POT2_POS_OUTFOOD_FLIP  = 10  # 2号锅外倒菜位,翻转位
POT2_POS_OUTFOOD_LEVEL = 4.14  # 2号锅外倒菜位，水平位
POT2_POS_INFOOD_FLIP  = 5.03  # 2号锅内倒菜位,翻转位
POT2_POS_INFOOD_LEVEL = 4.14  # 2号锅内倒菜位，水平位
POT2_POS_WASHPOT_FLIP  = -10.9  # 2号锅洗锅位,翻转位
POT2_POS_WASHPOT_LEVEL = 4.14  # 2号锅洗锅位，水平位
POT2_POS_FIREPOT_FLIP  = 0  # 2号锅烧菜位,翻转位
POT2_POS_FIREPOT_LEVEL = 0  # 2号锅烧菜位，水平位
POT2_POS_DROPFOOD_FLIP  = 20.2 # 号锅最终倒菜位置
POT_POS_SAFE_FLIP2 = 5.03  # 锅移动安全位,翻转位


#######加料板配置###########

POT1_FLAVORMOTOR1 = 1
POT1_FLAVORMOTOR2 = 2
POT1_FLAVORMOTOR3 = 3
POT1_FLAVORMOTOR4 = 4
POT1_FLAVORMOTOR5 = 5
POT1_FLAVORMOTOR6 = 6
POT1_FLAVORMOTOR7 = 7
POT1_FLAVORMOTOR8 = 8
POT1_FLAVORMOTOR9 = 9
POT1_FLAVORMOTOR10 = 10
POT1_FLAVORMOTOR11 = 11
POT1_FLAVORMOTOR12 = 12

POT2_FLAVORMOTOR13 = 13
POT2_FLAVORMOTOR14 = 14
POT2_FLAVORMOTOR15 = 15
POT2_FLAVORMOTOR16 = 16
POT2_FLAVORMOTOR17 = 17
POT2_FLAVORMOTOR18 = 18
POT2_FLAVORMOTOR19 = 19
POT2_FLAVORMOTOR20 = 20
POT2_FLAVORMOTOR21 = 21
POT2_FLAVORMOTOR22 = 22
POT2_FLAVORMOTOR23 = 23
POT2_FLAVORMOTOR24 = 24



########DC旋转板配置######
POT1_SPIN_MOTOR = 0  # 1号锅旋转DC电机编号
POT2_SPIN_MOTOR = 1  # 2号锅旋转DC电机编号




########其它配置###########

RESET_PULSES = 3200000 #复位给的脉冲数
MICRO_STEP = 128  #当前步进电机细分
FB_CHECK_INTERVAL = 0.05        #坐标反馈检查间隔  #0.1 isOK
MTSTATUS_CHECK_INTERVAL = 0.05  #电机状态检查间隔  #0.2 isOK
ADJUSTSPEED_INTERVAL = 0.05      #动态调速间隔
ACC_BOUND = 0.4  #曲线运动加速度开始位置百分比
DEC_BOUND = 0.8  #减速运动减速开始位置百分比

FLIP_EXITPOS = 1.0  #翻转同步退出位置
MOVE_EXITPOS = 2.8  #移动同步退出位置
FLIP_EXITPOS2 = 4.0 #洗锅翻转退出位置

POT1_WAIT_LEVEL = 3.0  #1号锅阻塞时等待水平位置
POT2_WAIT_LEVEL = 3.0  #2号锅阻塞时等待水平位置


#动作组->子动作参数Key 映射 
ACTION_PARAMS_KEYLIST = {
    "takefood_fire": [
        ("v", "flip_out_togetfood"),
        ("h", "move_out_togetfood", [
            ("h", "move_to_wait"),
            ("h", "move_to_track"),
        ]),
        ("h", "move_in_tofirefood"),
        ("v", "flip_in_tofirefood"),
    ],
    "resetzero":[
       ("h","moveh_zero"),
       ("v","movev_zero")
    ]
}

#子动作参数KEY->命令参数 映射
ACTION_PARAMS_CONFIG = {
    "flip_out_togetfood_1": {
        "speed": 200,
        "target": 4.5,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_out_togetfood_1": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_to_wait_1": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_to_track_1": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_in_tofirefood_1": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_in_tofirefood_1": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_out_togetfood_2": {
        "speed": 200,
        "target": 4.5,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_out_togetfood_2": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_to_wait_2": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_to_track_2": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_in_tofirefood_2": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_in_tofirefood_2": {
        "speed": 1000,
        "target":4.6,
        "varspeed":False,
        "quitinadvance":0
    },
    "moveh_zero_1":{
        "speed": 10,
        "target":0,
        "varspeed":False,
        "quitinadvance":0
    },
    "moveh_zero_2":{
        "speed": 10,
        "target":0,
        "varspeed":False,
        "quitinadvance":0
    },
    "movev_zero_1":{
        "speed": 10,
        "target":0,
        "varspeed":False,
        "quitinadvance":0
    },
    "movev_zero_2":{
        "speed": 10,
        "target":0,
        "varspeed":False,
        "quitinadvance":0
    }
}

TIMEOUT = 60 #电机单步动作超时

# 优先级定义（越小越优先）
PRIORITY_EMERGENCY = 0
PRIORITY_CONTROL = 1
PRIORITY_NORMAL = 2