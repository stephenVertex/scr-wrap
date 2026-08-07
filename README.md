# scr-wrap

A Python utility for wrapping screenshots in browser frames with various background options.

## Usage

```bash
./scr-wrap prime                    # Print the agent-facing usage guide
./scr-wrap screenshot.png -b gradient
./scr-wrap screenshot.png -b fractal-7 -s
./scr-wrap image1.png image2.png -b mixtone
```

Run `./scr-wrap prime` before first use in an agent session, or after context
compaction, to refresh the tool's command surface and conventions.

## Background Options

- **Built-in gradients**: gradient, mixtone, colorful, blurred
- **Fractal Glass Gradients**: fractal-1 through fractal-40 (or fractal-01 through fractal-40)
- **Custom**: Provide path to any image file

Use `./scr-wrap --list-backgrounds` to see all available options.

## Fractal Backgrounds Attribution

The fractal backgrounds (fractal-*.jpg) are from:
https://elements.envato.com/fractal-glass-gradients-PKX4RMT

## Installation

This utility uses `uv` for dependency management. To install globally:

```bash
cd scr-wrap
./install.sh  # Create symlink in ~/.local/bin
```
