import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';

class ApiService {
  // Use your static IP for physical device testing
  static const String baseUrl = 'http://192.168.254.101:5000';

  // --- MODE: Baybayin to Tagalog (SVM + HOG + Image) ---
  Future<String> uploadAndTranslate(XFile imageFile, String mode) async {
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
        final data = jsonDecode(response.body);
        return data['translated_text'] ?? "No translation found";
      } else {
        return "Server Error: ${response.statusCode}";
      }
    } catch (e) {
      return "Connection Error: $e";
    }
  }

  // --- MODE: Tagalog to Baybayin (Linguistic Rule-Based) ---
  // This sends JSON text instead of a file
  Future<String> translateTagalogToBaybayin(String tagalogText) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/api/translate'), // Changed from /api/ttb
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': tagalogText,
        'mode': 'Tagalog to Baybayin' // Tell Flask which logic to use
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Ensure this matches the key 'translated_text' in your Flask response
      return data['translated_text'] ?? "Translation failed"; 
    } 
    return "Server Error: ${response.statusCode}";
  } catch (e) {
    return "Connection Error: $e";
  }
}
}