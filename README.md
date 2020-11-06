# Dragonfruit AI Coding Challenge Submission
## by Jullian Yapeter

### **The Scenario**

In this challenge, we are working with a researcher to diagnose cancer within microorganisms, referred to as parasites. 
Each parasite is photographed twice under an electron microscope (100,000 x 100,000 pixels): the first image shows the 
parasite's body , and the second image shows the parasite's veins (body and veins pixels are black and background 
pixels are white).

These images must be processed into smaller-to-store formats, in a way that the processing routine can be inversed to 
get back the original images. Additionally, we must be able to calculate whether the parasite has cancer. If the number 
of veins pixels within the parasite's body exceeds 10% of the total number of body pixels, the parasite is deemed to 
have cancer. This calculation must be done as efficiently as possible.

Images must be simulated to be used in testing the processing methodology before the real images are provided.

### **The Method**

***Simulation***
Parasites are envisioned as amorphous blobs that are quite random but contiguous. veins are envisioned as thin and 
random strings.

The first step is to simulate the parasite images, keeping in mind the restriction that the parasite must be taking up 
at least 25% of the image. I interpret this as the **bounding box** of the parasite must take up 25% of the image 
(accounts for skinny and long parasites).

To do this, I created a Frame class which generates random outer and inner frames, where the inner frame will be taken 
up by the parasite's body, and the outer frame is where the inner frame will be placed into given an anchor point 
(outer frame coordinate which represents the inner frame's top left corner). The inner frame is ensured to be at least 
25% of the outer frame.

The generated Frame object is then passed into my Simulator class which uses recursion to randomly draw on the given 
Frame canvas. The drawing action is made using a "brush" of specified width that randomly walks around the canvas. 
The body is drawn using a large brush width within the inner frame, and the veins are drawn with a smaller brush widht 
within the outer frame. For the veins, a direction heuristic is programmed, so that it doesn't simply draw a ball of 
veins, but rather something more realistic. the body image is resized so that its bounding box takes up the 
entire inner frame.

The generated images are then saved as TIFFs, which is lossless and thus helps us benchamark our compression 
capacity better.

***Processing (Compression)***

To process the images, I envisioned and implemented a framework that encapsulates the processing, processing validation,
cancer calculation, and the saving of processed images. This framework can also take in as a parameter the processing 
(compression) technique to be used. A superclass called MicroImageLarge was implemented, which can be inherited from 
in order to create more compression techniques. For this challenge I implemented 2: 
**ScanLinesMicroImage** and **BitMapMicroImage**.

**ScanLinesMicroImage** extends MicroImageLarge and is capable of compressing binary images by simply recording the 
number of pixels before a chnage in the image from either white to black or black to white. The pixels are counted in 
order of left to right, top to bottom. Also encoded in the processed image are, the size (#rows and #cols) of the 
original image (encoded in a unit8-safe way) and a check byte that confirms which processing technique was used. While 
uint8 ints can be safely used to record the number of pixels before a colour switch (ensured by a subroutine), uint16 
is recommended because there will be less elements to store, and that compensates for the larger data type.

**BitMapMicroImage** extends MicroImageLarge and is capable of compressing binary images by converting pixel data to 
use 1 bit each, either 1 for a positive pixel or 0 for a background pixel. Also encoded in the processed image are, 
the size (#rows and #cols) of the original image (encoded in a unit8-safe way) and a check byte that confirms which 
processing technique was used. Uint8 is used here.

In both these techniques, a validation routine is implemented which checks that raw_img = inv_process(process(raw_img)).
They're also capable of reporting the resulting compression rate (processed img size / original img size * 100%).

Each of these techniques implements a cancer calcuation mechanism. And they have been tested, arriving at the same 
number regardless of technique.

MicroImageLarge and its subclasses have been implemented in such a way where they can perform their functions without 
loading the whole raw image at once, thus it saves RAM.

### **Running the Test Program**

1. Clone this repository, and `cd` into it.
2. Run `pip install requirements`.
3. Create the following directories: `data`, `data/collected`, `data/processed`. They will hold the results of 
   simulation and of processing.
4. `cd` into the root of the repository.
5. Run `main.py > output.txt`, I implemented an end-to-end procedure from simulation to processing to validation.
6. Close the series of displayed images as they appear to continue running the program.
7. Check contents of `output.txt` for the results.

### **My Results**

**Ran on 4MB images of body and veins and it compressed to 5.4KB and 41KB respectively using ScanLines method.
-----PAR 0-----
Body Process & Inverse Validity: True
Veins Process & Inverse Validity: True
Veins to Body %: 14.582373360366171
Has cancer: True
BODY DATA :
---RAW---
total size of raw data (bytes): 4000122

---PROCESSED---
num elements : 2691
size of each element (bytes): 2
total size of processed data (bytes): 5382
Percentage of original size (%): 0.0013454589635016132

VEINS DATA :
---RAW---
total size of raw data (bytes): 4000122

---PROCESSED---
num elements : 20482
size of each element (bytes): 2
total size of processed data (bytes): 40964
Percentage of original size (%): 0.0102406876590264

**Ran on 4MB images of body and veins and it compressed both to 500KB respectively using BitMap method.
-----PAR 1-----
Body Process & Inverse Validity: True
Veins Process & Inverse Validity: True
Veins to Body %: 14.582373360366171
Has cancer: True
BODY DATA :
---RAW---
total size of raw data (bytes): 4000122

---PROCESSED---
num elements : 500011
size of each element (bytes): 1
total size of processed data (bytes): 500011
Percentage of original size (%): 0.12499893753240526

VEINS DATA :
---RAW---
total size of raw data (bytes): 4000122

---PROCESSED---
num elements : 500011
size of each element (bytes): 1
total size of processed data (bytes): 500011
Percentage of original size (%): 0.12499893753240526

### **Worst Case Analysis**

ScanLines technique works best on uniform and contiguous shapes. In its worst case, if the image was a perfect 
checkerboard where the pixel color changes after every pixel, it could take up: 
For uint16: 2 bytes per pixel x 100,000 x 100,000 + a little bit of header data = 20GB
For unit8 : 1 byte per pixel x 100,000 x 100,000 + a little bit of header data = 10GB

Which is why I implemented the BitMap method, which has a tightbound of: 
1 bit per pixel x 100,000 x 100,000 + a little bit of header data = 1.25GB 
for any 100,000 x 100,000 image.

### **Improving Speed**

To improve speed for smaller images, I wrote a MicroImage (no large) class which loads the whole image as a numpy array
and performs cancer cells calculations by simply summing up the element-wise product of the body and veins images and 
dividing it by the sum of the body image array.

This runs much faster, albeit using more memory.