from ultralytics import YOLO

def train_model():
    # 1. Load the base model (pre-trained on COCO dataset)
    model = YOLO('yolov8n.pt') 

    # 2. Train it on YOUR industrial data
    # epochs=20 is enough for a prototype. 
    # imgsz=640 is standard resolution.
    results = model.train(
        data='./datasets/NEU_DET/data.yaml',
        epochs=20,
        imgsz=640,
        project='runs/detect',
        name='forbes_defect_model'
    )
    
    # 3. Validate the model (Check accuracy)
    metrics = model.val()
    print(f"mAP50-95: {metrics.box.map}") # Mean Average Precision

    # 4. Export the model to use in your app
    model.export(format='pt')
    print("Training Complete. Model saved to runs/detect/forbes_defect_model/weights/best.pt")

if __name__ == '__main__':
    train_model()