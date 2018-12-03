

def scatterStatevectors(axes, statevectors):
    xs = list(map(lambda x: x.posX(), statevectors))
    ys = list(map(lambda x: x.posY(), statevectors))
    zs = list(map(lambda x: x.posZ(), statevectors))
    axes.scatter(xs, ys, zs)

def plotLine(axes, statevec_a, statevec_b, color = 'b'):
    axes.plot(xs=[statevec_a.posX(), statevec_b.posX()],
              ys=[statevec_a.posY(), statevec_b.posY()],
              zs=[statevec_a.posZ(), statevec_b.posZ()],
              c=color)
