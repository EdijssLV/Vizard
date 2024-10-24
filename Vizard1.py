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

zombie_speed = 0.02
zombie_disappear_radius = 0.5
zombie_health = 30

red_object_speed = 0.02
red_object_disappear_radius = 0.5
red_object_health = 50
red_object_stop_radius = 3

zombies = []
red_objects = []

num_zombies = 5
num_reds = 2

def spawn_zombie():
    zombie = viz.addChild('zomb.obj')
    zombie.setPosition(get_random_position_around_character(spawn_radius))
    zombies.append(zombie)

def spawn_red_object():
    red = viz.addChild('red.obj')
    red.setPosition(get_random_position_around_character(spawn_radius))
    red_objects.append(red)

def check_and_spawn_enemies():
    global num_zombies, num_reds
    
    if not zombies and not red_objects:
        print("All enemies defeated! Spawning new wave...")
        num_zombies += 2  # Increase zombie count by 2 for each wave
        num_reds += 1  # Increase red object count by 1 for each wave
        
        for _ in range(num_zombies):
            spawn_zombie()
        
        for _ in range(num_reds):
            spawn_red_object()
    
    # Schedule the next check
    vizact.ontimer(2, check_and_spawn_enemies)  # Changed from 0.1 to 2 seconds

# Start the enemy check loop
check_and_spawn_enemies()

def move_all_zombies():
    global health_points, last_hit_time, zombie_health
    
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
                health_points -= 10
                health_display.message(f'Health: {health_points}')
                last_hit_time = current_time

            if health_points <= 0:
                zombie.remove()
                health_display.message('Health: 0 (Game Over)')
                zombies.remove(zombie)
        
        else:
            if distance > 0:
                direction = [direction[0] / distance, 0, direction[2] / distance]
                zombie.setPosition([zombie_pos[0] + direction[0] * zombie_speed, zombie_pos[1], zombie_pos[2] + direction[2] * zombie_speed])

def move_all_red_objects():
    global health_points, last_hit_time, red_object_health

    character_pos = character.getPosition()

    for red in red_objects[:]:
        red_pos = red.getPosition()
        
        direction = [character_pos[0] - red_pos[0], 0, character_pos[2] - red_pos[2]]
        distance = math.sqrt(direction[0] ** 2 + direction[2] ** 2)
        
        angle_to_character = math.degrees(math.atan2(direction[0], direction[2])) + 180
        red.setEuler([angle_to_character, 0, 0])
        
        if distance < red_object_stop_radius:
            continue
        
        if distance < red_object_disappear_radius:
            current_time = time.time()
            if current_time - last_hit_time >= hit_cooldown:
                health_points -= 10
                health_display.message(f'Health: {health_points}')
                last_hit_time = current_time

            if health_points <= 0:
                red.remove()
                health_display.message('Health: 0 (Game Over)')
                red_objects.remove(red)
                return
        
        else:
            if distance > 0:
                direction = [direction[0] / distance, 0, direction[2] / distance]
                red.setPosition([red_pos[0] + direction[0] * red_object_speed, red_pos[1], red_pos[2] + direction[2] * red_object_speed])

vizact.ontimer(0, move_all_zombies)
vizact.ontimer(0, move_all_red_objects)

bullet_speed = 10
active_bullets = []

def shoot_bullet():
    character_position = character.getPosition()
    character_orientation = character.getEuler()

    bullet = viz.addChild("jar.obj")

    bullet.setPosition(character_position[0], 0.7, character_position[2])
    bullet.setEuler(character_orientation)
    
    # Function to move the bullet forward
    def move_bullet():
        # Get the current position of the bullet
        bullet_pos = bullet.getPosition()
        camera_orientation = viz.MainView.getEuler()
        # Calculate the forward direction based on the character's yaw (horizontal rotation)
        yaw = character_orientation[0]
        pitch = math.radians(camera_orientation[1])  # Vertical rotation
        forward_x = math.sin(math.radians(yaw))
        forward_y = math.sin(pitch-0.25)
        forward_z = math.cos(math.radians(yaw))
        
        forward_vector = viz.Vector(forward_x, forward_y, forward_z) * -bullet_speed * viz.elapsed()
        new_bullet_pos = bullet_pos + forward_vector 

        # Update tShe bullet's position
        bullet.setPosition(new_bullet_pos)
        
        for red in red_objects[:]:
            red_pos = red.getPosition()
            distance = vizmat.Distance(bullet_pos, red_pos)
            if distance < 0.8:  # Adjust this value to change the collision radius
                red.remove()
                red_objects.remove(red)
                bullet.remove()
                return  # Stop the bullet movement
        
        for zombie in zombies[:]:
            zombie_pos = zombie.getPosition()
            distance = vizmat.Distance(bullet_pos, zombie_pos)
            if distance < 0.8:  # Adjust this value to change the collision radius
                zombie.remove()
                zombies.remove(zombie)
                bullet.remove()
                return
        
        # Remove the bullet if it's gone too far
        if vizmat.Distance(bullet_pos, character_position) > 20:
            bullet.remove()
            return
    vizact.ontimer(0, move_bullet)
    
def on_mouse_click(button):
    if button == viz.MOUSEBUTTON_LEFT:
        shoot_bullet()
viz.callback(viz.MOUSEDOWN_EVENT, on_mouse_click)

