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
        self.is_dead = False
        self.death_timer = 0.0
        self.fall_axis = random.choice(["x", "z"])
        self.fall_sign = random.choice([-1, 1])
        self.knockback = Vec3(0, 0, 0)

    def die(self, hit_dir=None):
        if self.is_dead:
            return
        self.is_dead = True
        self.collider = None
        self.color = color.rgb(190, 45, 45)
        if self.head and not self.head.is_empty():
            self.head.color = color.rgb(210, 90, 90)
        if hit_dir is not None:
            flat_dir = Vec3(hit_dir.x, 0, hit_dir.z)
            if flat_dir.length() > 0.01:
                self.knockback = flat_dir.normalized() * 6.5

    def update(self):
        if self.is_dead:
            self.death_timer += time.dt

            # Плавное заваливание на землю
            if self.fall_axis == "x":
                self.rotation_x = lerp(self.rotation_x, 90 * self.fall_sign, time.dt * 9)
            else:
                self.rotation_z = lerp(self.rotation_z, 90 * self.fall_sign, time.dt * 9)

            self.y = lerp(self.y, 0.45, time.dt * 9)

            # Небольшое отбрасывание при ударе с затуханием
            if self.knockback.length() > 0.05:
                self.position += self.knockback * time.dt
                self.knockback = lerp(self.knockback, Vec3(0, 0, 0), time.dt * 7)

            if self.death_timer >= 2.5:
                if self in npcs:
                    npcs.remove(self)
                destroy(self)
            return

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

WEAPONS = {
    "pistol": {
        "name": "Glock-17",
        "category": "ПИСТОЛЕТЫ",
        "price": 0,
        "owned": True,
        "cooldown": 0.24,
        "auto": False,
        "range": 65,
        "reward": 50,
        "rate_text": "Средний",
        "mode_text": "Одиночный",
        "default_pos": Vec3(0.38, -0.30, 0.72),
        "flash_pos": Vec3(0, 0.04, 0.25),
        "ui_pos": (-0.43, 0.14),
        "preview_scale": 0.22,
    },
    "uzi": {
        "name": "Micro UZI",
        "category": "ПИСТОЛЕТЫ-ПУЛЕМЁТЫ",
        "price": 150,
        "owned": False,
        "cooldown": 0.065,
        "auto": True,
        "range": 70,
        "reward": 50,
        "rate_text": "Очень высокий",
        "mode_text": "Автомат",
        "default_pos": Vec3(0.40, -0.30, 0.72),
        "flash_pos": Vec3(0, 0.03, 0.34),
        "ui_pos": (-0.15, 0.14),
        "preview_scale": 0.20,
    },
    "ak47": {
        "name": "AK-47",
        "category": "ВИНТОВКИ",
        "price": 350,
        "owned": False,
        "cooldown": 0.11,
        "auto": True,
        "range": 100,
        "reward": 60,
        "rate_text": "Высокий",
        "mode_text": "Автомат",
        "default_pos": Vec3(0.42, -0.32, 0.75),
        "flash_pos": Vec3(0, 0.02, 0.85),
        "ui_pos": (0.13, 0.14),
        "preview_scale": 0.145,
    },
    "sniper": {
        "name": "AWP",
        "category": "ВИНТОВКИ",
        "price": 600,
        "owned": False,
        "cooldown": 0.75,
        "auto": False,
        "range": 160,
        "reward": 100,
        "rate_text": "Низкий",
        "mode_text": "Снайперский",
        "default_pos": Vec3(0.44, -0.33, 0.78),
        "flash_pos": Vec3(0, 0.02, 1.05),
        "ui_pos": (0.13, -0.09),
        "preview_scale": 0.125,
    },
}

WEAPON_ORDER = ["pistol", "uzi", "ak47", "sniper"]
current_weapon_key = "pistol"
GUN_DEFAULT_POS = WEAPONS["pistol"]["default_pos"]

gun = Entity(parent=camera, position=GUN_DEFAULT_POS, rotation=(0, -3, 0))
gun_parts = []
muzzle_flash = None


def hide_flash(flash_obj):
    if flash_obj and not flash_obj.is_empty():
        flash_obj.enabled = False


