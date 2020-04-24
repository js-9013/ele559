import meep as mp
from meep import mpb
import numpy as np
import matplotlib as plt
import ipyvolume as ipv
import argparse

nbtin = mp.Medium(epsilon = 20) #barium titanium niobates 30-70!
sapphire = mp.Medium(epsilon = 10)

res = 0.05 

gdsII_file = 'project.gds'

NBTIN_LAYER = 10
SAPPHIRE_LAYER = 1
CELL_LAYER = 7
SOURCE_LAYER = 3
PORT1_LAYER = 2
PORT2_LAYER = 5

nbtin_layer = mp.get_GDSII_prisms(nbtin, gdsII_file, NBTIN_LAYER)
sapphire_layer = mp.get_GDSII_prisms(sapphire, gdsII_file, SAPPHIRE_LAYER)

port1_vol = mp.GDSII_vol(gdsII_file, PORT1_LAYER, zmin = 0, zmax = 0)
port2_vol = mp.GDSII_vol(gdsII_file, PORT2_LAYER, zmin = 0, zmax = 0)
src_vol = mp.GDSII_vol(gdsII_file, SOURCE_LAYER, zmin=0, zmax=0)
cell = mp.GDSII_vol(gdsII_file, CELL_LAYER, zmin = 0, zmax = 0)

dpml = 1 #?

lcen = 207000
fcen = 1/lcen
df = 0.2*fcen

geometry = sapphire_layer + nbtin_layer

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

mode1 = sim.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(volume=port1_vol))
mode2 = sim.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(volume=port2_vol))

sim.run(until_after_sources=400)

p1_coeff = sim.get_eigenmode_coefficients(mode1, [1], eig_parity = mp.NO_PARITY).alpha[0,0,0]
p2_coeff = sim.get_eigenmode_coefficients(mode2, [1], eig_parity = mp.NO_PARITY).alpha[0,0,1]

print(p1_coeff**2)
print('\n')
print(p2_coeff**2)

trans = abs(p1_coeff)**2/abs(p2_coeff)**2
print(trans)
