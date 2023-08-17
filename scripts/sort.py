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
            image = Image.open(image_path)
            prediction = detector.detect(image)
        if prediction == 1:
            shutil.copy(image_path, include)
        else:
            shutil.copy(image_path, exclude)


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