def create_weapon_parts(parent_obj, w_key, parts_list=None):
    wood_color = color.rgb(135, 75, 30)
    metal_color = color.rgb(38, 40, 44)
    dark_metal = color.rgb(25, 25, 28)

    def add_part(**kwargs):
        e = Entity(parent=parent_obj, **kwargs)
        if parts_list is not None:
            parts_list.append(e)
        return e

    if w_key == "pistol":
        add_part(model="cube", position=(0, 0.04, 0.04), scale=(0.055, 0.06, 0.30), color=metal_color)
        add_part(model="cube", position=(0, 0.005, 0.04), scale=(0.05, 0.03, 0.29), color=dark_metal)
        add_part(model="cube", position=(0, -0.07, -0.06), rotation=(-16, 0, 0), scale=(0.048, 0.16, 0.075), color=dark_metal)
        add_part(model="cube", position=(0, 0.078, 0.16), scale=(0.012, 0.02, 0.015), color=color.white)
        add_part(model="cube", position=(0, 0.078, -0.09), scale=(0.03, 0.02, 0.015), color=metal_color)

    elif w_key == "uzi":
        add_part(model="cube", position=(0, 0.02, 0.02), scale=(0.075, 0.11, 0.34), color=metal_color)
        add_part(model="cube", position=(0, 0.03, 0.24), scale=(0.03, 0.03, 0.14), color=dark_metal)
        add_part(model="cube", position=(0, -0.08, -0.01), rotation=(-8, 0, 0), scale=(0.055, 0.14, 0.075), color=dark_metal)
        add_part(model="cube", position=(0, -0.20, -0.025), rotation=(-8, 0, 0), scale=(0.042, 0.18, 0.055), color=color.rgb(55, 58, 64))
        add_part(model="cube", position=(0, 0.04, -0.20), scale=(0.05, 0.025, 0.16), color=color.gray)
        add_part(model="cube", position=(0, 0.088, 0.15), scale=(0.014, 0.025, 0.015), color=color.white)

    elif w_key == "ak47":
        add_part(model="cube", position=(0, 0, 0), scale=(0.07, 0.11, 0.42), color=metal_color)
        add_part(model="cube", position=(0, 0.06, -0.02), scale=(0.065, 0.03, 0.38), color=color.rgb(50, 52, 58))
        add_part(model="cube", position=(0, -0.035, -0.36), rotation=(10, 0, 0), scale=(0.06, 0.11, 0.34), color=wood_color)
        add_part(model="cube", position=(0, -0.11, -0.10), rotation=(-18, 0, 0), scale=(0.05, 0.14, 0.07), color=wood_color)
        add_part(model="cube", position=(0, 0.005, 0.33), scale=(0.068, 0.085, 0.26), color=wood_color)
        add_part(model="cube", position=(0, 0.055, 0.32), scale=(0.04, 0.04, 0.24), color=metal_color)
        add_part(model="cube", position=(0, 0.02, 0.62), scale=(0.025, 0.025, 0.38), color=dark_metal)
        add_part(model="cube", position=(0, 0.055, 0.76), scale=(0.015, 0.05, 0.02), color=metal_color)
        add_part(model="cube", position=(0, -0.14, 0.10), rotation=(16, 0, 0), scale=(0.052, 0.16, 0.09), color=color.rgb(45, 45, 50))
        add_part(model="cube", position=(0, -0.27, 0.15), rotation=(32, 0, 0), scale=(0.052, 0.16, 0.09), color=color.rgb(45, 45, 50))
    elif w_key == "sniper":
        sniper_green = color.rgb(65, 92, 55)
        add_part(model="cube", position=(0, -0.01, 0.05), scale=(0.075, 0.10, 0.58), color=sniper_green)
        add_part(model="cube", position=(0, -0.025, -0.36), scale=(0.065, 0.12, 0.34), color=sniper_green)
        add_part(model="cube", position=(0, -0.11, -0.12), rotation=(-15, 0, 0), scale=(0.052, 0.14, 0.07), color=dark_metal)
        add_part(model="cube", position=(0, -0.11, 0.06), scale=(0.055, 0.12, 0.11), color=dark_metal)
        add_part(model="cube", position=(0, 0.02, 0.62), scale=(0.028, 0.028, 0.65), color=dark_metal)
        add_part(model="cube", position=(0, 0.02, 0.96), scale=(0.04, 0.04, 0.08), color=metal_color)
        add_part(model="cube", position=(0, 0.075, 0.05), scale=(0.025, 0.04, 0.04), color=metal_color)
        add_part(model="cube", position=(0, 0.075, 0.22), scale=(0.025, 0.04, 0.04), color=metal_color)
        add_part(model="cube", position=(0, 0.115, 0.12), scale=(0.058, 0.058, 0.38), color=dark_metal)
        add_part(model="cube", position=(0, 0.115, 0.32), scale=(0.068, 0.068, 0.07), color=metal_color)
        add_part(model="cube", position=(0, 0.115, -0.072), scale=(0.045, 0.045, 0.01), color=color.cyan)
