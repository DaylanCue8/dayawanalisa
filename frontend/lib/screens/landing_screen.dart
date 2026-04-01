import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../widgets/info_modal.dart';
import '../widgets/evaluation_modal.dart';

const Color _kYellow = Color(0xFFFFC107);
const Color _kBlack = Colors.black;

class DayawLandingScreen extends StatefulWidget {
  const DayawLandingScreen({super.key});

  @override
  State<DayawLandingScreen> createState() => _DayawLandingScreenState();
}

class _DayawLandingScreenState extends State<DayawLandingScreen> {
  final ApiService _apiService = ApiService();
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _textController = TextEditingController();

  String selectedMode = 'Baybayin to Tagalog';
  String _translatedResult = "Result will appear here";
  bool _isLoading = false;
  Uint8List? _webImage;

  double _confidenceScore = 0.0;
  Map<String, dynamic>? _lastImageResponse;

  /// --- CORE TRANSLATION LOGIC ---

  Future<void> _handleTextTranslation(String text) async {
    if (text.trim().isEmpty) {
      setState(() {
        _translatedResult = "Result will appear here";
        _confidenceScore = 0.0;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _translatedResult = "Translating...";
    });

    final response = await _apiService.uploadAndTranslateDetailed(
      null,
      selectedMode,
      text: text,
    );

    setState(() {
      _isLoading = false;
      if (response != null) {
        _translatedResult = response['translated_text'] ?? "No result";
        _confidenceScore = (response['confidence'] as num).toDouble();
      } else {
        _translatedResult = "Error: Connection Failed";
        _confidenceScore = 0.0;
      }
    });
  }

  Future<void> _processImage(XFile? photo) async {
    if (photo == null) return;
    final bytes = await photo.readAsBytes();

    setState(() {
      _isLoading = true;
      _webImage = bytes;
      _translatedResult = "Processing Image...";
    });

    final response = await _apiService.uploadAndTranslateDetailed(photo, selectedMode);

    setState(() {
      _isLoading = false;
      if (response != null) {
        _lastImageResponse = response;
        _translatedResult = response['translated_text'] ?? "No result";

        String status = response['status']?.toString().toLowerCase() ?? "";
        if (status == 'success' || status == 'low_confidence') {
          Future.delayed(const Duration(milliseconds: 500), () {
            if (mounted) _showEvaluation(response);
          });
        }
      } else {
        _translatedResult = "Error: Connection Failed";
      }
    });
  }

  Future<void> _uploadFromGallery() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.gallery);
    _processImage(photo);
  }

  Future<void> _captureFromCamera() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
    );
    _processImage(photo);
  }

  void _showEvaluation(Map<String, dynamic> data) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => EvaluationModal(
        detections: data['individual_detections'] ?? [],
        averageConfidence: (data['confidence'] as num).toDouble(),
        translatedText: data['translated_text'] ?? "",
      ),
    );
  }

  void _showInfoModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => const InfoModal(),
    );
  }

  void _showChartModal() {
    if (_lastImageResponse != null) {
      _showEvaluation(_lastImageResponse!);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("No recognition data yet. Capture or upload an image first."),
        ),
      );
    }
  }

  void _showModeSelector() {
    showModalBottomSheet(
      context: context,
      builder: (context) => _buildModeSelectorSheet(),
    );
  }

  /// --- UI BUILDERS ---

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            _buildTopNav(),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                child: _buildMainCard(),
              ),
            ),
            const SizedBox(height: 16),
            _buildActionButtons(),
            const SizedBox(height: 16),
            _buildBottomSection(),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  // ── Top navigation bar ──────────────────────────────────────────────────────

  Widget _buildTopNav() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _navItem("about", onTap: _showInfoModal),
          _navItem("how", onTap: _showInfoModal),
          // Centre: logo acts as the "dayaw" tab
          Image.asset('assets/images/dayawlogo.png', height: 40),
          _navItem("chart", onTap: _showChartModal),
          _navItem("settings", onTap: _showModeSelector),
        ],
      ),
    );
  }

  Widget _navItem(String label, {VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Text(
          label,
          style: const TextStyle(
            fontSize: 13,
            color: _kBlack,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  // ── Main yellow card ─────────────────────────────────────────────────────────

  Widget _buildMainCard() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: _kYellow,
        borderRadius: BorderRadius.circular(24),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: selectedMode == 'Tagalog to Baybayin'
            ? _buildTextInputView()
            : _buildImageView(),
      ),
    );
  }

  Widget _buildTextInputView() {
    Color getConfidenceColor() {
      if (_confidenceScore >= 95) return Colors.green;
      if (_confidenceScore >= 75) return Colors.orange;
      return Colors.red;
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextField(
            controller: _textController,
            onChanged: _handleTextTranslation,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 18, color: _kBlack),
            decoration: InputDecoration(
              hintText: "I-type ang Tagalog dito...",
              hintStyle: TextStyle(color: _kBlack.withAlpha(128)),
              fillColor: Colors.white.withAlpha(200),
              filled: true,
              suffixIcon: const Icon(Icons.translate, color: _kBlack),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide.none,
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: const BorderSide(color: _kBlack, width: 1),
              ),
            ),
          ),
          const SizedBox(height: 36),
          if (_isLoading)
            const CircularProgressIndicator(color: _kBlack)
          else ...[
            Text(
              _translatedResult,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 60,
                color: _kBlack,
                fontFamily: 'Baybayin',
              ),
            ),
            // System Confidence Display
            if (_translatedResult != "Result will appear here")
              Padding(
                padding: const EdgeInsets.only(top: 20),
                child: Column(
                  children: [
                    Text(
                      "${_confidenceScore.toInt()}%",
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: getConfidenceColor(),
                      ),
                    ),
                    const Text(
                      "System Confidence",
                      style: TextStyle(color: _kBlack, fontSize: 13),
                    ),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
  }

  Widget _buildImageView() {
    return Stack(
      alignment: Alignment.center,
      children: [
        if (_webImage != null)
          Positioned.fill(child: Image.memory(_webImage!, fit: BoxFit.contain)),
        if (_webImage == null)
          const Padding(
            padding: EdgeInsets.all(48),
            child: Icon(Icons.image_outlined, size: 80, color: Colors.white54),
          ),
        if (_isLoading)
          const CircularProgressIndicator(color: _kBlack)
        else if (_translatedResult != "Result will appear here" &&
            _translatedResult != "Processing Image...")
          Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.black54,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              _translatedResult,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
      ],
    );
  }

  // ── Action buttons row ───────────────────────────────────────────────────────

  Widget _buildActionButtons() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Upload – outlined yellow border
          Expanded(
            child: OutlinedButton.icon(
              onPressed: _uploadFromGallery,
              icon: const Icon(Icons.upload_outlined, color: _kBlack),
              label: const Text("Upload", style: TextStyle(color: _kBlack)),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: _kYellow, width: 2),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Centre – profile icon (opens mode selector)
          Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: _kYellow, width: 2),
            ),
            child: IconButton(
              onPressed: _showModeSelector,
              icon: const Icon(Icons.person_outline, color: _kBlack),
              iconSize: 28,
            ),
          ),
          const SizedBox(width: 12),
          // Capture – filled yellow with camera icon
          Expanded(
            child: ElevatedButton.icon(
              onPressed: _captureFromCamera,
              icon: const Icon(Icons.camera_alt, color: _kBlack),
              label: const Text("Capture", style: TextStyle(color: _kBlack)),
              style: ElevatedButton.styleFrom(
                backgroundColor: _kYellow,
                foregroundColor: _kBlack,
                padding: const EdgeInsets.symmetric(vertical: 14),
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Bottom white icon section ────────────────────────────────────────────────

  Widget _buildBottomSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(20),
            blurRadius: 12,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          // Chart icon – filled yellow circle
          GestureDetector(
            onTap: _showChartModal,
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: const BoxDecoration(
                color: _kYellow,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.bar_chart, color: _kBlack, size: 22),
            ),
          ),
          // Settings icon
          GestureDetector(
            onTap: _showModeSelector,
            child: const Icon(Icons.settings_outlined, color: _kBlack, size: 28),
          ),
          // Hex / Baybayin symbol icon
          GestureDetector(
            onTap: _showInfoModal,
            child: const Icon(Icons.hexagon_outlined, color: _kBlack, size: 28),
          ),
        ],
      ),
    );
  }

  // ── Mode selector bottom sheet ───────────────────────────────────────────────

  Widget _buildModeSelectorSheet() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            "Translation Mode",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          _modeOption('Baybayin to Tagalog', Icons.image_outlined),
          const SizedBox(height: 12),
          _modeOption('Tagalog to Baybayin', Icons.keyboard_outlined),
        ],
      ),
    );
  }

  Widget _modeOption(String mode, IconData icon) {
    final bool isSelected = selectedMode == mode;
    return GestureDetector(
      onTap: () {
        setState(() {
          selectedMode = mode;
          _translatedResult = "Result will appear here";
          _webImage = null;
          _textController.clear();
          _confidenceScore = 0.0;
        });
        Navigator.pop(context);
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? _kYellow : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isSelected ? _kYellow : Colors.grey.shade300,
            width: 2,
          ),
        ),
        child: Row(
          children: [
            Icon(icon, color: _kBlack),
            const SizedBox(width: 12),
            Text(
              mode,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: _kBlack,
              ),
            ),
            if (isSelected) ...[
              const Spacer(),
              const Icon(Icons.check_circle, color: _kBlack),
            ],
          ],
        ),
      ),
    );
  }
}
