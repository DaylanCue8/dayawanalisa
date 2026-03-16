import 'dart:typed_data'; // For web image bytes
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

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
  Uint8List? _webImage; // To store the preview image bytes

  final List<String> translationModes = ['Baybayin to Tagalog', 'Tagalog to Baybayin', 'Sanayin'];

  Future<void> _captureAndTranslate() async {
    final XFile? photo = await _picker.pickImage(source: ImageSource.camera);

    if (photo != null) {
      // Get bytes for the preview
      final bytes = await photo.readAsBytes();
      
      setState(() {
        _isLoading = true;
        _webImage = bytes; // Show the photo in the gray box
        _translatedResult = "Processing...";
      });

      // FIX: Pass 'photo' (XFile) directly to the service
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
            const SizedBox(height: 20),
            const Center(child: Text('dayaw', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.brown))),
            const SizedBox(height: 20),
            
            // Main Gray Analysis Area
            Expanded(
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 20),
                decoration: BoxDecoration(
                  color: const Color(0xFFE0E0E0),
                  borderRadius: BorderRadius.circular(15),
                ),
                clipBehavior: Clip.antiAlias, // Clips the image to the corners
                child: Stack(
                  children: [
                    // Show captured image if it exists
                    if (_webImage != null)
                      Positioned.fill(child: Image.memory(_webImage!, fit: BoxFit.cover)),
                    
                    // Semi-transparent overlay for text
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
            GestureDetector(onTap: _captureAndTranslate, child: _buildCameraWidget()),
            const SizedBox(height: 30),
            _buildModeSelector(),
          ],
        ),
      ),
    );
  }

  // ... (Keep your _buildCameraWidget and _buildModeSelector as they were)
  Widget _buildCameraWidget() {
    return Container(
      height: 80, width: 80,
      decoration: BoxDecoration(color: Colors.white, shape: BoxShape.circle, border: Border.all(color: Colors.black12, width: 2)),
      child: Center(child: Container(height: 60, width: 60, decoration: const BoxDecoration(color: Color(0xFFD3D3D3), shape: BoxShape.circle))),
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
              decoration: isSelected ? const BoxDecoration(border: Border(bottom: BorderSide(width: 2))) : null,
              child: Text(mode, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal)),
            ),
          );
        }).toList(),
      ),
    );
  }
}