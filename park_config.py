import cv2
import numpy as np
import cvzone
import pickle

# Configuration variables for ease of modification
video_file = 'video.mp4'  # Path to the video file for processing
pickle_file = 'parking_data.pkl'  # File to store and load parking data
frame_width = 1020  # Width to resize the video frames
frame_height = 500  # Height to resize the video frames

class ParkingConfigurator:
    def __init__(self, video_path, pickle_path):
        # Initialize video capture with the given path
        self.cap = cv2.VideoCapture(video_path)
        self.pickle_path = pickle_path  # Path to save/load the polyline data
        self.polylines = []  # List to store the coordinates of polylines
        self.parking_numbers = []  # List to store corresponding parking numbers
        self.drawing = False  # Flag to indicate if we are currently drawing a polyline
        self.current_poly = []  # Temporary storage for the current polyline points
        self.load_poly_data()  # Attempt to load existing parking data

    def load_poly_data(self):
        # Load polyline and parking number data from a file
        try:
            with open(self.pickle_path, "rb") as f:
                data = pickle.load(f)
                self.polylines, self.parking_numbers = data['polylines'], data['parking_numbers']
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            # If loading fails, start with empty lists
            print("No previous data found or data corrupted. Starting fresh.")

    def save_poly_data(self):
        # Save the polyline and parking number data to a file
        try:
            with open(self.pickle_path, "wb") as f:
                data = {'polylines': self.polylines, 'parking_numbers': self.parking_numbers}
                pickle.dump(data, f)
        except pickle.PicklingError:
            # If saving fails, notify the user
            print("Data could not be saved.")

    def mouse_callback(self, event, x, y, flags, param):
        # Mouse event callback function to draw and store polylines
        if event == cv2.EVENT_LBUTTONDOWN:
            # Start a new polyline
            self.drawing = True
            self.current_poly = [(x, y)]
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            # Add points to the polyline as the mouse moves
            self.current_poly.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            # Finish the polyline
            self.drawing = False
            # Prompt the user to enter the parking area number in the terminal
            area_number = input("Enter the parking area number: ")
            if area_number:
                # If a number was entered, store the polyline and number
                self.parking_numbers.append(area_number)
                self.polylines.append(np.array(self.current_poly, np.int32))

    def delete_parking_number(self):
        # Prompt the user to enter the parking number to delete
        delete_number = input("Enter the parking number to delete: ")
        if delete_number in self.parking_numbers:
            index = self.parking_numbers.index(delete_number)
            del self.polylines[index]
            del self.parking_numbers[index]
            print(f"Parking spot number {delete_number} deleted.")
        else:
            print(f"No parking spot found with number {delete_number}.")

    def run(self):
        # Main loop to handle the frame processing
        cv2.namedWindow('Frame')
        cv2.setMouseCallback('Frame', self.mouse_callback)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                # If frame reading fails, restart from the beginning of the video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Resize the frame to the specified dimensions
            frame = cv2.resize(frame, (frame_width, frame_height))

            # Draw all polylines and parking numbers on the frame
            for i, polyline in enumerate(self.polylines):
                cv2.polylines(frame, [polyline], True, (0, 0, 255), 2)
                cvzone.putTextRect(frame, f'{self.parking_numbers[i]}', tuple(polyline[0]), 1, 1)

            cv2.imshow('Frame', frame)
            key = cv2.waitKey(50) & 0xFF

            if key == ord('s'):
                # Save the data if 's' is pressed
                print("Saving data...")
                self.save_poly_data()
                print("Data saved.")

            if key == ord('d'):
                # Call the method to delete a parking number
                self.delete_parking_number()
                # Save immediately after deletion
                self.save_poly_data()

            if key == ord('q'):
                print("Quitting...")
                # Exit the loop if 'q' is pressed
                break

        # Release the video capture and destroy all windows when done
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Instantiate the configurator and run it
    pc = ParkingConfigurator(video_file, pickle_file)
    pc.run()
