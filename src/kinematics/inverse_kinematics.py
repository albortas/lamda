import numpy as np
from math import sqrt, asin, acos, pi, sin, sin, cos

def forward_kinematics (theta, legs, side): #Forward Kinematics
    """ Calculo de puntos de artic """
    """
       s = 1 for left leg (pierna izquierda)
       s = -1 for right leg (pierna derecha)
    """
    x1 = 0
    y1 =  legs['d'] * sin(theta[0])
    z1 = -legs['d'] * cos(theta[0])
    
    x2 = 0
    y2 =side * legs['L0'] * cos(theta[0]) + legs['d'] * sin(theta[0])
    z2 =side * legs['L0'] * sin(theta[0]) - legs['d'] * cos(theta[0]) 
            
    x3 = - legs['L1'] *sin(theta[1])
    y3 = side * legs['L0'] * cos(theta[0]) - (- legs['d'] - legs['L1'] * cos(theta[1])) * sin(theta[0])
    z3 = side * legs['L0'] * sin(theta[0]) + (- legs['d'] - legs['L1'] * cos(theta[1])) * cos(theta[0])
    
    return [
        x1, x2, x3,
        y1, y2, y3,
        z1, z2, z3
    ]

def inverse_kinematics(x, y, z, legs, side):
    """Calulo de cinematica de inversa"""
    """
       s = 1 for left leg (pierna izquierda)
       s = -1 for right leg (pierna derecha)
    """
       
    OG = sqrt(y**2 + z**2)
    BG = sqrt(OG**2 - legs['L0']**2)
    AG = BG - legs['d']
    AC = sqrt(x**2 + AG**2)
    try:
        alpha = asin(BG / OG)
        beta = asin(y / OG)
        theta1 = side * (-pi/2 + alpha) + beta
        theta3 = acos((legs['L1']**2 + legs['L2']**2 - AC**2)/(2 * legs['L1'] * legs['L2'])) - pi
        gamma = -asin(x/AC)
        sigma = acos((legs['L1']**2 + AC**2 - legs['L2']**2)/(2 * legs['L1'] * AC))
        theta2 = gamma + sigma
        
    except ValueError:
        print('ValueError IK')
        theta1 = theta2 = theta3 = pi/2  # Valores default
        
    return [theta1, theta2, theta3]

def inverse_kinematics_all(pos_init, legs):
    #LF, RF, RR, LR
    foot = [1, -1, -1, 1]
    angles = np.zeros((3,4))    
    for i in range(4):
        x = pos_init[0,i]
        y = pos_init[1,i]
        z = pos_init[2,i]
        angles[:,i] = inverse_kinematics(x, y, z, legs, foot[i])
    return angles

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider

    # Configuración inicial
    leg_lengths = {
        'L0': 1.0,
        'L1': 1.0,
        'd': 1.0
    }

    initial_angles = [np.pi/2, np.pi/2, np.pi/2]
    side = 1

    # Función para actualizar la gráfica
    def update(val):
        theta1 = s_theta1.val
        theta2 = s_theta2.val
        theta3 = s_theta3.val
        
        joint_angles = [theta1, theta2, theta3]
        
        # Actualizar las posiciones
        positions = forward_kinematics(joint_angles, leg_lengths, side)
        
        # Actualizar los puntos en la gráfica
        graph_base.set_offsets([0, 0])
        graph_base.set_3d_properties([0], 'blue')
        
        graph_hip1_yaw.set_offsets([positions[0], positions[3]])
        graph_hip1_yaw.set_3d_properties([positions[6]], 'green')
        
        graph_hip2_yaw.set_offsets([positions[1], positions[4]])
        graph_hip2_yaw.set_3d_properties([positions[7]], 'orange')
        
        graph_knee.set_offsets([positions[2], positions[5]])
        graph_knee.set_3d_properties([positions[8]], 'red')
        
        # Actualizar la posición del efector final
        x_target = positions[2]
        y_target = positions[5]
        z_target = positions[8]
        
        graph_target.set_offsets([x_target, y_target])
        graph_target.set_3d_properties([z_target], 'red')
        
        # Actualizar las conexiones
        line_base2s1.set_data([0, positions[0]], [0, positions[3]])
        line_base2s1.set_3d_properties([0, positions[6]])
        
        line_s12s2.set_data([positions[0], positions[1]], [positions[3], positions[4]])
        line_s12s2.set_3d_properties([positions[6], positions[7]])
        
        line_s2knee.set_data([positions[1], positions[2]], [positions[4], positions[5]])
        line_s2knee.set_3d_properties([positions[7], positions[8]])
        
        # Conexión del efector final
        line_knee_target.set_data([positions[2], x_target], [positions[5], y_target])
        line_knee_target.set_3d_properties([positions[8], z_target])
        
        fig.canvas.draw_idle()

    # Crear la figura y el ax principal
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(bottom=0.4)  # Espacio para los sliders

    # Inicializar la gráfica
    positions_initial = forward_kinematics(initial_angles, leg_lengths, side)

    # Plot de las articulaciones
    graph_base = ax.scatter(0, 0, 0, color='blue', s=100, label='Base')
    graph_hip1_yaw = ax.scatter(positions_initial[0], positions_initial[3], positions_initial[6], color='green', s=50, label='hip 1')
    graph_hip2_yaw = ax.scatter(positions_initial[1], positions_initial[4], positions_initial[7], color='orange', s=50, label='hip 2')
    graph_knee = ax.scatter(positions_initial[2], positions_initial[5], positions_initial[8], color='red', s=50, label='knee')
    graph_target = ax.scatter(positions_initial[2], positions_initial[5], positions_initial[8], color='red', s=50, label='Target Point')

    # Plot de las conexiones
    line_base2s1, = ax.plot([0, positions_initial[0]], [0, positions_initial[3]], [0, positions_initial[6]], color='blue')
    line_s12s2, = ax.plot([positions_initial[0], positions_initial[1]], [positions_initial[3], positions_initial[4]], [positions_initial[6], positions_initial[7]], color='blue')
    line_s2knee, = ax.plot([positions_initial[1], positions_initial[2]], [positions_initial[4], positions_initial[5]], [positions_initial[7], positions_initial[8]], color='blue')
    line_knee_target, = ax.plot([positions_initial[2], positions_initial[2]], [positions_initial[5], positions_initial[5]], [positions_initial[8], positions_initial[8]], color='red', linestyle='--')

    # Configurar los sliders
    ax_theta1 = plt.axes([0.2, 0.3, 0.6, 0.03])
    ax_theta2 = plt.axes([0.2, 0.25, 0.6, 0.03])
    ax_theta3 = plt.axes([0.2, 0.2, 0.6, 0.03])

    s_theta1 = Slider(ax_theta1, 'Theta1', 0, 2*np.pi, valinit=initial_angles[0])
    s_theta2 = Slider(ax_theta2, 'Theta2', 0, 2*np.pi, valinit=initial_angles[1])
    s_theta3 = Slider(ax_theta3, 'Theta3', 0, 2*np.pi, valinit=initial_angles[2])

    # Conectar los sliders con la función de actualización
    s_theta1.on_changed(update)
    s_theta2.on_changed(update)
    s_theta3.on_changed(update)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Forward Kinematics Visualization')
    ax.legend()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)

    plt.show()


        