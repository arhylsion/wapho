import os
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def get_font_path(font_type, selected_font=None, uploaded_file=None):
    if font_type == "upload" and uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        font_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(font_path)
        return font_path
    elif font_type == "default" and selected_font:
        return os.path.join("fonts", selected_font)
    else:
        return None


def add_watermark_to_image(image_path, font_path, text, font_size, spacing_x, spacing_y, color, rotation, output_format):
    img = Image.open(image_path).convert("RGBA")
    base_width, base_height = img.size

    extended_size = int((base_width**2 + base_height**2) ** 0.5)
    watermark_layer = Image.new("RGBA", (extended_size, extended_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark_layer)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        font = ImageFont.load_default()

    try:
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
    except AttributeError:
        text_width = font.getlength(text)

    step_x = max(spacing_x, text_width + 10)

    for y in range(0, extended_size, spacing_y):
        for x in range(0, extended_size, step_x):
            draw.text((x, y), text, font=font, fill=color)

    rotated_layer = watermark_layer.rotate(rotation, expand=True)
    left = (rotated_layer.width - base_width) // 2
    top = (rotated_layer.height - base_height) // 2
    right = left + base_width
    bottom = top + base_height
    cropped_layer = rotated_layer.crop((left, top, right, bottom))

    combined = Image.alpha_composite(img, cropped_layer)
    if output_format.lower() == 'jpg':
        combined = combined.convert("RGB")

    output_io = BytesIO()
    format_pillow = 'JPEG' if output_format.lower() == 'jpg' else output_format.upper()
    combined.save(output_io, format=format_pillow)
    output_io.seek(0)
    return output_io


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_file = request.files['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
        image_file.save(image_path)

        font_type = request.form.get('font_option', 'default')
        selected_font = request.form.get('default_font')
        uploaded_font = request.files.get('font')

        font_path = get_font_path(font_type, selected_font, uploaded_font)

        text = request.form.get('text') or 'SAMPLE'
        font_size = int(request.form.get('font_size') or 36)
        spacing_x = int(request.form.get('spacing_x') or 200)
        spacing_y = int(request.form.get('spacing_y') or 150)
        rotation = int(request.form.get('rotation') or 45)

        rgba_hex = request.form.get('color') or '#000000'
        alpha = int(request.form.get('alpha') or 128)
        rgba = tuple(int(rgba_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)

        output_format = request.form.get('format') or 'png'

        result_io = add_watermark_to_image(image_path, font_path, text, font_size, spacing_x, spacing_y, rgba, rotation, output_format)

        return send_file(result_io, as_attachment=True, download_name=f"watermarked.{output_format}")

    return render_template('index.html')


@app.route('/preview', methods=['POST'])
def preview_watermark():
    image_file = request.files.get('image')
    if not image_file:
        return "Image required", 400

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
    image_file.save(image_path)

    font_type = request.form.get('font_option', 'default')
    selected_font = request.form.get('default_font')
    uploaded_font = request.files.get('font')

    font_path = get_font_path(font_type, selected_font, uploaded_font)

    text = request.form.get('text', 'SAMPLE')
    font_size = int(request.form.get('font_size', 36))
    rotation = int(request.form.get('rotation', 45))
    spacing_x = int(request.form.get('spacing_x', 200))
    spacing_y = int(request.form.get('spacing_y', 150))
    color = request.form.get('color', '#ff0000')
    alpha = 255
    output_format = request.form.get('format', 'png')

    rgba = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4)) + (alpha,)

    result_io = add_watermark_to_image(
        image_path=image_path,
        font_path=font_path,
        text=text,
        font_size=font_size,
        spacing_x=spacing_x,
        spacing_y=spacing_y,
        color=rgba,
        rotation=rotation,
        output_format=output_format
    )

    mimetype = 'image/png' if output_format.lower() == 'png' else 'image/jpeg'
    return send_file(result_io, mimetype=mimetype)


if __name__ == '__main__':
    app.run(debug=True)
