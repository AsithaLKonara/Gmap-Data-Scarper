import { useEffect, useRef } from 'react';

interface EarthBackgroundProps {
  className?: string;
}

export default function EarthBackground({ className = '' }: EarthBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Earth rotation angle
    let rotation = 0;
    const rotationSpeed = 0.003;

    // Create base gradient for space background
    const createSpaceGradient = () => {
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, 'rgba(15, 23, 42, 0.8)'); // Dark blue
      gradient.addColorStop(0.5, 'rgba(30, 41, 59, 0.7)'); // Darker blue
      gradient.addColorStop(1, 'rgba(15, 23, 42, 0.8)'); // Dark blue
      return gradient;
    };

    // Create earth sphere with lighting
    const createEarthGradient = (centerX: number, centerY: number, radius: number) => {
      // Base ocean color
      const oceanGradient = ctx.createRadialGradient(
        centerX - radius * 0.4,
        centerY - radius * 0.4,
        radius * 0.2,
        centerX,
        centerY,
        radius
      );
      oceanGradient.addColorStop(0, 'rgba(59, 130, 246, 0.7)'); // Bright blue (light)
      oceanGradient.addColorStop(0.4, 'rgba(37, 99, 235, 0.6)'); // Ocean blue
      oceanGradient.addColorStop(0.7, 'rgba(29, 78, 216, 0.5)'); // Deep blue
      oceanGradient.addColorStop(1, 'rgba(30, 64, 175, 0.4)'); // Dark blue (shadow)
      return oceanGradient;
    };

    // Draw stars
    const drawStars = () => {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      for (let i = 0; i < 100; i++) {
        const x = (i * 137.5) % canvas.width;
        const y = (i * 237.5) % canvas.height;
        const size = Math.random() * 1.5;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    // Draw continents with better shape
    const drawContinents = (centerX: number, centerY: number, radius: number, angle: number) => {
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(angle);

      // Draw continents with green color
      ctx.fillStyle = 'rgba(34, 197, 94, 0.5)';
      
      // North America
      ctx.beginPath();
      ctx.ellipse(-radius * 0.35, -radius * 0.15, radius * 0.18, radius * 0.25, -0.3, 0, Math.PI * 2);
      ctx.fill();
      
      // Europe
      ctx.beginPath();
      ctx.ellipse(radius * 0.05, -radius * 0.1, radius * 0.12, radius * 0.18, 0.2, 0, Math.PI * 2);
      ctx.fill();
      
      // Africa
      ctx.beginPath();
      ctx.ellipse(radius * 0.15, radius * 0.15, radius * 0.1, radius * 0.25, 0.1, 0, Math.PI * 2);
      ctx.fill();
      
      // Asia
      ctx.beginPath();
      ctx.ellipse(radius * 0.35, -radius * 0.05, radius * 0.22, radius * 0.2, -0.2, 0, Math.PI * 2);
      ctx.fill();
      
      // Australia
      ctx.beginPath();
      ctx.ellipse(radius * 0.4, radius * 0.35, radius * 0.08, radius * 0.06, 0, 0, Math.PI * 2);
      ctx.fill();
      
      // South America
      ctx.beginPath();
      ctx.ellipse(-radius * 0.25, radius * 0.35, radius * 0.08, radius * 0.2, -0.1, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
    };

    // Draw atmospheric glow
    const drawAtmosphere = (centerX: number, centerY: number, radius: number) => {
      const atmosphereGradient = ctx.createRadialGradient(
        centerX,
        centerY,
        radius,
        centerX,
        centerY,
        radius * 1.15
      );
      atmosphereGradient.addColorStop(0, 'rgba(59, 130, 246, 0.1)');
      atmosphereGradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.05)');
      atmosphereGradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
      
      ctx.fillStyle = atmosphereGradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius * 1.15, 0, Math.PI * 2);
      ctx.fill();
    };

    // Animation loop
    const animate = () => {
      // Clear canvas
      ctx.fillStyle = createSpaceGradient();
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw stars
      drawStars();

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const radius = Math.min(canvas.width, canvas.height) * 0.35;

      // Draw earth sphere
      ctx.save();
      const earthGradient = createEarthGradient(centerX, centerY, radius);
      ctx.fillStyle = earthGradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.fill();

      // Draw continents
      drawContinents(centerX, centerY, radius, rotation);

      // Draw edge highlight
      ctx.strokeStyle = 'rgba(147, 197, 253, 0.3)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Draw atmosphere
      drawAtmosphere(centerX, centerY, radius);

      // Draw glow effect
      ctx.shadowBlur = 80;
      ctx.shadowColor = 'rgba(59, 130, 246, 0.4)';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.2)';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.shadowBlur = 0;

      ctx.restore();

      // Update rotation
      rotation += rotationSpeed;
      if (rotation > Math.PI * 2) {
        rotation = 0;
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={`fixed inset-0 w-full h-full object-cover pointer-events-none ${className}`}
      style={{ zIndex: 0 }}
    />
  );
}

