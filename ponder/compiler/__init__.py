from SNBT import SNBTCompound

from ponder import Ponder
from ponder.compiler.logger import get_logger

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
                pos_str = f"{x}, 0, {z}"

                if (x % 2 == 0 and z % 2 == 0) or (x % 2 == 1 and z % 2 == 1):  # 若xz坐标奇偶相同则为白色方块
                    world[pos_str] = {"block": "minecraft:snow_block", "state": {}, "nbt": ""}
                    commands.append({0, f"setblock {x + x_offset} "
                                        f"{0 + y_offset} "
                                        f"{z + z_offset} minecraft:snow_block"})
                else:  # 若坐标奇偶不同则为黑色方块
                    world[pos_str] = {"block": "minecraft:light_gray_concrete", "state": {}, "nbt": ""}
                    commands.append({0, f"setblock {x + x_offset} "
                                        f"{0 + y_offset} "
                                        f"{z + z_offset} minecraft:light_gray_concrete"})

    # TODO: 大型棋盘格生成

    # 重放操作
    logger.debug(f"正在重放{len(ponder.commands)}条操作...")

    for i in ponder.commands:
        pos_str = f"{i['pos'][0]}, {i['pos'][1]}, {i['pos'][2]}"

        if i['type'] == "place":  # 放置方块
            state_snbt_str = SNBTCompound(i['state']).dump()
            state_str = state_snbt_str[1:-1]  # 去除{}
            nbt_snbt_str = SNBTCompound(i['nbt']).dump()
            block = 'minecraft:' + i['block'] if len(i['block'].split(':')) == 1 else i['block']  # 检查命名空间

            if world.get(pos_str):  # 检查方块是否存在
                # 若存在则直接替换方块
                command = (f"setblock {i['pos'][0] + x_offset} "
                           f"{i['pos'][1] + y_offset} "
                           f"{i['pos'][2] + z_offset} air")

                commands.append([i['time'], command])

                command = (f"setblock {i['pos'][0] + x_offset} "
                           f"{i['pos'][1] + y_offset} "
                           f"{i['pos'][2] + z_offset} {block}"
                           f"[{state_str.replace(':"', '="')}]{nbt_snbt_str}")

                commands.append([i['time'], command])

                # 更新世界
                world[pos_str] = {"block": block, "state": i['state'], "nbt": i['nbt']}

            else:  # 若不存在则放置方块
                # 如果方块下方不存在方块则放置一个屏障
                if world.get(f"{i['pos'][0]}, {i['pos'][1] - 1}, {i['pos'][2]}") is None:
                    commands.append([i['time'], f"setblock {i['pos'][0] + x_offset} "
                                                f"{i['pos'][1] + y_offset - 1} "
                                                f"{i['pos'][2] + z_offset} minecraft:barrier"])

                    world[f"{i['pos'][0]}, {i['pos'][1] - 1}, {i['pos'][2]}"] = \
                        {"block": "minecraft:barrier", "state": {}, "nbt": ""}

                command = (f"summon falling_block {i['pos'][0] + x_offset} "
                           f"{i['pos'][1] + y_offset + 0.3} "
                           f"{i['pos'][2] + z_offset} ")

                # 添加方块状态
                command += '{BlockState:{Name:"' + block + '",Properties:' + state_snbt_str

                # 添加NBT
                command += "},TileEntityData:" + nbt_snbt_str

                command += ",NoGravity:1b,Motion:[0.0,-0.1,0.0]}"
                commands.append([i['time'], command])

                # 更新世界
                world[pos_str] = {"block": block, "state": i['state'], "nbt": i['nbt']}

        elif i['type'] == "remove":  # 移除方块
            if world.get(pos_str):  # 检查方块是否存在
                # 若存在则移除方块
                command = (f"setblock {i['pos'][0] + x_offset} "
                           f"{i['pos'][1] + y_offset} "
                           f"{i['pos'][2] + z_offset} air")

                command += " destroy" if i['animation'] == "destroy" else ""  # 若动画效果为destroy则添加destroy参数
                commands.append([i['time'], command])

                # 添加动画效果
                animation_map = {
                    "y+": '[0., 0.2, 0.]',
                    "y-": '[0., -0.2, 0.]',
                    "x+": '[0.2, 0., 0.]',
                    "x-": '[-0.2, 0., 0.]',
                    "z+": '[0., 0., 0.2]',
                    "z-": '[0., 0., -0.2]',
                }

                state_snbt_str = SNBTCompound(world[pos_str]['state']).dump()
                state_str = state_snbt_str[1:-1]  # 去除{}
                nbt_snbt_str = SNBTCompound(world[pos_str]['nbt']).dump()
                block = 'minecraft:' + world[pos_str]['block'] if len(world[pos_str]['block'].split(':')) == 1 \
                    else world[pos_str]['block']  # 检查命名空间

                if i['animation'] in animation_map:  # 若有动画效果则播放动画
                    command = (f"summon falling_block {i['pos'][0] + x_offset} "
                               f"{i['pos'][1] + y_offset} "
                               f"{i['pos'][2] + z_offset} " + "{BlockState:{Name:\"" + block + "\",Properties:{"
                               + state_str + "}}, TileEntityData:" + nbt_snbt_str + ", NoGravity:1b, "
                                                                                    "Time: 597, Motion:" +
                               animation_map[i['animation']] + "}")

                    commands.append([i['time'], command])
                # 更新世界
                del world[pos_str]

        elif i['type'] == "text":  # 显示文字

            # 显示文字
            command = (f"summon text_display {i['pos'][0] + x_offset} "
                       f"{i['pos'][1] + y_offset} "
                       f"{i['pos'][2] + z_offset} {{text:'\"{i['text']}\"', Tags:[\"{i['time'] + i['duration']}\"]"
                       f", see_through:1b, Rotation:{i['rotation']}}}")
            commands.append([i['time'], command])

            # 执行清除
            command = f"kill @e[tag={i['time'] + i['duration']}]"
            commands.append([i['time'] + i['duration'], command])

    logger.info(f"已将{len(ponder.commands)}条操作编译为{len(commands)}条指令.")
    return commands
