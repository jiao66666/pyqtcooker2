BOARDTYPE_FEEDER = 1     # 加料板
BOARDTYPE_FIVE_AXIS = 2  # 五轴板
BOARDTYPE_DC = 3         # 直流板


POT1_MOVE_MOTOR = 2  # 1号锅移动电机编号
POT1_FLIP_MOTOR = 1  # 1号锅翻转电机编号
POT2_MOVE_MOTOR = 4  # 2号锅移动电机编号
POT2_FLIP_MOTOR = 3  # 2号锅翻转电机编号



POT1_POS_OUTFOOD_FLIP  = 10  # 1号锅外倒菜位,翻转位
POT1_POS_OUTFOOD_LEVEL = 4.16  # 1号锅外倒菜位，水平位
POT1_POS_INFOOD_FLIP  = 5.05  # 1号锅内倒菜位,翻转位
POT1_POS_INFOOD_LEVEL = 4.16  # 1号锅内倒菜位，水平位
POT1_POS_WASHPOT_FLIP  = -11.8  # 1号锅洗锅位,翻转位
POT1_POS_WASHPOT_LEVEL = 4.16  # 1号锅洗锅位，水平位
POT1_POS_FIREPOT_FLIP  = 0  # 1号锅烧菜位,翻转位
POT1_POS_FIREPOT_LEVEL = 0  # 1号锅烧菜位，水平位

POT_POS_SAFE_FLIP = 5.05  # 锅移动安全位,翻转位


MICRO_STEP = 128  #当前步进电机细分
FB_CHECK_INTERVAL = 0.05        #坐标反馈检查间隔  #0.1 isOK
MTSTATUS_CHECK_INTERVAL = 0.05  #电机状态检查间隔  #0.2 isOK
ADJUSTSPEED_INTERVAL = 0.05      #动态调速间隔
ACC_BOUND = 0.4  #曲线运动加速度开始位置百分比
DEC_BOUND = 0.8  #减速运动减速开始位置百分比

FLIP_EXITPOS = 1.0  #翻转同步退出位置
MOVE_EXITPOS = 2.5  #移动同步退出位置
