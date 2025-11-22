# video_processor.py
import cv2
import os
import numpy as np
from collections import defaultdict, deque
from pose_classifier import PoseClassifier  # your existing classifier
from datetime import datetime
from pathlib import Path

class VideoProcessor:
    def __init__(self, video_path, output_dir, smooth_window=5):
        self.video_path = video_path
        self.base_output_dir = Path(output_dir)
        self.classifier = PoseClassifier()
        self.smooth_window = smooth_window  # frames for smoothing confidences
        self.frames = []  # will hold per-frame dicts
        
        # Prepare output folder
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = Path(video_path).stem
        self.session_dir = self.base_output_dir / f"{video_name}_{timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        print(f"[VideoProcessor] Session folder: {self.session_dir}")

    # Utilities
    def _safe_div(self, a, b, eps=1e-6):
        return a / (b + eps)

    def _landmark_xy(self, lm):
        return (lm.x, lm.y)

    def _visibility_ok(self, lm, thr=0.4):
        # MediaPipe landmarks have visibility and presence properties sometimes
        v = getattr(lm, "visibility", None)
        if v is None:
            return True
        return v >= thr

    # Stage 1: extract frames + landmarks + classifier
    def extract_frames(self, sample_rate=1):
        """
        Read video and record per-frame:
          - frame_number, timestamp
          - classifier phase & confidence
          - normalized landmarks (wrist/elbow/shoulder/hip/nose)
        sample_rate: process every `sample_rate` frame (1 = every frame)
        """
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_idx = 0
        saved = 0
        print("[extract_frames] Starting frame extraction...")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % sample_rate != 0:
                frame_idx += 1
                continue

            results = self.classifier.detect_pose(frame)
            phase, conf = self.classifier.classify_shot_phase(results)

            # default record
            record = {
                "frame_idx": frame_idx,
                "timestamp": frame_idx / fps,
                "phase_raw": phase,        # e.g., "Shot pocket", "Set point", ...
                "phase_conf": float(conf), # 0.0-1.0
                "frame": frame,
                "landmarks": None          # will fill below if available
            }

            if results and results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                # Try to extract key points (right and left)
                try:
                    keypoints = {}
                    for name in [
                        "RIGHT_WRIST", "LEFT_WRIST",
                        "RIGHT_ELBOW", "LEFT_ELBOW",
                        "RIGHT_SHOULDER", "LEFT_SHOULDER",
                        "RIGHT_HIP", "LEFT_HIP",
                        "NOSE"
                    ]:
                        idx = getattr(self.classifier.mp_pose.PoseLandmark, name).value
                        keypoints[name] = {
                            "x": lm[idx].x,
                            "y": lm[idx].y,
                            "visibility": getattr(lm[idx], "visibility", 1.0)
                        }
                    record["landmarks"] = keypoints
                except Exception:
                    record["landmarks"] = None

            self.frames.append(record)
            frame_idx += 1

            if frame_idx % 50 == 0:
                print(f"[extract_frames] processed {frame_idx} frames")

        cap.release()
        print(f"[extract_frames] Done. Total processed frames: {len(self.frames)}")
        # compute normalization and velocities next
        self._compute_normalized_metrics()
        return self.frames

    # Stage 2: normalization & velocities
    def _compute_normalized_metrics(self):
        """
        For each frame with landmarks, compute:
         - torso_length (shoulder to hip)
         - shoulder_width
         - normalized wrist/elbow/head heights relative to torso
         - wrist/elbow x-offset relative to shoulder center and normalized by shoulder_width
         - placeholder for velocities (computed next)
        """
        for rec in self.frames:
            lm = rec["landmarks"]
            rec.update({
                "torso_length": None,
                "shoulder_width": None,
                "shoulder_center_x": None,
                "dominant_hand": None,  # determined later
                "wrist_y_norm": None,
                "elbow_y_norm": None,
                "wrist_x_offset_norm": None,
                "elbow_x_offset_norm": None,
            })
            if lm is None:
                continue
            rs = lm["RIGHT_SHOULDER"]
            ls = lm["LEFT_SHOULDER"]
            rh = lm["RIGHT_HIP"]
            lh = lm["LEFT_HIP"]
            nose = lm["NOSE"]
            rw = lm["RIGHT_WRIST"]
            re = lm["RIGHT_ELBOW"]
            lw = lm["LEFT_WRIST"]
            le = lm["LEFT_ELBOW"]

            # torso length approximate (average shoulders to average hips)
            shoulder_y = 0.5 * (rs["y"] + ls["y"])
            hip_y = 0.5 * (rh["y"] + lh["y"])
            torso_length = abs(shoulder_y - hip_y) + 1e-6
            shoulder_width = abs(rs["x"] - ls["x"]) + 1e-6
            shoulder_center_x = 0.5 * (rs["x"] + ls["x"])

            rec["torso_length"] = torso_length
            rec["shoulder_width"] = shoulder_width
            rec["shoulder_center_x"] = shoulder_center_x

            # normalize wrist/elbow vertical position by torso length relative to hip
            # hip center y:
            hip_center_y = 0.5 * (rh["y"] + lh["y"])
            # use right side by default; we'll pick dominant side later
            rec["right_wrist_y_norm"] = (rw["y"] - hip_center_y) / torso_length
            rec["right_elbow_y_norm"] = (re["y"] - hip_center_y) / torso_length
            rec["left_wrist_y_norm"] = (lw["y"] - hip_center_y) / torso_length
            rec["left_elbow_y_norm"] = (le["y"] - hip_center_y) / torso_length

            # horizontal offsets relative to shoulder center and normalized by shoulder width
            rec["right_wrist_x_offset"] = abs(rw["x"] - shoulder_center_x) / shoulder_width
            rec["left_wrist_x_offset"] = abs(lw["x"] - shoulder_center_x) / shoulder_width
            rec["nose_y_norm"] = (nose["y"] - hip_center_y) / torso_length

            # copy raw points for velocity/comparison
            rec["right_wrist_xy"] = (rw["x"], rw["y"])
            rec["left_wrist_xy"] = (lw["x"], lw["y"])
            rec["right_elbow_xy"] = (re["x"], re["y"])
            rec["left_elbow_xy"] = (le["x"], le["y"])

        # Now compute velocities (frame-to-frame deltas) and pose_deltas
        prev = None
        for i, rec in enumerate(self.frames):
            rec["vel_wrist_y"] = 0.0
            rec["vel_wrist_x"] = 0.0
            rec["pose_delta"] = 0.0
            if prev and rec["landmarks"] and prev["landmarks"]:
                # velocity for dominant detection use both sides
                # delta of wrist y in normalized coordinates (use average torso normalization)
                prev_torso = prev.get("torso_length", 1.0)
                cur_torso = rec.get("torso_length", 1.0)
                # compute using raw y coordinates (normalized by current torso)
                prev_rw_y = prev.get("right_wrist_xy", (0,0))[1]
                cur_rw_y = rec.get("right_wrist_xy", (0,0))[1]
                # convert to normalized distances by torso of current frame
                rec["vel_wrist_y"] = (cur_rw_y - prev_rw_y) / (cur_torso + 1e-6)
                rec["vel_wrist_x"] = (rec.get("right_wrist_xy", (0,0))[0] - prev.get("right_wrist_xy",(0,0))[0]) / (rec.get("shoulder_width",1e-6))
                # pose_delta: L2 across key points (right wrist/elbow/shoulder)
                pts_cur = np.array([
                    rec.get("right_wrist_xy",[0,0]),
                    rec.get("right_elbow_xy",[0,0]),
                    (rec.get("shoulder_center_x",0), 0)
                ]).reshape(-1)
                pts_prev = np.array([
                    prev.get("right_wrist_xy",[0,0]),
                    prev.get("right_elbow_xy",[0,0]),
                    (prev.get("shoulder_center_x",0), 0)
                ]).reshape(-1)
                rec["pose_delta"] = float(np.linalg.norm(pts_cur - pts_prev))
            prev = rec

        # Smooth confidences (simple moving average)
        self._smooth_confidences()

        # Determine dominant hand (use average wrist positions over frames with landmarks)
        self._determine_dominant_hand()

    def _smooth_confidences(self):
        # moving average of phase confidences across last self.smooth_window frames
        q = deque(maxlen=self.smooth_window)
        for rec in self.frames:
            q.append(rec["phase_conf"])
            rec["phase_conf_smooth"] = float(np.mean(q))

    def _determine_dominant_hand(self):
        # Use aggregate: the wrist that is lower (smaller y normalized) on average is likely the shooting hand
        right_vals = []
        left_vals = []
        for rec in self.frames:
            if rec["landmarks"] is None: 
                continue
            if "right_wrist_y_norm" in rec:
                right_vals.append(rec["right_wrist_y_norm"])
                left_vals.append(rec["left_wrist_y_norm"])
        if len(right_vals) < 3:
            self.dominant = "right"  # default
            return
        right_med = np.nanmedian(right_vals)
        left_med = np.nanmedian(left_vals)
        self.dominant = "right" if right_med < left_med else "left"
        print(f"[dominant_hand] determined dominant hand: {self.dominant}")

    # Candidate scoring
    def _collect_phase_candidates(self):
        """
        Build candidate lists for phases: 'Shot pocket', 'Set point', 'Follow through'
        Each candidate contains:
          - frame_idx, phase_conf_smooth, normalized heights, velocities, forwardness, pose_delta
        """
        pockets = []
        sets = []
        fts = []
        for rec in self.frames:
            if rec["landmarks"] is None:
                continue
            phase_name = rec["phase_raw"]
            conf = rec.get("phase_conf_smooth", rec.get("phase_conf", 0.0))
            # pick dominant side's normalized metrics
            if self.dominant == "right":
                wrist_y_norm = rec.get("right_wrist_y_norm")
                elbow_y_norm = rec.get("right_elbow_y_norm")
                wrist_x_offset = rec.get("right_wrist_x_offset")
                wrist_xy = rec.get("right_wrist_xy")
                elbow_xy = rec.get("right_elbow_xy")
            else:
                wrist_y_norm = rec.get("left_wrist_y_norm")
                elbow_y_norm = rec.get("left_elbow_y_norm")
                wrist_x_offset = rec.get("left_wrist_x_offset")
                wrist_xy = rec.get("left_wrist_xy")
                elbow_xy = rec.get("left_elbow_xy")

            candidate = {
                "frame_idx": rec["frame_idx"],
                "timestamp": rec["timestamp"],
                "conf": conf,
                "wrist_y_norm": wrist_y_norm,
                "elbow_y_norm": elbow_y_norm,
                "wrist_x_offset": wrist_x_offset,
                "vel_y": rec.get("vel_wrist_y", 0.0),
                "vel_x": rec.get("vel_wrist_x", 0.0),
                "pose_delta": rec.get("pose_delta", 0.0),
                "frame": rec["frame"]
            }

            # bucket by raw label (we allow off-labels, but prefer matching labels)
            if "pocket" in phase_name.lower():
                pockets.append(candidate)
            elif "set" in phase_name.lower():
                sets.append(candidate)
            elif "follow" in phase_name.lower():
                fts.append(candidate)
            else:
                # also include high-confidence frames as potential candidates for any phase
                if conf > 0.7:
                    # heuristic: if wrist low -> pocket; if wrist ~ head -> set; if wrist high -> ft
                    if wrist_y_norm is None:
                        continue
                    if wrist_y_norm > 0.2:
                        pockets.append(candidate)
                    elif wrist_y_norm <= 0.2 and wrist_y_norm >= -0.1:
                        sets.append(candidate)
                    else:
                        fts.append(candidate)

        # Sort by descending confidence (best first)
        pockets.sort(key=lambda x: x["conf"], reverse=True)
        sets.sort(key=lambda x: x["conf"], reverse=True)
        fts.sort(key=lambda x: x["conf"], reverse=True)
        return pockets, sets, fts

    def _score_candidate(self, candidate, phase_type, reference=None):
        """
        Score a single candidate for a given phase.
        reference: for set -> pocket candidate to compare heights; for ft -> set candidate.
        We use a combination of classifier confidence + heuristics:
        - pocket: prefers lower wrist_y_norm, positive upward velocity soon after (handled in sequence scoring)
        - set: prefers wrist near head (~0 to -0.15), low vel_y (pause), low pose_delta
        - ft: prefers wrist above set (more negative y_norm), low vel, forwardness (vel_x or x offset)
        """
        score = 0.0
        conf = candidate["conf"]
        score += conf * 50.0  # classifier confidence weighted heavily

        wy = candidate.get("wrist_y_norm", 0.0)
        vel = candidate.get("vel_y", 0.0)
        pd = candidate.get("pose_delta", 0.0)
        xoff = candidate.get("wrist_x_offset", 0.0)

        if phase_type == "pocket":
            # ideal pocket wrist around 0.1..0.25 (slightly above hip)
            ideal = 0.15
            tol = 0.25
            dist = abs(wy - ideal)
            score += max(0, (tol - dist)) * 20.0
            # pocket tends to have upward motion after it (vel < 0 means upward because y decreases up)
            # but for single-frame scoring we lightly reward small upward movement in immediate next frames handled later
            score += max(0, -vel) * 10.0  # negative vel (upward) is good
        elif phase_type == "set":
            # set point wrist around slightly above head: approx -0.05
            ideal = -0.05
            tol = 0.20
            dist = abs(wy - ideal)
            score += max(0, (tol - dist)) * 50.0
            # reward low velocity (a pause) but allow some micro-movement
            score += max(0, (0.3 - abs(vel))) * 35.0
            # reward stable pose (low pose_delta) but allow natural sway
            score += max(0, (0.25 - pd)) * 25.0
            # slightly prefer centered positions (xoff small)
            score += max(0, (0.6 - xoff)) * 15.0
        elif phase_type == "ft":
            # follow through expect wrist slightly above head (negative small), and forward extension
            ideal = -0.08
            tol = 0.28
            dist = abs(wy - ideal)
            score += max(0, (tol - dist)) * 50.0
            # reward very low velocity (holding)
            score += max(0, (0.15 - abs(vel))) * 30.0
            # reward forwardness: small x offset in direction of forward (we don't know orientation, so prefer non-centered)
            score += (xoff) * 10.0
            # reward low pose delta (held)
            score += max(0, (0.2 - pd)) * 20.0

        # small penalty for huge pose deltas (noisy)
        score -= min(pd * 10.0, 10.0)
        return float(score)

    # Sequence building & selection
    def find_best_sequence(self, max_candidates=8):
        """
        Build best chronological sequences (pocket -> set -> ft), encourage order via bonuses,
        return best 3-frame sequence or fallback to 2-frame / 1-frame.
        """
        pockets, sets, fts = self._collect_phase_candidates()
        if not (pockets or sets or fts):
            return None

        # limit candidates to top-k for combinatorial tractability
        pockets = pockets[:max_candidates]
        sets = sets[:max_candidates]
        fts = fts[:max_candidates]

        best_seq = None
        best_score = -1e9

        # Try full triplets
        for p in pockets:
            for s in sets:
                if s["frame_idx"] <= p["frame_idx"]:
                    continue
                for f in fts:
                    if f["frame_idx"] <= s["frame_idx"]:
                        continue
                    # compute individual scores
                    sp = self._score_candidate(p, "pocket")
                    ss = self._score_candidate(s, "set", reference=p)
                    sf = self._score_candidate(f, "ft", reference=s)

                    # chronology bonus (increase if proper chronological order)
                    chrono_bonus = 0.0
                    # prefer reasonably spaced frames (set some expected time spacing)
                    time_gap_ps = s["timestamp"] - p["timestamp"]
                    time_gap_sf = f["timestamp"] - s["timestamp"]
                    # bonus if gaps look realistic (nonzero and not huge)
                    if 0.03 < time_gap_ps < 2.5:
                        chrono_bonus += 15.0
                    if 0.03 < time_gap_sf < 2.5:
                        chrono_bonus += 20.0

                    # height spacing bonus: set should be above pocket, ft above set
                    height_bonus = 0.0
                    if s["wrist_y_norm"] is not None and p["wrist_y_norm"] is not None:
                        if s["wrist_y_norm"] < p["wrist_y_norm"]:
                            height_bonus += 10.0
                    if f["wrist_y_norm"] is not None and s["wrist_y_norm"] is not None:
                        if f["wrist_y_norm"] < s["wrist_y_norm"]:
                            height_bonus += 12.0

                    # motion pause bonus: set should have low vel (pause)
                    motion_bonus = 0.0
                    if abs(s.get("vel_y", 0.0)) < 0.06 and s.get("pose_delta", 1.0) < 0.12:
                        motion_bonus += 20.0
                    # ft should be relatively held
                    if abs(f.get("vel_y", 0.0)) < 0.05:
                        motion_bonus += 12.0

                    total = sp + ss + sf + chrono_bonus + height_bonus + motion_bonus

                    # small penalty if chosen frames are extremely close (likely same frame)
                    if (s["frame_idx"] - p["frame_idx"]) < 2:
                        total -= 10
                    if (f["frame_idx"] - s["frame_idx"]) < 2:
                        total -= 10

                    if total > best_score:
                        best_score = total
                        best_seq = {
                            "pocket": p,
                            "set": s,
                            "ft": f,
                            "score": total
                        }

        # If we found a good triplet, return it
        if best_seq and best_score > 20.0:
            return ("triplet", best_seq)

        # Try best pair combos: pocket+set, set+ft, pocket+ft
        best_pair = None
        best_pair_score = -1e9
        pairs = []
        # pocket + set
        for p in pockets:
            for s in sets:
                if s["frame_idx"] <= p["frame_idx"]:
                    continue
                score = self._score_candidate(p, "pocket") + self._score_candidate(s, "set")
                # encourage height and pause
                if s["wrist_y_norm"] is not None and p["wrist_y_norm"] is not None and s["wrist_y_norm"] < p["wrist_y_norm"]:
                    score += 12.0
                if abs(s.get("vel_y",0)) < 0.1:
                    score += 12.0
                if score > best_pair_score:
                    best_pair_score = score
                    best_pair = ("pocket_set", {"pocket": p, "set": s, "score": score})
        # set + ft
        for s in sets:
            for f in fts:
                if f["frame_idx"] <= s["frame_idx"]:
                    continue
                score = self._score_candidate(s, "set") + self._score_candidate(f, "ft")
                if f["wrist_y_norm"] is not None and s["wrist_y_norm"] is not None and f["wrist_y_norm"] < s["wrist_y_norm"]:
                    score += 8.0
                if abs(f.get("vel_y",0)) < 0.05:
                    score += 8.0
                if score > best_pair_score:
                    best_pair_score = score
                    best_pair = ("set_ft", {"set": s, "ft": f, "score": score})
        # pocket + ft
        for p in pockets:
            for f in fts:
                if f["frame_idx"] <= p["frame_idx"]:
                    continue
                score = self._score_candidate(p, "pocket") + self._score_candidate(f, "ft")
                if f["wrist_y_norm"] is not None and p["wrist_y_norm"] is not None and f["wrist_y_norm"] < p["wrist_y_norm"]:
                    score += 5.0
                if score > best_pair_score:
                    best_pair_score = score
                    best_pair = ("pocket_ft", {"pocket": p, "ft": f, "score": score})

        if best_pair and best_pair_score > 15.0:
            return ("pair", best_pair)

        # Otherwise choose the single best frame across all candidates
        all_candidates = pockets + sets + fts
        if not all_candidates:
            return None
        best_single = max(all_candidates, key=lambda c: c["conf"])
        return ("single", {"single": best_single, "score": best_single["conf"]})

    # Save result frames
    def save_sequence_frames(self, sequence):
        """
        sequence returned from find_best_sequence:
         - ("triplet", {"pocket":..., "set":..., "ft":..., "score":...})
         - ("pair",  ("pocket_set"|..., {...}))
         - ("single", {...})
        """
        if sequence is None:
            print("[save_sequence_frames] No candidates found.")
            return

        kind, data = sequence
        saved_paths = []
        if kind == "triplet":
            seq = data
            for label in ["pocket", "set", "ft"]:
                cand = seq[label]
                conf = cand["conf"]
                fname = f"{label}_{cand['frame_idx']}_conf{conf:.2f}.jpg"
                path = self.session_dir / fname
                cv2.imwrite(str(path), cand["frame"])
                saved_paths.append(path)
            print(f"[save_sequence_frames] Saved triplet. Score: {seq['score']:.2f}")
        elif kind == "pair":
            pair_type, payload = data
            for label, cand in payload.items():
                if label == "score":
                    continue
                conf = cand["conf"]
                fname = f"{label}_{cand['frame_idx']}_conf{conf:.2f}.jpg"
                path = self.session_dir / fname
                cv2.imwrite(str(path), cand["frame"])
                saved_paths.append(path)
            print(f"[save_sequence_frames] Saved pair ({pair_type}). Score: {payload['score']:.2f}")
        elif kind == "single":
            payload = data
            cand = payload["single"]
            fname = f"single_{cand['frame_idx']}_conf{cand['conf']:.2f}.jpg"
            path = self.session_dir / fname
            cv2.imwrite(str(path), cand["frame"])
            saved_paths.append(path)
            print(f"[save_sequence_frames] Saved single. Conf: {cand['conf']:.2f}")

        return saved_paths

    # High-level run
    def process_and_save(self):
        self.extract_frames()
        seq = self.find_best_sequence()
        saved = self.save_sequence_frames(seq)
        print("[process_and_save] Done.")
        return seq, saved


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python video_processor.py <video_path> <output_dir>")
        sys.exit(1)
    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    vp = VideoProcessor(video_path, output_dir)
    seq, paths = vp.process_and_save()
    #print("Result:", seq)
    if paths:
        print("Saved files:", paths)
