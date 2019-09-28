import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib import cm
import os
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from matplotlib.image import imread
import numpy as np
from osgeo import gdal

thresh = [0.9, 0.87, 0.85, 0.83, 0.8, 0.7, 0.6, 0.5]
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

infostring_DTT = "This map was made with Cartopy and Anaconda3 (Python version 3.7.7)\n" \
             "Projection: EPSG 32662 (central_longitude=0.0)\n" \
             "WGS84 Bounds: -180.0000, -90.0000, 180.0000, 90.0000\n\n" \
             "The data was gathered through ICARUS. ICARUS is part of a\n" \
             "Master's thesis at the Institute of Geography \n" \
             "at the University of Bern (GIUB), Switzerland.\n\n" \
             "Author information (both map and ICARUS):\n" \
             "Benjamin A. Schuepbach\n" \
             "Immatr.No: 14-100-564\n" \
             "Master's Student at GIUB\n" \
             "benjamin.schuepbach@students.unibe.ch\n"\
             "Road Shapefile Credits: www.openstreetmap.org and www.mapcruzin.com"


def addCredits(ax, info, x=-135.0, y=-85.0, zoom=None):
    """This should automate adding credits to the map, as well as information about CCRS and other important stuff."""


    if zoom == "Tokyo":
        ax.text(x, y, s=infostring_DTT, fontsize=7, ha='center', color=colors['coldwhite'],
                bbox=dict(facecolor=colors["darkgrey"], alpha=0.5, edgecolor=colors["darkgrey"]))
    else:
        ax.text(x, y, s=infostring, fontsize=7, ha='center', color=colors['coldwhite'],
                bbox=dict(facecolor=colors["darkgrey"], alpha=0.5, edgecolor=colors["darkgrey"]))

def mapHarvests(proj, delimiter=', ', issLog=None):
    """Produces a map of all Harvests from the Raspberry Pi"""
    lat_arr = []
    lon_arr = []
    color_arr = []


    harvests = os.listdir("input_data/harvests")
    last_day = harvests[-1][-6:-4]

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



    #set up map, aspect ratio is 2:1
    fig_height = 20
    fig = plt.figure(figsize=(fig_height, fig_height/2))
    ax = fig.add_axes([0.05, 0.05, 0.87, 0.87], projection=proj)
    ax.set_global()

    #add features to the map
    ax.coastlines()
    ax.add_feature(cfeature.OCEAN, color=colors["black"], alpha=1)
    ax.add_feature(cfeature.LAND, color=colors["grey"], alpha=1)
    ax.add_feature(cfeature.BORDERS, linewidth=0.7)
    #ax.stock_img()

    #add gridlines
    gl = ax.gridlines(xlocs=range(-180, 181, 60), ylocs=range(-90, 100, 30), draw_labels=True, color=colors["grey"], linewidth=0.2,)
    gl.xlabel_style = {"color":colors["grey"]}
    gl.ylabel_style = {"color":colors["grey"]}
    gl.xlabels_top = False
    gl.ylabels_left = False

    #add points to map (s= sets size of each point, c= sets colour of each point, alpha= sets opacity (between 0 and 1))
    plt.scatter(-1000, 10000, s=30, c=colors["gold"], marker="s", edgecolor='black', linewidth=0.5, alpha=1, transform=proj, label='Tweets, n = {}'.format(n))
    plt.scatter(lat_arr, lon_arr, s=4, c=colors["gold"], marker="s", alpha=0.2, transform=proj)

    # check if ISS path should be mapped as well, set title accordingly
    if not issLog:
        # plt.suptitle("TWEETS WITH MEDIA APPENDED", color=colors["grey"], fontsize=20, fontweight='bold')
        plt.title("TWEETS WITH MEDIA AND GEOTAG APPENDED\nMAY 12 - SEPTEMBER 23 2019", color=colors["grey"],
                  fontsize=20,
                  fontweight='bold', pad=15)

        # add additional information
        leg = plt.legend(loc="lower center", fontsize=12)

        addCredits(ax, infostring)

        # save the figure and show on screen
        plt.savefig("Saved_Maps/map_harvests")
        print("Harvests mapped\n")
        # plt.show()

    else:
        iss_lat = []
        iss_lon = []

        with open(issLog) as infile:
            while True:
                try:
                    line = infile.readline()
                    dict = eval(line)

                    iss_lat.append(dict['latitude'])
                    iss_lon.append(dict['longitude'])

                except:
                    break
        #plot
        plt.scatter(-200000, 300000, s=30, c=colors["pink"], marker="s", edgecolor=colors["black"], linewidth=0.5, alpha=1, transform=proj, label="ISS Orbit")
        plt.scatter(iss_lon, iss_lat, s=5, c=colors["pink"], marker="s", alpha=0.5, transform=proj)

        plt.title("COMPARING TWEETS WITH ISS ORBIT\nTWEETS MAY 12 - JUNE {} 2019, ISS Orbit JUNE 21".format(last_day),
                  color=colors["grey"], fontsize=20,
                  fontweight='bold', pad=15)

        # add additional information
        leg = plt.legend(loc="lower center", fontsize=12)

        addCredits(ax, infostring)

        # save the figure and show on screen
        plt.savefig("Saved_Maps/map_harvests_iss")
        print("Harvests mapped\n")
        # plt.show()

