import cv2
import argparse

def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True,
                help="path to the output image")
    ap.add_argument("-d", "--device", required=False, type=int,
                default=0, help="device to use, int")
    args = vars(ap.parse_args())
    return args


def main():
    args = parseArgs()
    capture = cv2.VideoCapture(args["device"])
    _,image = capture.read()
    cv2.imshow("oi", image)

    cv2.imwrite(args["output"], image)
    cv2.waitKey(0)

if __name__ == "__main__":
    main()