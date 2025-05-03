from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image():
    # Erstelle ein 300x450 Bild mit grauem Hintergrund
    img = Image.new("RGB", (300, 450), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Zeichne einen Rahmen
    draw.rectangle([(10, 10), (290, 440)], outline=(200, 200, 200), width=2)
    
    # Füge Text hinzu
    text = "Kein Bild\nverfügbar"
    
    # Versuche, eine Schriftart zu laden, oder verwende default
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
    
    # Berechne Textposition für Zentrierung
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    text_x = (300 - text_width) // 2
    text_y = (450 - text_height) // 2
    
    # Zeichne den Text
    draw.text((text_x, text_y), text, fill=(120, 120, 120), font=font, align="center")
    
    # Speichere das Bild
    output_dir = "static"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "placeholder.jpg")
    img.save(output_path, "JPEG", quality=90)
    print(f"Platzhalter-Bild erstellt: {output_path}")

if __name__ == "__main__":
    create_placeholder_image()

