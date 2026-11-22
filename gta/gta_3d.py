установить для запуска py -m pip install ursina
import random
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

window.title = "Mini GTA 3D (Minecraft Edition)"
window.borderless = False
window.fps_counter.enabled = True

Sky()
DirectionalLight(y=10, z=5, shadows=True)
AmbientLight(color=color.rgba(150, 150, 150, 0.5))

ground = Entity(
    model="plane",
    collider="box",
    scale=(160, 1, 160),
    color=color.dark_gray,
    texture="white_cube",
    texture_scale=(80, 80),
)

buildings = []
building_colors = [color.light_gray, color.gray, color.azure, color.orange, color.brown]

for x in range(-60, 61, 24):
    for z in range(-60, 61, 24):
        if abs(x) < 15 and abs(z) < 15:
            continue
        h = random.randint(8, 26)
        b = Entity(
            model="cube",
            collider="box",
            position=(x, h / 2, z),
            scale=(14, h, 14),
            color=random.choice(building_colors),
            texture="brick",
            texture_scale=(4, h // 2),
        )
        buildings.append(b)


class Car(Entity):
    def __init__(self, pos, car_color=color.red):
        super().__init__(
            model="cube",
            collider="box",
            position=pos,
            scale=(2.4, 1.1, 4.5),
            color=car_color,
        )
        self.cabin = Entity(
            parent=self,
            model="cube",
            position=(0, 0.75, -0.1),
            scale=(0.85, 0.7, 0.55),
            color=color.black66,
        )
        self.speed = 0.0
        self.max_speed = 28.0
        self.occupied = False

    def update(self):
        if not self.occupied:
            return

        if held_keys["w"]:
            self.speed = min(self.speed + 18 * time.dt, self.max_speed)
        elif held_keys["s"]:
            self.speed = max(self.speed - 22 * time.dt, -self.max_speed * 0.5)
        else:
            self.speed = lerp(self.speed, 0, time.dt * 2.5)

        if abs(self.speed) > 0.5:
            turn_dir = 1 if self.speed > 0 else -1
            if held_keys["a"]:
                self.rotation_y -= 95 * time.dt * turn_dir
            if held_keys["d"]:
                self.rotation_y += 95 * time.dt * turn_dir

        old_pos = self.position
        self.position += self.forward * self.speed * time.dt

        if self.intersects().hit:
            self.position = old_pos
            self.speed *= -0.3

        camera.position = lerp(
            camera.position,
            self.position - self.forward * 11 + Vec3(0, 5, 0),
            time.dt * 8,
        )
        camera.look_at(self.position + Vec3(0, 1.5, 0))


class NPC(Entity):
    def __init__(self, pos):
        super().__init__(
            model="cube",
            collider="box",
            position=pos,
            scale=(0.9, 1.9, 0.9),
            color=color.yellow,
        )
        self.head = Entity(
            parent=self,
            model="cube",
            position=(0, 0.75, 0),
            scale=(0.7, 0.45, 0.7),
            color=color.peach,
        )
        self.dir = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        self.timer = random.uniform(1, 4)

    def update(self):
        self.timer -= time.dt
        if self.timer <= 0:
            self.dir = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
            self.timer = random.uniform(2, 5)

        old_pos = self.position
        self.position += self.dir * 2.5 * time.dt
        if self.intersects().hit or abs(self.x) > 75 or abs(self.z) > 75:
            self.position = old_pos
            self.dir = -self.dir


player = FirstPersonController(position=(0, 2, 0), speed=8)
player.cursor.color = color.red

GUN_DEFAULT_POS = Vec3(0.42, -0.32, 0.75)
wood_color = color.rgb(135, 75, 30)
metal_color = color.rgb(38, 40, 44)

gun = Entity(parent=camera, position=GUN_DEFAULT_POS, rotation=(0, -3, 0))

Entity(parent=gun, model="cube", position=(0, 0, 0), scale=(0.07, 0.11, 0.42), color=metal_color)
Entity(parent=gun, model="cube", position=(0, 0.06, -0.02), scale=(0.065, 0.03, 0.38), color=color.rgb(50, 52, 58))
Entity(parent=gun, model="cube", position=(0, -0.035, -0.36), rotation=(10, 0, 0), scale=(0.06, 0.11, 0.34), color=wood_color)
Entity(parent=gun, model="cube", position=(0, -0.11, -0.10), rotation=(-18, 0, 0), scale=(0.05, 0.14, 0.07), color=wood_color)
Entity(parent=gun, model="cube", position=(0, 0.005, 0.33), scale=(0.068, 0.085, 0.26), color=wood_color)
Entity(parent=gun, model="cube", position=(0, 0.055, 0.32), scale=(0.04, 0.04, 0.24), color=metal_color)
Entity(parent=gun, model="cube", position=(0, 0.02, 0.62), scale=(0.025, 0.025, 0.38), color=color.rgb(25, 25, 28))
Entity(parent=gun, model="cube", position=(0, 0.055, 0.76), scale=(0.015, 0.05, 0.02), color=metal_color)
Entity(parent=gun, model="cube", position=(0, -0.14, 0.10), rotation=(16, 0, 0), scale=(0.052, 0.16, 0.09), color=color.rgb(45, 45, 50))
Entity(parent=gun, model="cube", position=(0, -0.27, 0.15), rotation=(32, 0, 0), scale=(0.052, 0.16, 0.09), color=color.rgb(45, 45, 50))

muzzle_flash = Entity(
    parent=gun,
    model="sphere",
    position=(0, 0.02, 0.85),
    scale=0.14,
    color=color.yellow,
    enabled=False,
)

cars = [
    Car((6, 0.6, 8), color.red),
    Car((-8, 0.6, 12), color.blue),
    Car((12, 0.6, -10), color.green),
    Car((-12, 0.6, -14), color.orange),
]

npcs = [
    NPC((random.randint(-50, 50), 1, random.randint(-50, 50)))
    for _ in range(25)
]

current_car = None
money = 0
wanted = 0
fire_cooldown = 0.0

hud_text = Text(
    text="$ 0   |   Wanted: 0*",
    position=(-0.85, 0.45),
    scale=1.5,
    color=color.white,
    background=True,
)
help_text = Text(
    text="WASD - ходить/ехать | Space - прыжок | F - сесть/выйти из машины | ЛКМ - огонь из АК-47",
    position=(-0.85, -0.45),
    scale=1.1,
    color=color.light_gray,
)


def update_hud():
    hud_text.text = f"$ {money}   |   Wanted: {wanted}*"


def shoot():
    global money, wanted, fire_cooldown
    if current_car or fire_cooldown > 0:
        return

    fire_cooldown = 0.11  
    
    muzzle_flash.enabled = True
    invoke(setattr, muzzle_flash, "enabled", False, delay=0.04)
    gun.position = GUN_DEFAULT_POS + Vec3(0, 0.02, -0.08)
    gun.rotation_x = -4
    gun.animate_position(GUN_DEFAULT_POS, duration=0.09)
    gun.animate_rotation_x(0, duration=0.09)

    hit_info = raycast(camera.world_position, camera.forward, distance=75, ignore=[player, gun])
    if hit_info.hit and isinstance(hit_info.entity, NPC):
        destroy(hit_info.entity)
        npcs.remove(hit_info.entity)
        money += 50
        wanted = min(5, wanted + 1)
        update_hud()


def input(key):
    global current_car, wanted

    if key == "left mouse down":
        shoot()

    if key == "f":
        if current_car:
            player.position = current_car.position + current_car.right * 3 + Vec3(0, 1, 0)
            player.enabled = True
            gun.enabled = True
            camera.parent = player.camera_pivot
            camera.position = (0, 0, 0)
            camera.rotation = (0, 0, 0)
            current_car.occupied = False
            current_car = None
        else:
            for c in cars:
                if distance(player.position, c.position) < 5:
                    current_car = c
                    c.occupied = True
                    player.enabled = False
                    gun.enabled = False
                    camera.parent = scene
                    wanted = min(5, wanted + 1)
                    update_hud()
                    break


def update():
    global money, wanted, fire_cooldown

    if fire_cooldown > 0:
        fire_cooldown -= time.dt

    if held_keys["left mouse"] and not current_car:
        shoot()

    if current_car and abs(current_car.speed) > 4:
        for npc in npcs[:]:
            if distance(current_car.position, npc.position) < 3.2:
                destroy(npc)
                npcs.remove(npc)
                money += 50
                wanted = min(5, wanted + 1)
                update_hud()


app.run()
