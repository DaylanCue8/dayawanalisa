import 'package:flutter/material.dart';
import '../services/api_service.dart';

class EvaluationModal extends StatefulWidget {
  final List<dynamic> detections;
  final double averageConfidence;
  final String translatedText;
  final int sessionId;

  const EvaluationModal({
    super.key,
    required this.detections,
    required this.averageConfidence,
    required this.translatedText,
    required this.sessionId,
  });

  @override
  State<EvaluationModal> createState() => _EvaluationModalState();
}

class _EvaluationModalState extends State<EvaluationModal> {
  bool _isArchived = false;
  bool _isProcessing = false;

  /// --- HANDLE BULK ARCHIVE ---
  Future<void> _handleBulkArchive(BuildContext context, List<Map<String, dynamic>> eligible) async {
    if (_isArchived || _isProcessing) return;

    setState(() => _isProcessing = true);

    final ApiService apiService = ApiService();
    // Ensure we pass the list as expected by the ApiService
    bool success = await apiService.archiveBulkCharacters(eligible, widget.sessionId);

    if (!mounted) return; // Standard check before using context after an async gap

    setState(() {
      _isProcessing = false;
      if (success) _isArchived = true;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success ? "Salamat! Data archived." : "Failed to archive."),
        backgroundColor: success ? Colors.green : Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Defensive mapping: Ensure every detection is treated as a Map safely
    final List<Map<String, dynamic>> eligibleDetections = widget.detections
        .where((d) => d is Map && (d['is_eligible'] ?? false))
        .map((d) => Map<String, dynamic>.from(d as Map))
        .toList();

    return Container(
      // Use Constraints instead of fixed height for better responsiveness
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.85,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
      child: Column(
        mainAxisSize: MainAxisSize.min, // Shrinks modal to content
        children: [
          // Handle/Grabber for the bottom sheet
          Container(
            width: 40,
            height: 5,
            margin: const EdgeInsets.only(bottom: 10),
            decoration: BoxDecoration(color: Colors.grey[300], borderRadius: BorderRadius.circular(10)),
          ),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Text(
                      "dayaw",
                      style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.orange[700]),
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Text("Translation Result", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  Text(
                    widget.translatedText,
                    style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.brown),
                  ),
                  const SizedBox(height: 20),
                  _buildStatRow("Detected Characters:", "${widget.detections.length}"),
                  _buildStatRow("Average Confidence:", "${widget.averageConfidence.toStringAsFixed(1)}%"),
                  const Divider(height: 40),
                  
                  // --- EVALUATION TABLE ---
                  Table(
                    defaultVerticalAlignment: TableCellVerticalAlignment.middle,
                    children: [
                      const TableRow(
                        decoration: BoxDecoration(border: Border(bottom: BorderSide(color: Colors.grey, width: 0.5))),
                        children: [
                          Padding(padding: EdgeInsets.all(8.0), child: Text("Char", style: TextStyle(fontWeight: FontWeight.bold))),
                          Padding(padding: EdgeInsets.all(8.0), child: Text("Conf.", style: TextStyle(fontWeight: FontWeight.bold))),
                          Padding(padding: EdgeInsets.all(8.0), child: Text("Status", style: TextStyle(fontWeight: FontWeight.bold))),
                        ],
                      ),
                      // Map your items to table rows
                      ...widget.detections.map((d) => _buildTableRow(d as Map<String, dynamic>)),
                    ],
                  ),
                  const SizedBox(height: 30),

                  // --- PERMISSION CARD ---
                  if (eligibleDetections.isNotEmpty)
                    _buildArchivePermissionCard(context, eligibleDetections)
                  else
                    const Center(
                      child: Text("No high-confidence characters eligible.", style: TextStyle(color: Colors.grey, fontSize: 12)),
                    ),
                  const SizedBox(height: 30),
                  _buildLearningTip(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildArchivePermissionCard(BuildContext context, List<Map<String, dynamic>> eligible) {
    // Logic for button and colors
    final Color? cardColor = _isArchived ? Colors.grey[100] : Colors.orange[50];
    final Color borderColor = _isArchived ? Colors.grey[300]! : Colors.orange[200]!;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: borderColor),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                _isArchived ? Icons.cloud_done : Icons.volunteer_activism,
                color: _isArchived ? Colors.grey : Colors.orange[800],
              ),
              const SizedBox(width: 10),
              Text(
                _isArchived ? "Data Saved to Archive" : "Help Dayaw Grow",
                style: TextStyle(fontWeight: FontWeight.bold, color: _isArchived ? Colors.grey : Colors.black),
              ),
            ],
          ),
          const SizedBox(height: 10),
          if (!_isArchived)
            Text("We detected ${eligible.length} high-quality strokes. Permit us to save them?"),
          const SizedBox(height: 15),
          ElevatedButton.icon(
            onPressed: (_isArchived || _isProcessing) ? null : () => _handleBulkArchive(context, eligible),
            icon: _isProcessing
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : Icon(_isArchived ? Icons.check : Icons.check_circle_outline),
            label: Text(_isArchived ? "Archived Successfully" : "Archive All Eligible Strokes"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange[800],
              foregroundColor: Colors.white,
              disabledBackgroundColor: Colors.grey[400],
              disabledForegroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 45),
            ),
          ),
        ],
      ),
    );
  }

  TableRow _buildTableRow(Map<String, dynamic> d) {
    // JSON numbers can come as int or double; num.parse/cast is safer
    final double conf = (d['confidence'] as num).toDouble();
    final bool isExcellent = conf > 90;

    return TableRow(
      children: [
        Padding(padding: const EdgeInsets.all(8.0), child: Text(d['char']?.toString() ?? '?', style: const TextStyle(fontSize: 18))),
        Padding(padding: const EdgeInsets.all(8.0), child: Text("${conf.toStringAsFixed(1)}%")),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Text(
            isExcellent ? "Excellent" : "Good",
            style: TextStyle(
              color: isExcellent ? Colors.green : Colors.blueGrey,
              fontWeight: FontWeight.bold,
              fontSize: 11,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(label),
          const SizedBox(width: 10),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildLearningTip() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: Colors.grey[100], borderRadius: BorderRadius.circular(10)),
      child: const Text("Tip: Clear handwriting improves AI learning!", style: TextStyle(fontSize: 12)),
    );
  }
}