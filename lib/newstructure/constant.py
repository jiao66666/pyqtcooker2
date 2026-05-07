BOARDTYPE_FEEDER = 1     # 加料板
BOARDTYPE_FIVE_AXIS = 2  # 五轴板
BOARDTYPE_DC = 3         # 直流板


POT1_MOVE_MOTOR = 2  # 1号锅移动电机编号
POT1_FLIP_MOTOR = 1  # 1号锅翻转电机编号
POT2_MOVE_MOTOR = 4  # 2号锅移动电机编号
POT2_FLIP_MOTOR = 3  # 2号锅翻转电机编号

MOTOR_LIST = [POT1_MOVE_MOTOR,POT1_FLIP_MOTOR,POT2_MOVE_MOTOR,POT2_FLIP_MOTOR]

POT1_SPIN_MOTOR = 0  # 1号锅旋转DC电机编号
POT2_SPIN_MOTOR = 1  # 2号锅旋转DC电机编号

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
    }
}

TIMEOUT = 60 #电机单步动作超时