import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../widgets/info_modal.dart';
import '../widgets/evaluation_modal.dart';

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

  // NEW: Added to track the linguistic confidence score
  double _confidenceScore = 0.0;

  final List<String> translationModes = [
    'Baybayin to Tagalog',
    'Tagalog to Baybayin',
  ];

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
      text: text
    );

    setState(() {
      _isLoading = false;
      if (response != null) {
        _translatedResult = response['translated_text'] ?? "No result";
        // CAPTURE CONFIDENCE: Ensuring we extract the value from the API
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
    final XFile? photo = await _picker.pickImage(source: ImageSource.camera, imageQuality: 85);
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
        // Pass the session_id from the API response to the modal
        sessionId: data['session_id'] ?? 0,
      ),
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
            const SizedBox(height: 10),
            _buildHeader(),
            const SizedBox(height: 20),
            Expanded(
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 20),
                decoration: BoxDecoration(
                  color: const Color(0xFFF5F5F5), // Light gray background
                  borderRadius: BorderRadius.circular(15),
                ),
                clipBehavior: Clip.antiAlias,
                child: selectedMode == 'Tagalog to Baybayin'
                    ? _buildTextInputView()
                    : _buildImageView(),
              ),
            ),
            const SizedBox(height: 30),
            if (selectedMode != 'Tagalog to Baybayin')
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 30),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    GestureDetector(onTap: _uploadFromGallery, child: _buildUploadWidget()),
                    const SizedBox(width: 40),
                    GestureDetector(onTap: _captureFromCamera, child: _buildCameraWidget()),
                  ],
                ),
              ),
            const SizedBox(height: 30),
            _buildModeSelector(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 15),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const SizedBox(width: 40), // Placeholder to balance info icon
          Image.asset('assets/images/dayawlogo.png', height: 50),
          IconButton(
            icon: const Icon(Icons.info_outline, color: Colors.brown),
            onPressed: () => showModalBottomSheet(
              context: context,
              builder: (context) => const InfoModal(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextInputView() {
    // Helper to change color based on confidence level
    Color getConfidenceColor() {
      if (_confidenceScore >= 95) return Colors.green;
      if (_confidenceScore >= 75) return Colors.orange;
      return Colors.red;
    }

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextField(
            controller: _textController,
            onChanged: _handleTextTranslation,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 18),
            decoration: InputDecoration(
              hintText: "I-type ang Tagalog dito...",
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              suffixIcon: const Icon(Icons.translate, color: Colors.brown),
            ),
          ),
          const SizedBox(height: 40),
          if (_isLoading)
            const CircularProgressIndicator(color: Colors.brown)
          else ...[
            Text(
              _translatedResult,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 60,
                color: Color.fromARGB(255, 0, 0, 0),
                fontFamily: 'Baybayin', 
              ),
            ),
            
            // COMPLETED: System Confidence Display
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
                      style: TextStyle(color: Colors.grey, fontSize: 13),
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
      children: [
        if (_webImage != null) Positioned.fill(child: Image.memory(_webImage!, fit: BoxFit.contain)),
        Center(
          child: _isLoading
              ? const CircularProgressIndicator(color: Colors.brown)
              : Text(
                  _translatedResult,
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: _webImage != null ? Colors.white : Colors.black54,
                  ),
                ),
        ),
      ],
    );
  }

  Widget _buildCameraWidget() => Container(
    height: 75, width: 75,
    decoration: const BoxDecoration(color: Colors.brown, shape: BoxShape.circle),
    child: const Icon(Icons.camera_alt, color: Colors.white, size: 30),
  );

  Widget _buildUploadWidget() => Column(
    children: const [
      Icon(Icons.photo_library, size: 30, color: Colors.grey),
      Text("Gallery", style: TextStyle(fontSize: 12, color: Colors.grey)),
    ],
  );

  Widget _buildModeSelector() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: translationModes.map((mode) {
        bool isSelected = mode == selectedMode;
        return GestureDetector(
          onTap: () => setState(() {
            selectedMode = mode;
            _translatedResult = "Result will appear here";
            _webImage = null;
            _textController.clear();
            _confidenceScore = 0.0;
          }),
          child: Column(
            children: [
              Text(
                mode,
                style: TextStyle(
                  color: isSelected ? Colors.brown : Colors.grey,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
              if (isSelected)
                Container(margin: const EdgeInsets.only(top: 4), height: 2, width: 40, color: Colors.brown),
            ],
          ),
        );
      }).toList(),
    );
  }
}