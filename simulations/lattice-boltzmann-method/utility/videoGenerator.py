import cv2
import os
import pathlib

# Define test name manually if needed or ...
test_name = "" 

# ... get the latest test name
test_dir = pathlib.Path(__file__).parents[1] / "bin" / "export"
if test_name.__len__() <= 4:
    test_list = os.listdir(test_dir)
    test_list.sort()

    if test_list:
        test_name = test_list[-1]
    else:
        print("No tests found in the directory.")

# Get the path to the PNG images
image_dir = test_dir / test_name / "png"

# Output video file name and path
video_name = str(test_name)+".mp4"
video_path = pathlib.Path(__file__).parents[0] / "videos" / video_name

# Frame rate (frames per second)
frame_rate = 60  # Adjust as needed (default for FluidX3D frames is 60)

# Get the list of PNG files in the directory
image_files = sorted([os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith('.png')])

if not image_files:
    print("No PNG images found in the directory.")
    exit()

# Get the dimensions of the first image
first_image = cv2.imread(image_files[0])
height, width, layers = first_image.shape

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec as needed
out = cv2.VideoWriter(str(video_path), fourcc, frame_rate, (width, height))

# Loop through the image files and write each frame to the video
img_index = 0
for image_file in image_files:
    frame = cv2.imread(image_file)
    out.write(frame)
    print(f"Writing frame {img_index}/{len(image_files)}")
    img_index += 1

# Release the VideoWriter and close all OpenCV windows
out.release()
cv2.destroyAllWindows()

print(f"Video '{video_path}' generated successfully.")
