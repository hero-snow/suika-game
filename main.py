import pygame
import pymunk
import pymunk.pygame_util

# --- 設定 ---
WIDTH, HEIGHT = 600, 800  # 画面サイズ
FPS = 60                  # フレームレート

# --- 初期化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Suika Game Base")
clock = pygame.time.Clock()

# --- 物理空間の作成 ---
space = pymunk.Space()
space.gravity = (0.0, 900.0)  # 重力 (x, y) 下方向に900

# デバッグ描画用（物理演算の結果をそのまま線で表示してくれる便利なツール）
draw_options = pymunk.pygame_util.DrawOptions(screen)

# --- 壁を作る関数 ---
def create_walls(space, width, height):
    # 静的物体（Static）として壁を作る
    walls = [
        pymunk.Segment(space.static_body, (50, height - 50), (width - 50, height - 50), 5), # 床
        pymunk.Segment(space.static_body, (50, height - 50), (50, 50), 5),                 # 左壁
        pymunk.Segment(space.static_body, (width - 50, height - 50), (width - 50, 50), 5)  # 右壁
    ]
    for wall in walls:
        wall.elasticity = 0.5  # 跳ね返り係数 (0.0〜1.0)
        wall.friction = 0.5    # 摩擦
    space.add(*walls)

# --- ボールを作る関数 ---
def create_ball(space, x, y):
    mass = 1        # 重さ
    radius = 30     # 半径
    moment = pymunk.moment_for_circle(mass, 0, radius) # 慣性モーメント
    body = pymunk.Body(mass, moment)
    body.position = x, y
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.8 # よく弾む
    shape.friction = 0.5
    space.add(body, shape)

# 壁を生成
create_walls(space, WIDTH, HEIGHT)

# --- メインループ ---
running = True
while running:
    # 1. イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # クリックしたらその場所にボールを落とす
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # 壁の外に出ないように制限
            if 50 < x < WIDTH - 50:
                create_ball(space, x, 50) # 高さは50の位置から落とす

    # 2. 物理演算の更新
    space.step(1 / FPS)

    # 3. 描画
    screen.fill((255, 255, 255)) # 背景を白に
    space.debug_draw(draw_options) # Pymunkのデバッグ描画機能を使う
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()