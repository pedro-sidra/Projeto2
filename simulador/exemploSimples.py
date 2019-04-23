"""
Exemplo de uso da classe Simulador4e

Essa classe facilita o uso do simulador do quarto eixo.

Ela gerencia:
    - Rotação da peça
    - Eixos e plots
"""

import numpy as np
from Simulador4e import Simulador4e


# *---- Define as funções de cálculo para cada método que vamos usar
# Calcula pelo método da "sombra" (came de face plana)
# Uma função de update DEVE receber esses dois parametros
# -sim_params possui parametros da simulação
# -state  é do controle do usuário, são as var. de estado desse cálculo


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
    return (*pShadow,state)


# Calcula pelo método da "came" (laser)
def calc_came(sim_params, state):
    theta = sim_params['theta']
    points = sim_params['points']

    x, y = points
    y_zero = np.isclose(x, 0, atol=1e-2, rtol=1e-2)
    x_came = np.max(y[y_zero])

    return ([0, 0],
            [0, x_came],
            state)


def main():
    # Cria um objeto de simulador do 4o eixo
    # Ele mostra uma grade 2x3 de gráficos,
    # E usa 360 frames em uma rotação (1 frame/grau)
    sim = Simulador4e(dims=(1, 2),
                      frames=360,)

    # para cada item da grade, adiciona:
    # uma peça
    # um plot que se atualiza, calculando um dos métodos definidos

    sim.add_piece((0, 0), color='k-')
    sim.add_plot((0, 0),
                 calc_shadow,
                 color='ro-'
                 )

    sim.add_piece((0, 1), color='k-')
    sim.add_plot((0, 1),
                 calc_came,
                 color='bo-'
                 )


    # Roda a simulação
    sim.run()

if __name__=="__main__":
    main()