def mapICARUS(proj, delimiter='; ', threshold=thresh, cmap=c_map):
    """Produces a map of ICARUS outputs"""

    for value in threshold:

        lat_arr = []
        lon_arr = []
        color_arr = []


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

                            if prediction > value:
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
                            color_arr.append(round(float(max(pred_arr)), 2))

                        else:
                            pass

                    except IndexError:
                        break

        # set up map, aspect ratio is 2:1
        fig_height = 20
        fig = plt.figure(figsize=(fig_height, fig_height / 2))
        ax = fig.add_axes([0.05, 0.05, 1, 0.9], projection=proj)
        # set extent ([x0,x1,y0,y1])
        ax.set_global()

        # add features to the map
        ax.coastlines()
        ax.add_feature(cfeature.OCEAN, color=colors["black"], alpha=1)
        ax.add_feature(cfeature.LAND, color=colors["grey"], alpha=1)
        ax.add_feature(cfeature.BORDERS, linewidth=0.7)
        # ax.stock_img()

        # add gridlines
        gl = ax.gridlines(xlocs=range(-180, 181, 60), ylocs=range(-90, 100, 30), draw_labels=True,
                          color=colors["grey"], linewidth=0.2, )
        gl.xlabel_style = {"color": colors["grey"]}
        gl.ylabel_style = {"color": colors["grey"]}
        gl.xlabels_top = False
        gl.ylabels_left = False

        # add points to map (s= sets size of each point, c= sets colour of each point according to a third array, in combination with cmap, which then gives the actual colormap, alpha= sets opacity (between 0 and 1))
        map = plt.scatter(lat_arr, lon_arr, s=0, marker="s", alpha=1, transform=proj, c=color_arr, cmap=cmap, vmin=0.5, vmax=1)
        plt.scatter(lat_arr, lon_arr, s=10, marker="s", alpha=0.65, transform=proj, c=color_arr, cmap=cmap, vmin=0.5, vmax=1)
        plt.scatter(-200000, 2000000, s=30, marker="s", edgecolor='black', linewidth=0.5, alpha=1, transform=proj, c=colors["cmap_max"], label="Predictions with threshold {}, n = {}".format(value, n))

        # add colorbar and legend
        bar = plt.colorbar(map, shrink=0.75, pad=0.03)
        bar.set_label("Prediction Confidence", labelpad=20, fontsize=12)
        leg = plt.legend(loc="lower center", fontsize=12)

        for t in leg.get_texts():
            t.set_va('center')

        # add titles and stuff
        # plt.suptitle("ALL SEASON ROADS DETECTED USING ICARUS ON TWEETS WITH APPENDED MEDIA")
        plt.title(
        "ALL SEASON ROADS DETECTED USING ICARUS ON TWEETS WITH APPENDED MEDIA AND GEOTAG\nMAY 12 - JUNE 12 2019, PREDICTION THRESHOLD {}".format(
                value), color=colors["grey"], pad=20, fontsize=20, fontweight='bold')

        # add additional information
        addCredits(ax, infostring)

        # save the figure and show on screen
        plt.savefig("Saved_Maps/map_ICARUS_Japan_thresh{}".format(int(value * 100)))
        print("Threshold: {} -- ICARUS Output Mapped\n".format((value)))
        # plt.show()