def build_weapon_model(w_key):
    global gun_parts, muzzle_flash, GUN_DEFAULT_POS

    for part in gun_parts:
        if part and not part.is_empty():
            destroy(part)
    gun_parts.clear()

    if muzzle_flash and not muzzle_flash.is_empty():
        destroy(muzzle_flash)
    muzzle_flash = None

    create_weapon_parts(gun, w_key, gun_parts)

    muzzle_flash = Entity(
        parent=gun,
        model="sphere",
        position=WEAPONS[w_key]["flash_pos"],
        scale=0.14,
        color=color.yellow,
        enabled=False,
    )

    GUN_DEFAULT_POS = WEAPONS[w_key]["default_pos"]
    gun.position = GUN_DEFAULT_POS


def equip_weapon(w_key):
    global current_weapon_key
    if not WEAPONS[w_key]["owned"]:
        return
    current_weapon_key = w_key
    build_weapon_model(w_key)
    update_hud()
    refresh_shop_ui()

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
shop_open = False
hud_text = Text(
text="$ 0   |   Wanted: 0*   |   Оружие: Glock-17",
position=(-0.85, 0.45),
scale=1.4,
color=color.white,
background=True,
)
help_text = Text(
text="WASD - ходить/ехать | Space - прыжок | F - машина | ЛКМ - огонь | B - Магазин CS2 | 1-4 - оружие",
position=(-0.85, -0.45),
scale=1.05,
color=color.light_gray,
)

#--- МЕНЮ ПОКУПКИ ОРУЖИЯ В СТИЛЕ CS2 ---

shop_panel = Entity(parent=camera.ui, enabled=False)
Entity(parent=shop_panel, model="quad", scale=(2, 2), color=color.rgba(8, 12, 18, 185), z=0.6)
Entity(parent=shop_panel, model="quad", scale=(1.26, 0.76), color=color.rgba(16, 22, 30, 235), z=0.5)
Entity(parent=shop_panel, model="quad", position=(0, 0.378), scale=(1.26, 0.008), color=color.rgb(235, 165, 45), z=0.4)
Text(
parent=shop_panel,
text="МЕНЮ ЗАКУПКИ  //  AMMUNATION",
position=(-0.58, 0.335),
origin=(-0.5, 0),
scale=1.45,
color=color.white,
z=0.1,
)
shop_money_text = Text(
parent=shop_panel,
text="$ 0",
position=(0.58, 0.335),
origin=(0.5, 0),
scale=1.7,
color=color.rgb(115, 225, 110),
z=0.1,
)
columns = [
("1  ПИСТОЛЕТЫ", -0.43),
("2  ПИСТОЛЕТЫ-ПУЛЕМЁТЫ", -0.15),
("3  ВИНТОВКИ", 0.13),
]
for col_title, col_x in columns:
    Entity(parent=shop_panel, model="quad", position=(col_x, 0.275), scale=(0.255, 0.038), color=color.rgba(255, 255, 255, 22), z=0.4)
