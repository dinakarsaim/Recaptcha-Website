from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import cv2
from ultralytics import YOLO

# Initialize Flask app
app = Flask(__name__)

# Load the trained YOLOv8 model
model = YOLO("best.pt")  # Replace with your trained model weights

# Ensure required folders exist
UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/predict", methods=["POST"])
# def predict():
#     results = {}

#     for i in range(1, 5):  # Loop for 4 images
#         file_key = f"file{i}"
#         if file_key in request.files:
#             file = request.files[file_key]

#             # Save uploaded image
#             image_path = os.path.join(UPLOAD_FOLDER, file.filename)
#             file.save(image_path)

#             # Run YOLOv8 inference
#             yolo_results = model(image_path)

#             # Save detection result
#             result_image_path = os.path.join(RESULT_FOLDER, f"result_{file.filename}")
#             for result in yolo_results:
#                 im_array = result.plot()  # Get image with bounding boxes
#                 cv2.imwrite(result_image_path, im_array)

#             # Store result path for frontend
#             results[f"image_path{i}"] = f"/results/result_{file.filename}"

#     return jsonify(results)
@app.route("/predict", methods=["POST"])
def predict():
    results = {}
    selected_object = request.form.get("selected_object", "all")  # Get selected object

    for i in range(1, 5):
        file_key = f"file{i}"
        image_path = None
        if file_key in request.files:
            file = request.files[file_key]
            image_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(image_path)
        
            # Run YOLOv8 inference
            yolo_results = model(image_path)
            # filtered_results = []  # To store filtered objects

            for result in yolo_results:
                filtered_results = []
                # im_array = result.plot()  # Get image with all detections
                
                # Filter detected objects
                for box in result.boxes:
                    class_id = int(box.cls[0])  # Get class index
                    class_name = result.names[class_id]  # Get object name
                    
                    if selected_object == "all" or class_name == selected_object:
                        filtered_results.append(box)

                # Draw only the filtered objects
                result.boxes = filtered_results  # Keep only selected objects
                im_array = result.plot()  # Re-plot with filtered boxes
                
                # Save filtered image
                result_image_path = os.path.join(RESULT_FOLDER, f"result_{file.filename}")
                cv2.imwrite(result_image_path, im_array)

                # Store result path for frontend
                results[f"image_path{i}"] = f"/results/result_{file.filename}"

    return jsonify(results)

# Serve processed images
@app.route("/results/<filename>")
def get_result(filename):
    return send_from_directory(RESULT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)