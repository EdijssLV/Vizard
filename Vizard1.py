import viz
import vizshape
import vizact
import vizinput
import math
import random
import time

viz.window.setSize(1280, 720)
viz.go()

viz.clearcolor(viz.SKYBLUE)
viz.MainView.getHeadLight().enable()

floor_size = 50
floor = vizshape.addPlane(size=(floor_size, floor_size), axis=vizshape.AXIS_Y, cullFace=False)
floor.setPosition(0, 0, 0)
floor.color([1, 1, 1])

def spawn_walls(num_walls):
    for _ in range(num_walls):
        wall = viz.addChild(f'assets/monkey.obj')
        wall.setPosition([random.uniform(-floor_size/2, floor_size/2), 0, random.uniform(-floor_size/2, floor_size/2)])
        random_scale = random.uniform(1, 3.0)
        wall.setScale([random_scale, random_scale, random_scale])
        random_rotation = random.uniform(0, 360)
        wall.setEuler([random_rotation, 0, 0])

viz.MainView.getHeadLight().enable()
viz.MainView.getHeadLight().setPosition([0, 0, 0])
viz.MainView.getHeadLight().setEuler([0, 0, 0])
viz.MainView.getHeadLight().intensity(1.2)

spawn_walls(50)

arena = viz.addChild(f'assets/arena.obj')

health_points = 100
hit_cooldown = 2
last_hit_time = 0

health_display = viz.addText(f'Health: {health_points}', viz.SCREEN)
health_display.setPosition(0.05, 0.95)
health_display.fontSize(24)

score = 0
score_display = viz.addText(f'Score: {score}', viz.SCREEN)
score_display.setPosition(0.05, 0.9)
score_display.fontSize(24)

def update_score(points):
    global score
    score += points
    score_display.message(f'Score: {score}')

b = viz.addText(f'X', viz.SCREEN)
b.setPosition(0.49, 0.75)
b.fontSize(30)

character = viz.addChild('assets/rambo.obj')
character.setPosition([0, 0, 0])

camera_distance = 4
camera_height = 1.5
yaw = 0
pitch = 0

def update_camera():
    character_pos = character.getPosition()
    camera_pos = [character_pos[0] + camera_distance * math.sin(math.radians(yaw)),
                  character_pos[1] + camera_height,
                  character_pos[2] + camera_distance * math.cos(math.radians(yaw))]
    target_offset = [0, 0.5, 0]
    target_pos = [character_pos[0] + target_offset[0],
                  character_pos[1] + target_offset[1],
                  character_pos[2] + target_offset[2]]
    viz.MainView.setPosition(camera_pos)
    viz.MainView.lookAt(target_pos)
    character.setEuler([yaw, 0, 0])

MOVE_SPEED = 10

def move(direction):
    euler = viz.MainView.getEuler()
    yaw_radians = math.radians(euler[0])
    move_dir = [math.sin(yaw_radians) * direction, 0, math.cos(yaw_radians) * direction]
    current_pos = character.getPosition()
    new_pos = [current_pos[0] + move_dir[0] * MOVE_SPEED * viz.elapsed(),
               current_pos[1],
               current_pos[2] + move_dir[2] * MOVE_SPEED * viz.elapsed()]
    
    new_pos[0] = max(-floor_size/2, min(floor_size/2, new_pos[0]))
    new_pos[2] = max(-floor_size/2, min(floor_size/2, new_pos[2]))
    
    character.setPosition(new_pos)

def move_forward():
    move(1)

def move_backward():
    move(-1)

def move_left():
    euler = viz.MainView.getEuler()
    yaw_radians = math.radians(euler[0] - 90)
    strafe_dir = [math.sin(yaw_radians), 0, math.cos(yaw_radians)]
    current_pos = character.getPosition()
    new_pos = [current_pos[0] + strafe_dir[0] * MOVE_SPEED * viz.elapsed(),
               current_pos[1],
               current_pos[2] + strafe_dir[2] * MOVE_SPEED * viz.elapsed()]
    
    new_pos[0] = max(-floor_size/2, min(floor_size/2, new_pos[0]))
    new_pos[2] = max(-floor_size/2, min(floor_size/2, new_pos[2]))
    
    character.setPosition(new_pos)

def move_right():
    euler = viz.MainView.getEuler()
    yaw_radians = math.radians(euler[0] + 90)
    strafe_dir = [math.sin(yaw_radians), 0, math.cos(yaw_radians)]
    current_pos = character.getPosition()
    new_pos = [current_pos[0] + strafe_dir[0] * MOVE_SPEED * viz.elapsed(),
               current_pos[1],
               current_pos[2] + strafe_dir[2] * MOVE_SPEED * viz.elapsed()]
    
    new_pos[0] = max(-floor_size/2, min(floor_size/2, new_pos[0]))
    new_pos[2] = max(-floor_size/2, min(floor_size/2, new_pos[2]))
    
    character.setPosition(new_pos)

