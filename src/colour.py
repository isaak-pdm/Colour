import argparse
import colorsys

from rich.console import Console
from rich import bar
console = Console()


def normalize_hex_code(hex_code):
    if hex_code[0] != "#":
        hex_code = "#" + hex_code
    if len(hex_code) == 4:
        hex_code = "#" + hex_code[1] * 2 + hex_code[2] * 2 + hex_code[3] * 2
    return hex_code


def hex_to_rgb(hex_color):
    hex_color = normalize_hex_code(hex_color)
    return tuple(int(b) / 255 for b in bytes.fromhex(hex_color[1:]))


def rgb_to_hex(rgb_color):
    hex_color = []
    for c in rgb_color:
        color = int(c * 255 + 0.5)
        hex_color.append(hex(color)[2:].zfill(2))
    return '#' + ''.join(hex_color)


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
    hue1 = shift_hue(color, spread / 360)
    hue2 = shift_hue(color, -spread / 360)
    return (color, hue1, hue2)


def generate_monochromatic(color):
    hls_color = colorsys.rgb_to_hls(*color)

    # Calculate lightness range and steps
    lightness_range = 94 - 6
    lightness_steps = 12

    # Generate monochromatic colors
    monochromatic_colors = [
        colorsys.hls_to_rgb(hls_color[0], (6 + lightness_range * i / (lightness_steps - 1)) / 100, hls_color[2])[:3]
        for i in range(lightness_steps)
    ]
    return monochromatic_colors


def closest_color_by_hue(color):
    color_map = {360: "red", 300: "purple", 240: "blue", 180: "teal", 120: "green", 60: "yellow", 30: "orange", 0: "red"}
    h, l, s = colorsys.rgb_to_hls(*color)
    hue = int(h * 360)
    closest_hue = min(color_map.keys(), key=lambda x: abs(x - hue))
    closest_color = color_map[closest_hue]
    if l < 0.3:
        closest_color = "dark " + closest_color
    elif l > 0.7:
        closest_color = "light " + closest_color
    if closest_color == "dark orange":
        closest_color = "brown"
    if closest_color == "dark yellow":
        closest_color = "olive"
    if s < 0.06:
        closest_color = "white" if l > 0.9 else "grey" if l > 0.1 else "black"
    return closest_color


def main():
    parser = argparse.ArgumentParser(
        description='Generate color schemes from a given color.')

    parser.add_argument(
        '-c', '--colors',
        nargs='*',
        help='one or more colors in hexadecimal code format',
        action='store',
        dest='color_str',
        default='')

    parser.add_argument(
        '-t', '--tui',
        help='show a text-based user interface to enter colors',
        action='store_true',
        default=False)

    parser.add_argument(
        '-w', '--web-safe',
        help='use web-safe colors',
        action='store_true',
        default=False)

    args = parser.parse_args()

    if args.color_str:
        color_str = ' '.join(args.color_str)
    else:
        color_str = input("Enter one or more colors in hexadecimal code format separated by spaces: ")

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
                print(f"Closest websafe color is: {shorthand}")

        # RGB percent bar chart
        r, g, b = avg_color
        r_bar = bar.Bar(100, 0, avg_color[0]*100, width=50, color="red", bgcolor="#4a4b4f")
        g_bar = bar.Bar(100, 0, avg_color[1]*100, width=50, color="green", bgcolor="#4a4b4f")
        b_bar = bar.Bar(100, 0, avg_color[2]*100, width=50, color="blue", bgcolor="#4a4b4f")
        print("")
        print("RGB color chart:")
        console.print(r_bar)
        console.print(g_bar)
        console.print(b_bar)
        print("")

        # Generate and print color schemes
        color = avg_color if not args.web_safe else web_safe_color
        color_schemes = [("Complementary Color Scheme:", generate_complementary(color)),
                 ("Analogous Color Scheme:", generate_analogous(color)),
                 ("Monochromatic Color Scheme:", generate_monochromatic(color))]

        for name, colors in color_schemes:
            hex_codes = [rgb_to_hex(c) for c in colors]
            color_display_strings = ["[{}]{}".format(hex_code, hex_code) for hex_code in hex_codes]
            color_scheme_string = ' '.join(color_display_strings)
            if 'Monochromatic' in name:
                console.print(f"{name} {color_scheme_string}")
            else:
                console.print(f"{name} {color_scheme_string}")

        monochromatic_colors = generate_monochromatic(color)
        dm = rgb_to_hex(monochromatic_colors[1])
        lm = rgb_to_hex(monochromatic_colors[-2])
        console.print(f"Dark Mode: [{lm} on {dm}]" + dm)
        console.print(f"Light Mode: [{dm} on {lm}]" + lm)


if __name__ == '__main__':
    main()
