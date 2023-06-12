import argparse
import colorsys
from rich.console import Console
from rich import bar

console = Console()

def normalize_hex_code(hex_code):
    return "#" + hex_code.lstrip("#")

def hex_to_rgb(hex_color):
    hex_color = normalize_hex_code(hex_color)
    if len(hex_color) == 4: # it's in shorthand form
        hex_color = '#' + ''.join([2*c for c in hex_color[1:]]) # expand it
    return tuple(int(b) / 255 for b in bytes.fromhex(hex_color[1:]))

def rgb_to_hex(rgb_color):
    return '#' + ''.join(hex(int(c * 255 + 0.5))[2:].zfill(2) for c in rgb_color)

def get_nearest_web_safe_color(color):
    return tuple(round(c * 255 / 51) * 51 / 255 for c in color)

def convert_web_safe_to_shorthand(color):
    return f"#{color[1::2]}" if color[1::2] == color[2::2] else color

def shift_hue(rgb_color, amount):
    h, l, s = colorsys.rgb_to_hls(*rgb_color)
    return colorsys.hls_to_rgb((h + amount) % 1.0, l, s)

def generate_complementary(color):
    return color, shift_hue(color, 0.5)

def generate_analogous(color, spread=30):
    return color, shift_hue(color, spread / 360), shift_hue(color, -spread / 360)

def generate_monochromatic(color):
    hls_color = colorsys.rgb_to_hls(*color)
    lightness_range = 94 - 6
    lightness_steps = 12
    return [colorsys.hls_to_rgb(hls_color[0], (6 + lightness_range * i / (lightness_steps - 1)) / 100, hls_color[2])[:3] for i in range(lightness_steps)]

def closest_color_by_hue(color):
    color_map = {360: "red", 300: "purple", 240: "blue", 180: "teal", 120: "green", 60: "yellow", 30: "orange", 0: "red"}
    h, l, s = colorsys.rgb_to_hls(*color)
    hue = int(h * 360)
    closest_hue = min(color_map.keys(), key=lambda x: abs(x - hue))
    closest_color = color_map[closest_hue]
    if closest_hue in [360, 0] and l < 0.5: closest_color = "black"
    elif closest_hue in [360, 0] and l > 0.5: closest_color = "white"
    return closest_color

def main():
    parser = argparse.ArgumentParser(description="This script will take a list of colors and compute an average of these colors.")
    parser.add_argument("color_str", metavar="color", type=str, nargs='*', help="Colors to average, in hexadecimal format. Can also be entered interactively.")
    parser.add_argument("-w", "--web-safe", action="store_true", help="Snap to web-safe colors.")
    args = parser.parse_args()
    color_str = ' '.join(args.color_str)

    colors = [hex_to_rgb(color) for color in (color_str if color_str else input("Enter colors (hex codes separated by spaces): ")).split()]

    if not colors:
        return print("No colors were entered.")

    num_colors = len(colors)
    avg_color = tuple(sum(c) / num_colors for c in zip(*colors))
    color_hex = rgb_to_hex(avg_color)
    console.print(f"The input is: [{color_hex}]{color_hex}", end="")
    console.print(f" ({closest_color_by_hue(avg_color)})")

    if args.web_safe:
        web_safe_color = get_nearest_web_safe_color(avg_color)
        web_safe_color_hex = rgb_to_hex(web_safe_color)
        shorthand = convert_web_safe_to_shorthand(web_safe_color_hex)
        console.print(f"{shorthand} is a websafe color." if web_safe_color == avg_color else f"Closest websafe color is: {shorthand}")

    r, g, b = avg_color
    r_bar = bar.Bar(100, 0, avg_color[0]*100, width=50, color="red", bgcolor="#4a4b4f")
    g_bar = bar.Bar(100, 0, avg_color[1]*100, width=50, color="green", bgcolor="#4a4b4f")
    b_bar = bar.Bar(100, 0, avg_color[2]*100, width=50, color="blue", bgcolor="#4a4b4f")
    console.print("\nRGB color chart:")
    console.print(r_bar)
    console.print(g_bar)
    console.print(b_bar)
    console.print("\n")

    color = avg_color if not args.web_safe else web_safe_color
    color_schemes = [
        ("Complementary Color Scheme:", generate_complementary(color)),
        ("Analogous Color Scheme:", generate_analogous(color)),
        ("Monochromatic Color Scheme:", generate_monochromatic(color))
    ]

    for name, colors in color_schemes:
        hex_codes = [rgb_to_hex(c) for c in colors]
        color_display_strings = ["[{}]{}".format(hex_code, hex_code) for hex_code in hex_codes]
        console.print(f"{name} {' '.join(color_display_strings)}")

    monochromatic_colors = generate_monochromatic(color)
    dm = rgb_to_hex(monochromatic_colors[1])
    lm = rgb_to_hex(monochromatic_colors[-2])
    console.print(f"Dark Mode: [{lm} on {dm}]{dm}")
    console.print(f"Light Mode: [{dm} on {lm}]{lm}")

if __name__ == '__main__':
    main()
