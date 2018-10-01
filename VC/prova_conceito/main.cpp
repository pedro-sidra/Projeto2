/*
 * Proof of concept for a computer vision system designed to
 * find a workpiece in a CNC's work area and reference it.
 *
 * This makes some assumptions about the image's environment:
 *
 * -> There is a reference object in the frame which is red, and
 *  it is the only red object
 *
 * -> The reference object is a rectangle 7x5 cm in size.
 *
 * -> There are some black objects, but the workpiece is the only
 *  object that is approximately a rectangle
 *
 * With these assumptions, this program calculates the distance
 * vector between the reference object and the workpiece.
 *
 * The algorithm for finding the red reference and the black
 * workpiece is a stand-in for more complex segmentation techniques,
 * but the process of calculating the distance remains the same,
 * regardless of the technique used to isolate these objects.
 *
 * The output is an image with the objects hightlighted and a
 * line representing the distance between them. The norm of 
 * the distance is also shown for comparison with the real-world
 * distance.
 *
 * */
// OpenCV Dependencies
#include <opencv2/opencv.hpp>
#include "opencv2/imgproc.hpp"
#include "opencv2/imgcodecs.hpp"
#include "opencv2/highgui.hpp"

// Cpp dependencies
#include <iostream>
#include <stdlib.h>
#include <stdio.h>

// No ::'s in this code...
using namespace cv;
using namespace std;

// High and low ranges for HSV values (used to detect Red)
Point HRangeRed(0,62);
Point SrangeRed(0,90);
Point VRangeRed(116,180);

// High limit of intensity for pixels that are considered black
int threshBlack =40;

// Isolates the red area defining the reference object
void getRedArea(Mat &src, Mat &dst)
{
	// Converts to HSV to handle color more easily
	cvtColor(src,dst,COLOR_BGR2HSV);
	// Segments only the red areas of the image
	inRange(src,
			Scalar(HRangeRed.x,SrangeRed.x,VRangeRed.x),
			Scalar(HRangeRed.y,SrangeRed.y,VRangeRed.y),
			dst);
	// Gets a elliptical structure for morphological opening
	// and closing
	Mat element = getStructuringElement(MORPH_ELLIPSE,Size(5,5));
	// Morphologically opens and closes the binary image
	// this eliminates small holes within and outside
	// of the interest objects
	morphologyEx(dst,dst,MORPH_OPEN, element);
	morphologyEx(dst,dst,MORPH_CLOSE, element);
}

// Segments the black areas in the source image
void getBlackArea(Mat &src, Mat &dest)
{
	// Converts to gray scale to handle black levels more easily
	cvtColor(src,dest,COLOR_BGR2GRAY);
	// Apllies threshold to convert to binary image
	threshold(dest, dest, threshBlack,255, THRESH_BINARY);
	// Morphologically opens and closes the image
	// this eliminates small holes within and outside
	// of the interest objects
	Mat element = getStructuringElement(MORPH_ELLIPSE,Size(5,5));
	morphologyEx(dest,dest,MORPH_OPEN, element);
	morphologyEx(dest,dest,MORPH_CLOSE, element);
}

// Creates trackbars to calibrate threshold values for red and black
void createTrackbars()
{
	createTrackbar("H Max Value","Result", &HRangeRed.y,359);
	createTrackbar("H Min Value","Result", &HRangeRed.x,359);

	createTrackbar("S Max Value","Result", &SrangeRed.y,180);
	createTrackbar("S Min Value","Result", &SrangeRed.x,180);

	createTrackbar("V Max Value","Result", &VRangeRed.y,180);
	createTrackbar("V Min Value","Result", &VRangeRed.x,180);

	createTrackbar("Black Max","Result", &threshBlack,180);
}

// function for sorting the points by their "top-leftedness"
// the heuristic is that the distance between the top-left point
// and all other points has x>0
// the sort function is used so the top-left point comes first
// in the vector
bool sortLeftPoint(Point a, Point b)
{
	return (b-a).x>0;
}

