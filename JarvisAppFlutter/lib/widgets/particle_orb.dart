import 'dart:math';
import 'package:flutter/material.dart';

class ParticleOrb extends StatefulWidget {
  const ParticleOrb({super.key});

  @override
  State<ParticleOrb> createState() => _ParticleOrbState();
}

class _ParticleOrbState extends State<ParticleOrb> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final List<_Particle> _particles;
  static const int particleCount = 120;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(seconds: 8))
      ..repeat();
    _particles = List.generate(particleCount, (_) => _Particle.random());
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          painter: _OrbPainter(_particles, _controller.value),
          child: Container(),
        );
      },
    );
  }
}

class _Particle {
  final Offset position;
  final double radius;
  final Color color;
  final double speed;

  _Particle(this.position, this.radius, this.color, this.speed);

  factory _Particle.random() {
    final random = Random();
    return _Particle(
      Offset((random.nextDouble() - 0.5) * 400, (random.nextDouble() - 0.5) * 400),
      random.nextDouble() * 3 + 1,
      Color.lerp(Colors.cyanAccent, Colors.blueAccent, random.nextDouble())!,
      random.nextDouble() * 0.8 + 0.2,
    );
  }
}

class _OrbPainter extends CustomPainter {
  final List<_Particle> particles;
  final double progress;

  _OrbPainter(this.particles, this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    for (final particle in particles) {
      final angle = progress * 2 * pi * particle.speed;
      final rotated = Offset(
        particle.position.dx * cos(angle) - particle.position.dy * sin(angle),
        particle.position.dx * sin(angle) + particle.position.dy * cos(angle),
      );
      final drawPos = center + rotated * 0.8;
      final paint = Paint()..color = particle.color.withOpacity(0.7);
      canvas.drawCircle(drawPos, particle.radius, paint);
    }

    final glow = Paint()
      ..shader = RadialGradient(
        colors: [Colors.cyanAccent.withOpacity(0.6), Colors.transparent],
      ).createShader(Rect.fromCircle(center: center, radius: 150));
    canvas.drawCircle(center, 150, glow);
  }

  @override
  bool shouldRepaint(covariant _OrbPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}
