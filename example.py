from ponder import Ponder
from ponder.compiler import compile_to_datapack

""" creepe_ponder示例程序 """

"""
    如果我们要开始一个新的思索, 请导入Ponder类, 并创建一个实例以进行操作.
    Ponder实例会自动根据大小创建地板, 当然, 你也可以放置在地板外的方块.
    
    Ponder示例创建的时候接受一个必填参数 size, 作为地板的大小.
    让我们创建一个5x5的标准地板:
"""

pond = Ponder(5)

"""
    现在, 我们可以开始编写我们的思索动画了.
    我们可以使用 Ponder 实例的一些方法来对这个动画进行操作.
    
    首先, 试试 place() 方法吧. 这个方法用于放置方块.
    place() 方法接受5个参数: 
    - time: 放置时间, 单位为rt(红石刻, 1/10秒), 最小为1
    - pos: (x, y, z) 坐标 地板位置x, y, z轴最小处为(0, 0, 0)
    - block: 方块名称, 'minecraft:'可省略
    - state: 方块状态, 如 {'facing': 'north'} (可选)
    - nbt: 方块NBT数据, 如 {'CustomName': 'My Entity'} (可选)
    
    让我们试试放置一个命令方块, 朝向下方(由方块状态决定), 命令内容为'/say hello world!':
"""

pond.place(0, (2, 1, 2), 'command_block', {'facing': 'down'}, {'Command': '/say hello world!'})

"""
    现在我们需要放置一个红石块, 用于激活. 由于红石块没有方块状态和NBT数据, 我们可以省略这两个参数:
"""

pond.place(15, (2, 2, 2), 'redstone_block')

"""
    如何移除这个红石块? 可以使用remove()方法:
    此方法接受3个参数:
    - time: 移除时间, 单位为rt, 最小为1
    - pos: (x, y, z) 坐标 地板位置x, y, z轴最小处为(0, 0, 0)
    - animation: 移除动画, 可选: 'y+', 'x+', 'x-', 'z+', 'z-', 'destroy' 默认为'y+' (可选)
    
    让我们试试移除刚才放置的红石块, 并使用'x-'动画:
"""

pond.remove(20, (2, 2, 2), 'x-')

"""
    另: 如果你使用place()方法, 但指定的坐标已经有方块存在, 则会自动覆盖掉原有方块(没有动画效果).
    
    试试将命令方块的指令改为'/say hello ponder!':
"""

pond.place(30, (2, 1, 2), 'command_block', {'facing': 'down'}, {'Command': '/say hello ponder!'})
pond.place(35, (2, 2, 2), 'redstone_block')

pond.remove(45, (2, 2, 2))
pond.remove(50, (2, 1, 2))

"""
    现在让我们来放置一些文本.
    我们可以使用text()方法来放置. 此方法接受5个参数:
    - time: 放置时间, 单位为rt, 最小为1
    - pos: (x, y, z) 坐标 地板位置x, y, z轴最小处为(0, 0, 0)
    - text: 文本内容
    - duration: 持续时间, 单位为rt (可选, 默认为20)
    - rotation: [deflection, pitch] 旋转角度, 单位为度 (可选, 默认为[0, 0])
      偏转角取值 0 - 360 度, 俯仰角取值 -90 - 90 度.
      
    试试创建一些角度, 持续时间不同的文本:
"""

pond.text(60, (1, 2, 2), 'Hello, world!', 40, [-10, 0])
pond.text(65, (2, 2, 2), 'Ponder is awesome!', 30, [0, 0])
pond.text(70, (3, 2, 2), 'This is a test!', 35, [10, 0])

"""
    最后, 我们需要编译这个动画.
    我们可以使用compile_to_datapack()方法来编译. 此方法接受5个参数:
    - ponder: 你的思索对象
    - version: 是否为1.21+版本 (可选, 默认为True)
    - pos_offset: 地板位置偏移 (可选, 默认为(0, 0, 0))
    - ponder_name: 数据包命名空间 (可选, 默认为'ponders')
    - output_dir: 输出路径 (可选, 默认为'.')
    
    让我们试试编译这个动画, 坐标偏移为(0, 1, 0), 命名空间为'ponder_test', 输出路径为./outputs.
    另外假设我们在使用1.20.1版本的Minecraft, 所以我们需要设置version参数为False:
"""

compile_to_datapack(pond, False, (0, 1, 0), 'ponder_test', './outputs')

"""
    编译完成后, 你会在outputs目录下看到一个名为ponder_test.zip的压缩文件, 这个文件就是你的思索动画了, 以数据包的形式保存.
    你可以在游戏中导入这个数据包, 然后在世界中运行这个动画.
    如何运行? 请使用/function <数据包命名空间>:main 指令.
    在这里, 命名空间为'ponder_test', 所以指令为/function ponder_test:main.
    
    另请额外注意, creepe_ponder不会检查拼写/语法, 如果无法运行, 请先检查你的代码, 确认是bug后再反馈.
    
    祝你玩得愉快!
"""