import os
import shutil

from SNBT import SNBTCompound

from ponder import Ponder


def compile_operations(ponder: Ponder, pos_offset: tuple = (0, 0, 0)) -> list:
    """
    编译你的思索对象为Minecraft指令
    :param ponder: 你的思索对象
    :param pos_offset: 偏移坐标
    :return: 指令列表和执行时间
    """
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
                block = 'minecraft:' + world[pos_str]['block'] if len(world[pos_str]['block'].split(':')) == 1\
                    else world[pos_str]['block']  # 检查命名空间

                if i['animation'] in animation_map:  # 若有动画效果则播放动画
                    command = (f"summon falling_block {i['pos'][0] + x_offset} "
                               f"{i['pos'][1] + y_offset} "
                               f"{i['pos'][2] + z_offset} " + "{BlockState:{Name:\"" + block + "\",Properties:{"
                               + state_str + "}}, TileEntityData:" + nbt_snbt_str + ", NoGravity:1b, "
                               "Time: 597, Motion:" + animation_map[i['animation']] + "}")

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


    return commands


def compile_to_datapack(ponder: Ponder, version: bool = True, pos_offset: tuple = (0, 0, 0), ponder_name: str = "ponders",
                        output_dir: str = "."):
    """
    编译思索对象为Minecraft数据包
    :param ponder: 你的思索对象
    :param version: 是否为1.21+版本
    :param ponder_name: 你的思索名称
    :param pos_offset: 偏移坐标
    :param output_dir: 输出目录
    :return: 输出路径
    """
    commands = compile_operations(ponder, pos_offset)
    print(commands)

    # 生成数据包主结构
    datapack_dir = f"{output_dir}/{ponder_name}"
    if not os.path.exists(datapack_dir):
        os.makedirs(datapack_dir)

    # 生成pack.mcmeta
    with open(f"{datapack_dir}/pack.mcmeta", "w", encoding="utf-8") as f:
        # FIXME: 寻找正确的pack_format
        f.write('{"pack":{"pack_format":48,"description":"使用creepe_ponder生成的思索数据包"}}')

    # 生成用于存放函数的文件夹
    function_dir = f"{datapack_dir}/data/{ponder_name}/function" if version else \
        f"{datapack_dir}/data/{ponder_name}/functions"  # 傻逼mojang是这样, 乱改数据包结构
    os.makedirs(function_dir)

    functions = {}  # 存放函数的列表
    # 整理每个时刻工作的指令
    for command in commands:
        time, command_str = command
        if time in functions:
            functions[time].append(command_str)
        else:
            functions[time] = [command_str]

    # 将指令写入函数文件
    for time, command_list in functions.items():
        function_path = f"{function_dir}/{time}.mcfunction"

        with open(function_path, "w", encoding="utf-8") as f:
            text = "# Generated by creepe_ponder 本函数文件由creepe_ponder生成\n"

            for command in command_list:
                text += str(command) + "\n"
            f.write(text)

    # 主函数文件
    main_function_path = f"{function_dir}/main.mcfunction"
    # 使用/schedule指令让函数文件按顺序执行
    with open(main_function_path, "w", encoding="utf-8") as f:
        text = "# Generated by creepe_ponder 本函数文件由creepe_ponder生成\n"

        for time in functions.keys():
            text += f"schedule function {ponder_name}:{time} {time * 2 + 1} append\n"  # rt转为gt, 并增加一个偏移量

        f.write(text)

    # 打包数据包
    shutil.make_archive(f"{output_dir}/{ponder_name}", "zip", datapack_dir)

    # 删除临时文件
    shutil.rmtree(datapack_dir)
