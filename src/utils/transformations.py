import numpy as np
def matriz_2d():
    Mp = np.array([ [1,0,0],
                    [0,1,0],
                    [0,0,0]])
    return Mp

def rotz(gamma):
    """
    Crea una matriz de rotacion 3x3 sobre el eje z
    """
    rz = np.array([[np.cos(gamma), -np.sin(gamma), 0],
                   [np.sin(gamma), np.cos(gamma), 0],
                   [0, 0, 1]])
    return rz

def xyz_rotation_matrix(thetax, thetay, thetaz, inverse = False):
    cx, sx = np.cos(thetax), np.sin(thetax)
    cy, sy = np.cos(thetay), np.sin(thetay)
    cz, sz = np.cos(thetaz), np.sin(thetaz)

    if inverse:
        # Rzyx = Rx * Ry * Rz
        M = np.array([
            [cy * cz, -sz * cy, sy],
            [sx * sy * cz + sz * cx, -sx * sy * sz + cx * cz, -sx * cy],
            [sx * sz - sy * cx * cz, sx * cz + sy * sz * cx, cx * cy]
        ])
    else:
        # Rxyz = Rz * Ry * Rx
        M = np.array([
            [cy * cz, sx * sy * cz - sz * cx, sx * sz + sy * cx * cz],
            [sz * cy, sx * sy * sz + cx * cz, -sx * cz + sy * sz * cx],
            [-sy, sx * cy, cx * cy]
        ])
    return M

def new_coordinates(M, x, y, z, dx = 0, dy = 0, dz = 0):
    """
    Transforma punto usando una matriz de rotación y una traslación.
    """
    point = np.array([x, y, z])
    offset = np.array([dx, dy, dz])
    transformed_point = M @ point + offset
    return transformed_point.tolist()

def new_coordinates_vec(rotation_matrix, x_array, y_array, z_array, dx=0, dy=0, dz=0):
    """
    Transforma múltiples puntos usando una matriz de rotación y una traslación.
    """
    # Apilar coordenadas en una matriz (3, n)
    points = np.stack([x_array, y_array, z_array])
    
    # Aplicar rotación: (3x3) @ (3xn) -> (3xn)
    rotated = np.dot(rotation_matrix, points)
    
    # Aplicar traslación (broadcasting automático)
    translated = rotated + np.vstack([dx, dy, dz])
    
    # Devolver como tres arrays separados
    return translated

def display_rotate(x_robot, y_robot, z_robot, theta_robot, xl, yl, zl, screen_x = 600, screen_y = 600):
    # Convertir xl, yl, zl en un array de forma (N, 3)
    #thetax, thetaz = np.pi/2 , 0 # ver plano zx
    #thetax, thetaz = np.pi , 0 # ver plano xy
    #thetax, thetaz = np.pi/2 , -np.pi/2 # ver plano zy
    thetax, thetaz = np.pi*(105/180) , -np.pi*(135/180) # ver plano xyz
    escala = 1
    coordenada_x, coordenada_y = screen_x/2, screen_y/2
    puntos = np.vstack((xl, yl, zl)).T  # Forma (N, 3)

    # Matrices de rotación
    Ma = xyz_rotation_matrix(theta_robot[3], theta_robot[4], theta_robot[2] + theta_robot[5], False)
    Mb = xyz_rotation_matrix(theta_robot[0], theta_robot[1], 0, False)
    M1 = xyz_rotation_matrix(thetax, 0, thetaz, True)   # Vista de camara

    # Transformaciones vectorizadas
    puntos_transformados_1 = puntos @ Ma.T + np.array([x_robot, y_robot, z_robot])
    puntos_transformados_2 = puntos_transformados_1 @ Mb.T
    puntos_transformados_3 = puntos_transformados_2 @ M1.T

    # Proyección en 2D
    proyeccion_2d = matriz_2d() @ puntos_transformados_3.T  # Forma (2, N)

    # Escalar y trasladar
    x = proyeccion_2d[0] * escala + coordenada_x
    y = proyeccion_2d[1] * escala + coordenada_y

    # Convertir a enteros y devolver como lista de tuplas
    puntos_2d = np.vstack((x.astype(int), y.astype(int))).T  # Forma (N, 2)
    return [tuple(punto) for punto in puntos_2d]