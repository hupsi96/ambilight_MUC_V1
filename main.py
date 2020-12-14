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
            
    #change strip color
    def changeColor(color):
        for i in range(len(strip)):
            stripStorage[i] = (float(color[0]),float(color[1]),float(color[2]),stripStorage[i][3],255.0)
        
    #Rurn off stip
    def turnOff():
        for i in range(len(strip)):
            stripStorage[i] = (float(strip[i][0]),float(strip[i][1]),float(strip[i][2]),float(strip[i][3]),stripStorage[i][4])
            strip[i] = (0,0,0,0)
        strip.show()
        
    def dimWhite(white):
        for i in range(len(strip)):
            stripStorage[i] = (stripStorage[i][0],stripStorage[i][1],stripStorage[i][2],float(white),stripStorage[i][4])
        fadeBrightness(stripStorage[0][4])
        
    def on_message(client, userdata, msg):
        global loop
        print(msg.topic+" "+str(msg.payload)) #TODO: to be remove for production
        
        t1 = Thread(target=runFade)
        t1.setDaemon(True)
        if loop:
            print("killed")
            loop = False
            t1.join()
            
        
        #Set Brightness
        if msg.topic == "ambilightLamp/set/brightness":
            value = float(msg.payload)
            fadeBrightness(value)
        elif msg.topic == "ambilightLamp/set/rgb":
            payload = str(msg.payload)[2:]
            payload = payload[:(len(payload)-1)]
            input = tuple(map(int,str(payload).split(',')))
            print(input)
            
            changeColor(input)
        elif msg.topic == "ambilightLamp/light/set":
            turnOff()
        elif msg.topic == "ambilightLamp/set/white":
            payload = str(msg.payload)[2:]
            payload = payload[:(len(payload)-1)]
            
            dimWhite(float(payload))
        elif msg.topic == "ambilightLamp/set/effect":
            loop = True
            print(loop)
            t1.start()
        
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