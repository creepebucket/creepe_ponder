from SNBT import SNBTCompound

from ..formats import *
from ..ponder import Ponder
from ..utils import euler_to_quaternion


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

    if size < 9:  # 小型棋盘格
        for x in range(size):
            for z in range(size):
                pos = (x, 0, z)

                if x % 2 == z % 2:  # 若xz坐标奇偶相同则为白色方块
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

        for x in range(size):
            for z in range(size):
                pos = (x, 0, z)
                chunkx = int(x / 3)
                chunkz = int(z / 3)

                if chunkx % 2 == chunkz % 2:  # 若区块坐标奇偶相同则为白色区块
                    if x % 3 == 1 and z % 3 == 1:  # 若坐标在白色区块中心则为黑色方块
                        world[pos] = {"block": "minecraft:light_gray_concrete", "state": {}, "nbt": ""}
                        commands.append({0, setblock_cmd.format(
                            x=x + x_offset,
                            y=0 + y_offset,
                            z=z + z_offset,
                            block_name="minecraft:light_gray_concrete",
                            block_state_stripped="",
                            nbt="")})
                    else:  # 若坐标不在中心则为白色方块
                        world[pos] = {"block": "minecraft:snow_block", "state": {}, "nbt": ""}
                        commands.append({0, setblock_cmd.format(
                            x=x + x_offset,
                            y=0 + y_offset,
                            z=z + z_offset,
                            block_name="minecraft:snow_block",
                            block_state_stripped="",
                            nbt="")})
                else:  # 若区块坐标奇偶不同则为黑色区块
                    if x % 3 == 1 and z % 3 == 1:  # 若坐标在黑色区块中心则为白色方块
                        world[pos] = {"block": "minecraft:snow_block", "state": {}, "nbt": ""}
                        commands.append({0, setblock_cmd.format(
                            x=x + x_offset,
                            y=0 + y_offset,
                            z=z + z_offset,
                            block_name="minecraft:snow_block",
                            block_state_stripped="",
                            nbt="")})
                    else:  # 若坐标不在中心则为黑色方块
                        world[pos] = {"block": "minecraft:light_gray_concrete", "state": {}, "nbt": ""}
                        commands.append({0, setblock_cmd.format(
                            x=x + x_offset,
                            y=0 + y_offset,
                            z=z + z_offset,
                            block_name="minecraft:light_gray_concrete",
                            block_state_stripped="",
                            nbt="")})

    # 重放操作
    logger.debug(f"正在重放{len(ponder.commands)}条操作...")

    for i in ponder.commands:
        if i['type'] == "place":  # 放置方块
            pos = (i['pos'][0], i['pos'][1], i['pos'][2])
            state_snbt = SNBTCompound(i['state']).dump()
            state_stripped = state_snbt[1:-1]  # 去除{}
            nbt_snbt_str = SNBTCompound(i['nbt']).dump()
            block = 'minecraft:' + i['block'] if len(i['block'].split(':')) == 1 else i['block']  # 检查命名空间

            if world.get(pos) is None or world.get(pos)['block'] != block:  # 如果方块改变则播放动画
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

            # 需要确保方块被放置
            commands.append([i['time'] + 2, setblock_cmd.format(
                x=i['pos'][0] + x_offset,
                y=i['pos'][1] + y_offset,
                z=i['pos'][2] + z_offset,
                block_name='air',
                block_state_stripped="",
                nbt="")])

            commands.append([i['time'] + 2, setblock_cmd.format(
                x=i['pos'][0] + x_offset,
                y=i['pos'][1] + y_offset,
                z=i['pos'][2] + z_offset,
                block_name=block,
                block_state_stripped=state_stripped.replace(':"', '="'),
                nbt=nbt_snbt_str)])

            # 更新世界
            world[pos] = {"block": block, "state": i['state'], "nbt": i['nbt']}

        elif i['type'] == "remove":  # 移除方块
            pos = (i['pos'][0], i['pos'][1], i['pos'][2])
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
            pos = (i['pos'][0], i['pos'][1], i['pos'][2])

            # 将旋转转化为四元数
            # 语法检查: yaw pitch roll取值
            yaw, pitch, roll = i['rotation']

            logger.error(
                f"语法错误! 文字{i['text']}(在{i['time']}生成, 坐标为{pos})的偏转角为{i['rotation'][0]}, 不符合0~360度的"
                f"范围, 可能无法渲染!") if not 0 <= yaw <= 360 else 0
            logger.error(
                f"语法错误! 文字{i['text']}(在{i['time']}生成, 坐标为{pos})的俯仰角为{i['rotation'][1]}, 不符合-90~90度的"
                f"范围, 可能无法渲染!") if not -90 <= pitch <= 90 else 0
            logger.error(
                f"语法错误! 文字{i['text']}(在{i['time']}生成, 坐标为{pos})的横滚角为{i['rotation'][2]}, 不符合-180~180度"
                f"的范围, 可能无法渲染!") if not -180 <= roll <= 180 else 0
            rotation = euler_to_quaternion(i['rotation'])

            # 显示文字
            commands.append([i['time'], text_display_cmd.format(
                x=pos[0] + x_offset,
                y=pos[1] + y_offset,
                z=pos[2] + z_offset,
                text=i['text'],
                tag=i['time'] + i['duration'],
                rotation=rotation)])

            # 执行清除
            command = f"kill @e[tag={i['time'] + i['duration']}]"
            commands.append([i['time'] + i['duration'], command])

        elif i['type'] == "entity":  # 生成实体
            pos = (i['pos'][0], i['pos'][1], i['pos'][2])

            commands.append([i['time'], summon_cmd.format(
                x=pos[0] + x_offset,
                y=pos[1] + y_offset,
                z=pos[2] + z_offset,
                entity_name=i['name'],
                nbt=SNBTCompound(i['nbt']).dump())])

        elif i['type'] == "command":  # 执行自定义指令
            command = i['command']

            if '<' in command and '>' in command:
                # 将用<>包裹的坐标进行转义, 添加偏移坐标
                start_index = command.find('<') + 1  # 去除"<"字符
                end_index = command.find('>')
                coord_str = command[start_index:end_index]
                x, y, z = coord_str.split(' ')

                x, y, z = int(x) + x_offset, int(y) + y_offset, int(z) + z_offset

                command = command.replace(f"<{coord_str}>", f"{x} {y} {z}")

            commands.append([i['time'], command])

    logger.info(f"已将 {len(ponder.commands)} 条操作编译为 {len(commands)} 条指令.")
    return commands
