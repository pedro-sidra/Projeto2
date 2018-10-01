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

bool sortLeftPoint(Point a, Point b)
{
	return a.x < b.x;
}

void findReference(Mat &image, Rect & output)
{
	vector<vector<Point> > contoursRed;
	vector<Vec4i> hierarchyRed;
	Mat redThresh;
	// Separate red area
	getRedArea(image, redThresh);
	findContours(redThresh, contoursRed, hierarchyRed,
			CV_RETR_TREE,
			CV_CHAIN_APPROX_SIMPLE);
	output = boundingRect(contoursRed[0]);

}


void findPiece(Mat &image,vector<Point> &workpiece)
{
	vector<vector<Point> > contoursBlack;
	vector<Vec4i> hierarchyBlack;
	Mat blackThresh;
	getBlackArea(image, blackThresh);
	findContours(blackThresh, contoursBlack, hierarchyBlack,
			CV_RETR_TREE,
			CV_CHAIN_APPROX_SIMPLE);
	for (size_t i = 0; i < contoursBlack.size(); ++i)
	{
		vector <Point> polyApprox;
		approxPolyDP(contoursBlack[i],
				polyApprox,
				8,
				true);
		if( polyApprox.size() ==4)
			workpiece = polyApprox;
	}	
}
Point findRelativeWorkpiecePosition(Rect &redRef, vector<Point> workpiece)
{
	sort (workpiece.begin(),workpiece.end(),sortLeftPoint);
	Point brRed = redRef.br();
	Point tlBlack = workpiece[0];
	return tlBlack-brRed;
}
int main(int argc, char** argv )
{
	// Variables setup
	Mat image;

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

	Rect referenceObject;
	vector<Point> workpiece;

	while(waitKey(30)!='q')
	{		
		image = imread( argv[1], 1 );

		findReference(image, referenceObject);
		findPiece(image,workpiece);

		// Height of the red area is ~5.0 and width is ~7.0
		// So take the average cmPerPixel for more precision
		double cmPerPixel = (5.0/referenceObject.height + 7.0/referenceObject.width)/2;


		Point relativePosition = findRelativeWorkpiecePosition(
				referenceObject,
				workpiece);

		rectangle(image, referenceObject, Scalar(0,0,255));
		polylines(image,workpiece, true, Scalar(255,255,0));
		line(image, referenceObject.br(),referenceObject.br()+relativePosition, Scalar(255,0,0));

		double workPieceDistance = cmPerPixel*norm(relativePosition);

		putText(image, "Distancia medida: " + to_string(workPieceDistance) + " cm" , Point (10,20), FONT_HERSHEY_SIMPLEX, 0.8, Scalar(255,255,255));

		// Display results
		imshow("Display Image", image);
	}
	return 0;
}