Text(
parent=shop_panel,
text=col_title,
position=(col_x, 0.275),
origin=(0, 0),
scale=0.88,
color=color.rgb(210, 218, 228),
z=0.1,
)
Entity(parent=shop_panel, model="quad", position=(0.44, 0.03), scale=(0.31, 0.53), color=color.rgba(255, 255, 255, 16), z=0.4)
info_title_text = Text(
parent=shop_panel,
text="Glock-17",
position=(0.305, 0.25),
origin=(-0.5, 0),
scale=1.35,
color=color.rgb(245, 185, 65),
z=0.1,
)
info_cat_text = Text(
parent=shop_panel,
text="ПИСТОЛЕТЫ",
position=(0.305, 0.21),
origin=(-0.5, 0),
scale=0.82,
color=color.light_gray,
z=0.1,
)
info_stats_text = Text(
parent=shop_panel,
text="",
position=(0.305, 0.06),
origin=(-0.5, 0),
scale=0.92,
color=color.white,
z=0.1,
)
info_price_text = Text(
parent=shop_panel,
text="СТОИМОСТЬ: БЕСПЛАТНО",
position=(0.305, -0.17),
origin=(-0.5, 0),
scale=1.05,
color=color.lime,
z=0.1,
)
shop_status_text = Text(
parent=shop_panel,
text="Нажмите на карточку оружия или [1-4] для покупки",
position=(-0.58, -0.325),
origin=(-0.5, 0),
scale=0.95,
color=color.light_gray,
z=0.1,
)
shop_cards = {}
preview_pivots = []
def update_inspector(w_key):
    w = WEAPONS[w_key]
    info_title_text.text = w["name"]
    info_cat_text.text = w["category"]
    info_stats_text.text = (
        f"Награда за цель:   + $ {w['reward']}\n\n"
        f"Темп стрельбы:     {w['rate_text']}\n\n"
        f"Дальность боя:     {w['range']} м\n\n"
        f"Режим стрельбы:   {w['mode_text']}"
    )
    if current_weapon_key == w_key:
        info_price_text.text = "СТАТУС: ЭКИПИРОВАНО"
        info_price_text.color = color.rgb(115, 225, 110)
    elif w["owned"]:
        info_price_text.text = "СТАТУС: В ИНВЕНТАРЕ"
        info_price_text.color = color.azure
    else:
        price_str = "БЕСПЛАТНО" if w["price"] == 0 else f"$ {w['price']}"
        info_price_text.text = f"ЦЕНА: {price_str}"
        info_price_text.color = color.gold if money >= w["price"] else color.rgb(235, 85, 85)


def handle_weapon_click(w_key):
    global money
    w = WEAPONS[w_key]
    update_inspector(w_key)

    if w["owned"]:
        equip_weapon(w_key)
        shop_status_text.text = f"Экипировано: {w['name']}"
        shop_status_text.color = color.azure
    else:
        if money >= w["price"]:
            money -= w["price"]
            w["owned"] = True
            equip_weapon(w_key)
            shop_status_text.text = f"Куплено и взято в руки: {w['name']}!"
            shop_status_text.color = color.lime
        else:
            need = w["price"] - money
            shop_status_text.text = f"Недостаточно средств! Не хватает $ {need}"
            shop_status_text.color = color.rgb(240, 80, 80)


for idx, w_key in enumerate(WEAPON_ORDER):

        w = WEAPONS[w_key]
cx, cy = w["ui_pos"]
slot_num = idx + 1
card_btn = Button(
parent=shop_panel,
text=" ",
position=(cx, cy),
scale=(0.255, 0.205),
color=color.rgba(34, 42, 54, 240),
highlight_color=color.rgba(58, 72, 92, 250),
on_click=Func(handle_weapon_click, w_key),
on_mouse_enter=Func(update_inspector, w_key),
z=0.3,
)
status_bar = Entity(
parent=shop_panel,
model="quad",
position=(cx, cy + 0.098),
scale=(0.255, 0.008),
color=color.gray,
z=0.2,
)
Text(
parent=shop_panel,
text=f"{slot_num}",
position=(cx - 0.112, cy + 0.075),
origin=(-0.5, 0),
scale=0.95,
color=color.rgb(235, 165, 45),
z=0.1,
)
Text(
parent=shop_panel,
text=w["name"],
position=(cx + 0.112, cy + 0.075),
origin=(0.5, 0),
scale=0.92,
color=color.white,
z=0.1,
)
pivot = Entity(
parent=shop_panel,
position=(cx, cy - 0.005, -0.05),
rotation=(14, 55, -8),
scale=w["preview_scale"],
)
create_weapon_parts(pivot, w_key)
preview_pivots.append(pivot)
price_text = Text(
parent=shop_panel,
text=" ",
position=(cx + 0.112, cy - 0.078),
origin=(0.5, 0),
scale=0.95,
color=color.lime,
z=0.1,
)
shop_cards[w_key] = {
"btn": card_btn,
"bar": status_bar,
"price": price_text,
}
close_btn = Button(
parent=shop_panel,
text="ЗАКРЫТЬ [B]",
text_size=0.85,
position=(0.48, -0.325),
scale=(0.22, 0.048),
color=color.rgb(165, 50, 50),
highlight_color=color.rgb(200, 65, 65),
on_click=lambda: toggle_shop(False),
z=0.2,
)
def refresh_shop_ui():
    shop_money_text.text = f"$ {money}"
