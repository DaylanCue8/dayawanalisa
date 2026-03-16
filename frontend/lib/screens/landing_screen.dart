import 'package:flutter/material.dart';

class DayawLandingScreen extends StatefulWidget {
  const DayawLandingScreen({super.key});

  @override
  State<DayawLandingScreen> createState() => _DayawLandingScreenState();
}

class _DayawLandingScreenState extends State<DayawLandingScreen> {
  String selectedMode = 'Baybayin to Tagalog';
  final List<String> translationModes = [
    'Baybayin to Tagalog',
    'Tagalog to Baybayin',
    'Sanayin'
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                const SizedBox(height: 20),
                // Logo
                Center(
                  child: Text(
                    'dayaw',
                    style: TextStyle(
                      fontFamily: 'serif',
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.brown,
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                // Analysis Area
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 20),
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: const Color(0xFFE0E0E0),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    padding: const EdgeInsets.all(20),
                    child: Center(
                      child: Text(
                        "(Assume that user captures Baybayin text)",
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.black.withOpacity(0.6),
                          fontSize: 16,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 30),
                // Camera Button
                _buildCameraButton(),
                const SizedBox(height: 30),
                // Bottom Mode Selector
                _buildModeSelector(),
              ],
            ),
            // Use Keyboard Button
            Positioned(
              right: 20,
              bottom: 160,
              child: ElevatedButton(
                onPressed: () => print("Keyboard Pressed"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF2F2F2),
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: const Text("Use Keyboard"),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCameraButton() {
    return Container(
      height: 80, width: 80,
      decoration: BoxDecoration(
        color: Colors.white,
        shape: BoxShape.circle,
        border: Border.all(color: Colors.black.withOpacity(0.2), width: 2),
      ),
      child: Center(
        child: Container(
          height: 60, width: 60,
          decoration: BoxDecoration(color: const Color(0xFFD3D3D3), shape: BoxShape.circle),
        ),
      ),
    );
  }

  Widget _buildModeSelector() {
    return Container(
      color: const Color(0xFFF9F9F9),
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: translationModes.map((mode) {
          final isSelected = mode == selectedMode;
          return GestureDetector(
            onTap: () => setState(() => selectedMode = mode),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
              decoration: isSelected
                  ? const BoxDecoration(border: Border(bottom: BorderSide(color: Colors.black, width: 2)))
                  : null,
              child: Text(
                mode,
                style: TextStyle(
                  color: isSelected ? Colors.black : Colors.black.withOpacity(0.5),
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