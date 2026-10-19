########电路板通用配置#########
BOARDTYPE_FEEDER = 1     # 加料板
BOARDTYPE_STEP = 2       # 锅步进板
BOARDTYPE_SPIN = 3       # 旋转板
BOARDTYPE_ICE  = 4       # 冰柜步进板

BOARD_NAME_MAP={
    "stepmotor":BOARDTYPE_STEP,
    "feedmotor":BOARDTYPE_FEEDER,
    "spinmotor":BOARDTYPE_SPIN,
    "icemotor":BOARDTYPE_ICE
}

# 电机类型 -> 控制板 ID
MOTOR_TYPE_BOARD_MAP = {
    "step_pot": BOARDTYPE_STEP,
    "spin_pot": BOARDTYPE_SPIN,
    "feeder_pot": BOARDTYPE_FEEDER,
    "ice_pot": BOARDTYPE_ICE,
}

########锅设置########
POT1 = 1
POT2 = 2


#######锅步进板配置######
POT_BACKUP_MOTOR=  0  # 空位
POT1_MOVE_MOTOR =  2  # 1号锅移动电机编号
POT1_FLIP_MOTOR =  1  # 1号锅翻转电机编号
POT2_MOVE_MOTOR =  4  # 2号锅移动电机编号
POT2_FLIP_MOTOR =  3  # 2号锅翻转电机编号

POT_MOTOR_LIST = [POT_BACKUP_MOTOR,POT1_MOVE_MOTOR,POT1_FLIP_MOTOR,POT2_MOVE_MOTOR,POT2_FLIP_MOTOR]

########冰柜步进配置#######
ICE_MOTOR_0 = 0 
ICE_MOTOR_1 = 1
ICE_MOTOR_2 = 2
ICE_MOTOR_3 = 3
ICE_MOTOR_4 = 4 

ICE_MOTOR_LIST = [ICE_MOTOR_0,ICE_MOTOR_1,ICE_MOTOR_2,ICE_MOTOR_3,ICE_MOTOR_4]



#########锅位置配置############
POT1_POS_OUTFOOD_FLIP  = 10  # 1号锅外倒菜位,翻转位
POT1_POS_OUTFOOD_LEVEL = 4.1  # 1号锅外倒菜位，水平位
POT1_POS_INFOOD_FLIP  = 4.5  # 1号锅内倒菜位,翻转位
POT1_POS_INFOOD_LEVEL = 4.1  # 1号锅内倒菜位，水平位
POT1_POS_WASHPOT_FLIP  = -10  # 1号锅洗锅位,翻转位
POT1_POS_WASHPOT_LEVEL = 4.1  # 1号锅洗锅位，水平位
POT1_POS_FIREPOT_FLIP  = 0  # 1号锅烧菜位,翻转位
POT1_POS_FIREPOT_LEVEL = 0  # 1号锅烧菜位，水平位
POT1_POS_DROPFOOD_FLIP  = 20 # 号锅最终倒菜位置
POT_POS_SAFE_FLIP1 = 4.5  # 锅移动安全位,翻转位

POT2_POS_OUTFOOD_FLIP  = 10  # 2号锅外倒菜位,翻转位
POT2_POS_OUTFOOD_LEVEL = 3.9  # 2号锅外倒菜位，水平位
POT2_POS_INFOOD_FLIP  = 5.0  # 2号锅内倒菜位,翻转位
POT2_POS_INFOOD_LEVEL = 3.9  # 2号锅内倒菜位，水平位
POT2_POS_WASHPOT_FLIP  = -10  # 2号锅洗锅位,翻转位
POT2_POS_WASHPOT_LEVEL = 3.9  # 2号锅洗锅位，水平位
POT2_POS_FIREPOT_FLIP  = 0  # 2号锅烧菜位,翻转位
POT2_POS_FIREPOT_LEVEL = 0  # 2号锅烧菜位，水平位
POT2_POS_DROPFOOD_FLIP  = 20 # 号锅最终倒菜位置
POT_POS_SAFE_FLIP2 = 5.0  # 锅移动安全位,翻转位


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


