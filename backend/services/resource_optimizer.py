"""Resource optimization utilities for memory and bandwidth efficiency."""
import io
import gzip
import brotli
from typing import Optional, bytes
from PIL import Image
import base64


class ResourceOptimizer:
    """Optimizes resources for memory and bandwidth efficiency."""
    
    @staticmethod
    def compress_image(
        image_data: bytes,
        max_size: tuple = (1920, 1080),
        quality: int = 85,
        format: str = "JPEG"
    ) -> bytes:
        """
        Compress image to reduce memory usage.
        
        Args:
            image_data: Original image bytes
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)
            format: Output format (JPEG, PNG, WEBP)
        
        Returns:
            Compressed image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Resize if needed
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed (for JPEG)
            if format == "JPEG" and image.mode != "RGB":
                image = image.convert("RGB")
            
            # Compress
            output = io.BytesIO()
            if format == "WEBP":
                image.save(output, format="WEBP", quality=quality, method=6)
            elif format == "PNG":
                image.save(output, format="PNG", optimize=True, compress_level=9)
            else:  # JPEG
                image.save(output, format="JPEG", quality=quality, optimize=True)
            
            return output.getvalue()
        except Exception:
            return image_data  # Return original on error
    
    @staticmethod
    def compress_text(
        text: str,
        algorithm: str = "gzip"
    ) -> bytes:
        """
        Compress text data.
        
        Args:
            text: Text to compress
            algorithm: Compression algorithm (gzip, brotli)
        
        Returns:
            Compressed bytes
        """
        text_bytes = text.encode("utf-8")
        
        if algorithm == "brotli":
            try:
                return brotli.compress(text_bytes, quality=6)
            except Exception:
                return gzip.compress(text_bytes)
        else:  # gzip
            return gzip.compress(text_bytes)
    
    @staticmethod
    def decompress_text(
        compressed_data: bytes,
        algorithm: str = "gzip"
    ) -> str:
        """
        Decompress text data.
        
        Args:
            compressed_data: Compressed bytes
            algorithm: Compression algorithm (gzip, brotli)
        
        Returns:
            Decompressed text
        """
        try:
            if algorithm == "brotli":
                try:
                    return brotli.decompress(compressed_data).decode("utf-8")
                except Exception:
                    return gzip.decompress(compressed_data).decode("utf-8")
            else:  # gzip
                return gzip.decompress(compressed_data).decode("utf-8")
        except Exception:
            return ""
    
    @staticmethod
    def optimize_screenshot(
        screenshot_data: bytes,
        target_size_kb: int = 200
    ) -> bytes:
        """
        Optimize screenshot for WebSocket streaming.
        
        Args:
            screenshot_data: Original screenshot bytes
            target_size_kb: Target size in KB
        
        Returns:
            Optimized screenshot bytes
        """
        # Try different quality levels to meet target size
        for quality in [85, 70, 60, 50, 40]:
            compressed = ResourceOptimizer.compress_image(
                screenshot_data,
                max_size=(1920, 1080),
                quality=quality,
                format="JPEG"
            )
            
            size_kb = len(compressed) / 1024
            if size_kb <= target_size_kb:
                return compressed
        
        # If still too large, resize more aggressively
        compressed = ResourceOptimizer.compress_image(
            screenshot_data,
            max_size=(1280, 720),
            quality=60,
            format="JPEG"
        )
        
        return compressed
    
    @staticmethod
    def encode_base64(data: bytes) -> str:
        """Encode bytes to base64 string."""
        return base64.b64encode(data).decode("utf-8")
    
    @staticmethod
    def decode_base64(encoded: str) -> bytes:
        """Decode base64 string to bytes."""
        return base64.b64decode(encoded)


# Global instance
_resource_optimizer = ResourceOptimizer()

def get_resource_optimizer() -> ResourceOptimizer:
    """Get global resource optimizer instance."""
    return _resource_optimizer