// Finds the reference object in the image and outputs
// a rect containing its coordinates
void findReference(Mat &image, Rect & output)
{
	// contour vector 
	// and hierarchy vector for the red contours in the image
	vector<vector<Point> > contoursRed;
	// Hierarchy represents if an object is inside another object
	vector<Vec4i> hierarchyRed;
	// binary image containing the red regions
	Mat redThresh;
	// Separate red area
	getRedArea(image, redThresh);
	// Find contours in the red area (we presume there's only one,
	// which is the red reference object)
	findContours(redThresh, contoursRed, hierarchyRed,
			CV_RETR_TREE,
			CV_CHAIN_APPROX_SIMPLE);
	output = boundingRect(contoursRed[0]);
}

// Finds the black workpiece in an image
void findPiece(Mat &image,vector<Point> &workpiece)
{
	// contour vector 
	// and hierarchy vector for the black contours in the image
	vector<vector<Point> > contoursBlack;
	vector<Vec4i> hierarchyBlack;

	// generate a binary image containing the black regions
	Mat blackThresh;
	getBlackArea(image, blackThresh);
	
	// Find all black contours in the image
	findContours(blackThresh, contoursBlack, hierarchyBlack,
			CV_RETR_TREE,
			CV_CHAIN_APPROX_SIMPLE);
	// Loop through all contours to filter them
	// (since there are multiple black contours, we 
	// need to find the rectangular one which is our object)
	for (size_t i = 0; i < contoursBlack.size(); ++i)
	{
		vector <Point> polyApprox;
		// approximate the shape by a simplified closed polygon
		// with 8-pixel precision
		approxPolyDP(contoursBlack[i],
				polyApprox,
				8,
				true);
		// if the polygon is a quadrilateral, it's our workpiece
		// (this is obviously not robust and is a stand-in)
		if( polyApprox.size() ==4)
			workpiece = polyApprox;
	}	
}
// Find the workpiece position relative to the red reference
// object. 
Point findRelativeWorkpiecePosition(Rect &redRef, vector<Point> workpiece)
{
	// this is used to find the top-left corner of the object
	sort (workpiece.begin(),workpiece.end(),sortLeftPoint);
	// Find the distance between the bottom-right corner of
	// the reference and the top-left corner of the workpiece.
	Point brRed = redRef.br();
	Point tlBlack = workpiece[0];
	return tlBlack-brRed;
}

int main(int argc, char** argv )
{
	// Image setup
	Mat image;
	image = imread( argv[1], 1 );
	if ( !image.data )
	{
		printf("No image data \n");
		return -1;
	}
	// Windows Setup
	namedWindow("Display Image", WINDOW_AUTOSIZE );
	namedWindow("Result", WINDOW_AUTOSIZE );
	createTrackbars();

	// Objects of interest
	Rect referenceObject;
	vector<Point> workpiece;

	// loops until the q key is pressed
	while(waitKey(30)!='q')
	{		
		// gets the image from the command line
		image = imread( argv[1], 1 );

		// finds the reference and the workiece
		findReference(image, referenceObject);
		findPiece(image,workpiece);

		// Height of the red reference is ~5.0cm and width is ~7.0 cm
		// So take the average cmPerPixel for each
		// measurement for more precision
		double cmPerPixel = (5.0/referenceObject.height + 7.0/referenceObject.width)/2;

		// Find the workpiece position relative to the reference
		Point relativePosition = findRelativeWorkpiecePosition(
				referenceObject,
				workpiece);

		// Draw the reference object, the workpiece,
		// and the distance between them
		rectangle(image, referenceObject, Scalar(0,0,255));
		polylines(image,workpiece, true, Scalar(255,255,0));
		line(image, referenceObject.br(),referenceObject.br()+relativePosition, Scalar(255,0,0));

		// Calculate the magnitude of the distance and show it
		double workPieceDistance = cmPerPixel*norm(relativePosition);
		putText(image, "Distancia medida: " + to_string(workPieceDistance) + " cm" , Point (10,20), FONT_HERSHEY_SIMPLEX, 0.8, Scalar(255,255,255));

		// Display resulting image
		imshow("Display Image", image);
	}
	return 0;
}
