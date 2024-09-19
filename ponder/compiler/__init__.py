from SNBT import SNBTCompound

from ponder import Ponder
from ponder.formats import *

logger = get_logger()


def compile_operations(ponder: Ponder, pos_offset: tuple = (0, 0, 0)) -> list:
    """
    编译你的思索对象为Minecraft指令
    :param ponder: 你的思索对象
    :param pos_offset: 偏移坐标
    :return: 指令列表和执行时间
    """
    logger.info("正在编译思索对象为指令...")

    world = {}  # 模拟世界
    commands = []  # 指令列表
    x_offset, y_offset, z_offset = pos_offset  # 偏移坐标

    # 生成思索地板
    size = ponder.size

    if size < 8:  # 小型棋盘格
        for x in range(size):
            for z in range(size):
                pos = (x, 0, z)

                if (x % 2 == 0 and z % 2 == 0) or (x % 2 == 1 and z % 2 == 1):  # 若xz坐标奇偶相同则为白色方块
                    world[pos] = {"block": "minecraft:snow_block", "state": {}, "nbt": ""}
                    commands.append({0, setblock_cmd.format(
                        x=x + x_offset,
                        y=0 + y_offset,
                        z=z + z_offset,
                        block_name="minecraft:snow_block",
                        block_state_stripped="",
                        nbt="")})
                else:  # 若坐标奇偶不同则为黑色方块
                    world[pos] = {"block": "minecraft:light_gray_concrete", "state": {}, "nbt": ""}
                    commands.append({0, setblock_cmd.format(
                        x=x + x_offset,
                        y=0 + y_offset,
                        z=z + z_offset,
                        block_name="minecraft:light_gray_concrete",
                        block_state_stripped="",
                        nbt="")})

    else:  # 大型棋盘格
        pass

        # TODO: 大型棋盘格生成

    # 重放操作
    logger.debug(f"正在重放{len(ponder.commands)}条操作...")

    for i in ponder.commands:
        pos = (i['pos'][0], i['pos'][1], i['pos'][2])

        if i['type'] == "place":  # 放置方块
            state_snbt = SNBTCompound(i['state']).dump()
            state_stripped = state_snbt[1:-1]  # 去除{}
            nbt_snbt_str = SNBTCompound(i['nbt']).dump()
            block = 'minecraft:' + i['block'] if len(i['block'].split(':')) == 1 else i['block']  # 检查命名空间

            if world.get(pos):  # 检查方块是否存在
                # 若存在则直接替换方块

                commands.append([i['time'], setblock_cmd.format(
                    x=i['pos'][0] + x_offset,
                    y=i['pos'][1] + y_offset,
                    z=i['pos'][2] + z_offset,
                    block_name='air',
                    block_state_stripped="",
                    nbt="")])

                commands.append([i['time'], setblock_cmd.format(
                    x=i['pos'][0] + x_offset,
                    y=i['pos'][1] + y_offset,
                    z=i['pos'][2] + z_offset,
                    block_name=block,
                    block_state_stripped=state_stripped.replace(':"', '="'),
                    nbt=nbt_snbt_str)])

                # 更新世界
                world[pos] = {"block": block, "state": i['state'], "nbt": i['nbt']}

            else:  # 若不存在则放置方块
                # 如果方块下方不存在方块则放置一个屏障
                if world.get((i['pos'][0], i['pos'][1] - 1, i['pos'][2])) is None:
                    commands.append([i['time'], setblock_cmd.format(
                        x=i['pos'][0] + x_offset,
                        y=i['pos'][1] + y_offset - 1,
                        z=i['pos'][2] + z_offset,
                        block_name="minecraft:barrier",
                        block_state_stripped="",
                        nbt="")])

                    world[(i['pos'][0], i['pos'][1] - 1, i['pos'][2])] = \
                        {"block": "minecraft:barrier", "state": {}, "nbt": ""}

                commands.append([i['time'], falling_block_cmd.format(
                    x=i['pos'][0] + x_offset,
                    y=i['pos'][1] + y_offset + 0.3,
                    z=i['pos'][2] + z_offset,
                    block_name=block,
                    block_state=state_stripped,
                    nbt=nbt_snbt_str,
                    motion_x=0.0,
                    motion_y=-0.1,
                    motion_z=0.0)])

                # 更新世界
                world[pos] = {"block": block, "state": i['state'], "nbt": i['nbt']}

        elif i['type'] == "remove":  # 移除方块
            if world.get(pos):  # 检查方块是否存在
                # 若存在则移除方块

                if i['animation'] == "destroy":  # 若动画效果为destroy则播放动画
                    command = setblock_cmd.format(
                        x=i['pos'][0] + x_offset,
                        y=i['pos'][1] + y_offset,
                        z=i['pos'][2] + z_offset,
                        block_name="air",
                        block_state_stripped="",
                        nbt="") + " destroy"

                    commands.append([i['time'], command])

                else:
                    # 添加动画效果
                    animation_map = {
                        "y+": (0.0, 0.2, 0.0),
                        "x+": (0.2, 0.0, 0.0),
                        "x-": (-0.2, 0.0, 0.0),
                        "z+": (0.0, 0.0, 0.2),
                        "z-": (0.0, 0.0, -0.2),
                    }

                    state_snbt = SNBTCompound(world[pos]['state']).dump()
                    state_stripped = state_snbt[1:-1]  # 去除{}
                    nbt_snbt_str = SNBTCompound(world[pos]['nbt']).dump()
                    block = 'minecraft:' + world[pos]['block'] if len(world[pos]['block'].split(':')) == 1 \
                        else world[pos]['block']  # 检查命名空间

                    if i['animation'] in animation_map:  # 若有动画效果则播放动画

                        commands.append([i['time'], falling_block_cmd.format(
                            x=i['pos'][0] + x_offset,
                            y=i['pos'][1] + y_offset,
                            z=i['pos'][2] + z_offset,
                            block_name=block,
                            block_state=state_stripped,
                            nbt=nbt_snbt_str,
                            motion_x=float(animation_map[i['animation']][0]),
                            motion_y=float(animation_map[i['animation']][1]),
                            motion_z=float(animation_map[i['animation']][2]))])

                # 更新世界和清除方块
                commands.append([i['time'], setblock_cmd.format(
                    x=i['pos'][0] + x_offset,
                    y=i['pos'][1] + y_offset,
                    z=i['pos'][2] + z_offset,
                    block_name="air",
                    block_state_stripped="",
                    nbt="")])

                del world[pos]

        elif i['type'] == "text":  # 显示文字

            # 显示文字
            commands.append([i['time'], text_display_cmd.format(
                x=i['pos'][0] + x_offset,
                y=i['pos'][1] + y_offset,
                z=i['pos'][2] + z_offset,
                text=i['text'],
                tag=i['time'] + i['duration'],
                deflection=i['rotation'][0],
                pitch=i['rotation'][1],)])

            # 执行清除
            command = f"kill @e[tag={i['time'] + i['duration']}]"
            commands.append([i['time'] + i['duration'], command])

    logger.info(f"已将{len(ponder.commands)}条操作编译为{len(commands)}条指令.")
    return commands
