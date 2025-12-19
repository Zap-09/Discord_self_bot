import os

from .utils import log
from PIL import Image


def convert_to_webp(
        image_file,
        output_path = None,
        color_mode = "RGBA",
        quality = 75,
        lossless = False,
        compress_level = 4):


    if not os.path.exists(image_file):
        log(f"Could not locate file: {image_file}","error")
        return None


    if not color_mode in ["RGBA","RGB","LA","L"]:
        log("Unknown color mode. Please use 'RGBA', 'RGB', 'L', 'LA'",t="error")
        return None

    if lossless and quality == 75:
        quality = None

    if quality and lossless:
        log("Both Quality and Lossless parameters are set to true. So Quality parameters will be ignored","warn")
        quality = None



    if quality and not lossless:
        if quality > 100:
            log("Quality Value was set over 100. Anything above 100 is redundant. Setting quality value to 100", "warn")
            quality = 100

        elif quality < 0:
            log("Quality Value was set under 0. Anything under 0 is redundant. Setting quality value to 0", "warn")
            quality = 0

    if compress_level > 6:
        log("Compress level was set over 6. Anything above 6 is redundant. Setting Compress level to 6", "warn")
        compress_level = 6

    elif compress_level < 0:
        log("Compress level was set under 0. Anything under 0 is redundant. Setting Compress level to 0", "warn")
        compress_level = 0


    with Image.open(image_file) as img:
        img = img.convert(color_mode)
        file_name = os.path.basename(image_file)
        base_name, _ = os.path.splitext(file_name)


        if output_path:
            try:
                os.makedirs(output_path, exist_ok=True)
            except:
                log("Invalid file path", t="error")
                return None
            if quality:
                img.save(os.path.join(output_path,f"{base_name}.webp"),"WEBP",quality = quality,lossless = lossless,method = compress_level)
            else:
                img.save(os.path.join(output_path,f"{base_name}.webp"),"WEBP",lossless = lossless,method = compress_level)

            return os.path.join(output_path,f"{base_name}.webp"),os.path.getsize(os.path.join(output_path,f"{base_name}.webp"))

        else:
            if quality:
                img.save(f"{base_name}","WEBP",quality = quality,lossless = lossless,method = compress_level)

            else:
                img.save(f"{base_name}","WEBP",lossless = lossless,method = compress_level)

        return f"{base_name}.webp",os.path.getsize(f"{base_name}.webp")
