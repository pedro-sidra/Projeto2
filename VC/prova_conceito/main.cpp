#include <stdio.h>
#include <opencv2/opencv.hpp>
#include "opencv2/imgproc.hpp"
#include "opencv2/imgcodecs.hpp"
#include "opencv2/highgui.hpp"
#include <iostream>
#include <stdlib.h>
using namespace cv;
using namespace std;

Point HRange(0,62);
Point SRange(0,90);
Point VRange(116,180);
int thresh =40;

void getRedArea(Mat &src, Mat &dst)
{
	cvtColor(src,dst,COLOR_BGR2HSV);
	inRange(src,
			Scalar(HRange.x,SRange.x,VRange.x),
			Scalar(HRange.y,SRange.y,VRange.y),
			dst);
	Mat element = getStructuringElement(MORPH_ELLIPSE,Size(5,5));
	morphologyEx(dst,dst,MORPH_OPEN, element);
	morphologyEx(dst,dst,MORPH_CLOSE, element);
}

void getBlackArea(Mat &src, Mat &dest)
{
	cvtColor(src,dest,COLOR_BGR2GRAY);
	threshold(dest, dest, thresh,255, THRESH_BINARY);
	Mat element = getStructuringElement(MORPH_ELLIPSE,Size(5,5));
	morphologyEx(dest,dest,MORPH_OPEN, element);
	morphologyEx(dest,dest,MORPH_CLOSE, element);
}

void createTrackbars()
{
	createTrackbar("H Max Value","Result", &HRange.y,359);
	createTrackbar("H Min Value","Result", &HRange.x,359);

	createTrackbar("S Max Value","Result", &SRange.y,180);
	createTrackbar("S Min Value","Result", &SRange.x,180);

	createTrackbar("V Max Value","Result", &VRange.y,180);
	createTrackbar("V Min Value","Result", &VRange.x,180);

	createTrackbar("Black Max","Result", &thresh,180);
}
int main(int argc, char** argv )
{
	// Variables setup
	Mat image, redThresh, blackThresh;

	// Image setup
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

	vector<vector<Point> > contoursRed;
	vector<vector<Point> > contoursBlack;
	vector<Vec4i> hierarchyRed;
	vector<Vec4i> hierarchyBlack;
	// Processing
	while(waitKey(30)!='q')
	{		
		image = imread( argv[1], 1 );
		// Separate red area
		getRedArea(image, redThresh);
		// Separate black area
		getBlackArea(image, blackThresh);

		// Get contours in both
		findContours(redThresh, contoursRed, hierarchyRed,
				CV_RETR_TREE,
				CV_CHAIN_APPROX_SIMPLE);
		findContours(blackThresh, contoursBlack, hierarchyBlack,
				CV_RETR_TREE,
				CV_CHAIN_APPROX_SIMPLE);
		// Draw contours in original image 
		drawContours(image, contoursRed,
					-1,Scalar(255,0,0),
					2,8);
		drawContours(image, contoursBlack,
					-1,Scalar(255,255,255),
					2,8);

		// Display results
		imshow("Display Image", image);
		imshow("Result", blackThresh);
	}
	return 0;
}
