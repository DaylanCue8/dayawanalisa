import 'package:flutter/material.dart';

class InfoModal extends StatelessWidget {
  const InfoModal({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.85,
      ),
      padding: const EdgeInsets.fromLTRB(24, 12, 24, 16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: colorScheme.outlineVariant,
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
            const SizedBox(height: 20),

            Text(
              "About Dayaw",
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: colorScheme.primary,
                  ),
            ),
            const SizedBox(height: 10),
            Text(
              "Dayaw is a research project from Leyte Normal University (LNU) dedicated to "
              "preserving the ancient Filipino script through AI-assisted recognition.",
              style: TextStyle(
                fontSize: 15,
                color: colorScheme.onSurface,
                height: 1.5,
              ),
            ),

            Divider(height: 40, color: colorScheme.outlineVariant),

            Text(
              "How to Write for the AI",
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: colorScheme.primary,
                  ),
            ),
            const SizedBox(height: 10),
            Text(
              "For the SVM + HOG model to recognize your handwriting accurately, "
              "please follow these visual guidelines:",
              style: TextStyle(
                fontSize: 14,
                color: colorScheme.onSurfaceVariant,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 15),

            // Supported Characters Section
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(16),
              ),
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Text(
                    "Supported Characters",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: colorScheme.onPrimaryContainer,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    alignment: WrapAlignment.center,
                    children: _buildCharacterChips(colorScheme),
                  ),
                  Divider(
                    height: 30,
                    color: colorScheme.onPrimaryContainer.withAlpha(60),
                  ),
                  Text(
                    "Vowel Markers (Kudlit)",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: colorScheme.onPrimaryContainer,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    "Dot Above: E/I  •  Dot Below: O/U  •  Cross: No Vowel",
                    style: TextStyle(
                      fontSize: 12,
                      color: colorScheme.onPrimaryContainer,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),
            Text(
              "Best Practices:",
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            BulletPoint(
              text: "Use black ink on plain white paper.",
              colorScheme: colorScheme,
            ),
            BulletPoint(
              text: "Keep characters separated (no touching).",
              colorScheme: colorScheme,
            ),
            BulletPoint(
              text: "Ensure dots/kudlits are clear and precise.",
              colorScheme: colorScheme,
            ),
            BulletPoint(
              text: "Avoid shadows or glare in your photos.",
              colorScheme: colorScheme,
            ),

            const SizedBox(height: 30),

            // Action button
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () => Navigator.pop(context),
                child: const Text("Ipagpatuloy"),
              ),
            ),

            const SizedBox(height: 20),
            Center(
              child: Text(
                "DAYAW – Capstone Project © 2026",
                style: TextStyle(
                  fontSize: 11,
                  color: colorScheme.onSurfaceVariant.withAlpha(140),
                  letterSpacing: 1.2,
                ),
              ),
            ),
            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildCharacterChips(ColorScheme colorScheme) {
    const chars = [
      'ᜀ', 'ᜊ', 'ᜃ', 'ᜇ', 'ᜄ', 'ᜑ', 'ᜎ', 'ᜌ', 'ᜈ', 'ᜅ', 'ᜉ', 'ᜐ', 'ᜆ', 'ᜏ', 'ᜌ',
    ];
    return chars
        .map(
          (c) => Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: colorScheme.surface,
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: colorScheme.shadow.withAlpha(20),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Text(
              c,
              style: TextStyle(fontSize: 22, color: colorScheme.primary),
            ),
          ),
        )
        .toList();
  }
}

class BulletPoint extends StatelessWidget {
  final String text;
  final ColorScheme colorScheme;

  const BulletPoint({
    super.key,
    required this.text,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "• ",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: colorScheme.primary,
              fontSize: 18,
            ),
          ),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 14,
                height: 1.4,
                color: colorScheme.onSurface,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
