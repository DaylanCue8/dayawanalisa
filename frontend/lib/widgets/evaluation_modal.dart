import 'package:flutter/material.dart';

class EvaluationModal extends StatelessWidget {
  final List<dynamic> detections;
  final double averageConfidence;
  final String translatedText;

  const EvaluationModal({
    super.key,
    required this.detections,
    required this.averageConfidence,
    required this.translatedText,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: colorScheme.outlineVariant,
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 1. App wordmark
            Center(
              child: Text(
                "dayaw",
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: colorScheme.primary,
                  letterSpacing: 1.5,
                ),
              ),
            ),
            const SizedBox(height: 20),

            // 2. Translation Result
            Text(
              "Translation Result",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: colorScheme.onSurface,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              translatedText,
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.bold,
                color: colorScheme.primary,
              ),
            ),
            const SizedBox(height: 20),

            // 3. Recognition Summary
            Text(
              "Recognition Summary",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: colorScheme.onSurface,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              "Your Baybayin writing has been successfully analyzed. "
              "The system detected characters and translated them into Tagalog syllables.",
              style: TextStyle(color: colorScheme.onSurfaceVariant, height: 1.5),
            ),

            const SizedBox(height: 20),

            // 4. Stats card
            Card(
              color: colorScheme.surfaceContainerLow,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    _buildStatRow(
                      context,
                      "Image Quality",
                      averageConfidence > 70 ? "Good" : "Fair",
                      colorScheme,
                    ),
                    const SizedBox(height: 8),
                    _buildStatRow(
                      context,
                      "Detected Characters",
                      "${detections.length}",
                      colorScheme,
                    ),
                    const SizedBox(height: 8),
                    _buildStatRow(
                      context,
                      "Average Confidence",
                      "${averageConfidence.toStringAsFixed(1)}%",
                      colorScheme,
                    ),
                  ],
                ),
              ),
            ),

            const Divider(height: 40),

            // 5. Character Recognition Evaluation Table
            Text(
              "Character Recognition Evaluation",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 15,
                color: colorScheme.onSurface,
              ),
            ),
            const SizedBox(height: 12),

            Table(
              columnWidths: const {
                0: FlexColumnWidth(1),
                1: FlexColumnWidth(1),
                2: FlexColumnWidth(1),
                3: FlexColumnWidth(1.5),
              },
              children: [
                TableRow(
                  decoration: BoxDecoration(
                    border: Border(
                      bottom: BorderSide(color: colorScheme.outlineVariant),
                    ),
                  ),
                  children: [
                    _tableHeader("Baybayin"),
                    _tableHeader("Detected"),
                    _tableHeader("Confidence"),
                    _tableHeader("Feedback"),
                  ],
                ),
                ...detections.map(
                  (d) => _buildTableRow(
                    d['char'] ?? '?',
                    d['char'] ?? '?',
                    "${d['confidence']}%",
                    _getFeedback(d['confidence']),
                    colorScheme,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 28),
            _buildLearningTip(colorScheme),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _tableHeader(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
      child: Text(
        text,
        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
      ),
    );
  }

  Widget _buildStatRow(
    BuildContext context,
    String label,
    String value,
    ColorScheme colorScheme,
  ) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: colorScheme.onSurface,
          ),
        ),
      ],
    );
  }

  String _getFeedback(dynamic conf) {
    double score = double.tryParse(conf.toString()) ?? 0.0;
    if (score > 85) return "Clear Stroke";
    if (score > 60) return "Accurate";
    return "Check Structure";
  }

  TableRow _buildTableRow(
    String char,
    String syl,
    String conf,
    String feedback,
    ColorScheme colorScheme,
  ) {
    return TableRow(
      children: [
        Padding(padding: const EdgeInsets.all(8), child: Text(char)),
        Padding(padding: const EdgeInsets.all(8), child: Text(syl)),
        Padding(padding: const EdgeInsets.all(8), child: Text(conf)),
        Padding(
          padding: const EdgeInsets.all(8),
          child: Text(
            feedback,
            style: TextStyle(
              fontSize: 11,
              color: colorScheme.secondary,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLearningTip(ColorScheme colorScheme) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.secondaryContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Learning Tip",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: colorScheme.onSecondaryContainer,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            "• Keep strokes bold and continuous\n"
            "• Maintain even spacing between characters\n"
            "• Avoid overlapping strokes",
            style: TextStyle(
              color: colorScheme.onSecondaryContainer,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
}
