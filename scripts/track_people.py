"""
云台跟踪人
"""
import sys
import time
from pathlib import Path

import cv2
import numpy

sys.path.insert(0, "/workspace/HighVenueServer/HiCamera")
from infer import human_detect_tracker, vis_detect_results, VideoWriter, basketball_detector
from camera import HIKCamera

if __name__ == '__main__':
    peoples = basketball_detector.infer(numpy.ones((100,100,3), numpy.uint8))
    camera = HIKCamera(ip="192.168.111.71", user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=20)
    video = Path("/workspace/HighVenueServer/HiCamera/scripts/output.mp4")
    video_writer = VideoWriter(video)
    # camera.save_real_data(video)
    last_people_id = None
    last_move_command = None
    speed = 2
    # camera.ptz_control(23, 0, 2)
    # time.sleep(3)
    # camera.ptz_control(23, 1, 2)
    #
    # camera.ptz_control(11, 0, 2)
    # time.sleep(2)
    # camera.ptz_control(11, 1, 2)
    for i in range(1 * 60 * 25):
        frame = camera.get_frame()
        s = time.time()
        peoples = human_detect_tracker.infer(frame)
        ids = set([people.id for people in peoples])
        if not ids:
            if last_move_command is not None:
                camera.ptz_control(last_move_command, 1, speed)
            video_writer.write(frame)
            continue
        if last_people_id not in ids:
            last_people_id = ids.pop()
        people = None
        for people in peoples:
            if people.id == last_people_id:
                break
        cv2.putText(frame, f"{last_move_command}", (20,20), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,0,255))
        frame = vis_detect_results(frame, [people])
        video_writer.write(frame)
        distance = 100
        if people.bbox.center.x > frame.shape[1] // 2 + distance:
            if people.bbox.center.y < frame.shape[0] // 2 - distance:
                if last_move_command == 26:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 26
                camera.ptz_control(last_move_command, 0, speed)
            elif people.bbox.rby > frame.shape[0] // 2 + distance:
                if last_move_command == 28:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 28
                camera.ptz_control(last_move_command, 0, speed)
            else:
                if last_move_command == 24:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 24
                camera.ptz_control(last_move_command, 0, speed)
        elif people.bbox.center.x < frame.shape[1] // 2 - distance:
            if people.bbox.center.y < frame.shape[0] // 2 - distance:
                if last_move_command == 25:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 25
                camera.ptz_control(last_move_command, 0, speed)
            elif people.bbox.rby > frame.shape[0] // 2 + distance:
                if last_move_command == 27:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 27
                camera.ptz_control(last_move_command, 0, speed)
            else:
                if last_move_command == 23:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 23
                camera.ptz_control(last_move_command, 0, speed)
        else:
            if people.bbox.center.y < frame.shape[0] // 2 - distance:
                if last_move_command == 21:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 21
                camera.ptz_control(last_move_command, 0, speed)
            elif people.bbox.rby > frame.shape[0] // 2 + distance:
                if last_move_command == 22:
                    continue
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
                last_move_command = 22
                camera.ptz_control(last_move_command, 0, speed)
            else:
                if last_move_command is not None:
                    camera.ptz_control(last_move_command, 1, speed)
        print(f"id={last_people_id} time={(time.time()-s)*1000}")
    camera.ptz_control(12, 0, 3)
    time.sleep(3)
    camera.ptz_control(12, 1, 3)
    video_writer.release(compress=False)
    # camera.stop_save_real_data()
    camera.stop_preview()
