import paho.mqtt.client as mqtt
import logging
import time
import neopixel
import board

from threading import Thread

loop = False #bool for infinite loops
t1 = Thread
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
        def wheel(pos):
            # Input a value 0 to 255 to get a color value.
            # The colours are a transition r - g - b - back to r.
            if pos < 0 or pos > 255:
                r = g = b = 0
            elif pos < 85:
                r = int(pos * 3)
                g = int(255 - pos * 3)
                b = 0
            elif pos < 170:
                pos -= 85
                r = int(255 - pos * 3)
                g = 0
                b = int(pos * 3)
            else:
                pos -= 170
                r = 0
                g = int(pos * 3)
                b = int(255 - pos * 3)
            return (r, g, b,0)
    
    
        def rainbow_cycle(wait):
            for j in range(255):
                for i in range(len(strip)):
                    pixel_index = (i * 256 // len(strip)) + j
                    strip[i] = wheel(pixel_index & 255)
                strip.show()
                time.sleep(wait)
        
        while loop:
            rainbow_cycle(0.1)
    
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
            
    def fadeStrip(input):
        currentCopy = stripStorage
        for i in range(1,256):
            for j in range(len(strip)):
                stripNew = [0.0]*5
                #print(strip)
                for k in range(5):
                    if stripStorage[j][k] > input[j][k]:
                        stripNew[k] = stripStorage[j][k] - ((stripStorage[j][k] - input[j][k]) / (255.0/float(i)))
                    else: 
                        stripNew[k] = stripStorage[j][k] + ((input[j][k] - stripStorage[j][k]) / (255.0/float(i)))

                strip[j] = (int(stripNew[0]*(stripNew[4]/255.0)),int(stripNew[1]*(stripNew[4]/255.0)),int(stripNew[2]*(stripNew[4]/255.0)),int(stripNew[3]*(stripNew[4]/255.0)))
                currentCopy[j] = (stripNew[0],stripNew[1],stripNew[2],stripNew[3],stripNew[4])
            strip.show()
            time.sleep(0.01)
        #print("input:")
        #print(input)
        #print("current")
        #print(currentCopy)
        
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
        global t1
        print(msg.topic+" "+str(msg.payload)) #TODO: to be remove for production
        
        if loop:
            print("killed")
            loop = False
            t1.join()
            
        
        #Set Brightness
        if msg.topic == "ambilightLamp/set/brightness":
            value = float(msg.payload)
            input = stripStorage
            #print(input)
            for i in range(len(input)):
                input[i] = (input[i][0],input[i][1],input[i][2],input[i][3],value)
            #print(value)
            #print(input)
            fadeStrip(input)
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
            t1 = Thread(target=runFade)
            t1.setDaemon(True)
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