vizact.onkeydown('w', move_forward)
vizact.onkeydown('s', move_backward)
vizact.onkeydown('a', move_left)
vizact.onkeydown('d', move_right)

MOUSE_SENSITIVITY = 0.1

def onMouseMove(e):
    global yaw, pitch
    yaw += e.dx * MOUSE_SENSITIVITY
    pitch -= e.dy * MOUSE_SENSITIVITY
    pitch = max(-90, min(90, pitch))
    update_camera()

viz.mouse.setVisible(False)
viz.mouse.setTrap(True)
viz.callback(viz.MOUSE_MOVE_EVENT, onMouseMove)

vizact.ontimer(0, update_camera)

def get_random_position_around_character(radius):
    character_pos = character.getPosition()
    angle = random.uniform(0, 2 * math.pi)
    x_offset = radius * math.cos(angle)
    z_offset = radius * math.sin(angle)
    return [character_pos[0] + x_offset, 0, character_pos[2] + z_offset]

spawn_radius = 15

zombie_disappear_radius = 0.5
zombie_health = 30

zombies = []

num_zombies = 3


def spawn_zombie():
    zombie = viz.addChild('assets/zomb.fbx')
    #zombie.setPosition([random.uniform(-floor_size/2, floor_size/2), 0, random.uniform(-floor_size/2, floor_size/2)])
    zombie.setPosition(get_random_position_around_character(spawn_radius))
    zombie.health = zombie_health 
    zombies.append(zombie)
    zombie.setScale([0.01, 0.01, 0.01])
    zombie.speed = random.uniform(0.03, 0.07)

def check_and_spawn_enemies():
    global num_zombies
    
    if not zombies:
        print("All enemies defeated!")
        num_zombies += 2
        
        for _ in range(num_zombies):
            spawn_zombie()
    
    vizact.ontimer(5, check_and_spawn_enemies)

check_and_spawn_enemies()

def move_all_zombies():
    global health_points, last_hit_time
    
    character_pos = character.getPosition()

    for zombie in zombies[:]:
        zombie_pos = zombie.getPosition()
        
        direction = [character_pos[0] - zombie_pos[0], 0, character_pos[2] - zombie_pos[2]]
        distance = math.sqrt(direction[0] ** 2 + direction[2] ** 2)
        
        angle_to_character = math.degrees(math.atan2(direction[0], direction[2])) + 180
        zombie.setEuler([angle_to_character, 0, 0])
        
        if distance < zombie_disappear_radius:
            current_time = time.time()
            if current_time - last_hit_time >= hit_cooldown:
                health_points -= 15
                health_display.message(f'Health: {health_points}')
                last_hit_time = current_time

            if health_points <= 0:
                zombie.remove()
                health_display.message('Health: 0 (Game Over)')
                zombies.remove(zombie)
                vizinput.message('Game Over! Final Score: \n{} points!'.format(score))
                viz.quit()
        
        else:
            if distance > 0:
                direction = [direction[0] / distance, 0, direction[2] / distance]
                zombie.setPosition([zombie_pos[0] + direction[0] * zombie.speed, zombie_pos[1], zombie_pos[2] + direction[2] * zombie.speed])

vizact.ontimer(0, move_all_zombies)

bullet_speed = 50
active_bullets = []

def shoot_bullet():
    character_position = character.getPosition()
    character_orientation = character.getEuler()

    bullet = vizshape.addSphere(radius=0.1,
               slices=4,
               stacks=4,
               axis=vizshape.AXIS_Y)

    bullet.setPosition(character_position[0], 0.7, character_position[2])
    bullet.setEuler(character_orientation)
    
    def move_bullet():
        bullet_pos = bullet.getPosition()
        camera_orientation = viz.MainView.getEuler()
        
        yaw = character_orientation[0]
        pitch = math.radians(camera_orientation[1])
        forward_x = math.sin(math.radians(yaw))
        forward_y = math.sin(pitch-0.25)
        forward_z = math.cos(math.radians(yaw))
        
        forward_vector = viz.Vector(forward_x, forward_y, forward_z) * -bullet_speed * viz.elapsed()
        new_bullet_pos = bullet_pos + forward_vector 

        bullet.setPosition(new_bullet_pos)
        
        for zombie in zombies[:]:
            zombie_pos = zombie.getPosition()
            distance = vizmat.Distance(bullet_pos, zombie_pos)
            if distance < 0.8:
                zombie.health -= 10
                if zombie.health <= 0:
                    zombie.remove()
                    zombies.remove(zombie)
                    update_score(int(500 * zombie.speed))
                bullet.remove()
                return
        
        if vizmat.Distance(bullet_pos, character_position) > 20:
            bullet.remove()
            return
    vizact.ontimer(0, move_bullet)
    
def on_mouse_click(button):
    if button == viz.MOUSEBUTTON_LEFT:
        shoot_bullet()
viz.callback(viz.MOUSEDOWN_EVENT, on_mouse_click)