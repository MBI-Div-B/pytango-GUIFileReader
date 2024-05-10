from encodings import utf_8
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState,Attr, WAttribute
from tango import AttrWriteType, PipeWriteType
from tango.futures import DeviceProxy
import re
import cv2
import numpy as np
import pyautogui


class CoordinateStore:
    def __init__(self,img):
        self.points = [-1,-1,-1,-1]
        self.img = img
        self.orgIm = np.copy(img)
        self.quit = False

    def select_point(self,event,x,y,flags,param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.points[0] = int(x)
            self.points[1] = int(y)
            self.img = np.copy(self.orgIm)
        elif event == cv2.EVENT_LBUTTONUP:
            self.points[2] = int(x)-self.points[0]
            self.points[3] = int(y)-self.points[1]
            cv2.rectangle(self.img, self.points[0:2],(x, y),(0, 255, 255),1)

class GUITextReader(Device):
    def read_float(self, attr):
        im = pyautogui.screenshot(region=self.attrDict[attr.get_name()])
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    def get_coordinates(self):
        img = np.array(pyautogui.screenshot())
        coordinateStore1 = CoordinateStore(img)
        # Create a window and bind the function to window
        cv2.namedWindow("Choose Attribute Area")
        # Connect the mouse button to our callback function
        cv2.setMouseCallback("Choose Attribute Area", coordinateStore1.select_point)
        # display the window
        while True:
            cv2.imshow("Choose Attribute Area", coordinateStore1.img)
            if cv2.waitKey(10) == 27 or cv2.getWindowProperty("Choose Attribute Area", cv2.WND_PROP_VISIBLE) <1:
                break
        cv2.destroyAllWindows()
        return coordinateStore1.points
    
    attributeCoordinates = attribute(
        name = "attributeCoordinates",
        label = "Coordinates of the data to read",
        dtype = ((int,),),
        max_dim_x=1024,
        max_dim_y=1024,
        hw_memorized = True,
        access = AttrWriteType.READ_WRITE
    )




    def init_device(self):
        Device.init_device(self)
        print(self.get_name())
        self.d = DeviceProxy(self.get_name())
        attrDict = {}
        self._attributeCoordinates = (0,0)
        self.set_state(DevState.ON)


    def read_attributeCoordinates(self):
        return attributeCoordinates.get_value()

    def write_attributeCoordinates(self,num):
        num = self.get_coordinates()
        self._attributeCoordinates = num
        attributeCoordinates.set_value(num)

    @command(
        dtype_in='DevString',
        doc_in="dev_name",
        display_level=DispLevel.EXPERT,
    )
    @DebugIt()
    def create_float_attributes(self, argin):
        print(self.attributeCoordinates.get_name())
        self.d.write_attribute(self.attributeCoordinates.get_name(),[[-1,-1]], wait=True)
        attrDict[argin] = points
        #dev = tango.DeviceProxy(self.get_name)
        
        attr = attribute(
            name=argin,
            dtype=float,
            access=AttrWriteType.READ,
            label=argin,
        ).to_attr()
        self.add_attribute(attr,r_meth=self.read_float)
    
        
        
def main(args=None, **kwargs):
    return run((GUITextReader,), args=args, **kwargs)



if __name__ == '__main__':
    main()
