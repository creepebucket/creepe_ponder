from .formats import logger


class Ponder:
    """ 创建一个思索类, 用于记录用户每一步的操作, 并在编译器中重放并编译为Minecraft命令. """

    def __init__(self, size: int):
        """
        初始化思索类, 并生成棋盘格地板.
        :param size: 边长
        """

        if size > 8 and size % 3 != 0:
            logger.critical('初始化思索失败: 边长超过7的大型棋盘格尺寸应为3的倍数')

        self.size = size
        self.commands = []  # 记录用户的命令

    def block(self, time: int, pos: tuple, block: str, state: dict = {}, nbt: dict = {}):
        """
        对一个方块进行放置, 也可以替换同一个方块或改变其状态.
        :param time: 放置时间, 单位为rt(红石刻, 1/10秒)
        :param pos: (x, y, z) 坐标 地板位置x, y, z轴最小处为(0, 0, 0)
        :param block: 方块名称, 'minecraft:'可省略
        :param state: 方块状态, 如 {'facing': 'north'}
        :param nbt: 方块NBT数据, 如 {'CustomName': 'My Entity'}
        """

        self.commands.append({
            'type': 'place',
            'time': time,
            'pos': pos,
            'block': block,
            'state': state,
            'nbt': nbt
        })

    def remove(self, time: int, pos: tuple, animation: str = 'y+'):
        """
        对一个方块进行移除.
        :param time: 移除时间, 单位为rt(红石刻, 1/10秒)
        :param pos: (x, y, z) 坐标 地板位置x, y, z轴最小处为(0, 0, 0)
        :param animation: 移除动画, 可选: 'y+', 'x+', 'x-', 'z+', 'z-', 'destroy'
        """

        self.commands.append({
            'type': 'remove',
            'time': time,
            'pos': pos,
            'animation': animation
        })

    def text(self, time: int, pos: tuple, text: str, duration: int = 20, rotation: list = [0, 0, 0]):
        """
        显示一段文字.
        :param time: 显示时间, 单位为rt(红石刻, 1/10秒)
        :param pos: (x, y, z) 坐标 地板位置x, y, z轴最小处为(0, 0, 0)
        :param text: 文字内容
        :param rotation: (yaw, pitch, roll) 旋转角度, 单位为度(°)
        :param duration: 持续时间, 单位为rt(红石刻, 1/10秒)
        """

        self.commands.append({
            'type': 'text',
            'time': time,
            'pos': pos,
            'text': text,
            'rotation': rotation,
            'duration': duration
        })

    def entity(self, time: int, pos: tuple, name: str, nbt: dict = {}):
        """
        生成一个实体.
        :param time: 显示时间, 单位为rt(红石刻, 1/10秒)
        :param pos: (x, y, z) 坐标 地板位置x, y, z轴最小处为(0, 0, 0)
        :param name: 实体名称, 如 'minecraft:cow'
        :param nbt: 实体NBT数据, 如 {'CustomName': 'My Cow'}
        """

        self.commands.append({
            'type': 'entity',
            'time': time,
            'pos': pos,
            'name': name,
            'nbt': nbt
        })

    def command(self, time: int, command: str):
        """
        执行一个自定义命令.
        注意: 在需要使用坐标的场景中, 需要使用<你的坐标>进行转义以支持坐标偏移, 如 tp 1 1 1 -> tp <1 1 1>
        :param time: 执行时间, 单位为rt(红石刻, 1/10秒)
        :param command: 要执行的命令, 如 'gamerule doDaylightCycle false' 不允许前导/
        """

        self.commands.append({
            'type': 'command',
            'time': time,
            'command': command
        })
