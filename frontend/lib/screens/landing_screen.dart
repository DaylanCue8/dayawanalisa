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

  /// --- UI BUILDERS ---

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 10),
            _buildHeader(colorScheme),
            const SizedBox(height: 16),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Card(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: selectedMode == 'Tagalog to Baybayin'
                        ? _buildTextInputView(colorScheme)
                        : _buildImageView(colorScheme),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (selectedMode != 'Tagalog to Baybayin')
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: _buildImageActions(colorScheme),
              ),
            const SizedBox(height: 24),
            _buildModeSelector(colorScheme),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(ColorScheme colorScheme) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Placeholder to balance the info button
          const SizedBox(width: 48),
          Image.asset('assets/images/dayawlogo.png', height: 50),
          IconButton(
            icon: Icon(Icons.info_outline, color: colorScheme.primary),
            tooltip: 'About Dayaw',
            onPressed: () => showModalBottomSheet(
              context: context,
              isScrollControlled: true,
              builder: (context) => const InfoModal(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextInputView(ColorScheme colorScheme) {
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
            style: const TextStyle(fontSize: 18),
            decoration: InputDecoration(
              hintText: "I-type ang Tagalog dito...",
              fillColor: colorScheme.surfaceContainerHighest,
              suffixIcon: Icon(Icons.translate, color: colorScheme.primary),
            ),
          ),
          const SizedBox(height: 36),
          if (_isLoading)
            CircularProgressIndicator(color: colorScheme.primary)
          else ...[
            Text(
              _translatedResult,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 60,
                color: colorScheme.primary,
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
                    Text(
                      "System Confidence",
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
  }

  Widget _buildImageView(ColorScheme colorScheme) {
    return Stack(
      children: [
        if (_webImage != null)
          Positioned.fill(child: Image.memory(_webImage!, fit: BoxFit.contain)),
        Center(
          child: _isLoading
              ? CircularProgressIndicator(color: colorScheme.primary)
              : Text(
                  _translatedResult,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: _webImage != null
                        ? Colors.white
                        : colorScheme.onSurfaceVariant,
                  ),
                ),
        ),
      ],
    );
  }

  Widget _buildImageActions(ColorScheme colorScheme) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Gallery picker – outlined button
        OutlinedButton.icon(
          onPressed: _uploadFromGallery,
          icon: const Icon(Icons.photo_library_outlined),
          label: const Text("Gallery"),
          style: OutlinedButton.styleFrom(
            foregroundColor: colorScheme.onSurfaceVariant,
            side: BorderSide(color: colorScheme.outlineVariant),
          ),
        ),
        const SizedBox(width: 32),
        // Camera capture – filled button (primary action)
        FilledButton.icon(
          onPressed: _captureFromCamera,
          icon: const Icon(Icons.camera_alt_outlined),
          label: const Text("Camera"),
        ),
      ],
    );
  }

  Widget _buildModeSelector(ColorScheme colorScheme) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: SegmentedButton<String>(
        segments: const [
          ButtonSegment(
            value: 'Baybayin to Tagalog',
            label: Text('Baybayin → Tagalog'),
            icon: Icon(Icons.image_outlined),
          ),
          ButtonSegment(
            value: 'Tagalog to Baybayin',
            label: Text('Tagalog → Baybayin'),
            icon: Icon(Icons.keyboard_outlined),
          ),
        ],
        selected: {selectedMode},
        onSelectionChanged: (Set<String> newSelection) {
          setState(() {
            selectedMode = newSelection.first;
            _translatedResult = "Result will appear here";
            _webImage = null;
            _textController.clear();
            _confidenceScore = 0.0;
          });
        },
        style: ButtonStyle(
          backgroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return colorScheme.primaryContainer;
            }
            return null;
          }),
          foregroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return colorScheme.onPrimaryContainer;
            }
            return colorScheme.onSurfaceVariant;
          }),
        ),
      ),
    );
  }
}
