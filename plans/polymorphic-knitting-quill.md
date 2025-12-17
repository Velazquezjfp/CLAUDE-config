# Face Module v4 Implementation Plan

## Final Decisions (Confirmed with User)

| Decision | Choice |
|----------|--------|
| Primary Detector | **MediaPipe Pose** (32k stars, Google maintained) |
| Fallback | YOLOv5 CrowdHuman (optional, for future if needed) |
| Min Size Threshold | 10% of original image height |
| Blur Mode Control | API header (`blur-mode: standard` or `fast`) |
| Fallback Trigger | No detection OR confidence < 0.5 |
| Fallback Action | Blur top 25% if standing (H > W * 1.5) |

---

## Problem Statement

Current `face_detect.py` using MTCNN fails on:
- Low resolution person subframes (30-56px width in test)
- Side profiles and back of heads
- Test showed 0 faces blurred despite 6 persons detected

## Recommended Solution: MediaPipe Pose + YOLOv5 CrowdHuman Hybrid

### Why This Approach?

**MediaPipe Pose** (Primary):
- 32.3k GitHub stars, actively maintained by Google (v0.10.26 July 2025)
- Detects head position from body landmarks (nose, eyes, ears)
- Works even when person facing away (derives from body pose)
- Lightweight: `pip install mediapipe` - no large model downloads
- Fast inference

**YOLOv5 CrowdHuman** (Secondary/Alternative):
- Specifically trained for head detection on CrowdHuman dataset
- Provides bounding boxes (vs landmarks from MediaPipe)
- Can be used if MediaPipe Pose fails on very small subframes

---

## Architecture Overview

```
app.py
  └── detector.py (YOLOv7-E6) → person bounding boxes
        └── face_module/
              ├── __init__.py
              ├── head_detector.py    # Main orchestrator
              ├── pose_head.py        # MediaPipe Pose head extraction
              ├── yolo_head.py        # YOLOv5 CrowdHuman (optional)
              └── blur_utils.py       # Blurring utilities
```

---

## Files to Create

### 1. `face_module/__init__.py`
Export main function: `blur_heads(person_coordinates, image_path, original_size, mode='standard')`

### 2. `face_module/head_detector.py`
Main orchestrator with two modes:
- **standard**: Process all person subframes ≥ 10% image height
- **fast**: Only process larger subframes, blackout smaller ones

```python
def blur_heads(person_coordinates, image_path, original_size, mode='standard'):
    """
    Args:
        person_coordinates: List of [x, y, w, h] from detector.py
        image_path: Path to saved image (./image.jpg)
        original_size: (width, height) of original image before any processing
        mode: 'standard' or 'fast'

    Returns:
        base64 encoded blurred image or None
    """
```

### 3. `face_module/pose_head.py`
MediaPipe Pose-based head detection:
- Extract head region from pose landmarks (nose, eyes, ears)
- Calculate bounding box around head landmarks
- Confidence threshold: 0.5 for visibility

### 4. `face_module/blur_utils.py`
- Gaussian blur application
- Fallback blur (top 25% for standing persons)
- Base64 encoding

---

## Processing Pipeline

```
For each person bounding box:
1. Calculate relative height: person_h / original_image_h
2. Filter by threshold:
   - 'fast' mode: Skip if relative_height < 10%
   - 'standard' mode: Process all

3. Extract subframe from image

4. Run MediaPipe Pose:
   - If landmarks detected with confidence > 0.5:
     → Calculate head bounding box from landmarks
     → Apply Gaussian blur to head region

   - If no detection OR confidence < 0.5:
     → Check if standing person (H > W * 1.5)
     → If yes: blur top 25% of bounding box
     → If no: skip (likely crouching/vehicle)

5. Return base64 encoded result image
```

---

## Files to Modify

### `app.py` (lines 57-79)
Replace:
```python
from face_detect import face_detect
# ...
blurred_image_base64 = face_detect(person_coordinates_filtered)
```

With:
```python
from face_module import blur_heads
# ...
original_size = get_original_image_size()  # Need to track this
blurred_image_base64 = blur_heads(
    person_coordinates_filtered,
    './image.jpg',
    original_size,
    mode='standard'  # or from header
)
```

### `detector.py` (line 145)
Add original image size to return value or save it for reference.

---

## Dependencies Changes

### Remove from `requirements.txt`:
```
facenet-pytorch==2.6.0  # MTCNN - no longer needed
```

### Add to `requirements.txt`:
```
mediapipe>=0.10.0  # Google's pose estimation
```

### Optional (for YOLOv5 head detection fallback):
Model weights from: https://github.com/MahenderAutonomo/yolov5-crowdhuman

---

## Size Threshold Logic

Using **relative sizes** to handle image processing transformations:

```python
# In head_detector.py
MIN_RELATIVE_HEIGHT = 0.10  # 10% of original image height

def should_process(person_bbox, original_size, mode):
    _, _, pw, ph = person_bbox
    original_w, original_h = original_size

    relative_height = ph / original_h

    if mode == 'fast' and relative_height < MIN_RELATIVE_HEIGHT:
        return False
    return True
```

---

## Fallback Logic

```python
def apply_fallback_blur(image, bbox):
    """
    Blur top 25% of bounding box for standing persons.
    Only applies if: height > width * 1.5 (standing)
    """
    x, y, w, h = bbox

    if h > w * 1.5:  # Standing person
        head_height = int(h * 0.25)
        head_region = image[y:y+head_height, x:x+w]
        blurred = cv2.GaussianBlur(head_region, (99, 99), 30)
        image[y:y+head_height, x:x+w] = blurred
        return True
    return False
```

---

## version4.md Tracking File

Create `version4.md` at project root with:

### Dependencies to REMOVE:
- `facenet-pytorch==2.6.0` (MTCNN)

### Files to REMOVE:
- `face_detect.py` (replaced by face_module/)

### Dependencies to ADD:
- `mediapipe>=0.10.0`

### Files to ADD:
- `face_module/__init__.py`
- `face_module/head_detector.py`
- `face_module/pose_head.py`
- `face_module/blur_utils.py`
- `face_module/yolo_head.py` (optional)

---

## Implementation Order

1. Create `face_module/` directory structure
2. Implement `blur_utils.py` (blurring + fallback + encoding)
3. Implement `pose_head.py` (MediaPipe Pose integration)
4. Implement `head_detector.py` (orchestrator with modes)
5. Update `__init__.py` exports
6. Modify `app.py` to use new module
7. Update `detector.py` to track original image size
8. Update `requirements.txt`
9. Create `version4.md` tracking file
10. Test with `test_api.py`
11. Remove old `face_detect.py`

---

## API Headers Update

**New header: `blur-mode`**
- `blur-mode: standard` (default) - process all person subframes
- `blur-mode: fast` - skip subframes where person height < 10% of original image

Update `app.py` to read this header:
```python
blur_mode = request.headers.get('blur-mode', 'standard')
```

---

## Research Sources

- [MediaPipe Pose](https://github.com/google-ai-edge/mediapipe) - 32.3k stars
- [YOLOv5 CrowdHuman](https://github.com/MahenderAutonomo/yolov5-crowdhuman) - head detection
- [InsightFace](https://github.com/deepinsight/insightface) - 27.2k stars (SCRFD/RetinaFace)
- [SCUT-HEAD Dataset](https://github.com/HCIILAB/SCUT-HEAD-Dataset-Release) - head detection benchmark
