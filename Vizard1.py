import viz
import vizshape
import vizact

# Initialize the window
#viz.window.setSize(1280, 720)
viz.go()
viz.clearcolor(viz.SKYBLUE)

# Add a floor
floor_size = 32
floor = vizshape.addPlane(size=(floor_size, floor_size))
floor.setPosition(0, 0, 0)
floor.color(viz.WHITE)

# Add an avatar
character = viz.add('red.obj')
character.setPosition(0, 0, 0)

camera_height = 1.5  # Height of the camera from the player's position
yaw = 0  # Horizontal rotation
pitch = 0  # Vertical rotation
sensitivity = 0.2  # Mouse sensitivity for looking around

# Hide the mouse cursor
viz.mouse.setVisible(viz.OFF)

# Lock the mouse within the window
viz.mouse.setTrap(viz.ON)

# Function to update the camera
def update_camera():
    global yaw, pitch

    # Get the current mouse position (normalized between 0.0 and 1.0)
    x, y = viz.mouse.getPosition()

    # Calculate yaw (left-right) and pitch (up-down) changes based on the cursor movement
    yaw = (x - 0.5) * 360  # Scale yaw from the normalized mouse position
    pitch = -(y - 0.5) * 180  # Scale pitch from the normalized mouse position

    # Clamp pitch to avoid flipping the view upside down
    pitch = max(-89.0, min(89.0, pitch))

    # Get the character's position
    character_pos = character.getPosition()

    # Set the camera position at the character's position with the camera height
    camera_pos = [character_pos[0],
                  character_pos[1] + camera_height,
                  character_pos[2]]

    # Update camera position and orientation
    viz.MainView.setPosition(camera_pos)
    viz.MainView.setEuler([yaw, pitch, 0])

    # Make the character face the direction of the camera (yaw only)
    character.setEuler([yaw, 0, 0])

# Call the update_camera function every frame
vizact.ontimer(0, update_camera)