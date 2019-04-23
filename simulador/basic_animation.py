"""
Matplotlib Animation Example

Usado para testar animaçoes na matplotlib

author: Jake Vanderplas
email: vanderplas@astro.washington.edu
website: http://jakevdp.github.com
license: BSD
Please feel free to use and modify this, but keep the above information. Thanks!
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

FRAMES = 240

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()

same_plot = False


def create_subplot(fig, i, xlim=(-2, 2), ylim=(-2, 2), **kwargs):
    ax = fig.add_subplot((310 + i) if same_plot else (230 + i),
                         adjustable='box',
                         aspect=1,
                         xlim=xlim, ylim=ylim,
                         **kwargs)
    ax.grid(True)
    ax.axis('on')
    ax.set_title(kwargs.get('title', ''))
    return ax


ax_came = create_subplot(fig, 1, title='Peça Rotacionando')
ax_shadow = create_subplot(fig, 1 if same_plot else 4,
                           title='Peça Rotacionando')

ax_cameplot = create_subplot(fig, 2 if same_plot else 2, title='d(theta)')
ax_shadowplot = create_subplot(fig, 2 if same_plot else 5, title='d(theta)')

ax_reccame = create_subplot(
    fig, 3 if same_plot else 3, title='Reconstrução', projection='polar')
ax_reccame.set_ylim(0, 2)
ax_reccame.set_rticks([])
ax_recshadow = create_subplot(
    fig, 3 if same_plot else 6, title='Reconstrução', projection='polar')
ax_recshadow.set_ylim(0, 2)
ax_recshadow.set_rticks([])

piece_came, piece_shadow = [ax.plot([], [], lw=2)[0]
                            for ax in (ax_came, ax_shadow)]

rec_came, rec_shadow = [ax.plot([], [], color, lw=2)[0]
                        for ax, color in ((ax_reccame, 'r-'), (ax_recshadow, 'g-'))]

line_came, *lines_shadow = [ax.plot([], [], color, lw=2)[0]
                            for ax, color in ((ax_came, 'ro-'), (ax_shadow, 'k-'), (ax_shadow, 'go-'))]

plot_came, plot_shadow = [ax.plot([], [], color, lw=2)[0]
                          for ax, color in ((ax_cameplot, 'r-'), (ax_shadowplot, 'g-'))]

r_points = []

points = np.array([
    [1, 0],
    [1, 0],
    [-0.5, 1],
    [-0.5, -1],
])
# circle_half = np.vstack((np.cos(np.linspace(1*np.pi,2*np.pi, 400)), np.sin(np.linspace(1*np.pi,2*np.pi, 400))))


def sample_points_incomplete(points, n=10000):
    next_points = np.roll(points, -1, axis=(0))
    out = np.linspace([points[0, 0], points[0, 1]],
                      [next_points[0, 0], next_points[0, 1]], n/points.shape[0]).T
    for p, nextp in zip(points[1:-1], next_points[1:-1]):
        out = np.hstack([
            out,
            np.linspace([p[0], p[1]], [nextp[0], nextp[1]],
                        n/points.shape[0]).T
        ])

    return out


def sample_points(points, n=10000):
    next_points = np.roll(points, -1, axis=(0))
    out = np.linspace([points[0, 0], points[0, 1]],
                      [next_points[0, 0], next_points[0, 1]], n/points.shape[0]).T
    for p, nextp in zip(points[1:], next_points[1:]):
        out = np.hstack([
            out,
            np.linspace([p[0], p[1]], [nextp[0], nextp[1]],
                        n/points.shape[0]).T
        ])

    return out


def rect(a, b, n=400):

    side_samples = int(n/4)

    # Cria um quadrado pedaço-por-pedaço
    y = np.hstack([
        np.linspace(-b/2, b/2, side_samples),
        np.ones(side_samples)*b/2,
        np.linspace(b/2, -b/2, side_samples),
        -np.ones(side_samples)*b/2,
    ]
    )

    # Cria um quadrado pedaço-por-pedaço
    x = np.hstack([
        np.ones(side_samples)*a/2,
        np.linspace(a/2, -a/2, side_samples),
        -np.ones(side_samples)*a/2,
        np.linspace(-a/2, a/2, side_samples),
    ]
    )

    x, y = [np.roll(v, 1) for v in (x, y)]

    # Aplica um shift para que o vetor comece no centro do
    # lado direito do quadrado

    return np.array((x, y))


# r_points = rect(a=1, b=0.5, n=400)
r_points = sample_points(points)
# r_points = np.hstack((sample_points_incomplete(points),circle_half))
came_timeplot = np.zeros(FRAMES)
shadow_timeplot = np.zeros(FRAMES)

dtheta = (2*np.pi)/FRAMES

c, s = np.cos(dtheta), np.sin(dtheta)
R = np.array([[c, -s], [s, c]])


def init():
    [line.set_data([], []) for line in
     (piece_came,
      piece_shadow,
      line_came,
      *lines_shadow,
      plot_came,
      plot_shadow,
      rec_came,
      rec_shadow)]
    return (piece_came,
            piece_shadow,
            line_came,
            *lines_shadow,
            plot_came,
            plot_shadow,
            rec_came,
            rec_shadow)

# animation function.  This is called sequentially


def animate(i):
    global r_points, came_timeplot, shadow_timeplot, ax

    r_points = R@r_points

    # Pontos de interesse:
    x, y = r_points
    y_zero = np.isclose(x, 0, atol=1e-2, rtol=1e-2)
    x_came = np.max(y[y_zero])
    x_shadow = np.max(y)
    origin = np.array([0, 0]).reshape(-1, 1)

    pShadow = np.array([
        [-2, 2],
        [x_shadow, x_shadow],
    ])
    pShadow2 = np.array([
        [0, 0],
        [0, x_shadow],
    ])

    pCame = np.array([
        [0, 0],
        [0, x_came],
    ])

    came_timeplot = np.roll(came_timeplot, 1)
    came_timeplot[int(FRAMES/2)] = x_came

    shadow_timeplot = np.roll(shadow_timeplot, 1)
    shadow_timeplot[int(FRAMES/2)] = x_shadow

    piece_came.set_data(*r_points)
    piece_shadow.set_data(*r_points)
    lines_shadow[0].set_data(*pShadow)
    lines_shadow[1].set_data(*pShadow2)
    line_came.set_data(*pCame)

    plot_shadow.set_data(
        np.linspace(-2, 2, len(shadow_timeplot)), shadow_timeplot)
    plot_came.set_data(np.linspace(-2, 2, len(came_timeplot)), came_timeplot)

    rec_came.set_data(np.linspace(0, FRAMES*dtheta, FRAMES), came_timeplot)
    rec_shadow.set_data(np.linspace(
        0, FRAMES*dtheta, FRAMES), shadow_timeplot)

    return (piece_came,
            piece_shadow,
            line_came,
            *lines_shadow,
            plot_came,
            plot_shadow,
            rec_came,
            rec_shadow)


# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=FRAMES, interval=2, blit=True)

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
# anim.save('basic_animation.mp4', fps=60, extra_args=['-vcodec', 'libx264'])

plt.show()

# plt.polar(np.linspace(0, FRAMES*dtheta, FRAMES), came_timeplot, 'r-')
# plt.polar(np.linspace(0, FRAMES*dtheta, FRAMES), shadow_timeplot, 'g-')
# plt.savefig('reconstruction.png')
