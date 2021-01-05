# RPi-Robot-

CREDIT:
Special thanks to MoonYoung Lee and Peter A. Slater for their previous work with color detection and centroid calculations. 

AUTHORS: 
Srinivasan Seetharaman - Designed and implemented the tag recognition module using RasPi Camera and openCV.  
Albert Quizon - Circuit design and mechanical subsystem. 


ABSTRACT

A lot of homes have some form of plants, all of which need some sort of scheduled watering. A sprinkler or even drip irrigation system could work but would not be able to really handle a diverse set of plants. These systems are usually too expensive to implement around the house, and generally are more appropriate outdoors where stray water will be absorbed into the surrounding soil or ground.

The best way to water is to focus on the roots, not the leaves. Wetting the foliage results in a higher chance that diseases take ahold of the plant and cause problems. In addition, too much watering can be bad for the plants, so the frequency of watering would have to change based on the weather and sunlight.

We designed a robot to help with the collection of issues by watering specific targets at a designated time. The robot will monitor the soil for moisture levels and provide water then the moisture levels drop too low. It will be able to handle multiple plants which can be spread around the robot.


SOFTWARE - High level Design:

The initial stages of software development began with moisture sensor testing. Once we confirmed the digital outputs, we created callback functions to handle changes in the moisture levels. This was a much more robust form of handling moisture sensor readings because they can interrupt the process at any point. In the callback functions, the triggered sensor ID was added to the needsWater queue, which lists the order in which plants are to be watered. A sensor will not be added to the queue is it is already in the queue. This is an implementation of FIFO, first in first out. The callback functions allow for sensors to be added to the queue even while the robot is in the process of watering another plant.

The next step was to test the different subsystems independently to ensure their functionality and test system requirements. We needed to make sure that the water pump was neither too weak nor too powerful. We wrote some test scripts that would toggle GPIO outputs in order to test the relay that controls the water pump.

We then tested the servo movements using previously developed pwm calibration code. Since we were using FS5103R continuous rotation servos without a built in potentiometer, we had to figure out the stopping pulse requirements, which we determined to be about INSERT VALUE ms. We then wrote functions that defined servo movement for quick reference when writing the finite state machine.

The image processing technique involved the usage of openCV and PiCamera module on the RPi. We used the PiRGBArray to import RGB input from the picamera which is converted into a 2D array. The first step in this process is to convert the incoming RGB color schema into HSV color scheme. The reason why we decided to convert RGB to HSV color scheme is the simplicity in using HSV. It allows us to easily isolate the required color of the tag we are using through the use of simple hues. Hues are the bounded range for the color that we want identify.

We specified 3 tag colors: Red, Green and Yellow. We chose these 3 colors because we have the luxury of having a buffer in terms of color ranges. We defined the lower bound and the upper bound for the 3 colors through which we were able to recognize the above mentioned tags. We also defined a black color bounds for when the robot is in the waiting state and should not recognize any objects.

One of the biggest advantages converting from RGB to HSV is that HSV provides us with a more robust platform for detection. The hues are broad enough to cover the apparent colors, regardless of saturation or value. Next we perform a matrix operation on the pixel values that thresholds the colors to form a binary matrix of pixels which allows us to detect the colored tags. We reduce the noise from the resulting binary outputs using a morphological filter, which allows us to dilate the binary matrix. The filter provides us with a better output on which we can perform accurate contour detection. The output binary matrix obtained after dilation using the morphological filter maintains the edges and also fills up any values that have not been connected in the surrounding body.

We perform our contour detection using the Open CV library. The resulting binary matrix generated is used as the input for the contour detection function which provides us with a list of object boundaries. This list however does contain noise and elements which might interfere with our object detection. To prevent any erroneous detection, we filtered our contours out based on size. If the detected contour was smaller than a specified pixel area, it is not detected as an object. We also allowed our code to calculate the rough estimate of the centroid of the given tag. This was required because this allowed us to align our robot with the centroid. During our initial testing phase to help us with any underlying debugging issues, we overlaid the detected contour and shift into the raw RGB capture frame and displayed it to make sure we were capturing the required tag and not any stray elements.

