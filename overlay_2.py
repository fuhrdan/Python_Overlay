import cv2
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat

# Read text file (Modify filename as needed)
def read_text_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # Ensure at least 5 lines (fill missing ones with "No Data")
    while len(lines) < 5:
        lines.append("No Data")
    return [line.strip() for line in lines[:5]]

# Load text from file
text_file = "overlay_text.txt"
upper_text, lower_text, bullet1, bullet2, bullet3 = read_text_file(text_file)

# Open the real camera
cap = cv2.VideoCapture(0)

# Get camera resolution
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Calculate overlay position (Bottom 1/6 of screen)
overlay_height = height // 6
overlay_y_start = height - overlay_height

# Flags for UI elements
overlay_visible = False
bullet_states = [False, False, False]  # Tracks visibility of each bullet

# Open virtual camera
with pyvirtualcam.Camera(width, height, fps=30, fmt=PixelFormat.BGR) as cam:
    print(f"Virtual camera started: {cam.device}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        # Flip image for a mirror effect
        frame = cv2.flip(frame, 1)

        # Draw overlay if visible
        if overlay_visible:
            overlay = np.ones((overlay_height, width, 3), dtype=np.uint8) * 255
            overlay = cv2.addWeighted(frame[overlay_y_start:height, 0:width], 0.8, overlay, 0.2, 0)

            # Define font and sizes
            font = cv2.FONT_HERSHEY_TRIPLEX
            font_scale_upper = 1.2
            font_scale_lower = 0.6
            thickness_upper = 3
            thickness_lower = 2

            # Calculate text size
            upper_size = cv2.getTextSize(upper_text, font, font_scale_upper, thickness_upper)[0]
            lower_size = cv2.getTextSize(lower_text, font, font_scale_lower, thickness_lower)[0]

            # Calculate center positions
            upper_x = (width - upper_size[0]) // 2
            upper_y = (overlay_height // 3) + (upper_size[1] // 2)

            lower_x = (width - lower_size[0]) // 2
            lower_y = (2 * overlay_height // 3) + (lower_size[1] // 2)

            # Add upper text (Large font)
            cv2.putText(overlay, upper_text, (upper_x, upper_y), font, font_scale_upper, (0, 0, 0), thickness_upper, cv2.LINE_AA)

            # Add lower text (Small font)
            cv2.putText(overlay, lower_text, (lower_x, lower_y), font, font_scale_lower, (0, 0, 0), thickness_lower, cv2.LINE_AA)

            # Overlay onto the main frame
            frame[overlay_y_start:height, 0:width] = overlay

        # Draw bullet points (if enabled)
        bullet_font_size = 0.7
        bullet_thickness = 2
        bullet_y_start = 50  # Start at the top-left corner

        bullet_texts = [bullet1, bullet2, bullet3]
        for i, bullet_text in enumerate(bullet_texts):
            if bullet_states[i]:  # If bullet point is enabled
                bullet_pos = (20, bullet_y_start + (i * 40))  # Offset each bullet down
                ##cv2.putText(frame, f"{bullet_text}", bullet_pos, font, bullet_font_size, (0, 0, 0), bullet_thickness, cv2.LINE_AA)
                # Draw black outline (border)
                cv2.putText(frame, f"- {bullet_text}", bullet_pos, font, bullet_font_size, (0, 0, 0), bullet_thickness + 2, cv2.LINE_AA)
                
                # Draw white text on top
                cv2.putText(frame, f"- {bullet_text}", bullet_pos, font, bullet_font_size, (255, 255, 255), bullet_thickness, cv2.LINE_AA)

        # Send frame to virtual camera
        cam.send(frame)
        cam.sleep_until_next_frame()

        # Show preview
        cv2.imshow("Virtual Camera Output", frame)

        # Check key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Clear everything
            overlay_visible = False
            bullet_states = [False, False, False]
        elif key == ord('c'):  # Toggle overlay
            overlay_visible = not overlay_visible
        elif key == ord('v'):  # Show bullet 1
            bullet_states[0] = not bullet_states[0]
        elif key == ord('b'):  # Show bullet 2
            bullet_states[1] = not bullet_states[1]
        elif key == ord('n'):  # Show bullet 3
            bullet_states[2] = not bullet_states[2]

cap.release()
cv2.destroyAllWindows()
