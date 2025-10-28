#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Morai ZED LANDMARK Demo — BODY_38
----------------------------------------------------------------------
지원 모드:
  1) SVO 파일 재생 (--mode svo --svo path.svo)
  2) ZED 카메라 실시간 (--mode zed)
"""

import os, sys, time, argparse
import cv2

# ------------------------------
# Constants
# ------------------------------
BODY_COLOR = (225,255,0)

# ==========================================================
# BODY_38 Skeleton 렌더링 유틸
# ==========================================================
def render_body38(bgr, body_list, sl, color=(225,255,0)):
    """ZED BODY_38 본 연결선을 OpenCV로 시각화"""
    if not body_list:
        return False
    for body in body_list:
        keypoints = getattr(body, "keypoint_2d", [])
        if keypoints is None or len(keypoints) < 38:
            continue
        for part in sl.BODY_38_BONES:
            a_idx, b_idx = part[0].value, part[1].value
            a = keypoints[a_idx]; b = keypoints[b_idx]
            if (0 <= a[0] < bgr.shape[1] and 0 <= b[0] < bgr.shape[1]):
                cv2.line(bgr, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), color, 1, cv2.LINE_AA)
        # 각 관절 표시
        for (x, y) in keypoints:
            if 0 <= x < bgr.shape[1] and 0 <= y < bgr.shape[0]:
                cv2.circle(bgr, (int(x), int(y)), 3, color, -1)
    return True


# ==========================================================
# ZED SVO Backend
# ==========================================================
class ZEDSVOBackend:
    def __init__(self, svo_path, body_format="BODY_38"):
        import pyzed.sl as sl
        self.sl = sl
        self.zed = sl.Camera()

        init_params = sl.InitParameters()
        init_params.set_from_svo_file(svo_path)
        init_params.depth_mode = sl.DEPTH_MODE.NEURAL
        init_params.coordinate_units = sl.UNIT.METER
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError(f"ZED open failed: {err}")

        self.zed.enable_positional_tracking(sl.PositionalTrackingParameters())
        bt = sl.BodyTrackingParameters()
        bt.enable_tracking = True
        bt.enable_body_fitting = True
        bt.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
        bt.body_format = getattr(sl.BODY_FORMAT, body_format)
        self.zed.enable_body_tracking(bt)

        self.body_rt = sl.BodyTrackingRuntimeParameters()
        self.body_rt.detection_confidence_threshold = 40
        self.body_format = bt.body_format

        info = self.zed.get_camera_information()
        self.src_w = info.camera_configuration.resolution.width
        self.src_h = info.camera_configuration.resolution.height

        self.image = sl.Mat()
        self.bodies = sl.Bodies()

    def read(self):
        if self.zed.grab() != self.sl.ERROR_CODE.SUCCESS:
            return None, None
        self.zed.retrieve_image(self.image, self.sl.VIEW.LEFT, self.sl.MEM.CPU)
        self.zed.retrieve_bodies(self.bodies, self.body_rt)
        np_bgra = self.image.get_data().copy()
        bgr = cv2.cvtColor(np_bgra, cv2.COLOR_BGRA2BGR)

        body_list = getattr(self.bodies, "body_list", [])
        if not body_list:
            print("[DEBUG] no body detected in this frame")
            return bgr, None

        # --- 모든 사람 렌더링 ---
        render_body38(bgr, body_list, self.sl)

        # --- 각 사람의 keypoints 정규화 ---
        all_kps = []
        for body in body_list:
            kps = body.keypoint_2d
            confs = getattr(body, "keypoint_confidence", [])
            kps_norm = []
            for i in range(len(kps)):
                x_px, y_px = float(kps[i][0]), float(kps[i][1])
                c = float(confs[i]) if i < len(confs) else 1.0
                kps_norm.append({"x": x_px / self.src_w, "y": y_px / self.src_h, "v": c})
            all_kps.append({
                "id": getattr(body, "id", -1),
                "confidence": getattr(body, "confidence", 0.0),
                "keypoints": kps_norm
            })

        # target = None
        # best_conf = -1.0
        # for b in body_list:
        #     conf = float(getattr(b, "confidence", 0.0))
        #     if conf > best_conf and len(getattr(b, "keypoint_2d", [])) > 0:
        #         best_conf = conf
        #         target = b
        #
        # kps_norm = None
        # if target is not None:
        #     # 바디 스켈레톤 시각화
        #     render_body38(bgr, [target], self.sl)
        #
        #     # keypoints 정규화
        #     kps = target.keypoint_2d
        #     confs = getattr(target, "keypoint_confidence", [])
        #     kps_norm = []
        #     for i in range(len(kps)):
        #         x_px, y_px = float(kps[i][0]), float(kps[i][1])
        #         c = float(confs[i]) if i < len(confs) else 1.0
        #         kps_norm.append({"x": x_px / self.src_w, "y": y_px / self.src_h, "v": c})
        # else:
        #     print("[DEBUG] no body detected in this frame")

        return bgr

    def release(self):
        try:
            self.zed.disable_body_tracking()
            self.zed.disable_positional_tracking()
            self.zed.close()
        except Exception:
            pass


# ==========================================================
# ZED Live Backend
# ==========================================================
class ZEDLiveBackend(ZEDSVOBackend):
    def __init__(self, cam_id=0, body_format="BODY_38"):
        import pyzed.sl as sl
        self.sl = sl
        self.zed = sl.Camera()

        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD720
        init_params.depth_mode = sl.DEPTH_MODE.NEURAL
        init_params.coordinate_units = sl.UNIT.METER
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError(f"ZED live open failed: {err}")

        self.zed.enable_positional_tracking(sl.PositionalTrackingParameters())
        bt = sl.BodyTrackingParameters()
        bt.enable_tracking = True
        bt.enable_body_fitting = True
        bt.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
        bt.body_format = getattr(sl.BODY_FORMAT, body_format)
        self.zed.enable_body_tracking(bt)

        self.body_rt = sl.BodyTrackingRuntimeParameters()
        self.body_rt.detection_confidence_threshold = 40
        self.body_format = bt.body_format

        info = self.zed.get_camera_information()
        self.src_w = info.camera_configuration.resolution.width
        self.src_h = info.camera_configuration.resolution.height

        self.image = sl.Mat()
        self.bodies = sl.Bodies()

# ==========================================================
# Main loop
# ==========================================================
# ------------- main demo loop -------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", type=str, choices=["svo", "zed"], required=True)
    ap.add_argument("--svo", type=str)
    ap.add_argument("--device", type=str, default="cuda")
    ap.add_argument("--target-fps", type=float, default=15.0,
                    help="Input frame sampling rate (Hz) — match training FPS")
    ap.add_argument("--save-video", action="store_true",
                    help="Save the demo output as a video file (default: off)")
    ap.add_argument("--save-path", type=str, default=None,
                    help="Path to save output video (e.g. ./outputs/demo.mp4)")
    args = ap.parse_args()

    # -------------------------------
    # Backend 선택
    # -------------------------------
    if args.mode == "svo":
        if not args.svo:
            print("ERROR: --svo path is required")
            sys.exit(2)
        backend = ZEDSVOBackend(args.svo)
        title = f"Morai Demo - SVO: {os.path.basename(args.svo)}"
    else:
        backend = ZEDLiveBackend()
        title = "Morai Demo - ZED Live"

    # -------------------------------
    # Window & Video Writer 초기화
    # -------------------------------
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    out_writer = None
    save_path = None

    try:
        # -------------------------------
        # Main Loop
        # -------------------------------
        while True:
            bgr = backend.read()
            if bgr is None:
                break

            # --- 첫 프레임에서 VideoWriter 생성 ---
            if args.save_video and out_writer is None:
                target_fps = args.target_fps
                print(f"[INFO] Target FPS: {target_fps}")
                h, w = bgr.shape[:2]
                if args.save_path:
                    save_path = os.path.join(args.save_path, f"demo_output_{int(time.time())}.mp4")
                else:
                    save_path = os.path.join(os.getcwd(), f"demo_output_{int(time.time())}.mp4")
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                out_writer = cv2.VideoWriter(save_path, fourcc, target_fps, (w, h))
                print(f"[INFO] Saving output video to: {save_path}")

            cv2.imshow(title, bgr)

            # --- 저장 ---
            if args.save_video and out_writer is not None:
                out_writer.write(bgr)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break
    finally:
        backend.release()
        cv2.destroyAllWindows()
        if out_writer is not None:
            out_writer.release()
            print(f"[INFO] Video saved successfully: {save_path}")


if __name__ == "__main__":
    main()