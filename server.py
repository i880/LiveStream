
import socket
import cv2
import numpy as np
import tensorflow as tf
from  tensorflow.keras.models import load_model
import threading
import queue

class StreamServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.frame_queue = queue.Queue()
        self.classifier = classifier()
        self.keep_running = True
        # video writer for saving mp4
        self.output =  "output.mp4"
        self.fps = 30
        self.size = (640, 480)
        self.video_writer = cv2.VideoWriter(self.output, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, self.size)

    def build(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, self.port))
        s.listen(5)
        print(f"Server started at {self.ip}:{self.port}")
        return s
     

    def frame_process(self):
        while self.keep_running:
            try :
                frame = self.frame_queue.get(timeout=1)
                if frame is None:
                    continue

                state = self.classifier.classi(frame)
                print(f"the frame is {state}")
                annnotated_frame = cv2.putText(frame, state, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow('frame', annnotated_frame)
                self.video_writer.write(cv2.resize(annnotated_frame,self.size))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.keep_running = False
                    break
            except queue.Empty:
                continue





    def RcvStream(self, s):
        try:
            threads = 0
            for _  in range(4):
                t = threading.Thread(target=self.frame_process)
                t.deamon = True
                t.start()
                threads.append(t)

            while self.keep_running:
                c, addr = s.accept()
                print(f"Got connection from {addr}")
                data_buffer = b""
                try:
                    while True:
                        data = c.recv(2048)
                        if not data:
                            break
                        data_buffer += data
                        while b"--end-of-frame--" in data_buffer:
                            frame_data, data_buffer = data_buffer.split(b"--end-of-frame--", 1)
                            frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                            if frame is not None:
                                self.frame_queue.put(frame)
                                #state = self.classifier.classi(frame)
                                #display_frame = cv2.putText(frame, state, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                #display_frame = cv2.putText(frame, cont_sky, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                #display_frame = cv2.putText(frame, cont_nonky, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                # cv2.imwrite("stream.mp4",frame)
                                #cv2.imshow('frame', frame)
                                #classifier(frame)
                                #if cv2.waitKey(10) & 0xFF == ord('q'):
                                #    print("Exiting...")
                                #    c.close()
                                #    s.close()
                                #   cv2.destroyAllWindows()
                                #   exit()
                            else:
                                print("Error: Failed to decode frame")
                except Exception as e:
                    print(f"Connection error: {e}")
                finally:
                    c.close()

            for t in threads:
                t.join()


        finally:
            s.close()
            self.video_writer.release()
            cv2.destroyAllWindows()







#classifier image model 
class classifier():
    def __init__(self):
        self.model = load_model('/home/i880/programming/image_classification/models/sky_puppies_classification.h5')
        

    def classi(self,frame):
        image = tf.image.resize(frame, [256, 256])
        model = self.model.predict(np.expand_dims(image/255,0))
        state = []
        cont_sky = 0 
        cont_nonky = 0  
        if model > 0.5:
            state = 'human'
            cont_nonky +=1
            
        else:
            state = 'nothuman'
            cont_sky +=1
        print(f"the frame is {state} and could find")
        return state




# Run the StreamServer
if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    port = 3030
    server = StreamServer(ip, port)
    server_socket = server.build()
    server.RcvStream(server_socket)





'''


try:
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        
        data_buffer = b""
        while True:
            data = c.recv(2048)
            if not data:
                break
            data_buffer += data
            while b"--end-of-frame--" in data_buffer:
                frame_data, data_buffer = data_buffer.split(b"--end-of-frame--", 1)
                frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow('frame', frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        c.close()
                        s.close()
                        cv2.destroyAllWindows()
                        exit()
finally:
    s.close()
    cv2.destroyAllWindows()
'''
