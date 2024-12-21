import argparse
from PIL import Image

import base64
from io import BytesIO

def add_gcode_thumbnail(image, gcode):
    """
    Add a G-code thumbnail to the G-code file for Klipper.

    Args:
        image (PIL.Image.Image): Image to generate the thumbnail.
        gcode (list): G-code lines to append the thumbnail comment to.
    """
    thumbnail = image.copy()

    # Save thumbnail to an in-memory buffer
    buffer = BytesIO()
    thumbnail.save(buffer, format="PNG")
    buffer.seek(0)

    # Encode the image in Base64
    encoded_thumbnail = base64.b64encode(buffer.getvalue()).decode('ascii')
    thumbnail_comment = f"; thumbnail begin {thumbnail.size[0]}, {thumbnail.size[1]}\n"
    thumbnail_comment += f"; {encoded_thumbnail}\n"
    thumbnail_comment += f"; thumbnail end"

    # Insert the thumbnail comment at the top of the G-code
    gcode.insert(0, thumbnail_comment)
    
def png_to_gcode(input_file, output_file, laser_max_power=255, feed_rate=1500, fast_return_rate=3000, lines_per_mm=10):
    """
    Convert a PNG file to G-code for laser engraving with unidirectional engraving.

    Args:
        input_file (str): Path to the input PNG file.
        output_file (str): Path to the output G-code file.
        laser_max_power (int): Maximum laser power (e.g., 255 for 8-bit grayscale).
        feed_rate (int): Feed rate for engraving in mm/min.
        fast_return_rate (int): Feed rate for fast return in mm/min.
        lines_per_mm (int): Number of engraving lines per millimeter.
    """
    # Open the image and convert to grayscale
    image = Image.open(input_file).convert("L")
    dpi = image.info.get("dpi", (300, 300))[0]  # Default to 300 DPI if not present
    print(f"Input image DPI: {dpi}")

    # Calculate effective resolution
    pixel_size_mm = 1 / lines_per_mm
    width_mm = image.size[0] / dpi * 25.4  # Width in mm
    height_mm = image.size[1] / dpi * 25.4  # Height in mm
    new_width = int(width_mm * lines_per_mm)
    new_height = int(height_mm * lines_per_mm)

    # Resize image
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    pixels = image.load()

    # Save image as BMP for Klipper display
    bmp_path = output_file.replace(".gcode", ".bmp")
    image.save(bmp_path, format="BMP")

    # Initialize G-code
    gcode = [
        "G21 ; Set units to mm",
        "G90 ; Absolute positioning",
        "M5 ; Laser off",
        f"G1 F{feed_rate} ; Set feed rate for engraving",
    ]
    
    add_gcode_thumbnail(image, gcode)

    total_gcode_lines = 0  # Counter for statistics

    # Process the image row by row
    for y in range(new_height):
        # Check if the entire row is empty (no laser power required)
        if all(pixels[x, -y] == 255 for x in range(new_width)):
            continue  # Skip empty rows

        gcode.append(f"; Row {y}")
        x_start = None
        current_power = None

        for x in range(new_width):
            power = int((1 - pixels[x, -y] / 255) * laser_max_power)

            if power != current_power:
                if current_power is not None:
                    # Finish the previous segment
                    x_end = x - 1
                    gcode.append(f"G1 X{round(x_end * pixel_size_mm, 3)} Y{round(y * pixel_size_mm, 3)} S{current_power}")
                # Start a new segment
                x_start = x
                current_power = power

        # Finish the last segment in the row
        if current_power is not None:
            x_end = new_width - 1
            gcode.append(f"G1 X{round(x_end * pixel_size_mm, 3)} Y{round(y * pixel_size_mm, 3)} S{current_power}")

        # Add fast return
        gcode.append("M5 ; Laser off")  # Laser off at the end of the row
        gcode.append(f"G1 X0 Y{round((y + 1) * pixel_size_mm, 3)} F{fast_return_rate} ; Fast return")
        gcode.append(f"G1 F{feed_rate}")

        total_gcode_lines += 1

    # Finalize G-code
    gcode.append("G0 X0 Y0 ; Return to origin")
    gcode.append("M5 ; Ensure laser is off")
    gcode.append("M30 ; End of program")

    # Write to file
    with open(output_file, "w") as f:
        f.write("\n".join(gcode))

    # Print statistics
    print(f"G-code saved to {output_file}")
    print(f"Image dimensions: {width_mm:.2f} mm x {height_mm:.2f} mm")
    print(f"Total G-code lines: {total_gcode_lines}")

def main():
    parser = argparse.ArgumentParser(description="Convert PNG to G-code for laser engraving.")
    parser.add_argument("input_file", help="Path to the input PNG file.")
    parser.add_argument("output_file", help="Path to save the output G-code file.")
    parser.add_argument(
        "-p", "--power", type=int, default=255, help="Maximum laser power (default: 255)"
    )
    parser.add_argument(
        "-f", "--feedrate", type=int, default=1500, help="Feed rate for engraving in mm/min (default: 1200)"
    )
    parser.add_argument(
        "-r", "--fast_return_rate", type=int, default=3000, help="Feed rate for fast return in mm/min (default: 3000)"
    )
    parser.add_argument(
        "-l", "--lines_per_mm", type=int, default=10, help="Lines per millimeter (default: 10)"
    )
    args = parser.parse_args()

    # Call the conversion function with parsed arguments
    png_to_gcode(
        input_file=args.input_file,
        output_file=args.output_file,
        laser_max_power=args.power,
        feed_rate=args.feedrate,
        fast_return_rate=args.fast_return_rate,
        lines_per_mm=args.lines_per_mm,
    )

if __name__ == "__main__":
    main()

