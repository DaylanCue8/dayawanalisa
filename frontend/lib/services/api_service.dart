import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  // Store your base URL here so you only have to change it in one place!
  static const String baseUrl = 'http://192.168.254.113:5000';

  Future<String> fetchGreeting() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/greet'));

      if (response.statusCode == 200) {
        Map<String, dynamic> data = jsonDecode(response.body);
        return data['message'];
      } else {
        return "Server Error: ${response.statusCode}";
      }
    } catch (e) {
      return "Connection failed: $e";
    }
  }
}