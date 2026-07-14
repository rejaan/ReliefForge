from src.engine.processors.image_processing import ImageProcessor

print("Starte Test...")

height_map = ImageProcessor.load(
    "/Users/ray/Desktop/testbild.png"
)

print("Bild geladen!")
print("Breite:", height_map.width)
print("Höhe:", height_map.height)