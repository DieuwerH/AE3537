

def scatterStatevectors(axes, statevectors, color='none', marker='none'):
    xs = list(map(lambda x: x.posX(), statevectors))
    ys = list(map(lambda x: x.posY(), statevectors))
    zs = list(map(lambda x: x.posZ(), statevectors))
    if (color != 'none' and marker != 'none'):
        axes.scatter(xs, ys, zs, c=color, marker=marker)
    else:
        axes.scatter(xs, ys, zs)

def plotLine(axes, statevec_a, statevec_b, color = 'none'):
    if (color != 'none'):
        axes.plot(xs=[statevec_a.posX(), statevec_b.posX()],
                  ys=[statevec_a.posY(), statevec_b.posY()],
                  zs=[statevec_a.posZ(), statevec_b.posZ()],
                  c=color)
    else:
        axes.plot(xs=[statevec_a.posX(), statevec_b.posX()],
                  ys=[statevec_a.posY(), statevec_b.posY()],
                  zs=[statevec_a.posZ(), statevec_b.posZ()])

def plotLines(axes, statevecs_a, statevecs_b, color='none'):
    for sv_a, sv_b in zip(statevecs_a, statevecs_b):
        plotLine(axes, sv_a, sv_b, color=color)

def plotAxesMarkers(ax):
    ax.plot(xs=[0, 6000], ys=[0, 0], zs=[0, 0], c='r')
    ax.plot(xs=[0, 0], ys=[0, 6000], zs=[0, 0], c='g')
    ax.plot(xs=[0, 0], ys=[0, 0], zs=[0, 6000], c='b')