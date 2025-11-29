import os
from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np

app = Flask(__name__)

# --- LOAD MODELS ---
# Path to your trained weights
MODEL_PATH = os.path.join('runs', 'detect', 'forbes_defect_model2', 'weights', 'best.pt')

try:
    model = YOLO(MODEL_PATH)
    print(f"✅ Loaded Custom Model: {MODEL_PATH}")
except:
    print("⚠️ Custom model not found, loading generic YOLOv8n")
    model = YOLO('yolov8n.pt')

# --- HELPER: OPENCV RUST DETECTION ---
def detect_rust_opencv(image_path):
    img = cv2.imread(image_path)
    if img is None: return 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Define Rust Color Range (Brown/Orange)
    lower_rust = np.array([10, 100, 20])
    upper_rust = np.array([25, 255, 255])
    mask = cv2.inRange(hsv, lower_rust, upper_rust)
    percentage = (cv2.countNonZero(mask) / (img.shape[0] * img.shape[1])) * 100
    return round(percentage, 2)

# --- MAIN ANALYSIS FUNCTION ---
def analyze_image(image_path):
    detections = []
    defect_found = False
    highest_severity = "PASS"
    
    # 1. Run YOLOv8 (Deep Learning)
    results = model(image_path)
    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]
            
            # Confidence Threshold
            if conf > 0.25: 
                defect_found = True
                detections.append(f"{label} ({round(conf*100)}%)")
                
                # Severity Logic for YOLO Classes
                if label in ['crazing', 'pitted_surface']:
                    highest_severity = "CRITICAL"
                elif label in ['inclusion', 'patches']:
                    highest_severity = "MAJOR"
                else:
                    highest_severity = "MINOR"

    # 2. Run OpenCV (Color Fallback)
    rust_percent = detect_rust_opencv(image_path)
    
    # Logic: If YOLO missed it, but it's very rusty, flag it!
    if rust_percent > 5.0:
        defect_found = True
        detections.append(f"Surface Corrosion ({rust_percent}%)")
        
        # Upgrade severity if rust is bad
        if rust_percent > 20 and highest_severity != "CRITICAL":
            highest_severity = "CRITICAL"
        elif rust_percent > 10 and highest_severity == "PASS":
            highest_severity = "MAJOR"
        elif highest_severity == "PASS":
            highest_severity = "MINOR"

    # 3. Format Output
    if detections:
        # Remove duplicates and join
        ai_observation_str = "Detected: " + ", ".join(list(set(detections)))
    else:
        ai_observation_str = "No significant defects detected."

    return {
        "is_defect": defect_found,
        "suggested_severity": highest_severity,
        "ai_observation": ai_observation_str
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data or 'file_path' not in data:
        return jsonify({"error": "No file path provided"}), 400

    # Resolve Path
    image_path = data['file_path']
    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', image_path))

    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404

    try:
        result = analyze_image(full_path)
        # LOGGING: Print result to terminal so you can see what happened
        print(f"Analysis Result for {image_path}: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)