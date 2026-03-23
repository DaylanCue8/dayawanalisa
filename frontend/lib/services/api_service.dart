import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';

class ApiService {
  // Ensure this matches your computer's IPv4 address
  static const String baseUrl = 'http://192.168.254.107:5000';

  /// --- MODE: Baybayin to Tagalog (DETAILED for Evaluation Modal) ---
  /// Returns the full Map with 'translated_text', 'confidence', 'status', 
  /// and 'individual_detections' list.
  Future<Map<String, dynamic>?> uploadAndTranslateDetailed(XFile imageFile, String mode) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/translate'));
      
      var bytes = await imageFile.readAsBytes();
      
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: 'upload.jpg',
        contentType: MediaType('image', 'jpeg'),
      ));

      request.fields['mode'] = mode;

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        // Decodes the full JSON response for use in the Evaluation Modal
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        return null;
      }
    } catch (e) {
      print("Connection Error: $e");
      return null;
    }
  }

  /// --- MODE: Tagalog to Baybayin (Linguistic Rule-Based) ---
  Future<String> translateTagalogToBaybayin(String tagalogText) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/translate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'text': tagalogText,
          'mode': 'Tagalog to Baybayin' 
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['translated_text'] ?? "Translation failed"; 
      } 
      return "Server Error: ${response.statusCode}";
    } catch (e) {
      return "Connection Error: $e";
    }
  }

  /// Original Simple Method (Keep for compatibility)
  Future<String> uploadAndTranslate(XFile imageFile, String mode) async {
    final data = await uploadAndTranslateDetailed(imageFile, mode);
    return data?['translated_text'] ?? "No translation found";
  }
}