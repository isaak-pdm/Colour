import argparse
import colorsys
import sys

from rich.console import Console
console = Console()

def normalize_hex_code(hex_code):
    if hex_code[0] != "#":
        hex_code = "#" + hex_code
    if len(hex_code) == 4:
        hex_code = "#" + hex_code[1] * 2 + hex_code[2] * 2 + hex_code[3] * 2
    return hex_code

def hex_to_rgb(hex_color):
    # Normalize the hexadecimal code
    if hex_color[0] != '#':
        hex_color = '#' + hex_color
    if len(hex_color) == 4:
        hex_color = '#' + hex_color[1] * 2 + hex_color[2] * 2 + hex_color[3] * 2
    
    # Convert the hexadecimal code to RGB
    return tuple(int(b) / 255 for b in bytes.fromhex(hex_color[1:]))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*(int(c * 255 + 0.5) for c in rgb_color))

def get_nearest_web_safe_color(color):
    r, g, b = color
    r = round(r * 255 / 51) * 51
    g = round(g * 255 / 51) * 51
    b = round(b * 255 / 51) * 51
    return (r / 255, g / 255, b / 255)

def convert_web_safe_to_shorthand(color):
    # Strip the leading '#' character from the color string
    color = color[1:]

    if color[0] == color[1] and color[2] == color[3] and color[4] == color[5]:
        return f"#{color[0]}{color[2]}{color[4]}"
    else:
        return f"#{color}"

def shift_hue(rgb_color, amount):
    h, l, s = colorsys.rgb_to_hls(*rgb_color)
    h = (h + amount) % 1.0
    return colorsys.hls_to_rgb(h, l, s)

def generate_complementary(color):
    return (color, shift_hue(color, 0.5))

def generate_analogous(color, spread=30):
    return (color, shift_hue(color, spread / 360), shift_hue(color, -spread / 360))

def generate_monochromatic(color):
    hls_color = colorsys.rgb_to_hls(*color)
    lightness_range = 94 - 6
    lightness_steps = 12
    lightness_steps = [6 + lightness_range * i / (lightness_steps - 1) for i in range(lightness_steps)]
    monochromatic_colors = tuple(colorsys.hls_to_rgb(hls_color[0], lightness / 100, hls_color[2])[:3] for lightness in lightness_steps)
    return monochromatic_colors

def closest_color_by_hue(color):
    colors = ["red", "purple", "blue", "teal", "green", "yellow", "red"]
    hues = [360, 300, 240, 180, 120, 60, 0]

    h, l, _ = colorsys.rgb_to_hls(*color)
    hue = int(h * 360)
    hue_differences = [abs(hue - h) for h in hues]
    min_hue_difference = min(hue_differences)
    closest_color_index = hue_differences.index(min_hue_difference)
    closest_color = colors[closest_color_index]
    if l < 0.3:
        closest_color = "dark " + closest_color
    elif l > 0.7:
        closest_color = "light " + closest_color
    return closest_color

def main():
    parser = argparse.ArgumentParser(description='Generate color schemes from a given color.')
    parser.add_argument('-c', '--colors', nargs='*', help='one or more colors in hexadecimal code format', action='store', dest='color_str', default='')
    parser.add_argument('-t', '--tui', action='store_true', help='show a text-based user interface to enter colors', default=False)
    parser.add_argument('-w', '--web-safe', action='store_true', help='use web-safe colors', default=False)
    args = parser.parse_args()

    color_str = ' '.join(args.color_str) if args.color_str else input("Enter one or more colors in hexadecimal code format separated by spaces: ")
    
    colors = [hex_to_rgb(c) for c in color_str.split()]
    
    num_colors = len(colors)
    if num_colors == 0:
        print("No colors were entered.")
    else:
        avg_color = tuple(sum(c) / num_colors for c in zip(*colors))
        color_hex = rgb_to_hex(avg_color)
        console.print(f"The input is: [{color_hex}]{color_hex} ({closest_color_by_hue(avg_color)})")
        if args.web_safe:
            web_safe_color = get_nearest_web_safe_color(avg_color)
            web_safe_color_hex = rgb_to_hex(web_safe_color)
            shorthand = convert_web_safe_to_shorthand(web_safe_color_hex)
            if web_safe_color == avg_color:
                print(f"{shorthand} is a websafe color.")
            else:
                console.print(f"Closest websafe color is: [{web_safe_color_hex}]{shorthand}")

    # Generate and print color schemes
    color = avg_color if not args.web_safe else web_safe_color
    print("Complementary Color Scheme:", ' '.join(rgb_to_hex(c) for c in generate_complementary(color)))
    print("Analogous Color Scheme:", ' '.join(rgb_to_hex(c) for c in generate_analogous(color)))
    print(f"Monochromatic Color Scheme: {' '.join(rgb_to_hex(c) for c in generate_monochromatic(color))}")

if __name__ == '__main__':
    main()
