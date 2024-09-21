"""
    此文件用于定义格式化字符串, 如指令格式
"""
import logging

from colorama import Fore, Style

from ponder.formats import *

""" 彩色日志格式 """


class CustomColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def __init__(self, custom_text, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.custom_text = custom_text

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        # 紫色自定义文本
        custom_text_colored = Fore.MAGENTA + self.custom_text + Style.RESET_ALL
        # 青色时间
        time_colored = Fore.CYAN + self.formatTime(record, self.datefmt) + Style.RESET_ALL
        # 日志等级颜色
        levelname_colored = level_color + record.levelname + Style.RESET_ALL
        # 内容颜色
        message_color = level_color if record.levelno >= logging.WARNING else Fore.WHITE

        # 白色符号
        white_symbols = Fore.WHITE
        reset_color = Style.RESET_ALL

        # 构建最终的日志格式
        log_message = (f"{custom_text_colored} {white_symbols}| {time_colored} {white_symbols}[{levelname_colored}"
                       f"{white_symbols}] {message_color}{record.getMessage()}{reset_color}")
        return log_message


# 创建一个logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 创建一个formatter，设置日志格式和颜色
formatter = CustomColorFormatter(custom_text="CreepePonder", datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)

# 添加handler到logger中
logger.addHandler(ch)


def get_logger():
    return logger


""" 指令格式 """

falling_block_cmd = (
    'summon falling_block {x} {y} {z} {{BlockState:{{Name:"{block_name}",Properties:{{{block_state}}}'
    '}},TileEntityData:{nbt},NoGravity:1b,Time:596,Motion:[{motion_x},{motion_y},{motion_z}]}}'
)
setblock_cmd = 'setblock {x} {y} {z} {block_name}[{block_state_stripped}]{nbt}'
summon_cmd = 'summon {entity_name} {x} {y} {z} {nbt}'
text_display_cmd = (
    'summon text_display {x} {y} {z} {{text:\'"{text}"\',Tags:["{tag}"],see_through:1b,transformation:'
    '{{left_rotation: {rotation}, translation: [0, 0, 0], right_rotation: [0, 0, 0, 1], scale: [1, 1'
    ', 1]}}}}'
)
