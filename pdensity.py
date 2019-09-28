import os
import numpy as np
from scipy import stats
from sklearn.neighbors import KernelDensity
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib import cm
import os

#choose mode: 1 is for harvest density, 2 is for ICARUS predictions densities

mode = 1

threshold = 0.5
issLog = 'input_data/iss_log/ISS_info.txt'
c_map = cm.afmhot

epsg_projections = {"web_mercator": "3857", "plate_carree":"32662"}
colors = {"grey":"#494a4c",
          "black":"#0c0c0c",
          "blue":"#000856",
          "purple":"#8c0289",
          "pink":"#ef47ff",
          "ocean": "#98cbea",
          "land": "#ead9d0",
          "yellow": "#ffd644",
          "darkgrey": "#333333",
          "gold":"#ffc300",
          "coldwhite": "#eff5ff",
          "cmap_max": "#FFFEC6"}

#drawing gridlines is currently not supportet with epsg projections and only works for 'plate carree' and 'Mercator'
proj = ccrs.PlateCarree()

infostring = "This map was made with Cartopy and Anaconda3 (Python version 3.7.7)\n" \
             "Projection: EPSG 32662 (central_longitude=0.0)\n" \
             "WGS84 Bounds: -180.0000, -90.0000, 180.0000, 90.0000\n\n" \
             "The data was gathered through ICARUS. ICARUS is part of a\n" \
             "Master's thesis at the Institute of Geography \n" \
             "at the University of Bern (GIUB), Switzerland.\n\n" \
             "Author information (both map and ICARUS):\n" \
             "Benjamin A. Schuepbach\n" \
             "Immatr.No: 14-100-564\n" \
             "Master's Student at GIUB\n" \
             "benjamin.schuepbach@students.unibe.ch"



def densityCalculation(lon_arr, lat_arr):


    latlon_arr = np.column_stack((lat_arr,lon_arr))
    print("Arrays stacked.")
    print(latlon_arr)


    xmin = -180
    xmax = 180
    ymin = -90
    ymax = 90

    X, Y = np.mgrid[xmin:xmax:90j, ymin:ymax:45j]
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([lat_arr,lon_arr])

    kernel = stats.gaussian_kde(values)
    Z = np.reshape(kernel(positions).T, Y.shape)

    return Z




def addCredits(ax, info, x=-135.0, y=-85.0):
    """This should automate adding credits to the map, as well as information about CCRS and other important stuff."""
    ax.text(x=-135, y=-85, s=info, fontsize=7, ha='center', color=colors['coldwhite'], bbox=dict(facecolor=colors["darkgrey"], alpha=0.5, edgecolor=colors["darkgrey"]))

def harvestDensity():

    lat_arr = []
    lon_arr = []

    harvests = os.listdir("input_data/harvests")
    delimiter = ','

    n=0

    for file in harvests:
        with open("input_data/harvests/" + file) as infile:

            while True:
                try:
                    # filter out lat/lon values, append to arrays for later plotting
                    line = infile.readline().split(delimiter)
                    lat = line[0]
                    lon = line[1]

                    lat_arr.append(float(lat))
                    lon_arr.append(float(lon))
                    n += 1

                except IndexError:
                    break

    return lat_arr, lon_arr, n

def ICARUSdensity(thresh=0.5):

    lat_arr = []
    lon_arr = []
    delimiter = ';'

    outputs = os.listdir("input_data/icarus_output")
    n = 0

    for file in outputs:
        with open("input_data/icarus_output/" + file) as infile:

            while True:
                try:
                    # filter out lat/lon values, append to arrays for later plotting
                    line = infile.readline().split(delimiter)

                    predictions = eval(line[5])
                    pred_arr = []

                    d = 0
                    for prediction in predictions:
                        prediction = predictions[d]['confidence']

                        if prediction > thresh:
                            pred_arr.append(prediction)
                            d += 1
                            n += 1

                        else:
                            d += 1

                    if len(pred_arr) > 0:
                        lat = line[0]
                        lon = line[1]

                        lat_arr.append(float(lat))
                        lon_arr.append(float(lon))


                    else:
                        pass

                except IndexError:
                    break
    n = len(pred_arr)

    return lat_arr, lon_arr, n

def createMap(proj,which_results_shall_be_mapped, lat_arr, lon_arr, n):

    #density = densityCalculation(lon_arr, lat_arr)

    # set up map, aspect ratio is 2:1
    fig_height = 20
    fig = plt.figure(figsize=(fig_height, fig_height / 2))
    ax = fig.add_axes([0.05, 0.05, 0.87, 0.87], projection=proj)
    ax.set_global()

    # add features to the map
    ax.coastlines()
    ax.add_feature(cfeature.OCEAN, color=colors["black"], alpha=1)
    ax.add_feature(cfeature.LAND, color=colors["grey"], alpha=1)
    ax.add_feature(cfeature.BORDERS, linewidth=0.7)
    # ax.stock_img()

    # add gridlines
    gl = ax.gridlines(xlocs=range(-180, 181, 60), ylocs=range(-90, 100, 30), draw_labels=True, color=colors["grey"],
                      linewidth=0.2, )
    gl.xlabel_style = {"color": colors["grey"]}
    gl.ylabel_style = {"color": colors["grey"]}
    gl.xlabels_top = False
    gl.ylabels_left = False

    # add points to map (s= sets size of each point, c= sets colour of each point, alpha= sets opacity (between 0 and 1))
    #ax.imshow(np.rot90(np.flip(density,1)), extent=[-180,180,-90,90], cmap=cm.afmhot, alpha=0.7)
    plt.scatter(lat_arr, lon_arr, s=4, c=colors["gold"], marker="s", alpha=0.001, transform=proj)

    # plt.suptitle("TWEETS WITH MEDIA APPENDED", color=colors["grey"], fontsize=20, fontweight='bold')
    plt.title("TWEETS WITH MEDIA AND GEOTAG APPENDED\nMAY 12 - SEPTEMBER 23 2019", color=colors["grey"],
              fontsize=20,
              fontweight='bold', pad=15)


    addCredits(ax, infostring)

    # save the figure and show on screen
    plt.savefig("Saved_Maps/map_density_{}".format(which_results_shall_be_mapped))
    print("mapping completed\n")
    # plt.show()

def map():

    if mode ==1:
        lat_arr, lon_arr, n = harvestDensity()
        print("Harvests processed.")
        createMap(proj, "Harvests", lat_arr, lon_arr, n)
        print("Harvest Density mapped.")




    elif mode ==2:
        lat_arr, lon_arr, n = ICARUSdensity(threshold)
        print("Predictions processed.")
        createMap(proj, "Predictions", lat_arr, lon_arr, n)
        print("Prediction Density mapped.")


    else:
        print("Error, please use a valid mode!")




map()