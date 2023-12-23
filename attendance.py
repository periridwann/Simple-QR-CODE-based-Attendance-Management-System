import os
import cv2
import json
import traceback
from dateutil import tz
from loguru import logger
from datetime import datetime
from pyzbar.pyzbar import decode


class Attendance:
    def __init__(self) -> None:
        self.zone = tz.gettz('Asia/Jakarta')
    
    def initialize_json_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {}
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)

        return data
    
    def daily_attendence(self, employee_id, employee_name, employee_status):
        ndate = datetime.now().astimezone(self.zone)
        str_ndate = ndate.strftime('%d-%m-%Y')
        os.makedirs("data", exist_ok=True)
        file_path = f'./data/{str_ndate}.json'
        
        data = self.initialize_json_file(file_path)
        if employee_id in data:
            logger.info(f'[!!] Success update {employee_id}.')
            update_value = {
                'date': str_ndate,
                'out_time': ndate.strftime('%d-%m-%Y %H:%M:%S'),
                'total': data[employee_id]['total'] + 1
            }
            data[employee_id].update(**update_value)
        else:
            logger.info(f'[!!] Success insert {employee_id}.')
            data[employee_id] = {
                    'employee_name': employee_name,
                    'employee_status': employee_status,
                    'date': str_ndate,
                    'in_time': ndate.strftime('%d-%m-%Y %H:%M:%S'),
                    'total': 1
                }
        
        if data[employee_id]['total'] <= 2:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
        else:
            logger.info('Daily attendance limit reached!')

    def recognize_qr_code(self, frame):
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            return json.loads(data)

    def main(self):
        cap = cv2.VideoCapture(0)

        while True:
            try:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to capture frame")
                    break

                data = self.recognize_qr_code(frame)
                if data:
                    str_data = {key: str(value) for key, value in data.items()}
                    self.daily_attendence(**str_data)
                    break

                cv2.imshow("QR Code Attendance", frame)
                
                if cv2.waitKey(1) == ord("q"):
                    break
                
            except Exception:
                traceback.print_exc()
                
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    Attendance().main()