FEED_MOTOR_LIST = [
    POT1_FLAVORMOTOR1,
    POT1_FLAVORMOTOR2,
    POT1_FLAVORMOTOR3,
    POT1_FLAVORMOTOR4,
    POT1_FLAVORMOTOR5,
    POT1_FLAVORMOTOR6,
    POT1_FLAVORMOTOR7,
    POT1_FLAVORMOTOR8,
    POT1_FLAVORMOTOR9,
    POT1_FLAVORMOTOR10,
    POT1_FLAVORMOTOR11,
    POT1_FLAVORMOTOR12,

    POT2_FLAVORMOTOR13,
    POT2_FLAVORMOTOR14,
    POT2_FLAVORMOTOR15,
    POT2_FLAVORMOTOR16,
    POT2_FLAVORMOTOR17,
    POT2_FLAVORMOTOR18,
    POT2_FLAVORMOTOR19,
    POT2_FLAVORMOTOR20,
    POT2_FLAVORMOTOR21,
    POT2_FLAVORMOTOR22,
    POT2_FLAVORMOTOR23,
    POT2_FLAVORMOTOR24,
]


########DC旋转板配置######
POT1_SPIN_MOTOR = 0  # 1号锅旋转DC电机编号
POT2_SPIN_MOTOR = 1  # 2号锅旋转DC电机编号

SPIN_MOTOR_LIST = [POT1_SPIN_MOTOR,POT2_SPIN_MOTOR]


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



#动作组->子动作参数Key 映射  【参数说明】"h":水平步进电机，"v":垂直步进电机, "s":旋转DC电机 ，"f":加料电机
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
       ("h","move_in_tofirefood"),
       ("v","flip_in_tofirefood")
    ],
    "take_fire_pour":[
        ("h", "move_in_tofirefood"),
        ("v", "flip_in_tofirefood"),
        ("v", "flip_out_togetfood"),
        ("h", "move_out_togetfood", [
            ("h", "move_to_wait"),
            ("h", "move_to_track"),
        ]),
        ("h", "move_in_tofirefood"),
        ("v", "flip_in_tofirefood"),
        ("v", "flip_out_togetfood"),
        ("h", "move_out_togetfood", [
            ("h", "move_to_wait"),
            ("h", "move_to_track"),
        ]),
        ("v", "flip_out_pour"),
        ("v", "flip_in_wash"),
        ("v", "flip_out_getfood"),
        ("h", "move_in_tofirefood"),
        ("v", "flip_in_tofirefood")
    ],
    "go_to_pos_outfood":[
        ("v","flip_to_safepos"),
        ("h","move_out_togetfood", [
            ("h", "move_to_wait"),
            ("h", "move_to_track"),
        ]),
        ("v","flip_to_outfood")
    ],
    "go_to_pos_infood":[
        ("v","flip_to_safepos"),
        ("h","move_out_togetfood", [
            ("h", "move_to_wait"),
            ("h", "move_to_track"),
        ]),
        ("v","flip_to_infood")
    ],
    "go_to_pos_washpot":[
        ("v","flip_to_safepos"),
        ("h","move_out_togetfood", [
            ("h", "move_to_wait"),
            ("h", "move_to_track"),
        ]),
        ("v","flip_to_washpot")
    ],
    "go_to_pos_firepot":[
        ("v","flip_to_safepos"),
        ("h","move_in_tofirefood", [
            ("h", "move_to_wait"),
            ("h", "move_to_track"),
        ]),
        ("v","flip_in_firepot")
    ],
    "test_movemove":[
        ("h","move_out"),
        ("h","move_zero")
    ],
    "test_moveflip":[
        ("v","flip_out"),
        ("h","move_out")
    ],
    "test_moveflip_reset":[
        ("h","move_zero"),
        ("v","flip_zero")
    ],
    "test_all":[
        ("v","flip_out"),
        ("h","move_out"),
        ("h","move_zero"),
        ("v","flip_zero"),
        ("v","flip_out"),
        ("h","move_out"),
        ("v","flip_pour"),
        ("v","flip_wash"),
        ("v","flip_out"),
        ("h","move_zero"),
        ("v","flip_zero")
    ],
    "test_move_spin":[
        ("h","move_out"),
        ("s","spin_for_wash"),
        ("h","move_zero")
    ]
}


#连续自动动作参数配置
BASE_SPEED = 360  
POT1_VSAFE_POS = 4.5
POT2_VSAFE_POS = 5.0
POT1_HSAFE_POS = 4.1
POT2_HSAFE_POS = 3.9
POT1_WAIT_POS  = 1.5
POT2_WAIT_POS  = 1
POT_POUR_POS   = 20
POT_WASH_POS   = -10
POT_RESET_POS  = 0
POT_INTAKE_POS   = 10

