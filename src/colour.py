import argparse
import colorsys
import sys

def hex_to_rgb(hex_color):
    return tuple(int(b) / 255 for b in bytes.fromhex(hex_color[1:]))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*(int(c * 255 + 0.5) for c in rgb_color))

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

def main():
    parser = argparse.ArgumentParser(description='Generate color schemes from a given color.')
    parser.add_argument('-c', '--colors', nargs='*', help='one or more colors in hexadecimal code format', action='store', dest='color_str', default='')
    parser.add_argument('-t', '--tui', action='store_true', help='show a text-based user interface to enter colors', default=False)
    args = parser.parse_args()

    color_str = ' '.join(args.color_str) if args.color_str else input("Enter one or more colors in hexadecimal code format separated by spaces: ")
    
    colors = [hex_to_rgb(c) for c in color_str.split()]
    
    num_colors = len(colors)
    if num_colors == 0:
        print("No colors were entered.")
    else:
        avg_color = tuple(sum(c) / num_colors for c in zip(*colors))
        print(f"The input is: {rgb_to_hex(avg_color)}")

    # Generate and print color schemes
    color = avg_color
    print("Complementary Color Scheme:", ' '.join(rgb_to_hex(c) for c in generate_complementary(color)))
    print("Analogous Color Scheme:", ' '.join(rgb_to_hex(c) for c in generate_analogous(color)))
    print(f"Monochromatic Color Scheme: {' '.join(rgb_to_hex(c) for c in generate_monochromatic(color))}")

if __name__ == '__main__':
    main()
