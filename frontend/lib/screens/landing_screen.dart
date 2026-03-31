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

  final List<String> translationModes = [
    'Baybayin to Tagalog',
    'Tagalog to Baybayin',
    'Sanayin'
  ];

  // Logic for Tagalog to Baybayin (Text-based)
  Future<void> _handleTextTranslation(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _translatedResult = "Translating...";
    });

    final result = await _apiService.translateTagalogToBaybayin(text);

    setState(() {
      _translatedResult = result;
      _isLoading = false;
    });
  }

  // Logic for Baybayin to Tagalog (Image-based)
  Future<void> _uploadFromGallery() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.gallery);

    if (photo != null) {
      final bytes = await photo.readAsBytes();

      // STEP 1: Show "Processing" state first
      setState(() {
        _isLoading = true;
        _webImage = bytes;
        _translatedResult = "Processing Image...";
      });

      // STEP 2: Wait for the API to actually process the image
      final response = await _apiService.uploadAndTranslateDetailed(photo, selectedMode);

      // STEP 3: Update the UI with the result FIRST
      setState(() {
        _isLoading = false;
        if (response != null) {
          _translatedResult = response['translated_text'] ?? "No result";
        } else {
          _translatedResult = "Error: Connection Failed";
        }
      });

      // STEP 4: Small delay to let the user see the result on the main screen
      // Then open the modal if the status is correct
      if (response != null) {
        String status = response['status']?.toString().toLowerCase() ?? "";
        
        if (status == 'success' || status == 'low_confidence') {
          // Future.delayed ensures the UI has finished its last build cycle
          Future.delayed(const Duration(milliseconds: 500), () {
            if (mounted) {
              _showEvaluation(response);
            }
          });
        }
      }
    }
  }

  Future<void> _captureFromCamera() async {
  final XFile? photo = await _picker.pickImage(
    source: ImageSource.camera,
    imageQuality: 85, // compress a bit for faster upload
  );

  if (photo != null) {
    final bytes = await photo.readAsBytes();

    // Show loading + preview
    setState(() {
      _isLoading = true;
      _webImage = bytes;
      _translatedResult = "Processing Image...";
    });

    // Send to API
    final response = await _apiService.uploadAndTranslateDetailed(photo, selectedMode);

    // Update UI
    setState(() {
      _isLoading = false;
      if (response != null) {
        _translatedResult = response['translated_text'] ?? "No result";
      } else {
        _translatedResult = "Error: Connection Failed";
      }
    });

    // Show evaluation modal
    if (response != null) {
      String status = response['status']?.toString().toLowerCase() ?? "";

      if (status == 'success' || status == 'low_confidence') {
        Future.delayed(const Duration(milliseconds: 500), () {
          if (mounted) {
            _showEvaluation(response);
          }
        });
      }
    }
  }
}

  // Helper function to trigger the Evaluation Modal
  void _showEvaluation(Map<String, dynamic> data) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent, // Allows for the rounded top corners
      builder: (context) => EvaluationModal(
        detections: data['individual_detections'] ?? [],
        averageConfidence: (data['confidence'] as num).toDouble(),
        translatedText: data['translated_text'] ?? "",
      ),
    );
  }
  
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

            // 1. MAIN DISPLAY AREA (Conditional)
            Expanded(
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 20),
                decoration: BoxDecoration(
                  color: const Color(0xFFE0E0E0),
                  borderRadius: BorderRadius.circular(15),
                ),
                clipBehavior: Clip.antiAlias,
                child: selectedMode == 'Tagalog to Baybayin'
                    ? _buildTextInputView()
                    : _buildImageView(),
              ),
            ),

            const SizedBox(height: 30),

            // 2. BUTTON ROW (Hidden if in Text Mode to keep UI clean)
            if (selectedMode != 'Tagalog to Baybayin')
              Padding(
  padding: const EdgeInsets.symmetric(horizontal: 30),
  child: Row(
    children: [
      Expanded(
        child: Align(
          alignment: Alignment.centerLeft,
          child: GestureDetector(
            onTap: _uploadFromGallery,
            child: _buildUploadWidget(),
          ),
        ),
      ),

      // ✅ CAMERA BUTTON (FIXED)
      GestureDetector(
  onTap: () {
    print("📷 CAMERA BUTTON CLICKED"); // 👈 ADD THIS
    _captureFromCamera();
  },
  child: _buildCameraWidget(),
),
      const Expanded(child: SizedBox()),
    ],
  ),
),

            const SizedBox(height: 30),

            // 3. MODE SELECTOR
            _buildModeSelector(),
          ],
        ),
      ),
    );
  }

  // Header Component
  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 10),
      child: Stack(
        alignment: Alignment.center,
        children: [
          Center(
            child: Image.asset(
              'assets/images/dayawlogo.png',
              height: 60,
              fit: BoxFit.contain,
            ),
          ),
          Align(
            alignment: Alignment.centerRight,
            child: IconButton(
              icon: const Icon(Icons.info_outline, color: Colors.brown),
              onPressed: () {
                showModalBottomSheet(
                  context: context,
                  isScrollControlled: true,
                  shape: const RoundedRectangleBorder(
                    borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
                  ),
                  builder: (context) => const InfoModal(),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  // View for Tagalog to Baybayin
  Widget _buildTextInputView() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TextField(
            controller: _textController,
            onChanged: (val) => _handleTextTranslation(val),
            decoration: InputDecoration(
              hintText: "I-type ang Tagalog dito...",
              filled: true,
              fillColor: Colors.white,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
              suffixIcon: const Icon(Icons.translate, color: Colors.brown),
            ),
          ),
          const SizedBox(height: 40),
          if (_isLoading)
            const CircularProgressIndicator(color: Colors.brown)
          else
            Text(
              _translatedResult,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 40, // Larger font for Baybayin characters
                color: Colors.brown,
                fontWeight: FontWeight.bold,
              ),
            ),
          const SizedBox(height: 10),
          const Text("Baybayin Result", style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  // View for Baybayin to Tagalog (Image Upload)
  Widget _buildImageView() {
    return Stack(
      children: [
        if (_webImage != null)
          Positioned.fill(
            child: Image.memory(_webImage!, fit: BoxFit.contain),
          ),
        Container(
          color: _webImage != null ? Colors.black26 : Colors.transparent,
          padding: const EdgeInsets.all(20),
          child: Center(
            child: _isLoading
                ? const CircularProgressIndicator(color: Colors.white)
                : Text(
                    _translatedResult,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: _webImage != null ? Colors.white : Colors.black54,
                    ),
                  ),
          ),
        ),
      ],
    );
  }

  Widget _buildCameraWidget() {
    return Container(
      height: 85, width: 85,
      decoration: BoxDecoration(
        color: Colors.white,
        shape: BoxShape.circle,
        border: Border.all(color: Colors.black12, width: 2),
      ),
      child: Center(
        child: Container(
          height: 65, width: 65,
          decoration: const BoxDecoration(
            color: Color(0xFFF0F0F0),
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.camera_alt, color: Colors.white, size: 35),
        ),
      ),
    );
  }

  Widget _buildUploadWidget() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          height: 60, width: 60,
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            border: Border.all(color: Colors.black12, width: 2),
          ),
          child: const Icon(Icons.photo_library, size: 28, color: Colors.grey),
        ),
        const SizedBox(height: 4),
        const Text("Upload", style: TextStyle(fontSize: 13, color: Colors.grey)),
      ],
    );
  }

  Widget _buildModeSelector() {
    return Container(
      color: const Color(0xFFF9F9F9),
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: translationModes.map((mode) {
          bool isSelected = mode == selectedMode;
          return GestureDetector(
            onTap: () => setState(() {
              selectedMode = mode;
              _translatedResult = "Result will appear here";
              _webImage = null;
              _textController.clear();
            }),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
              decoration: isSelected
                  ? const BoxDecoration(
                      border: Border(bottom: BorderSide(width: 2, color: Colors.brown)))
                  : null,
              child: Text(
                mode,
                style: TextStyle(
                  color: isSelected ? Colors.brown : Colors.black54,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}