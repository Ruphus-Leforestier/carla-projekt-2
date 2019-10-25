import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random
import logging
import time
import numpy as np

obj_lst = []
IMG_WIDTH =640
IMG_HEIGHT = 480

# 1- erzeuge eine Klient-Instanz und gebe ihm zurueck samt ihrer Welt
def initialisiere_klient_instanz():
    klient = carla.Client('localhost', 2000)
    klient.set_timeout(4.5)
    welt = klient.get_world()
    return klient, welt, welt.get_blueprint_library()

# 2- fuege Objekt in der Welt hinzu
# --> Auto
def fuege_neues_auto_hinzu(welt, bp_lib, obj_location_int, obj_class='vehicle', obj_verfeinern=None):
    neues_obj = None
    neues_obj_snapshot = None

    if obj_verfeinern is None:
        obj_verfeinern = str('*')
        obj_bp = random.choice(bp_lib.filter(obj_class + str('.') + obj_verfeinern))
        obj_pos = welt.get_map().get_spawn_points()[obj_location_int]
        neues_obj = welt.spawn_actor(obj_bp, obj_pos)
        neues_obj_snapshot = welt.get_snapshot()
        welt.wait_for_tick()
        print("Objekt hinzugefuegt")
    else:
        obj_bp = random.choice(bp_lib.filter(obj_class + str('.') + obj_verfeinern))
        obj_pos = welt.get_map().get_spawn_points()[obj_location_int]
        neues_obj = welt.spawn_actor(obj_bp, obj_pos)
        neues_obj_snapshot = welt.get_snapshot()
        welt.wait_for_tick()
        print("Objekt hinzugefuegt")

    return neues_obj, neues_obj_snapshot

# --> Sensor
def fuege_neuer_sensor_hinzu(welt, bp_lib, verbundene_obj, loc_x=1.5, loc_y=0.0, loc_z=0.8):
    sensor_tranform = carla.Transform(carla.Location(x=loc_x, y=loc_y, z=loc_z))

    sensor = welt.spawn_actor(bp_lib, sensor_tranform, attach_to=verbundene_obj)
    sensor_snapshot = welt.get_snapshot()
    welt.wait_for_tick()

    return sensor, sensor_snapshot
# 3- stelle Objekt-Verhalten ein
# --> Auto
def auto_verhalten_einstellen(auto_obj, geschindigkeit, steuerung):
    auto_obj.apply_control(carla.VehicleControl(throttle=geschindigkeit,
                                                steer=steuerung))
    print("Autoeinstellingen aktualisiert!")

# --> Sensor
def sensor_bilder_einnahme_einstellen(sensor_lib, bild_breite=IMG_WIDTH,
                        bild_groesse=IMG_HEIGHT,bild_perspektiv=110):
    sensor_lib.set_attribute('image_size_x', str(bild_breite))
    sensor_lib.set_attribute('image_size_y', str(bild_groesse))
    sensor_lib.set_attribute('fov', str(bild_perspektiv))
    print("Sensoreinstellungen aktualisiert!")

def process_img(img):
    np_img = np.array(img.raw_data)
    img_reshaped = np_img.reshape(IMG_HEIGHT, IMG_WIDTH, 4)

    print(img_reshaped[:, :, :3])
    #img.save_to_disk('bilder/autos/test01/%04d.png'% img.frame)
def obj_daten_debuggen(auto_obj):
    print("Acc: {}, Vel: {}, Loc: {}".format(auto_obj.get_acceleration(), auto_obj.get_velocity(), auto_obj.get_location()))
    box = auto_obj.bounding_box
    print("Location Box: {}, Extent: {}".format(box.location, box.extent))

# Helligkeit der Simulatorsicht steuern (Wetter)
def wetter_einstellen(welt, sonne_orientierung, wolkigkeit, regen_rate):
    wetter = carla.WeatherParameters(
        sun_altitude_angle=sonne_orientierung,
        cloudyness=wolkigkeit,
        precipitation=regen_rate
    )
    welt.set_weather(wetter)
    print("Wetter: ", wetter)
# Waypoint testen
def weg_in_der_stadt_debuggen(welt, auto_obj, wege_projetieren=False, projektion_type=None):
    map = welt.get_map()
    print("NAME der STADT: ", map.name)
    wege_spur = map.get_waypoint(
        auto_obj.get_location(),
        project_to_road=wege_projetieren,
        lane_type=projektion_type
        )
    auto_obj.set_transform(wege_spur.transform)

def welt_einstellen(klient, welt, kamera, neue_welt='Town03', synchr=True):
    # welt aendern: world = client.load_world('Town01') --> world = client.reload_world()
    # synchronisieren
    einstellungen = welt.get_settings()
    einstellungen.synchronous_mode = synchr
    welt.apply_settings(einstellungen)

def zeichneBox(welt, auto_obj=None):
    debug = welt.debug
    w_snap = welt.get_snapshot()
    print("has ID: ", w_snap.has_actor(auto_obj.id))
    print("find ID: ", w_snap.find(auto_obj.id))
    #print("has ID: ", w_snap.has_actor(auto_obj.id))

def main():
    try:
        klient, welt, blueprint_lib = initialisiere_klient_instanz()

        wetter_einstellen(welt, 80.0, 1.0, 5.0)

        model_auto, auto_snapshot = fuege_neues_auto_hinzu(welt=welt,
                                        bp_lib=blueprint_lib,
                                        obj_location_int=0,
                                        obj_verfeinern='mercedes-benz.*')

        obj_lst.append(model_auto)
        
        sensor_lib = welt.get_blueprint_library().find('sensor.camera.rgb')
        sensor, sensor_snapshot = fuege_neuer_sensor_hinzu(welt=welt,
                                        bp_lib=sensor_lib,
                                        verbundene_obj=model_auto)
        
        obj_lst.append(sensor)
        print("Auto-Snap:\n", auto_snapshot, "\nSensor-Snap:\n", sensor_snapshot)

        sensor_bilder_einnahme_einstellen(sensor_lib)
        auto_verhalten_einstellen(model_auto, 1.0, 0.0)
        obj_daten_debuggen(model_auto)

        wege_typ = carla.LaneType.Driving | carla.LaneType.Sidewalk
        weg_in_der_stadt_debuggen(welt=welt, auto_obj=model_auto, wege_projetieren=True, projektion_type=wege_typ)
        # kamera.listen(lambda img: process_img(img=img))
        zeichneBox(welt, auto_snapshot)
        print(model_auto.id)
        time.sleep(6)
    
    finally:
        print("destroying actors...")
        for held in obj_lst:
            held.destroy()
        print("\nDone")

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("All is done!")