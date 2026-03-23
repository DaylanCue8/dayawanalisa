import 'package:flutter/material.dart';

class EvaluationModal extends StatelessWidget {
  final List<dynamic> detections;
  final double averageConfidence;
  final String translatedText; // Added this to pass the result (e.g., "LABA")

  const EvaluationModal({
    super.key,
    required this.detections,
    required this.averageConfidence,
    required this.translatedText, // Make sure to pass this from landing_screen
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
      ),
      padding: const EdgeInsets.all(20),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Logo
            Center(
              child: Text(
                "dayaw",
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange[700],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // 2. Translation Result (Moved to the top)
            const Text(
              "Translation Result",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 5),
            Text(
              translatedText,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.brown),
            ),
            const SizedBox(height: 20),
            
            // 3. Recognition Summary
            const Text(
              "Recognition Summary",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            const SizedBox(height: 10),
            const Text(
              "Your Baybayin writing has been successfully analyzed. The system detected characters and translated them into Tagalog syllables.",
              style: TextStyle(color: Colors.black87),
            ),
            
            const SizedBox(height: 20),

            // 4. Stats: Image Quality, Detected Characters, Avg Confidence
            _buildStatRow("Image Quality:", averageConfidence > 70 ? "Good" : "Fair"),
            _buildStatRow("Detected Characters:", "${detections.length}"),
            _buildStatRow("Average Confidence Score:", "${averageConfidence.toStringAsFixed(1)}%"),

            const Divider(height: 40),
            
            // 5. Character Recognition Evaluation Table
            const Text(
              "Character Recognition Evaluation",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 15),
            
            Table(
              columnWidths: const {
                0: FlexColumnWidth(1),
                1: FlexColumnWidth(1),
                2: FlexColumnWidth(1),
                3: FlexColumnWidth(1.5),
              },
              children: [
                const TableRow(
                  decoration: BoxDecoration(border: Border(bottom: BorderSide(color: Colors.grey))),
                  children: [
                    Padding(padding: EdgeInsets.all(8.0), child: Text("Baybayin", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12))),
                    Padding(padding: EdgeInsets.all(8.0), child: Text("Detected", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12))),
                    Padding(padding: EdgeInsets.all(8.0), child: Text("Confidence", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12))),
                    Padding(padding: EdgeInsets.all(8.0), child: Text("Feedback", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12))),
                  ],
                ),
                ...detections.map((d) => _buildTableRow(
                  d['char'] ?? '?', 
                  d['char'] ?? '?', 
                  "${d['confidence']}%", 
                  _getFeedback(d['confidence'])
                )),
              ],
            ),
            
            const SizedBox(height: 30),
            _buildLearningTip(),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  // Helper for the label: value rows
  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          const SizedBox(width: 10),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  String _getFeedback(dynamic conf) {
    double score = double.tryParse(conf.toString()) ?? 0.0;
    if (score > 85) return "Clear Stroke";
    if (score > 60) return "Accurate";
    return "Check Structure";
  }

  TableRow _buildTableRow(String char, String syl, String conf, String feedback) {
    return TableRow(children: [
      Padding(padding: const EdgeInsets.all(8.0), child: Text(char)),
      Padding(padding: const EdgeInsets.all(8.0), child: Text(syl)),
      Padding(padding: const EdgeInsets.all(8.0), child: Text(conf)),
      Padding(padding: const EdgeInsets.all(8.0), child: Text(feedback, style: const TextStyle(fontSize: 11, color: Colors.blueGrey))),
    ]);
  }

  Widget _buildLearningTip() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(color: Colors.grey[100], borderRadius: BorderRadius.circular(10)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text("Learning Tip", style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 5),
          Text("• Keep strokes bold and continuous"),
          Text("• Maintain even spacing between characters"),
          Text("• Avoid overlapping strokes"),
        ],
      ),
    );
  }
}