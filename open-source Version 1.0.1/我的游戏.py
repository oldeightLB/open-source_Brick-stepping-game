import arcade as aa
import _locale
import os
import sys
import easygui
import password
# resource
base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(base_dir)

_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

# 地图
map_scale = 0.5

# 窗口
screen_width = int(30 * 64 * map_scale)
screen_height = int(20 * 64 * map_scale)
screen_title = "踩砖块"
screen_color = aa.color.SKY_BLUE

# 玩家
player_move_speed = 5
player_jump_speed = 15
# 重力
gravity = 1
# 音频
jump_sound = 'sounds/jump1.wav'
bgm = 'sounds/只因你太美.wav'
# 游戏状态
game_status_image = {
    "游戏中": "空",
    "过关": "images/游戏过关2.png",
    "失败": "空",
    "通关": "images/游戏通关2.png",
}
# 游戏开始关卡
start_level = 1
max_level = 4

class MyGame(aa.Window):
    def __init__(self):
        super().__init__(screen_width, screen_height, screen_title)
        self.background_color = screen_color
        # 关卡
        self.level = start_level
        self.jump_sound = aa.load_sound(jump_sound)
        self.bgm = aa.load_sound(bgm)
        self.bgm.play(1)
        self.user_input = 0
    def setup(self):
        info = f'关卡{self.level}（按J键重置关卡，按F键输入密码跳关）'
        self.level_name=aa.Text(info,screen_width//2,screen_height-20,aa.color.BROWN,
                               font_size=15,anchor_x='center',anchor_y='center',)
        # 加载地图
        map_name = f"maps/level{self.level}.tmx"
        self.tile_map = aa.load_tilemap(map_name, scaling=map_scale)
        self.scene = aa.Scene.from_tilemap(self.tile_map)
        # 转换属性
        for brick in self.scene.name_mapping["砖块"]:
            brick.properties["num"] = int(brick.properties["num"])
        # 玩家
        self.player = self.scene.name_mapping["玩家"][0]
        # 物理引擎
        static = [self.scene.name_mapping["墙"], self.scene.name_mapping["砖块"]]
        # 添加移动的元素
        platforms = []
        if self.scene.name_mapping.get("移动的砖块"):
            platforms.append(self.scene.name_mapping["移动的砖块"])
        self.physics_engine = aa.PhysicsEnginePlatformer(self.player, walls=static, gravity_constant=gravity,
                                                         platforms=platforms)
        # 上一次是否在砖块上
        self.pre_is_on_brick = self.is_on_brick()
        # 数字为0砖块
        self.zero_brick_list = aa.SpriteList()
        # 游戏状态
        self.game_status = aa.Sprite()
        self.game_status.position = screen_width // 2, screen_height // 2
        self.game_status.scale = 0.5
        self.game_status.text = "游戏中"

        # 玩家相机
        self.player_camera = aa.Camera(screen_width, screen_height)
        # 游戏状态相机
        self.game_status_camera = aa.Camera(screen_width, screen_height)

    def on_draw(self):
        self.clear()
        if self.tile_map.width * self.tile_map.tile_width * map_scale > screen_width:
            self.player_camera.use()
        self.scene.draw()
        self.draw_brick_num()
        self.game_status_camera.use()
        self.game_status.draw()
        self.level_name.draw()     

    def on_update(self, time):
        self.physics_engine.update()
        self.deal_jump()
        if self.game_status.text == "游戏中":
            self.deal_game_status()
        self.move_player_camera()

    def on_key_press(self, key, modifiers):
        if key == aa.key.UP and self.physics_engine.can_jump():
            self.player.change_y = player_jump_speed
            self.jump_sound.play()
        elif key == aa.key.LEFT:
            self.player.change_x = -player_move_speed
        elif key == aa.key.RIGHT:
            self.player.change_x = player_move_speed

    def on_key_release(self, key, modifiers):
        if key in [aa.key.UP]:
            self.player.change_y = 0
        elif key in [aa.key.LEFT, aa.key.RIGHT]:
            self.player.change_x = 0
        if key == aa.key.J:
            self.setup()
        if key == aa.key.F:
            user_input = 0
            user_input = easygui.enterbox("请输入密码：")
            if user_input == password.password:
                if self.level < 4:
                    self.level += 1
                    self.setup()
                else:
                    easygui.ynbox('现在已经是最后一关了！')
            else:
                easygui.ynbox('密码错误！')
    def draw_brick_num(self):
        bricks = self.scene.name_mapping["砖块"]
        for brick in bricks:
            n = aa.Text(str(brick.properties["num"]), brick.center_x, brick.center_y, aa.color.BROWN,
                        font_size=15, anchor_x="center", anchor_y="center")
            n.draw()

    def is_on_brick(self):
        self.player.center_y -= 1
        result = self.player.collides_with_list(self.scene.name_mapping["砖块"])
        self.player.center_y += 1

        return result

    def deal_jump(self):
        current = self.is_on_brick()
        if not self.pre_is_on_brick and current:
            # 和砖块交互
            for brick in current:
                brick.properties["num"] -= 1
                # 更换砖块
                brick_image = f"images/brick{brick.properties['num']}.png"
                brick.texture = aa.load_texture(brick_image)
                # 统计数字为0砖块
                if brick.properties["num"] == 0:
                    self.zero_brick_list.append(brick)
        # 从地上开始跳跃，清除数字为0的砖块
        elif self.pre_is_on_brick and not current:
            for brick in self.zero_brick_list:
                brick.kill()
        self.pre_is_on_brick = current

    def deal_game_status(self):
        # 过关
        if len(self.scene.name_mapping["砖块"]) == 0:
            self.game_status.text = "过关"
            # 通关
            if self.level < max_level:
                self.level += 1
                self.setup()
            else:
                self.game_status.text = "通关"
        # 失败
        if self.player.top < 0 or self.is_collide_barrier():
            self.game_status.text = "失败"
            self.setup()
        # 更换游戏状态图片
        if game_status_image[self.game_status.text] != "空":
            self.game_status.texture = aa.load_texture(game_status_image[self.game_status.text])

    def is_collide_barrier(self):
        if self.scene.name_mapping.get("障碍物"):
            result = self.player.collides_with_list(self.scene.name_mapping["障碍物"])
            return result

    def move_player_camera(self):
        camera_x = self.player.center_x - screen_width // 2
        camera_y = self.player.center_y - screen_height // 2
        # 相机位置不超过左下边界
        if camera_x < 0:
            camera_x = 0
        if camera_y < 0:
            camera_y = 0
        camera_pos = camera_x, camera_y
        self.player_camera.move(camera_pos)


w = MyGame()
w.setup()
w.run()