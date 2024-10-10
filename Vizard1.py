import viz
import vizshape
import vizact
import vizinput
import math
import random

viz.window.setSize(1280 , 720)
viz.go()

viz.clearcolor(viz.SKYBLUE)
viz.MainView.getHeadLight().enable()

floor_size = 32
floor = vizshape.addPlane(size=(floor_size, floor_size), axis=vizshape.AXIS_Y, cullFace=False)
floor.setPosition(0, 0, 0)
floor.color(viz.WHITE)

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

jar = viz.addChild('red.obj')
jar_speed = 0.03
jar_disappear_radius = 0.1
points_to_deduct = 100

jar.setPosition([random.uniform(-floor_size / 2 + 1, floor_size / 2 - 1), 0.5, random.uniform(-floor_size / 2 + 1, floor_size / 2 - 1)])  # Spawn jar at a random location

def move_jar_towards_character():
    global score_player1, score_player2, timer_cycles  # Ensure correct player score is accessed
    
    character_pos = character.getPosition()
    jar_pos = jar.getPosition()
    
    # Calculate the direction towards the character
    direction = [character_pos[0] - jar_pos[0], 0, character_pos[2] - jar_pos[2]]
    distance = math.sqrt(direction[0] ** 2 + direction[2] ** 2)
    
    # If jar is within the disappearing radius, deduct points and remove jar
    if distance < jar_disappear_radius:
        jar.remove()
    else:
        # Move the jar towards the player if not within radius
        if distance > 0:
            direction = [direction[0] / distance, 0, direction[2] / distance]
            jar.setPosition([jar_pos[0] + direction[0] * jar_speed, jar_pos[1], jar_pos[2] + direction[2] * jar_speed])

# Update the timer to call the jar movement function
vizact.ontimer(0, move_jar_towards_character)