def mapICARUS_ZOOM(proj, delimiter='; ', threshold=thresh, cmap=c_map):
    """Produces a map of ICARUS outputs"""

    roads = 'input_data/GIS_data/tokyo_roads/tokyo_roads_esri.shp'
    roads_feature = ShapelyFeature(Reader(roads).geometries(), ccrs.PlateCarree())


    for value in threshold:

        lat_arr = []
        lon_arr = []
        color_arr = []


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

                            if prediction > value:
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
                            color_arr.append(round(float(max(pred_arr)), 2))

                        else:
                            pass

                    except IndexError:
                        break

        # set up map, aspect ratio is 2:1
        fig_height = 20
        fig = plt.figure(figsize=(fig_height, fig_height / 2))
        ax = fig.add_axes([0.05, 0.05, 1, 0.9], projection=proj)
        # set extent ([x0,x1,y0,y1]) for Japan [128.19, 155.9, 29.52, 49.7], Tokyo [139.6, 139.8, 35.46, 35.57]
        extents = {"Japan": [128.19, 155.9, 29.52, 49.7],
                   "DT_Tokyo":[139.6, 139.8, 35.46, 35.57],
                   "Tokyo": [139.685, 139.919, 35.624, 35.720],
                   "NYC_Manhattan": [-74.026, -73.927, 40.702, 40.801],
                   "NYC": [-74.150636, -73.8121, 40.64457, 40.8569] }

        set_ext = "Tokyo"

        ax.set_extent(extents[set_ext])

        # add features to the map (leave facecolor and change ONLY edgecolor!)
        ax.add_feature(roads_feature, edgecolor=colors['black'], facecolor='none', alpha = 0.8, linewidth=0.5, label="Roads")
        ax.coastlines()
        ax.add_feature(cfeature.OCEAN, color=colors["black"], alpha=1)
        ax.add_feature(cfeature.LAND, color=colors["grey"], alpha=1)
        ax.add_feature(cfeature.BORDERS, linewidth=0.7)



        # add gridlines
        gl = ax.gridlines(xlocs=range(-180, 181, 1), ylocs=range(-90, 100, 1), draw_labels=True,
                          color=colors["grey"], linewidth=0.2, )
        gl.xlabel_style = {"color": colors["grey"]}
        gl.ylabel_style = {"color": colors["grey"]}
        gl.xlabels_top = False
        gl.ylabels_left = False

        # add points to map (s= sets size of each point, c= sets colour of each point according to a third array, in combination with cmap, which then gives the actual colormap, alpha= sets opacity (between 0 and 1))
        map = plt.scatter(lat_arr, lon_arr, s=0, marker="s", alpha=1, transform=proj, c=color_arr, cmap=cmap, vmin=0.5, vmax=1)
        plt.scatter(lat_arr, lon_arr, s=10, marker="s", alpha=0.65, transform=proj, c=color_arr, cmap=cmap, vmin=0.5, vmax=1)
        plt.scatter(-200000, 2000000, s=30, marker="s", edgecolor='black', linewidth=0.5, alpha=1, transform=proj, c=colors["cmap_max"], label="Predictions")
        plt.scatter(-200000, 2000000, s=30, marker="_", edgecolor='black', linewidth=2, alpha=1, transform=proj,
                    c=colors["black"], label="Road Network")

        # add colorbar and legend
        bar = plt.colorbar(map, shrink=0.75, pad=0.03)
        bar.set_label("Prediction Confidence", labelpad=20, fontsize=12)
        leg = plt.legend(loc="lower center", fontsize=12)

        for t in leg.get_texts():
            t.set_va('center')

        # add titles and stuff
        # plt.suptitle("ALL SEASON ROADS DETECTED USING ICARUS ON TWEETS WITH APPENDED MEDIA")
        plt.title(
        "ALL SEASON ROADS DETECTED USING ICARUS ON TWEETS WITH APPENDED MEDIA AND GEOTAG\nMAY 12 - JUNE 12 2019, TOKYO (JPN), PREDICTION THRESHOLD {}".format(
                value), color=colors["grey"], pad=20, fontsize=20, fontweight='bold')


        print("Legend Location: ", extents[set_ext][0], extents[set_ext][2])
        # add additional information
        addCredits(ax, x=extents[set_ext][0]+0.028, y=extents[set_ext][2]+0.003, info=infostring_DTT, zoom=set_ext)

        # save the figure and show on screen
        plt.savefig("Saved_Maps/map_ICARUS_{}_thresh{}".format(set_ext, int(value * 100)))
        print("Threshold: {} -- ICARUS Output Mapped\n".format((value)))

