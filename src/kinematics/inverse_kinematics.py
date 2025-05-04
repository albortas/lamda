import numpy as np
from math import sqrt, asin, acos, pi, sin, sin, cos, atan
def inverse_kinematics(x, y, z, legs, side):
    """Calulo de cinematica de inversa
       s = 1 for left leg (pierna izquierda)
       s = -1 for right leg (pierna derecha)"""
       
    
             
    C = sqrt(y**2 + z**2)
    E = sqrt(C**2 - legs['L0']**2)
    D = E - legs['d']
    G = sqrt(x**2 + D**2)
    try:
        alpha = asin(E / C)
        beta = asin(y / C)
        theta1 = side * (-pi/2 + alpha) + beta
        theta3 = acos((legs['L1']**2 + legs['L2']**2 - G**2)/(2 * legs['L1'] * legs['L2']))
        gamma = atan(x/D)
        sigma = acos((legs['L1']**2 + G**2 - legs['L2']**2)/(2 * legs['L1'] * G))
        sigma = legs['L2'] * sin(theta3) / G
        theta2 = gamma + sigma
    except ValueError:
        print('ValueError IK')
        theta1 = theta2 = theta3 = pi/2  # Valores default
        
    return [theta1, theta2, theta3]

def forward_kinematics (theta, legs, side): #Forward Kinematics
    """ Calculation of articulation points """
    """
    s = 1 for left leg
    s = -1 for right leg
    """
    shoulder1_x = 0
    shoulder1_y =  legs['d'] * sin(theta[0])
    shoulder1_z = -legs['d'] * cos(theta[0])
    
    shoulder2_x = 0
    shoulder2_y =side * legs['L0'] * cos(theta[0]) + legs['d'] * sin(theta[0])
    shoulder2_z =side * legs['L0'] * sin(theta[0]) - legs['d'] * cos(theta[0]) 
            
    elbow_x = - legs['L1'] *sin(theta[1])
    elbow_y = side * legs['L0'] * cos(theta[0]) - (- legs['d'] - legs['L1'] * cos(theta[1])) * sin(theta[0])
    elbow_z = side * legs['L0'] * sin(theta[0]) + (- legs['d'] - legs['L1'] * cos(theta[1])) * cos(theta[0])
    
    return [
        shoulder1_x, shoulder2_x, elbow_x,
        shoulder1_y, shoulder2_y, elbow_y,
        shoulder1_z, shoulder2_z, elbow_z
    ]

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

    initial_angles = [np.pi/4, np.pi/4, np.pi/4]
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
        
        graph_shoulder1.set_offsets([positions[0], positions[3]])
        graph_shoulder1.set_3d_properties([positions[6]], 'green')
        
        graph_shoulder2.set_offsets([positions[1], positions[4]])
        graph_shoulder2.set_3d_properties([positions[7]], 'orange')
        
        graph_elbow.set_offsets([positions[2], positions[5]])
        graph_elbow.set_3d_properties([positions[8]], 'red')
        
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
        
        line_s2elbow.set_data([positions[1], positions[2]], [positions[4], positions[5]])
        line_s2elbow.set_3d_properties([positions[7], positions[8]])
        
        # Conexión del efector final
        line_elbow_target.set_data([positions[2], x_target], [positions[5], y_target])
        line_elbow_target.set_3d_properties([positions[8], z_target])
        
        fig.canvas.draw_idle()

    # Crear la figura y el ax principal
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.subplots_adjust(bottom=0.4)  # Espacio para los sliders

    # Inicializar la gráfica
    positions_initial = forward_kinematics(initial_angles, leg_lengths, side)

    # Plot de las articulaciones
    graph_base = ax.scatter(0, 0, 0, color='blue', s=100, label='Base')
    graph_shoulder1 = ax.scatter(positions_initial[0], positions_initial[3], positions_initial[6], color='green', s=50, label='Shoulder 1')
    graph_shoulder2 = ax.scatter(positions_initial[1], positions_initial[4], positions_initial[7], color='orange', s=50, label='Shoulder 2')
    graph_elbow = ax.scatter(positions_initial[2], positions_initial[5], positions_initial[8], color='red', s=50, label='Elbow')
    graph_target = ax.scatter(positions_initial[2], positions_initial[5], positions_initial[8], color='red', s=50, label='Target Point')

    # Plot de las conexiones
    line_base2s1, = ax.plot([0, positions_initial[0]], [0, positions_initial[3]], [0, positions_initial[6]], color='blue')
    line_s12s2, = ax.plot([positions_initial[0], positions_initial[1]], [positions_initial[3], positions_initial[4]], [positions_initial[6], positions_initial[7]], color='blue')
    line_s2elbow, = ax.plot([positions_initial[1], positions_initial[2]], [positions_initial[4], positions_initial[5]], [positions_initial[7], positions_initial[8]], color='blue')
    line_elbow_target, = ax.plot([positions_initial[2], positions_initial[2]], [positions_initial[5], positions_initial[5]], [positions_initial[8], positions_initial[8]], color='red', linestyle='--')

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


        