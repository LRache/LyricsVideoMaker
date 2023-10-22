from PIL import Image, ImageDraw


def generate_cover_circle_mask(radius: int):
    maskImage = Image.new("L", (radius * 4, radius * 4), 0)
    draw = ImageDraw.ImageDraw(maskImage)
    draw.ellipse((0, 0, radius * 4, radius * 4), fill=0xff)
    maskImage = maskImage.resize((radius * 2, radius * 2), Image.LANCZOS)
    return maskImage


def generate_background_image(angle: float, coverPosition: tuple[int, int],
                              coverImage: Image.Image, maskImage: Image.Image,
                              baseBackgroundImage: Image.Image):
    rotatedCoverImage = coverImage.rotate(angle, Image.BILINEAR)
    backgroundImage = baseBackgroundImage.copy()
    backgroundImage.paste(rotatedCoverImage, coverPosition, maskImage)
    return backgroundImage
