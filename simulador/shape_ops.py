import numpy as np


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
