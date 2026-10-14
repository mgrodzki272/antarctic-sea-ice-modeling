import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
 
df = pd.read_csv('daily_ice_edge.csv')
ice_data = df.drop(columns=['Date'])
 
min_ice = ice_data.min()
ice_values = min_ice.values
 
longitudes_deg = [int(col.replace('longitude_','').replace('E','')) for col in min_ice.index]
longitudes_rad = np.deg2rad(longitudes_deg)
lons = longitudes_rad
 
r = ice_values + 90
 
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, polar=True)
 
ax.plot(longitudes_rad, r, color='blue', linewidth=0.7)
 
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_rlabel_position(225)
ax.set_rmin(0)
ax.set_rmax(28)  
 
ax.set_title("Minimalny zasięg lodu wokół bieguna południowego", va='bottom')

plt.savefig('moje_wykresy_modelu.png', dpi=300, bbox_inches='tight')
plt.show()