for w_key in WEAPON_ORDER:
    w = WEAPONS[w_key]
card = shop_cards[w_key]
if current_weapon_key == w_key:
    card["btn"].color = color.rgba(38, 82, 58, 245)
    card["bar"].color = color.rgb(95, 225, 115)
    card["price"].text = "В РУКЕ"
    card["price"].color = color.rgb(115, 240, 130)
elif w["owned"]:
    card["btn"].color = color.rgba(36, 58, 84, 240)
    card["bar"].color = color.azure
    card["price"].text = "КУПЛЕНО"
    card["price"].color = color.azure
else:
    card["btn"].color = color.rgba(30, 36, 46, 240)
    card["bar"].color = color.rgb(235, 165, 45) if money >= w["price"] else color.rgb(120, 60, 60)
    card["price"].text = f"$ {w['price']}"
    card["price"].color = color.rgb(245, 195, 75) if money >= w["price"] else color.rgb(225, 85, 85)
update_inspector(current_weapon_key)
def toggle_shop(force_state=None):
    global shop_open
    if current_car:
        return
    shop_open = (not shop_open) if force_state is None else force_state
shop_panel.enabled = shop_open
mouse.locked = not shop_open
mouse.visible = shop_open
player.enabled = not shop_open
player.cursor.enabled = not shop_open
if shop_open:
    shop_status_text.text = "Нажмите на карточку оружия или [1-4] для покупки"
shop_status_text.color = color.light_gray
refresh_shop_ui()
def update_hud():
    w_name = WEAPONS[current_weapon_key]["name"]
    hud_text.text = f"$ {money}   |   Wanted: {wanted}*   |   Оружие: {w_name}"
def shoot():
    global money, wanted, fire_cooldown
    if current_car or shop_open or fire_cooldown > 0:
        return
w = WEAPONS[current_weapon_key]
fire_cooldown = w["cooldown"]
if muzzle_flash and not muzzle_flash.is_empty():
    muzzle_flash.enabled = True
invoke(hide_flash, muzzle_flash, delay=0.04)
gun.position = GUN_DEFAULT_POS + Vec3(0, 0.02, -0.08)
gun.rotation_x = -4
gun.animate_position(GUN_DEFAULT_POS, duration=0.09)
gun.animate_rotation_x(0, duration=0.09)
hit_info = raycast(camera.world_position, camera.forward, distance=w["range"], ignore=[player, gun])
if hit_info.hit and isinstance(hit_info.entity, NPC) and not hit_info.entity.is_dead:
    hit_info.entity.die(camera.forward)
money += w["reward"]
wanted = min(5, wanted + 1)
update_hud()
def input(key):
    global current_car, wanted

    if key == "b":
        toggle_shop()
        return

    if key in ("1", "2", "3", "4"):
        idx = int(key) - 1
        w_key = WEAPON_ORDER[idx]
        if shop_open:
            handle_weapon_click(w_key)
        elif WEAPONS[w_key]["owned"]:
            equip_weapon(w_key)
        return

    if shop_open:
        if key == "escape":
            toggle_shop(False)
        return

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

    if shop_open:
        for pivot in preview_pivots:
            pivot.rotation_y += 38 * time.dt
        return

    w = WEAPONS[current_weapon_key]
    if held_keys["left mouse"] and not current_car and w["auto"]:
        shoot()

    if current_car and abs(current_car.speed) > 4:
        for npc in npcs[:]:
            if not npc.is_dead and distance(current_car.position, npc.position) < 3.2:
                npc.die(current_car.forward * (1 if current_car.speed > 0 else -1))
                money += 50
                wanted = min(5, wanted + 1)
                update_hud()


build_weapon_model(current_weapon_key)
refresh_shop_ui()

app.run()

app.run()
