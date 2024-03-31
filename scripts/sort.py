import os
import shutil
import sys

from PIL import Image
from tqdm import tqdm

from philaudit.detector import Detector


def sort_images(all, include, exclude, detector):
    for image in tqdm(os.listdir(all), desc="Sorting Images with AI"):
        if image.endswith(".png"):
            image_path = os.path.join(all, image)
            try:
                with Image.open(image_path) as img:
                    prediction = detector.detect(img)
            except Exception as e:
                print(f"Error opening image {image_path}: {e}")
                prediction = (
                    0  # Set prediction to 0 if there's an error opening the image
                )

            if prediction == 1:
                shutil.move(image_path, include)
            else:
                shutil.move(image_path, exclude)
        else:
            continue


def main():
    year_image_root = sys.argv[1]  # "PhilAuditStorage/Images/year"
    weights = sys.argv[2]

    all = os.path.join(year_image_root, "All")
    include = os.path.join(year_image_root, "Include")
    exclude = os.path.join(year_image_root, "Exclude")
    detector = Detector(weights)
    sort_images(all, include, exclude, detector)
    print("Done!")


if __name__ == "__main__":
    main()
