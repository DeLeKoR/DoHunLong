import os, pygame as pg
from game.monster import Monster

def _safe_load(path):
    """Возвращает Surface либо None, если файла нет"""
    return pg.image.load(path) if os.path.exists(path) else None

class AnimatedMonster(Monster):
    def __init__(self, cell, speed, get_cell, get_cell_by_cord,
                 atlas_path, prefix, scale=1.0, draw_offset = 0):
        super().__init__(cell, speed, get_cell, get_cell_by_cord)
        self.prefix = prefix
        self.draw_offset_y = draw_offset
        # ── загружаем покадровые списки с проверкой ──
        def _dir_frames(suffix):
            frames=[_safe_load(os.path.join(
                   atlas_path,f"Walking/{suffix} walking",
                   f"{self.prefix} {suffix[0].upper()}W {i}.png")) for i in range(4)]
            return [f for f in frames if f]          # убираем None
        left  = _dir_frames("Left")
        right = _dir_frames("Right")
        up    = _dir_frames("Up")    or right       # нет? берём правые
        down  = _dir_frames("Down")  or right       # нет? тоже правые
        self.frames={"left":left,"right":right,"up":up,"down":down}
        # стартовый кадр
        self.image=self.frames["right"][0]
        if scale!=1.0:
            for dir_,lst in self.frames.items():
                self.frames[dir_]=[pg.transform.smoothscale(im,
                        (int(im.get_width()*scale),int(im.get_height()*scale))) for im in lst]
            self.image=self.frames["right"][0]
        self.current_dir="right";self.current_frame=0
        self.frame_delay=200;self.last_tick=pg.time.get_ticks()

    def _animate(self):
        now=pg.time.get_ticks()
        if now-self.last_tick>=self.frame_delay:
            self.last_tick=now
            self.current_frame=(self.current_frame+1)%len(self.frames[self.current_dir])
            self.image=self.frames[self.current_dir][self.current_frame]

    def draw(self, surface):
        self._animate()
        surface.blit(self.image, (self.rect.x, self.rect.y + self.draw_offset_y))

    def _update_dir(self,vx,vy):
        if abs(vx)>abs(vy):
            self.current_dir="right" if vx>0 else "left"
        else:
            self.current_dir="down" if vy>0 else "up"

class AiryMonster(AnimatedMonster):
    def __init__(self,cell,speed,get_cell,get_cell_by_cord):
        super().__init__(cell,speed,get_cell,get_cell_by_cord,
                         atlas_path="assets/images/enemy/Airy",
                         prefix="Airy",scale=0.16, draw_offset=-80)
        self.fight_prefix = "assets/images/enemy/Airy/Fighting/Airy Fighting"
        self.max_hp = 120
        self.damage = 20

class IronChanMonster(AnimatedMonster):
    def __init__(self,cell,speed,get_cell,get_cell_by_cord):
        super().__init__(cell,speed,get_cell,get_cell_by_cord,
                         atlas_path="assets/images/enemy/Iron Chan",
                         prefix="Iron Chan",scale=0.13)
        self.fight_prefix = "assets/images/enemy/Iron Chan/Fighting/Iron chan Fighting"
        self.max_hp = 60
        self.damage = 10