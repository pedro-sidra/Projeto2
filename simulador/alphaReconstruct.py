"""
"""

import numpy as np
from Simulador4e import Simulador4e

ra = 10
lamb = False


def calc_alpha(sim_params, state):
    global ra, lamb
    theta = sim_params['theta']
    points = sim_params['points']

    x, y = points

    alpha = np.arctan2((y), (ra-x))
    x_alpha = x[np.argmax(alpha)]
    y_alpha = y[np.argmax(alpha)]

    m = np.tan(np.pi-np.max(alpha))

    if not lamb:
        lamb = np.arctan2(np.sqrt(x_alpha**2+y_alpha**2), ra)

    return ([ra, -2],
            [0, m*(-2)-ra*m],
            state)


def reconstruct_shadow(sim_params, state):
    global ra, lamb

    x_rec, y_rec, lastshadow = state

    theta = sim_params['theta']
    dtheta = sim_params['dtheta']
    points = sim_params['points']

    x, y = points

    x_shadow = np.max(y)

    deltashadow = (x_shadow-lastshadow)/dtheta

    x = x_shadow * np.cos(theta) - deltashadow*np.sin(theta)
    y = x_shadow * np.sin(theta) + deltashadow*np.cos(theta)

    x_rec.append(x)
    y_rec.append(y)

    state = (x_rec, y_rec, x_shadow)
    return (x_rec,
            y_rec,
            state)


def reconstruct_alpha(sim_params, state):
    global ra, lamb

    x_rec, y_rec, lastPhi, lastdphi = state

    theta = sim_params['theta']
    dtheta = sim_params['dtheta']
    points = sim_params['points']

    x, y = points
    alpha = np.arctan2((y), (ra-x))
    x_alpha = x[np.argmax(alpha)]
    y_alpha = y[np.argmax(alpha)]

    phi = np.max(alpha)
    N = + theta - phi
    dphi = (phi-lastPhi)/dtheta

    x = ra*(np.cos(theta) + (np.cos(phi)*np.cos(N))/(dphi-1))
    y = ra*(np.sin(theta) + (np.cos(phi)*np.sin(N))/(dphi-1))

    # x= x[np.argmax(phi)]
    # y= y[np.argmax(phi)]

    x_rec.append(x)
    y_rec.append(y)

    state = (x_rec, y_rec, phi, dphi)
    return (x_rec,
            y_rec,
            state)


def calc_shadow(sim_params, state):

    # sim_params, no momento, é um dicionário com os seguintes parametros:
    # i  - iteração da simulação
    # points  - pontos da peça
    # theta  - angulo da peça
    # dtheta  - rotação em um frame

    theta = sim_params['theta']
    points = sim_params['points']

    x, y = points

    x_shadow = np.max(y)

    pShadow = np.array([
        [-2, 2],
        [x_shadow, x_shadow],
    ])

    # Função deve retornar : x,y, NewState
    # NewState contém os novos valores das variáveis de estado desse cálculo return (*pShadow, state)
    return (*pShadow, state)


def main():
    # Cria um objeto de simulador do 4o eixo
    # Ele mostra uma grade 2x3 de gráficos,
    # E usa 360 frames em uma rotação (1 frame/grau)
    sim = Simulador4e(dims=(2, 2),
                      frames=720,)

    # para cada item da grade, adiciona:
    # uma peça
    # um plot que se atualiza, calculando um dos métodos definidos

    sim.add_piece((0, 0), color='k-')
    sim.add_plot((0, 0),
                 calc_alpha,
                 color='yo-'
                 )
    sim.axes[0,0].set_title('Came Rotação')

    sim.add_plot((0, 1),
                 reconstruct_alpha,
                 states0=[[], [], 0, 0],
                 color='yo-'
                 )
    sim.axes[0,1].set_title('Reconstrução')

    sim.add_piece((1, 0), color='k-')
    sim.add_plot((1, 0),
                 calc_shadow,
                 color='ro-'
                 )
    sim.axes[1,0].set_title('Came Translação')

    sim.add_plot((1, 1),
                 reconstruct_shadow,
                 states0=[[],[],0],
                 color='ro-',
                 )
    sim.axes[1,1].set_title('Reconstrução')

    # Roda a simulação
    sim.run()


if __name__ == "__main__":
    main()
