import cv2


CAMERA_BACKENDS = {
    "DSHOW": cv2.CAP_DSHOW,
    "MSMF": cv2.CAP_MSMF,
    "ANY": cv2.CAP_ANY,
}


def main():
    print("Checking camera indices 0-9 with DSHOW, MSMF, and ANY.")
    print("Press any key in the preview window to continue.")
    print("Press q to quit.")

    for index in range(10):
        for backend_name, backend in CAMERA_BACKENDS.items():
            cap = cv2.VideoCapture(index, backend)
            if not cap.isOpened():
                print(f"{index} / {backend_name}: not available")
                cap.release()
                continue

            ret, frame = cap.read()
            if not ret:
                print(f"{index} / {backend_name}: opened, but no frame")
                cap.release()
                continue

            height, width = frame.shape[:2]
            print(f"{index} / {backend_name}: available ({width}x{height})")

            cv2.putText(
                frame,
                f"Index: {index}  Backend: {backend_name}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3,
                cv2.LINE_AA,
            )
            cv2.imshow("Camera check", frame)
            key = cv2.waitKey(0) & 0xFF
            cap.release()

            if key == ord("q"):
                cv2.destroyAllWindows()
                return

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
