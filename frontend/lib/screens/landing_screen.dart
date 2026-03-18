import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../widgets/info_modal.dart';

class DayawLandingScreen extends StatefulWidget {
  const DayawLandingScreen({super.key});

  @override
  State<DayawLandingScreen> createState() => _DayawLandingScreenState();
}

class _DayawLandingScreenState extends State<DayawLandingScreen> {
  final ApiService _apiService = ApiService();
  final ImagePicker _picker = ImagePicker();

  String selectedMode = 'Baybayin to Tagalog';
  String _translatedResult = "(Assume that user captures Baybayin text)";
  bool _isLoading = false;
  Uint8List? _webImage;

  final List<String> translationModes = [
    'Baybayin to Tagalog',
    'Tagalog to Baybayin',
    'Sanayin'
  ];

  // Function for Uploading from Gallery (Active)
  Future<void> _uploadFromGallery() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.gallery);

    if (photo != null) {
      final bytes = await photo.readAsBytes();

      setState(() {
        _isLoading = true;
        _webImage = bytes;
        _translatedResult = "Processing...";
      });

      final result = await _apiService.uploadAndTranslate(photo, selectedMode);

      setState(() {
        _translatedResult = result;
        _isLoading = false;
      });
    }
  }

  @override
Widget build(BuildContext context) {
  return Scaffold(
    backgroundColor: Colors.white,
    body: SafeArea(
      child: Column(
        children: [
          const SizedBox(height: 10),
          // HEADER AREA: Stack allows the info button to be on the right 
          // while the logo stays perfectly centered.
          Padding(
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
          ),
          
          const SizedBox(height: 20),

          // 1. MAIN DISPLAY AREA
          Expanded(
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: const Color(0xFFE0E0E0),
                borderRadius: BorderRadius.circular(15),
              ),
              clipBehavior: Clip.antiAlias,
              child: Stack(
                children: [
                  if (_webImage != null)
                    Positioned.fill(
                      child: Image.memory(_webImage!, fit: BoxFit.cover),
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
                                fontSize: 18,
                                fontStyle: FontStyle.italic,
                                color: _webImage != null ? Colors.white : Colors.black54,
                              ),
                            ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 30),

          // 2. BUTTON ROW
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
                GestureDetector(
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text("Camera capture is currently disabled."),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
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

  Widget _buildCameraWidget() {
    return Container(
      height: 85,
      width: 85,
      decoration: BoxDecoration(
        color: Colors.white,
        shape: BoxShape.circle,
        border: Border.all(color: Colors.black12, width: 2),
      ),
      child: Center(
        child: Container(
          height: 65,
          width: 65,
          decoration: const BoxDecoration(
            color: Color(0xFFF0F0F0), // Lighter gray to show it is inactive
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
          height: 60,
          width: 60,
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            border: Border.all(color: Colors.black12, width: 2),
          ),
          child: const Icon(Icons.photo_library, size: 28, color: Colors.grey),
        ),
        const SizedBox(height: 4),
        const Text(
          "Upload", 
          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: Colors.grey)
        ),
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
            onTap: () => setState(() => selectedMode = mode),
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