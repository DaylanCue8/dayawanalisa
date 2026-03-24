import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';

class ApiService {
  // 💡 PRO-TIP: Ensure your Flask app is running on host='0.0.0.0'
  // and your phone is on the same Wi-Fi as 192.168.254.108
  static const String baseUrl = 'http://192.168.254.108:5000';

  /// --- MODE: Baybayin to Tagalog (Detailed for Evaluation Modal) ---
  Future<Map<String, dynamic>?> uploadAndTranslateDetailed(XFile imageFile, String mode) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/translate'));
      
      // 1. Get file extension dynamically
      String extension = imageFile.path.split('.').last.toLowerCase();
      if (extension != 'jpg' && extension != 'jpeg' && extension != 'png') {
        extension = 'jpg'; // Default fallback
      }

      // 2. Read bytes and add to request
      var bytes = await imageFile.readAsBytes();
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: 'upload.$extension',
        contentType: MediaType('image', extension == 'png' ? 'png' : 'jpeg'),
      ));

      // 3. Add mode field
      request.fields['mode'] = mode;

      // 4. Send request with a 30-second timeout
      // (Deeper ML models can take time to process on a local CPU)
      var streamedResponse = await request.send().timeout(const Duration(seconds: 30));
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        print("Server Error: ${response.statusCode} - ${response.body}");
        return null;
      }
    } on SocketException catch (e) {
      print("Network Error (Check IP/Wi-Fi): $e");
      return null;
    } catch (e) {
      print("General Error: $e");
      return null;
    }
  }

  /// --- MODE: Tagalog to Baybayin (Text-based) ---
  Future<String> translateTagalogToBaybayin(String tagalogText) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/translate'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'text': tagalogText,
          'mode': 'Tagalog to Baybayin' 
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['translated_text'] ?? "Translation failed"; 
      } 
      return "Server Error: ${response.statusCode}";
    } catch (e) {
      print("Text Translation Error: $e");
      return "Connection Error. Check Server.";
    }
  }

  /// Original Simple Method (Maintains compatibility with older UI calls)
  Future<String> uploadAndTranslate(XFile imageFile, String mode) async {
    final data = await uploadAndTranslateDetailed(imageFile, mode);
    return data?['translated_text'] ?? "No translation found";
  }
}