import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

class SkeletonContainer extends StatelessWidget {
  final double width;
  final double height;
  final double borderRadius;

  const SkeletonContainer({
    super.key,
    required this.width,
    required this.height,
    this.borderRadius = 10,
  });

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Color(0xFF151E32),
      highlightColor: Color(0xFF1F2937),
      child: Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          color: Color(0xFF151E32),
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
    );
  }
}

class CourseSkeleton extends StatelessWidget {
  const CourseSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: Color(0xFF151E32),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SkeletonContainer(width: double.infinity, height: 160, borderRadius: 20),
          Padding(
            padding: const EdgeInsets.all(15.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SkeletonContainer(width: 80, height: 12),
                SizedBox(height: 10),
                SkeletonContainer(width: double.infinity, height: 16),
                SizedBox(height: 5),
                SkeletonContainer(width: 200, height: 16),
                SizedBox(height: 15),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    SkeletonContainer(width: 100, height: 12),
                    SkeletonContainer(width: 60, height: 16),
                  ],
                )
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class EventSkeleton extends StatelessWidget {
  const EventSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: Color(0xFF151E32),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SkeletonContainer(width: double.infinity, height: 150, borderRadius: 15),
          Padding(
            padding: EdgeInsets.all(15),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SkeletonContainer(width: 200, height: 18),
                SizedBox(height: 10),
                SkeletonContainer(width: 120, height: 12),
                SizedBox(height: 5),
                SkeletonContainer(width: 150, height: 12),
              ],
            ),
          )
        ],
      ),
    );
  }
}

class ForumTopicSkeleton extends StatelessWidget {
  const ForumTopicSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(bottom: 15),
      padding: EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Color(0xFF151E32),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SkeletonContainer(width: 200, height: 16),
          SizedBox(height: 10),
          SkeletonContainer(width: double.infinity, height: 12),
          SizedBox(height: 5),
          SkeletonContainer(width: 150, height: 12),
          SizedBox(height: 15),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              SkeletonContainer(width: 80, height: 10),
              SkeletonContainer(width: 40, height: 10),
            ],
          )
        ],
      ),
    );
  }
}