#子动作参数KEY->命令参数 映射
#varspeed 决定是否需要变速运行
#quitinadvance决定动作是否需要同时运行，而非串行运行（默认）
#pot_params决定1，2锅具体参数的覆盖
ACTION_PARAMS_CONFIG = {
    "flip_out_togetfood": {
        "speed": BASE_SPEED,
        "target": POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_VSAFE_POS
            },
            2: {
                "target": POT2_VSAFE_POS
            }
        }
    },
    "move_out_togetfood": {
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_HSAFE_POS
            },
            2: {
                "target": POT2_HSAFE_POS
            }
        }
    },
    "move_to_wait": {
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_WAIT_POS
            },
            2: {
                "target": POT2_WAIT_POS
            }
        }
    },
    "move_to_track": {
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_HSAFE_POS
            },
            2: {
                "target": POT2_HSAFE_POS
            }
        }
    },
    "move_in_tofirefood": {
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_in_tofirefood": {
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_out_pour": {
        "speed": BASE_SPEED,
        "target":POT_POUR_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_in_wash": {
        "speed": BASE_SPEED,
        "target":POT_WASH_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_out_getfood": {
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_VSAFE_POS
            },
            2: {
                "target": POT2_VSAFE_POS
            }
        }
    },
    "flip_to_safepos":{
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_VSAFE_POS
            },
            2: {
                "target": POT2_VSAFE_POS
            }
        }
    },

    "flip_to_outfood":{
        "speed": BASE_SPEED,
        "target":POT_POUR_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_to_infood":{
        "speed": BASE_SPEED,
        "target":POT_INTAKE_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_to_washpot":{
        "speed": BASE_SPEED,
        "target":POT_WASH_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_in_firepot":{
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "move_out":{
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_HSAFE_POS
            },
            2: {
                "target": POT2_HSAFE_POS
            }
        }
    },
    "move_zero":{
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_out":{
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0,
        "pot_params": {
            1: {
                "target": POT1_VSAFE_POS
            },
            2: {
                "target": POT2_VSAFE_POS
            }
        }
    },
    "flip_zero":{
        "speed": BASE_SPEED,
        "target":POT_RESET_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_pour":{
        "speed": BASE_SPEED,
        "target":POT_POUR_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "flip_wash":{
        "speed": BASE_SPEED,
        "target":POT_WASH_POS,
        "varspeed":False,
        "quitinadvance":0
    },
    "spin_for_wash":{
        "duration": 10000,
        "speed": 1000,
        "direction":1
    },
    "spin_for_fire":{
        "duration":100000,
        "speed": 500,
        "direction":-1
    }
}


# 不允许进行参数覆盖的动作白名单
ACTION_OVERRIDE_WHITE_LIST = {
    "move_to_wait",
    "move_to_track",
}


TIMEOUT = 60 #电机单步动作超时,单位秒

# 优先级定义（越小越优先）
PRIORITY_EMERGENCY = 0
PRIORITY_CONTROL = 1
PRIORITY_NORMAL = 2

#RS485最大队列命令缓冲数量
MAX_CMD_NUMS = 2000

#开发测试环境端口配置
DEV_STEP_PORT = "COM2"
DEV_FEED_PORT = "COM3"
DEV_SPIN_PORT = "COM4"
DEV_ICE_PORT  = "COM5"


#生产环境端口波动率设置
STEP_BAUT_RATE = 115200
FEED_BAUT_RATE = 9600
STEP_PORT   = "COM6"
FEED_PORT   = "COM7"
SPIN_PORT   = "COM8"
ICE_PORT    = "COM11"

POT_STATEMACHINE_INTERVAL = 0.05  #锅状态机主循环频率
BOARD_TIMEOUT = 1.0  # 生产环境可修改为1.0
MOTION_INTERVAL = 0.05  #动态调速度等参数控制器
MOCK_INTERVAL = 0.05   #模拟频率

STEP_POLLING_INTERVAL = 0.1   #步进电机轮询间隔时间
SPIN_POLLING_INTERVAL = 0.1   #旋转电机轮询间隔时间
FEEDER_POLLING_INTERVAL = 0.1 #加料电机轮询间隔时间
ICE_POLLING_INTERVAL  = 0.1   #冰柜电机轮询间隔时间

VAR_MIN_SPEED = 100
VAR_MAX_SPEED = 300