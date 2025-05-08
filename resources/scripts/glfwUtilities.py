import glfw as GLFW

def getKeyPressed(window: GLFW._GLFWwindow, key: int) -> bool:
    return GLFW.get_key(window, key) == GLFW.PRESS
