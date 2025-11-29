import os
import random
import shutil
import xml.etree.ElementTree as ET

# >>> 1) ADJUST THESE TWO PATHS IF NEEDED <<<

# Where the Kaggle NEU-DET is extracted
SOURCE_ROOT = r"archive/NEU-DET"

# Where you want the YOLO-ready dataset
TARGET_ROOT = r"ai_service/datasets/NEU_DET"

# Class list in fixed order -> YOLO class IDs will be 0..5
CLASSES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]


def ensure_dirs():
    """Create target directory layout."""
    for split in ["train", "valid"]:
        for t in ["images", "labels"]:
            os.makedirs(os.path.join(TARGET_ROOT, split, t), exist_ok=True)


def voc_xml_to_yolo_lines(xml_path):
    """
    Convert a single Pascal VOC .xml file to YOLO format lines.
    Returns a list of 'cls x_center y_center width height' strings.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    w = int(root.find("size/width").text)
    h = int(root.find("size/height").text)

    yolo_lines = []

    for obj in root.findall("object"):
        cls_name = obj.find("name").text
        if cls_name not in CLASSES:
            raise ValueError(f"Unknown class '{cls_name}' in {xml_path}")
        cls_id = CLASSES.index(cls_name)

        bnd = obj.find("bndbox")
        xmin = float(bnd.find("xmin").text)
        ymin = float(bnd.find("ymin").text)
        xmax = float(bnd.find("xmax").text)
        ymax = float(bnd.find("ymax").text)

        x_center = ((xmin + xmax) / 2.0) / w
        y_center = ((ymin + ymax) / 2.0) / h
        bw = (xmax - xmin) / w
        bh = (ymax - ymin) / h

        yolo_lines.append(
            f"{cls_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}"
        )

    return yolo_lines


def collect_all_xmls():
    """Return list of all annotation file paths from train + validation."""
    xml_files = []
    for split in ["train", "validation"]:
        ann_dir = os.path.join(SOURCE_ROOT, split, "annotations")
        for fname in os.listdir(ann_dir):
            if fname.endswith(".xml"):
                xml_files.append(os.path.join(ann_dir, fname))
    return xml_files


def find_image_for_xml(xml_path):
    """
    Given an xml file, find its corresponding image file under images/<class>/.
    We use <filename> and <object><name>.
    Handles cases where the extension is missing in the XML.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    raw_filename = root.find("filename").text.strip()  # e.g. "pitted_surface_32" or "pitted_surface_32.jpg"
    cls_name = root.find("object/name").text.strip()

    # If XML filename has no extension, assume .jpg
    if "." not in os.path.basename(raw_filename):
        candidates = [raw_filename + ext for ext in [".jpg", ".jpeg", ".png"]]
    else:
        candidates = [raw_filename]

    # Try both train and validation roots with all candidate names
    for split in ["train", "validation"]:
        for fname in candidates:
            candidate = os.path.join(
                SOURCE_ROOT, split, "images", cls_name, fname
            )
            if os.path.exists(candidate):
                return candidate, fname

    # If nothing found, error out
    raise FileNotFoundError(
        f"Image for {xml_path} not found. Tried: {candidates}"
    )


def write_yolo_label(label_path, yolo_lines):
    """Write YOLO lines to a .txt label file."""
    with open(label_path, "w") as f:
        f.write("\n".join(yolo_lines))


def create_yaml():
    """Create data.yaml in TARGET_ROOT."""
    yaml_content = """path: .
train: train/images
val: valid/images

names:
  0: crazing
  1: inclusion
  2: patches
  3: pitted_surface
  4: rolled-in_scale
  5: scratches
"""
    yaml_path = os.path.join(TARGET_ROOT, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)


def main():
    ensure_dirs()

    xml_files = collect_all_xmls()
    print(f"Found {len(xml_files)} annotation files.")

    random.shuffle(xml_files)

    n_train = int(0.7 * len(xml_files))  # 70/30 split
    train_set = set(xml_files[:n_train])

    for idx, xml_path in enumerate(xml_files, 1):
        split = "train" if xml_path in train_set else "valid"

        # Convert annotation to YOLO format
        yolo_lines = voc_xml_to_yolo_lines(xml_path)

        # Find image path
        img_path, filename = find_image_for_xml(xml_path)

        # Destination paths
        dest_img = os.path.join(TARGET_ROOT, split, "images", filename)
        dest_label = os.path.join(
            TARGET_ROOT,
            split,
            "labels",
            os.path.splitext(filename)[0] + ".txt",
        )

        # Copy image
        shutil.copyfile(img_path, dest_img)
        # Write label
        write_yolo_label(dest_label, yolo_lines)

        if idx % 50 == 0 or idx == len(xml_files):
            print(f"Processed {idx}/{len(xml_files)} files...")

    create_yaml()
    print("Done! YOLO dataset created at:", TARGET_ROOT)


if __name__ == "__main__":
    main()
