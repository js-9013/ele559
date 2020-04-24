import meep as mp
from meep import mpb
import numpy as np
import matplotlib.pyplot as plt
import ipyvolume as ipv

nbtin = mp.Medium(epsilon = 30) #barium titanium niobates 30-70!
sapphire = mp.Medium(epsilon = 10)

res = 0.05 

gdsII_file = 'project.gds'

NBTIN_LAYER = 10
SAPPHIRE_LAYER = 1
CELL_LAYER = 7 
SOURCE_LAYER = 3
PORT1_LAYER = 2
PORT2_LAYER = 5

sapphire_layer = mp.get_GDSII_prisms(sapphire, gdsII_file, SAPPHIRE_LAYER)
nbtin_layer = mp.get_GDSII_prisms(nbtin, gdsII_file, NBTIN_LAYER)

for obj in sapphire_layer:
    obj.height = 1

for obj in nbtin_layer:
    obj.height = 1

port1_vol = mp.GDSII_vol(gdsII_file, PORT1_LAYER, zmin = 0, zmax = 0)
port2_vol = mp.GDSII_vol(gdsII_file, PORT2_LAYER, zmin = 0, zmax = 0)
src_vol = mp.GDSII_vol(gdsII_file, SOURCE_LAYER, zmin=0, zmax=0)
cell = mp.GDSII_vol(gdsII_file, CELL_LAYER, zmin = 0, zmax = 0)

dpml = 2 #?

lcen = 207000
fcen = 1/lcen
df = 0.2*fcen

geometry = sapphire_layer+nbtin_layer

sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df),
                              size = src_vol.size,
                              center = src_vol.center,
                              eig_band=1,
                              eig_parity=mp.EVEN_Y+mp.ODD_Z,
                              eig_match_freq=True)]

sim = mp.Simulation(resolution=res,
                    cell_size=cell.size,
                    boundary_layers=[mp.PML(dpml)],
                    sources=sources,
                    geometry=geometry)

#sim.run(until_after_sources=100)

#eps_data = sim.get_epsilon()
#ez_data = np.real(sim.get_efield_z())

f = plt.figure(dpi=100)
sim.plot2D(ax=f.gca())
plt.savefig("name1.png")

#sim.run(until_after_sources=100)

#eps_data = sim.get_epsilon()
#ez_data = np.real(sim.get_efield_z())

#f = plt.figure(dpi=200)
#plt.imshow(np.transpose(eps_data), interpolation='spline36', cmap='binary')
#plt.imshow(np.flipud(np.transpose(ez_data)), interpolation='spline36', cmap='RdBu', alpha=0.9)
#plt.savefig("name2.png")
                    
