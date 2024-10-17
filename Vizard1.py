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

floor_size = 32
floor = vizshape.addPlane(size=(floor_size, floor_size), axis=vizshape.AXIS_Y, cullFace=False)
floor.setPosition(0, 0, 0)
floor.color(viz.WHITE)

health_points = 100
hit_cooldown = 1.5
last_hit_time = 0
health_display = viz.addText(f'Health: {health_points}', viz.SCREEN)
health_display.setPosition(0.05, 0.95)
health_display.fontSize(24)

character = viz.addChild('rambo.obj')
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
    character.setPosition(new_pos)

def move_right():
    euler = viz.MainView.getEuler()
    yaw_radians = math.radians(euler[0] + 90)
    strafe_dir = [math.sin(yaw_radians), 0, math.cos(yaw_radians)]
    current_pos = character.getPosition()
    new_pos = [current_pos[0] + strafe_dir[0] * MOVE_SPEED * viz.elapsed(),
               current_pos[1],
               current_pos[2] + strafe_dir[2] * MOVE_SPEED * viz.elapsed()]
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

zombie = viz.addChild('zomb.obj')
zombie_speed = 0.02
zombie_disappear_radius = 0.5
zombie_health = 50
zombie.setPosition(get_random_position_around_character(spawn_radius))

def move_zombie_towards_character():
    global health_points, last_hit_time, zombie_health
    
    character_pos = character.getPosition()
    zombie_pos = zombie.getPosition()
    
    direction = [character_pos[0] - zombie_pos[0], 0, character_pos[2] - zombie_pos[2]]
    distance = math.sqrt(direction[0] ** 2 + direction[2] ** 2)
    
    angle_to_character = math.degrees(math.atan2(direction[0], direction[2])) + 180
    zombie.setEuler([angle_to_character, 0, 0])
    
    if distance < zombie_disappear_radius:
        current_time = time.time()
        if current_time - last_hit_time >= hit_cooldown:
            health_points -= 10
            health_display.message(f'Health: {health_points}')
            last_hit_time = current_time
        
        if health_points <= 0:
            zombie.remove()
            health_display.message('Health: 0 (Game Over)')
    
    else:
        if distance > 0:
            direction = [direction[0] / distance, 0, direction[2] / distance]
            zombie.setPosition([zombie_pos[0] + direction[0] * zombie_speed, zombie_pos[1], zombie_pos[2] + direction[2] * zombie_speed])

vizact.ontimer(0, move_zombie_towards_character)

red_object = viz.addChild('red.obj')
red_object.setPosition(get_random_position_around_character(spawn_radius))
red_object_speed = 0.01
red_object_disappear_radius = 0.5
red_object_health = 30
red_object_stop_radius = 3
bullet_speed = 10
red_bullets = []

def shoot_red_bullet():
    bullet = vizshape.addSphere(radius=0.1, color=viz.RED)
    bullet.setPosition(red_object.getPosition()[0], red_object.getPosition()[1] + 1.0, red_object.getPosition()[2])
    character_pos = character.getPosition()
    direction = [character_pos[0] - bullet.getPosition()[0], 0, character_pos[2] - bullet.getPosition()[2]]
    distance = math.sqrt(direction[0] ** 2 + direction[2] ** 2)
    
    if distance > 0:
        direction = [direction[0] / distance, 0, direction[2] / distance]

    red_bullets.append((bullet, direction))

def update_red_bullets():
    global red_bullets
    
    for bullet, direction in red_bullets[:]:
        bullet_pos = bullet.getPosition()
        new_pos = [bullet_pos[0] + direction[0] * bullet_speed * viz.elapsed(),
                   bullet_pos[1],
                   bullet_pos[2] + direction[2] * bullet_speed * viz.elapsed()]
        bullet.setPosition(new_pos)
        
        character_pos = character.getPosition()
        distance_to_character = math.sqrt((new_pos[0] - character_pos[0]) ** 2 + (new_pos[2] - character_pos[2]) ** 2)
        
        if distance_to_character < 0.5:
            bullet.remove()
            red_bullets.remove((bullet, direction))
            global health_points
            health_points -= 10
            health_display.message(f'Health: {health_points}')
            if health_points <= 0:
                health_display.message('Health: 0 (Game Over)')

is_red_object_active = True

def move_red_object_towards_character():
    global health_points, last_hit_time, red_object_health, is_red_object_active
    
    if not is_red_object_active:
        return  # Stop processing if red object is no longer active

    character_pos = character.getPosition()
    red_object_pos = red_object.getPosition()
    
    direction = [character_pos[0] - red_object_pos[0], 0, character_pos[2] - red_object_pos[2]]
    distance = math.sqrt(direction[0] ** 2 + direction[2] ** 2)
    
    angle_to_character = math.degrees(math.atan2(direction[0], direction[2])) + 180
    red_object.setEuler([angle_to_character, 0, 0])
    
    if distance < red_object_stop_radius:
        return  # Red object stops moving when within the stop radius
    
    if distance < red_object_disappear_radius:
        current_time = time.time()
        if current_time - last_hit_time >= hit_cooldown:
            health_points -= 10
            health_display.message(f'Health: {health_points}')
            last_hit_time = current_time
            
        if health_points <= 0:
            red_object.remove()
            health_display.message('Health: 0 (Game Over)')
            is_red_object_active = False  # Set flag to False after red object is removed
            return  # Stop further processing
    
    else:
        if distance > 0:
            direction = [direction[0] / distance, 0, direction[2] / distance]
            red_object.setPosition([red_object_pos[0] + direction[0] * red_object_speed, red_object_pos[1], red_object_pos[2] + direction[2] * red_object_speed])

vizact.ontimer(0, move_red_object_towards_character)
vizact.ontimer(0, update_red_bullets)