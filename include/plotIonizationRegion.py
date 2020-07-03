import sys
import csv
import math
import numpy as np
import random
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from tempfile import TemporaryFile as tmp
from scipy.special import gamma

import getOsirisFields as osiris

#Definition of Constants
M_E = 9.109e-31                   #electron rest mass in kg
EC = 1.60217662e-19               #electron charge in C
EP_0 = 8.854187817e-12                #vacuum permittivity in C/(V m)
C = 299892458                     #speed of light in vacuum in m/s
N = 1e23                          #electron number density in 1/m^3
WP = np.sqrt(N*EC**2/(M_E*EP_0))   #plasma frequency in 1/s

Er = osiris.transE("EField_r.h5")
Ez = osiris.longE("EField_z.h5")

r,xi = osiris.axes("EField_r.h5",858.95)

#print((M_E * C * WP)/EC * 1e-9)  #Convert normalized field to GV/m

def W(E0):
  # Takes an electric field in normalized units and returns the ionization rate in s^-1
  # Define constants for calculating ionization rate for He
  gsE = 24.5 # unperturbed ground state energy in eV
  Z = 1 # charge number after ionization
  n = 0.746 # effective principal quantum number
  sigmaz = .47 # beam spread in z
  
  E = E0 * (M_E * C * WP)/EC * 1e-9  #Convert normalized field to GV/m

  W0 = 1.52e15 * 4**n * gsE / (n * gamma(2*n)) * (20.5*gsE**(3/2))**(2*n-1)
  
  W = W0/((E)**(2*n-1)) * math.exp(-6.83*gsE**(3/2)/E)
  return W 

def ionRatio(i,j):
  integral = 0
  for n in range(int(len(xi)/2),j):
    En = math.sqrt((Er[i,n])**2 + (Ez[i,n])**2)
    integral = integral + W(En) * (xi[n] - xi[n-1]) / WP
  ratio = 1 - math.exp(-1*integral)
  if ratio > 1.0:
    return 1.0
  return ratio


def plotIonizationRegion():
  dat = np.load('data.npz')
  xi = dat['xi']
  escaped = dat['esc']
  trail = []#dat['beam']
  drive = []
  eRatio  = np.zeros((len(r),len(xi)))
  n = 0
  for i in range(len(r)):
    for j in range(int(len(xi)/2.0), len(xi)):
            #if escaped[i,j] == 1:
#        ri = r[i]
#        xii = xi[j]
#        xif = dat['beam'][j]
#        drive.append(xi[j])
#        trail.append(dat['beam'][j])
#        n += 1
      print('Row ',i, "/",len(r),", Column ", j,"/",len(xi), end="\r", flush=True)
      #if Er[i,j] < -0.5:
      ratio =  ionRatio(i,j)
      if ratio > .1:
                #      print(ratio)
        eRatio[i][j] = ratio
  
  fig, ax  = plt.subplots(figsize=(9,6))
  E = Er 
  eRatio = np.ma.masked_where(eRatio == 0, eRatio)
  cmap = plt.cm.OrRd
  cmap.set_bad(color = (1,1,1,0))

  colors = ax.pcolormesh(xi ,r,E,norm=col.SymLogNorm(linthresh=0.03,linscale=0.03,vmin=-E.max(),vmax=E.max()),cmap="RdBu_r")
  
  colors2 = ax.pcolormesh(xi ,r,eRatio, cmap=cmap)
  tick_locations=[x*0.01 for x in range(2,10)]+ [x*0.01 for x in range(-10,-1)] + [x*0.1 for x in range(-10,10)] +[ x for x in range(-10,10)]
  cbar = fig.colorbar(colors,ax=ax,ticks=tick_locations, format=ticker.LogFormatterMathtext())
  cbar.set_label('$E_r$, Transverse Electric Field ($m_e c\omega_p / e$)')
  cbar2 = fig.colorbar(colors2,ax=ax)
  cbar2.set_label('$N_e/N_0$, Fraction of Ionized Atoms')

  ax.set_ylabel('r ($c/\omega_p$)')
  ax.set_title('Ionization Region')
  ax.set_xlabel("$\\xi$ ($c/\omega_p$)")
  
  #plt.xlim(xi[0], xi[-1])
  plt.xlim(5,9)
  plt.ylim(0,4)
  fn = "ionizationRegion.png"
  plt.savefig(fn,dpi=300,transparent=True)
  plt.show()
  return
plotIonizationRegion()