def barebonesHarvests(proj, delimiter=', ', issLog=None):
    """Produces a map of all Harvests from the Raspberry Pi"""
    lat_arr = []
    lon_arr = []
    color_arr = []


    harvests = os.listdir("input_data/harvests")
    last_day = harvests[-1][-6:-4]

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



    #set up map, aspect ratio is 2:1
    fig_height = 20
    fig = plt.figure(figsize=(fig_height, fig_height/2))
    ax = fig.add_axes([0.05, 0.05, 0.87, 0.87], projection=proj)

    #set extent ([x0,x1,y0,y1])
    ax.set_extent([120,150,-90,90])

    #add features to the map
    ax.coastlines()
    ax.add_feature(cfeature.OCEAN, color=colors["black"], alpha=1)
    ax.add_feature(cfeature.LAND, color=colors["grey"], alpha=1)
    ax.add_feature(cfeature.BORDERS, linewidth=0.7)
    #ax.stock_img()

    #add gridlines
    #gl = ax.gridlines(xlocs=range(-180, 181, 60), ylocs=range(-90, 100, 30), draw_labels=False, color=colors["grey"], linewidth=0.2,)
    #gl.xlabel_style = {"color":colors["grey"]}
    #gl.ylabel_style = {"color":colors["grey"]}
    #gl.xlabels_top = False
    #gl.ylabels_left = False

    #add points to map (s= sets size of each point, c= sets colour of each point, alpha= sets opacity (between 0 and 1))
    plt.scatter(-1000, 10000, s=30, c=colors["gold"], marker="s", edgecolor='black', linewidth=0.5, alpha=1, transform=proj, label='Tweets, n = {}'.format(n))
    plt.scatter(lat_arr, lon_arr, s=4, c=colors["gold"], marker="s", alpha=0.2, transform=proj)

    #save the figure and show on screen
    plt.savefig("Saved_Maps/barebones")
    print("done\n")
    plt.show()

def mapDensityFromImage():
    # set up map, aspect ratio is 2:1
    fig_height = 20
    fig = plt.figure(figsize=(fig_height, fig_height / 2))
    ax = fig.add_axes([0.05, 0.05, 1, 0.9], projection=proj)
    ax.set_global()

    print(proj)


    # ax.stock_img()



    # add gridlines
    gl = ax.gridlines(xlocs=range(-180, 181, 60), ylocs=range(-90, 100, 30), draw_labels=True, color=colors["grey"],
                      linewidth=0.2, )
    gl.xlabel_style = {"color": colors["grey"]}
    gl.ylabel_style = {"color": colors["grey"]}
    gl.xlabels_top = False
    gl.ylabels_left = False

    # read in tiff file from arcgis
    img_path = "input_data/DensityAnalysis/KDE_4M_H2.tif"
    img = imread(img_path)
    npimg = np.asarray(img)

    #assign nodata the value of nan, so as to not draw it later
    npimg = np.where(npimg<0.00001,np.nan,npimg)


    print(npimg.shape)

    #plot the map
    map = plt.imshow(npimg[:,:,0], origin='upper', extent=[-180, 180, -86, 86], alpha=1, cmap=cm.plasma_r, transform=proj, vmax=30)



    # add colorbar and legend
    bar = plt.colorbar(map, shrink=0.75, pad=0.03)

    #get rid of weird white lines in colorbar
    bar.set_alpha(1)
    bar.draw_all()

    #label the colorbar
    bar.set_label("Count Per Square Kilometer", labelpad=20, fontsize=12)



    # add features to the map
    ax.coastlines()
    ax.add_feature(cfeature.OCEAN, color=colors["black"], alpha=1)
    ax.add_feature(cfeature.LAND, color=colors["grey"], alpha=1)
    ax.add_feature(cfeature.BORDERS, linewidth=0.7)


    # plt.suptitle("TWEETS WITH MEDIA APPENDED", color=colors["grey"], fontsize=20, fontweight='bold')
    plt.title("DENSITY OF TWEETS WITH MEDIA AND GEOTAG APPENDED\nMAY 12 - SEPTEMBER 23 2019", color=colors["grey"],
              fontsize=20,
              fontweight='bold', pad=15)

    addCredits(ax, infostring)

    # save the figure and show on screen
    plt.savefig("Saved_Maps/map_harvests_density")
    print("Harvests mapped\n")
    # plt.show()

mapDensityFromImage()