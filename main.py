import paho.mqtt.client as mqtt
import logging
import time
import neopixel
import board

from threading import Thread

loop = False #bool for infinite loops

def main():
    global loop
    
    client = mqtt.Client()    #mqtt client
    
    ##########################################################
    # Setup Strip
    ##########################################################
    
    pixel_pin = board.D18
    num_pixels= 58
    ORDER = neopixel.GRBW
    strip = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER
    )
    
    stripStorage = [(255.0,63.0,0.0,100.0,255.0)]*num_pixels #(r,g,b,w,brightness) stores current value of the Strip
    
    #FadeLoop
    def runFade():
        global loop
        loop = True
        while loop:
            print("A")
            time.sleep(1)
    
    #set Brightness on Strip
    def fadeBrightness(bright):
        for i in range(len(strip)):
            current = stripStorage[i]
            current0 = (float(current[0])/float(current[4])) * float(bright)
            current1 = (float(current[1])/float(current[4])) * float(bright)
            current2 = (float(current[2])/float(current[4])) * float(bright)
            strip[i] = (int(current0),int(current1),int(current2),int(current[3]))
            stripStorage[i] = (current0,current1,current2,current[3],bright)
        strip.show()
            
        
    def on_message(client, userdata, msg):
        print(msg.topic+" "+str(msg.payload)) #TODO: to be remove for production
        
        #Set Brightness
        if msg.topic == "ambilightLamp/set/brightness":
            value = float(msg.payload)
            fadeBrightness(value)
        elif msg.topic == "ambilightLamp/set/rgb":
            payload = str(msg.payload)[2:]
            payload = payload[:(len(payload)-1)]
            print(payload)
        
        
        #t1 = Thread(target=runFade)
        #t1.setDaemon(True)
        #t1.start()
        
    def on_connect(client, userdata, flags, rc):
        client.subscribe("ambilightLamp/#")
        print("MQTT connected")
        print(client)
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.178.73", 1883, 60) #Connect to HA IP Adress
    client.loop_forever()
    



if __name__ == "__main__":
    main()