import gradio as gr
from PIL import Image, ImageDraw
import io

# Pricing
PRICE_PER_SQFT_SCREEN = 18
PRICE_PER_SQFT_SUNROOM = 95
PRICE_PER_SQFT_PATIOCOVER = 45
DOOR_HEIGHT_INCHES = 80  # Standard for scaling

def generate_overlay(image, frame_color, roof_style, door_count, enclosure_type, real_door_pixel_height, patio_width, patio_depth):
    sqft = patio_width * patio_depth
    if enclosure_type == "Screen Porch":
        price = sqft * PRICE_PER_SQFT_SCREEN
    elif enclosure_type == "Sunroom":
        price = sqft * PRICE_PER_SQFT_SUNROOM
    else:
        price = sqft * PRICE_PER_SQFT_PATIOCOVER

    img = Image.open(image).convert("RGBA")
    base = img.copy()

    pixel_per_inch = real_door_pixel_height / DOOR_HEIGHT_INCHES
    pixel_per_foot = pixel_per_inch * 12
    img_width, img_height = img.size

    frame_color_rgb = (255, 255, 255, 230) if frame_color == "White" else (90, 50, 20, 230)

    screen_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    screen_draw = ImageDraw.Draw(screen_layer, "RGBA")

    post_spacing_pixels = pixel_per_foot * 6
    x_positions = []
    x = 0
    while x < img_width:
        x_positions.append(x)
        x += post_spacing_pixels
    x_positions.append(img_width)

    chair_rail_height = pixel_per_inch * 36

    # Add fine screen texture
    for i in range(len(x_positions) - 1):
        panel_box = [(x_positions[i], 0), (x_positions[i+1], img_height)]
        screen_draw.rectangle(panel_box, fill=(180, 180, 180, 30))
        
        spacing = 20
        for y in range(0, img_height, spacing):
            screen_draw.line([(x_positions[i], y), (x_positions[i+1], y)], fill=(120, 120, 120, 20), width=1)
        for xline in range(int(x_positions[i]), int(x_positions[i+1]), spacing):
            screen_draw.line([(xline, 0), (xline, img_height)], fill=(120, 120, 120, 20), width=1)

    img = Image.alpha_composite(img, screen_layer)

    draw = ImageDraw.Draw(img, "RGBA")
    for x in x_positions:
        draw.line([(x, 0), (x, img_height)], fill=frame_color_rgb, width=8)
    
    draw.line([(0, 0), (img_width, 0)], fill=frame_color_rgb, width=10)
    draw.line([(0, img_height - 5), (img_width, img_height - 5)], fill=frame_color_rgb, width=10)
    draw.line([(0, chair_rail_height), (img_width, chair_rail_height)], fill=frame_color_rgb, width=8)

    if door_count > 0:
        door_width_pixels = pixel_per_foot * 3
        spacing = img_width // (door_count + 1)
        for i in range(1, door_count + 1):
            center_x = spacing * i
            draw.rectangle(
                [(center_x - door_width_pixels//2, img_height - pixel_per_inch * 80), (center_x + door_width_pixels//2, img_height)],
                outline=(0, 255, 0, 200),
                width=6
            )

    output_bytes = io.BytesIO()
    img.save(output_bytes, format="PNG")
    output_bytes.seek(0)

    return output_bytes, f"Estimated Price: ${price:,.2f} (Approximate for Georgia Market)"

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🏡 Custom Porch, Sunroom, and Patio Cover Designer (Georgia Market) — Pro Edition")

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="filepath", label="Upload a picture of your patio or porch")
            frame_color = gr.Radio(["White", "Bronze"], label="Frame Color")
            roof_style = gr.Dropdown(["Shed / Lean-to", "Open Gable", "Flat"], label="Roof Style")
            door_count = gr.Slider(0, 3, step=1, label="How many screen doors?")
            enclosure_type = gr.Radio(["Screen Porch", "Sunroom", "Patio Cover"], label="Type of Enclosure")
            real_door_pixel_height = gr.Number(label="Draw a line from floor to top of door. Enter pixel height here.")
            patio_width = gr.Number(label="Patio Width (Feet)")
            patio_depth = gr.Number(label="Patio Depth (Feet)")
            submit = gr.Button("Generate My Design")
        
        with gr.Column():
            output_image = gr.File(label="Downloadable Design Image (Click to Save)")
            output_text = gr.Textbox(label="Project Estimate 💰")
            request_quote = gr.Textbox(lines=4, label="(Optional) Enter Name, Email, Address to Request Full Quote")

    submit.click(
        generate_overlay,
        inputs=[input_image, frame_color, roof_style, door_count, enclosure_type, real_door_pixel_height, patio_width, patio_depth],
        outputs=[output_image, output_text]
    )

demo.launch()
