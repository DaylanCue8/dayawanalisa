import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';

class ApiService {
  static const String baseUrl = 'http://192.168.254.115:5000';

  /// --- UNIVERSAL TRANSLATION METHOD ---
  /// Handles both Baybayin to Tagalog (Image) and Tagalog to Baybayin (Text)
  Future<Map<String, dynamic>?> uploadAndTranslateDetailed(
    XFile? imageFile, 
    String mode, 
    {String? text} // Optional named parameter for TTB mode
  ) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/translate'));
      
      // 1. Add the Mode
      request.fields['mode'] = mode;

      // 2. Handle TAGALOG TO BAYBAYIN (Text Path)
      if (mode == 'Tagalog to Baybayin' && text != null) {
        request.fields['text'] = text;
      } 
      
      // 3. Handle BAYBAYIN TO TAGALOG (Image Path)
      else if (imageFile != null) {
        String extension = imageFile.path.split('.').last.toLowerCase();
        if (extension != 'jpg' && extension != 'jpeg' && extension != 'png') {
          extension = 'jpg';
        }

        var bytes = await imageFile.readAsBytes();
        request.files.add(http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: 'upload.$extension',
          contentType: MediaType('image', extension == 'png' ? 'png' : 'jpeg'),
        ));
      }

      // 4. Send and Timeout
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

  /// --- HELPER: Legacy Text-only caller ---
  Future<String> translateTagalogToBaybayin(String tagalogText) async {
    final data = await uploadAndTranslateDetailed(null, 'Tagalog to Baybayin', text: tagalogText);
    return data?['translated_text'] ?? "Translation failed";
  }

  /// --- HELPER: Legacy Image-only caller ---
  Future<String> uploadAndTranslate(XFile imageFile, String mode) async {
    final data = await uploadAndTranslateDetailed(imageFile, mode);
    return data?['translated_text'] ?? "No translation found";
  }
}