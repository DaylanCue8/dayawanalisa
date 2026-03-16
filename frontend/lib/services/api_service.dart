import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';

class ApiService {
  // Ensure this matches your Flask terminal output (192.168.x.x or 127.0.0.1)
  static const String baseUrl = 'http://192.168.254.101:5000';

  Future<String> uploadAndTranslate(XFile imageFile, String mode) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/translate'));
      
      // Read bytes (Works on both Web and Mobile)
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
}


