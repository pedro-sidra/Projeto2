"""
Classe-base para aplicações do simulador de quarto eixo

"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

from shape_ops import sample_points

FRAMES = 240


def default_axInit(ax):
    ax.grid(True)
    ax.axis('on')
    ax.set_title("")

    return ax.plot([], [], 'ro-')[0]


default_points = np.array([
    [1, 0],
    [1, 1],
    [-1, 1],
    [-1, -1],
    [1, -1],
])


class Simulador4e():
    def __init__(self, dims=(2, 2),
                 frames=240,
                 points=default_points,
                 xlim=(-2, 2), ylim=(-2, 2)):

        # *------------------PARAMETROS DA SIMULACAO
        self.frames = frames

        # Pontos da peça
        self.p_points = sample_points(points)

        # rotação em um frame
        self.dtheta = 2*np.pi/frames

        # matriz de rotação em um frame
        c, s = np.cos(self.dtheta), np.sin(self.dtheta)
        self.R = np.array([[c, -s], [s, c]])

        # *------------------PARAMETROS DOS PLOTS
        subplot_kw = dict(adjustable='box', aspect=1, xlim=xlim, ylim=ylim)

        # Cria os plots na grade especificada por dims
        self.fig, self.axes = plt.subplots(*dims, subplot_kw=subplot_kw)

        # Salva dims
        self.dims = dims
        self.axes = self.axes.reshape(self.dims)

        # Lista todos os plots adicionados (pode ter mais de um em um mesmo axs)
        self._plots = []
        # Cada plot adicionado recebe uma função de update
        self._plotUpdateFuncs = []
        # Cada plot adicionado recebe variáveis de estado únicas
        self._plotStates = []

        for a in self.axes.flatten():
            default_axInit(a)

    def init(self):
        [p.set_data([], []) for p in self._plots]
        return self._plots

    def animate(self, theta):

        i = theta/self.dtheta

        self.p_points = self.R@self.p_points

        sim_params = {'i': i,
                      'points': self.p_points,
                      'theta': theta,
                      'dtheta': self.dtheta}

        for i, (plot, update, state) in enumerate(zip(self._plots, self._plotUpdateFuncs, self._plotStates)):
            x, y, states = update(sim_params, state)
            self._plotStates[i] = states
            plot.set_data(x, y)

        return self._plots

    def run(self):
        anim = animation.FuncAnimation(self.fig, self.animate,
                                       init_func=self.init,
                                       frames=np.linspace(
                                           0, 2*np.pi, self.frames),
                                       interval=2, blit=True)
        plt.show()

    def add_piece(self, position, color='k-'):
        self.add_plot(position,
                      self._pieceUpdate,
                      color=color)

    def add_plot(self, position, updateFunc, states0=[], color='b-'):
        line, = self.axes[position].plot([], [], color, lw=2)
        self._plots.append(line)
        self._plotUpdateFuncs.append(updateFunc)
        self._plotStates.append(states0)

        return line

    def _pieceUpdate(self, sim_params, state):
        return (*self.p_points, state)

