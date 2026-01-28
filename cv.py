import json
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dataclasses import dataclass
import os
from datetime import datetime
from pdf2image import convert_from_path

OUTPUT_DIR = "cv_analysis"
IMAGES_DIR = "cv_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


def convert_pdf_to_images(pdf_path: str) -> List[str]:
    """Convert PDF to PNG images for analysis"""
    print(f"Converting PDF to images: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    pages = convert_from_path(pdf_path, dpi=300)
    image_paths = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, page in enumerate(pages):
        img_path = os.path.join(IMAGES_DIR, f"page_{i+1}_{timestamp}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)
        print(f"  Saved page {i+1}: {img_path}")
    
    print(f"Converted {len(pages)} pages to images")
    return image_paths


@dataclass
class BoundingBox:
    """Bounding box with classification"""
    x: int
    y: int
    width: int
    height: int
    feature_type: str  
    confidence: float
    properties: Dict[str, Any] = None

@dataclass
class FeatureAnalysis:
    """Analysis result for a specific feature"""
    bbox: BoundingBox
    rule_compliance: Dict[str, str]  
    measurements: Dict[str, float]
    notes: List[str]


def preprocess_image(image_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load and preprocess image for feature detection"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    cleaned = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(cleaned, (5, 5), 0)
    
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_clean)
    
    edges = cv2.Canny(binary, 50, 150)
    
    return img, gray, edges

def detect_walls(edges: np.ndarray, min_length: int = 100) -> List[BoundingBox]:
    """Detect wall sections using line detection - focus on main geometry"""
    bboxes = []
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=200, 
                           minLineLength=min_length, maxLineGap=20)
    
    if lines is not None:
]        filtered_lines = []
        img_height, img_width = edges.shape
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = float(np.sqrt((x2-x1)**2 + (y2-y1)**2))
            
            if length < min_length:
                continue
                
            margin = 50
            if (x1 < margin or x2 < margin or y1 < margin or y2 < margin or
                x1 > img_width-margin or x2 > img_width-margin or 
                y1 > img_height-margin or y2 > img_height-margin):
                continue
            
            filtered_lines.append(line)
        
        filtered_lines = filtered_lines[:15] 
        
        for i, line in enumerate(filtered_lines):
            x1, y1, x2, y2 = line[0]
            
            padding = 30
            x = min(x1, x2) - padding
            y = min(y1, y2) - padding
            width = abs(x2 - x1) + 2 * padding
            height = abs(y2 - y1) + 2 * padding
            
            length = float(np.sqrt((x2-x1)**2 + (y2-y1)**2))
            angle = float(np.arctan2(y2-y1, x2-x1) * 180 / np.pi)
            
            bbox = BoundingBox(
                x=max(0, int(x)), y=max(0, int(y)), 
                width=int(width), height=int(height),
                feature_type="wall",
                confidence=0.8,
                properties={"length": length, "angle": angle}
            )
            bboxes.append(bbox)
    
    return bboxes

def detect_corners(edges: np.ndarray) -> List[BoundingBox]:
    """Detect corner features using Harris corner detection - avoid text"""
    bboxes = []
    
    corners = cv2.cornerHarris(edges, 2, 3, 0.04)
    corners = cv2.dilate(corners, None)
    
    corner_coords = np.where(corners > 0.1 * corners.max())
    
    img_height, img_width = edges.shape
    margin = 80
    
    filtered_corners = []
    for y, x in zip(corner_coords[0], corner_coords[1]):
        if (x < margin or y < margin or 
            x > img_width-margin or y > img_height-margin):
            continue
        filtered_corners.append((y, x))
    
    if len(filtered_corners) > 10:
        corner_strengths = [corners[y, x] for y, x in filtered_corners]
        top_indices = np.argsort(corner_strengths)[-10:]
        filtered_corners = [filtered_corners[i] for i in top_indices]
    
    for y, x in filtered_corners:
        size = 50
        bbox = BoundingBox(
            x=max(0, int(x-size//2)), y=max(0, int(y-size//2)), 
            width=size, height=size,
            feature_type="corner",
            confidence=0.7,
            properties={"corner_response": float(corners[y, x])}
        )
        bboxes.append(bbox)
    
    return bboxes

def detect_junctions(edges: np.ndarray) -> List[BoundingBox]:
    """Detect T-junctions and cross-junctions"""
    bboxes = []
    
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (15, 15))
    junctions = cv2.morphologyEx(edges, cv2.MORPH_TOPHAT, kernel)
    
    contours, _ = cv2.findContours(junctions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]  # Max 10 junctions
    
    for contour in contours:
        if cv2.contourArea(contour) > 200:  # Higher threshold
            x, y, w, h = cv2.boundingRect(contour)
            
            padding = 30
            bbox = BoundingBox(
                x=max(0, int(x-padding)), y=max(0, int(y-padding)),
                width=int(w+2*padding), height=int(h+2*padding),
                feature_type="junction",
                confidence=0.6,
                properties={"area": float(cv2.contourArea(contour))}
            )
            bboxes.append(bbox)
    
    return bboxes

def detect_ribs(edges: np.ndarray) -> List[BoundingBox]:
    """Detect rib structures"""
    bboxes = []
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, 
                           minLineLength=30, maxLineGap=5)
    
    if lines is not None:
        lines = lines[:30]
        
        processed = set()
        for i, line1 in enumerate(lines):
            if i in processed:
                continue
                
            x1, y1, x2, y2 = line1[0]
            angle1 = np.arctan2(y2-y1, x2-x1)
            
            for j, line2 in enumerate(lines[i+1:], i+1):
                if j in processed:
                    continue
                    
                x3, y3, x4, y4 = line2[0]
                angle2 = np.arctan2(y4-y3, x4-x3)
                
                if abs(angle1 - angle2) < 0.2:  
                    dist = abs((y2-y1)*x3 - (x2-x1)*y3 + x2*y1 - y2*x1) / np.sqrt((y2-y1)**2 + (x2-x1)**2)
                    
                    if 10 < dist < 100:  
                        all_x = [x1, x2, x3, x4]
                        all_y = [y1, y2, y3, y4]
                        
                        padding = 15
                        bbox = BoundingBox(
                            x=max(0, int(min(all_x)-padding)), 
                            y=max(0, int(min(all_y)-padding)),
                            width=int(max(all_x)-min(all_x)+2*padding),
                            height=int(max(all_y)-min(all_y)+2*padding),
                            feature_type="rib",
                            confidence=0.7,
                            properties={"spacing": float(dist), "angle": float(angle1)}
                        )
                        bboxes.append(bbox)
                        processed.add(i)
                        processed.add(j)
                        break
    
    return bboxes[:5] 

def detect_bosses(gray: np.ndarray) -> List[BoundingBox]:
    """Detect boss/pad features using blob detection"""
    bboxes = []
    
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 1000 
    params.maxArea = 10000
    params.filterByCircularity = False
    params.filterByConvexity = True
    params.minConvexity = 0.7 
    
    detector = cv2.SimpleBlobDetector_create(params)
    
    keypoints = detector.detect(gray)
    
    keypoints = sorted(keypoints, key=lambda kp: kp.size, reverse=True)[:5]
    
    for kp in keypoints:
        x, y = int(kp.pt[0]), int(kp.pt[1])
        size = int(kp.size)
        
        bbox = BoundingBox(
            x=max(0, x-size), y=max(0, y-size),
            width=2*size, height=2*size,
            feature_type="boss",
            confidence=0.6,
            properties={"size": float(kp.size), "response": float(kp.response)}
        )
        bboxes.append(bbox)
    
    return bboxes



def analyze_wall_thickness(bbox: BoundingBox, gray: np.ndarray) -> Dict[str, float]:
    """Analyze wall thickness in bounding box region"""
    roi = gray[bbox.y:bbox.y+bbox.height, bbox.x:bbox.x+bbox.width]
    
    edges = cv2.Canny(roi, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    thicknesses = []
    for contour in contours:
        if len(contour) > 10:
            _, _, w, h = cv2.boundingRect(contour)
            thickness = min(w, h)  
            thicknesses.append(float(thickness))
    
    if thicknesses:
        return {
            "avg_thickness": float(np.mean(thicknesses)),
            "min_thickness": float(np.min(thicknesses)),
            "max_thickness": float(np.max(thicknesses)),
            "thickness_variation": float(np.std(thicknesses))
        }
    else:
        return {"avg_thickness": 0.0, "min_thickness": 0.0, "max_thickness": 0.0, "thickness_variation": 0.0}

def analyze_corner_angles(bbox: BoundingBox, edges: np.ndarray) -> Dict[str, float]:
    """Analyze corner angles in bounding box region"""
    roi = edges[bbox.y:bbox.y+bbox.height, bbox.x:bbox.x+bbox.width]
    
    lines = cv2.HoughLinesP(roi, 1, np.pi/180, threshold=30, 
                           minLineLength=20, maxLineGap=5)
    
    angles = []
    if lines is not None and len(lines) >= 2:
        for i, line1 in enumerate(lines):
            x1, y1, x2, y2 = line1[0]
            angle1 = np.arctan2(y2-y1, x2-x1)
            
            for line2 in lines[i+1:]:
                x3, y3, x4, y4 = line2[0]
                angle2 = np.arctan2(y4-y3, x4-x3)
                
                angle_diff = abs(angle1 - angle2) * 180 / np.pi
                if angle_diff > 90:
                    angle_diff = 180 - angle_diff
                
                angles.append(float(angle_diff))
    
    if angles:
        return {
            "min_angle": float(np.min(angles)),
            "avg_angle": float(np.mean(angles)),
            "acute_angles": int(sum(1 for a in angles if a < 90))
        }
    else:
        return {"min_angle": 90.0, "avg_angle": 90.0, "acute_angles": 0}

def analyze_junction_complexity(bbox: BoundingBox, edges: np.ndarray) -> Dict[str, int]:
    """Analyze junction complexity (number of intersecting sections)"""
    roi = edges[bbox.y:bbox.y+bbox.height, bbox.x:bbox.x+bbox.width]
    
    lines = cv2.HoughLinesP(roi, 1, np.pi/180, threshold=20, 
                           minLineLength=15, maxLineGap=3)
    
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2-y1, x2-x1) * 180 / np.pi
            if angle < 0:
                angle += 180
            angles.append(float(angle))
        
        unique_sections = 0
        processed = [False] * len(angles)
        
        for i, angle1 in enumerate(angles):
            if not processed[i]:
                unique_sections += 1
                processed[i] = True
                
                for j, angle2 in enumerate(angles[i+1:], i+1):
                    if not processed[j] and abs(angle1 - angle2) < 15:
                        processed[j] = True
        
        return {
            "total_lines": int(len(lines)),
            "unique_sections": int(unique_sections),
            "complexity_score": int(unique_sections)
        }
    else:
        return {"total_lines": 0, "unique_sections": 0, "complexity_score": 0}


def check_rule_compliance(analysis: FeatureAnalysis) -> Dict[str, str]:
    """Check casting design rule compliance for analyzed feature"""
    compliance = {}
    bbox = analysis.bbox
    measurements = analysis.measurements
    
    if bbox.feature_type == "wall":
        if "thickness_variation" in measurements:
            variation = measurements["thickness_variation"]
            if variation < 2.0:
                compliance["R5"] = "Yes"
            elif variation > 5.0:
                compliance["R5"] = "No"
            else:
                compliance["R5"] = "Needs Review"
        
        if "max_thickness" in measurements and "min_thickness" in measurements:
            ratio = measurements["max_thickness"] / max(measurements["min_thickness"], 1)
            if ratio < 2.0:
                compliance["R8"] = "Yes"
            elif ratio > 3.0:
                compliance["R8"] = "No"
            else:
                compliance["R8"] = "Needs Review"
    
    elif bbox.feature_type == "corner":
        if "acute_angles" in measurements:
            acute_count = measurements["acute_angles"]
            min_angle = measurements.get("min_angle", 90)
            
            if acute_count == 0 and min_angle > 45:
                compliance["R3"] = "Yes"
                compliance["R7"] = "Yes"
            elif acute_count > 2 or min_angle < 30:
                compliance["R3"] = "No"
                compliance["R7"] = "No"
            else:
                compliance["R3"] = "Needs Review"
                compliance["R7"] = "Needs Review"
    
    elif bbox.feature_type == "junction":
        if "unique_sections" in measurements:
            sections = measurements["unique_sections"]
            if sections <= 2:
                compliance["R4"] = "Yes"
            elif sections > 3:
                compliance["R4"] = "No"
            else:
                compliance["R4"] = "Needs Review"
    
    elif bbox.feature_type == "rib":
        if "spacing" in bbox.properties:
            spacing = bbox.properties["spacing"]
            if 15 < spacing < 50:  # Reasonable rib spacing
                compliance["R9"] = "Yes"
            elif spacing < 10 or spacing > 80:
                compliance["R9"] = "No"
            else:
                compliance["R9"] = "Needs Review"
    
    elif bbox.feature_type == "boss":
        if "size" in bbox.properties:
            size = bbox.properties["size"]
            if size < 30: 
                compliance["R10"] = "Yes"
            elif size > 60:
                compliance["R10"] = "No"
            else:
                compliance["R10"] = "Needs Review"
    
    return compliance


def visualize_analysis(image_path: str, analyses: List[FeatureAnalysis], output_path: str):
    """Create visualization with bounding boxes and analysis results"""
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.imshow(img_rgb)
    
    colors = {
        "wall": "blue",
        "corner": "red", 
        "junction": "green",
        "rib": "orange",
        "boss": "purple"
    }
    
    for analysis in analyses:
        bbox = analysis.bbox
        color = colors.get(bbox.feature_type, "gray")
        
        rect = patches.Rectangle(
            (bbox.x, bbox.y), bbox.width, bbox.height,
            linewidth=2, edgecolor=color, facecolor='none'
        )
        ax.add_patch(rect)
        
        label = f"{bbox.feature_type}\n{bbox.confidence:.2f}"
        ax.text(bbox.x, bbox.y-5, label, color=color, fontsize=8, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
        
        compliance_text = []
        for rule_id, result in analysis.rule_compliance.items():
            symbol = "✓" if result == "Yes" else "✗" if result == "No" else "?"
            compliance_text.append(f"{rule_id}:{symbol}")
        
        if compliance_text:
            ax.text(bbox.x + bbox.width + 5, bbox.y + bbox.height//2, 
                   "\n".join(compliance_text), fontsize=6, 
                   bbox=dict(boxstyle="round,pad=0.2", facecolor="lightyellow", alpha=0.8))
    
    ax.set_title("Casting Design Analysis - Feature Detection & Rule Compliance")
    ax.axis('off')
    
    legend_elements = [patches.Patch(color=color, label=feature_type.title()) 
                      for feature_type, color in colors.items()]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def analyze_casting_image(image_path: str) -> List[FeatureAnalysis]:
    """Complete analysis pipeline for casting image"""
    print(f"Analyzing image: {os.path.basename(image_path)}")
    
    img, gray, edges = preprocess_image(image_path)
    
    print("  Detecting features...")
    all_bboxes = []
    all_bboxes.extend(detect_walls(edges))
    all_bboxes.extend(detect_corners(edges))
    all_bboxes.extend(detect_junctions(edges))
    all_bboxes.extend(detect_ribs(edges))
    all_bboxes.extend(detect_bosses(gray))
    
    print(f"  Found {len(all_bboxes)} features")
    
    analyses = []
    for bbox in all_bboxes:
        if bbox.feature_type == "wall":
            measurements = analyze_wall_thickness(bbox, gray)
        elif bbox.feature_type == "corner":
            measurements = analyze_corner_angles(bbox, edges)
        elif bbox.feature_type == "junction":
            measurements = analyze_junction_complexity(bbox, edges)
        else:
            measurements = {}
        
        analysis = FeatureAnalysis(
            bbox=bbox,
            rule_compliance={},
            measurements=measurements,
            notes=[]
        )
        
        analysis.rule_compliance = check_rule_compliance(analysis)
        
        analyses.append(analysis)
    
    return analyses

def analyze_pdf_document(pdf_path: str) -> Dict[str, Any]:
    """Analyze entire PDF document with multiple pages"""
    print(f"=== ANALYZING PDF DOCUMENT ===")
    print(f"PDF: {pdf_path}")
    
    image_paths = convert_pdf_to_images(pdf_path)
    
    all_analyses = {}
    total_features = 0
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n--- Analyzing Page {i} ---")
        page_analyses = analyze_casting_image(image_path)
        all_analyses[f"page_{i}"] = {
            "image_path": image_path,
            "analyses": page_analyses,
            "feature_count": len(page_analyses)
        }
        total_features += len(page_analyses)
    
    return {
        "pdf_path": pdf_path,
        "total_pages": len(image_paths),
        "total_features": total_features,
        "pages": all_analyses
    }

def save_comprehensive_report(document_analysis: Dict[str, Any]) -> Tuple[str, str]:
    """Save comprehensive analysis report and visualizations"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report_path = os.path.join(OUTPUT_DIR, f"pdf_analysis_{timestamp}.json")
    
    report_data = {
        "pdf_path": document_analysis["pdf_path"],
        "timestamp": timestamp,
        "total_pages": document_analysis["total_pages"],
        "total_features": document_analysis["total_features"],
        "pages": {}
    }
    
    for page_id, page_data in document_analysis["pages"].items():
        report_data["pages"][page_id] = {
            "image_path": page_data["image_path"],
            "feature_count": page_data["feature_count"],
            "features": [
                {
                    "type": a.bbox.feature_type,
                    "bbox": [a.bbox.x, a.bbox.y, a.bbox.width, a.bbox.height],
                    "confidence": a.bbox.confidence,
                    "measurements": a.measurements,
                    "rule_compliance": a.rule_compliance,
                    "properties": a.bbox.properties or {}
                }
                for a in page_data["analyses"]
            ]
        }
    
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    viz_path = os.path.join(OUTPUT_DIR, f"pdf_visualization_{timestamp}.png")
    
    num_pages = document_analysis["total_pages"]
    if num_pages == 1:
        rows, cols = 1, 1
    elif num_pages <= 2:
        rows, cols = 1, 2
    elif num_pages <= 4:
        rows, cols = 2, 2
    elif num_pages <= 6:
        rows, cols = 2, 3
    else:
        rows, cols = 3, 3  
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    if num_pages == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    colors = {
        "wall": "blue",
        "corner": "red", 
        "junction": "green",
        "rib": "orange",
        "boss": "purple"
    }
    
    for i, (page_id, page_data) in enumerate(document_analysis["pages"].items()):
        if i >= len(axes):
            break
            
        ax = axes[i]
        
        img = cv2.imread(page_data["image_path"])
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ax.imshow(img_rgb)
        
        for analysis in page_data["analyses"]:
            bbox = analysis.bbox
            color = colors.get(bbox.feature_type, "gray")
            
            rect = patches.Rectangle(
                (bbox.x, bbox.y), bbox.width, bbox.height,
                linewidth=1, edgecolor=color, facecolor='none'
            )
            ax.add_patch(rect)
            
            ax.text(bbox.x, bbox.y-2, bbox.feature_type[0].upper(), 
                   color=color, fontsize=6, weight='bold')
        
        ax.set_title(f"Page {i+1} ({page_data['feature_count']} features)", fontsize=10)
        ax.axis('off')
    
    for i in range(num_pages, len(axes)):
        axes[i].axis('off')
    
    fig.suptitle(f"PDF Casting Analysis - {document_analysis['total_features']} Total Features", 
                fontsize=14, y=0.98)
    
    legend_elements = [patches.Patch(color=color, label=f"{feature_type.title()}") 
                      for feature_type, color in colors.items()]
    fig.legend(handles=legend_elements, loc='lower center', ncol=len(colors), 
              bbox_to_anchor=(0.5, 0.02))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, bottom=0.1)
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return report_path, viz_path

def main():
    """Main function for CV-based casting analysis"""
    
    # Get input PDF path
    pdf_path = input("Enter path to casting drawing PDF: ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: File must be a PDF: {pdf_path}")
        return
    
    try:
        document_analysis = analyze_pdf_document(pdf_path)
        
        report_path, viz_path = save_comprehensive_report(document_analysis)
        
        print(f"\n=== ANALYSIS COMPLETE ===")
        print(f"PDF: {os.path.basename(pdf_path)}")
        print(f"Pages analyzed: {document_analysis['total_pages']}")
        print(f"Total features detected: {document_analysis['total_features']}")
        
        for page_id, page_data in document_analysis["pages"].items():
            page_num = page_id.split('_')[1]
            feature_counts = {}
            for analysis in page_data["analyses"]:
                ftype = analysis.bbox.feature_type
                feature_counts[ftype] = feature_counts.get(ftype, 0) + 1
            
            if feature_counts:
                features_str = ", ".join([f"{count} {ftype}" for ftype, count in feature_counts.items()])
                print(f"  Page {page_num}: {page_data['feature_count']} features ({features_str})")
            else:
                print(f"  Page {page_num}: No features detected")
        
        all_rules = set()
        all_analyses = []
        for page_data in document_analysis["pages"].values():
            all_analyses.extend(page_data["analyses"])
            for analysis in page_data["analyses"]:
                all_rules.update(analysis.rule_compliance.keys())
        
        if all_rules:
            print(f"\nOverall Rule Compliance Summary:")
            for rule in sorted(all_rules):
                yes_count = sum(1 for a in all_analyses if a.rule_compliance.get(rule) == "Yes")
                no_count = sum(1 for a in all_analyses if a.rule_compliance.get(rule) == "No")
                review_count = sum(1 for a in all_analyses if a.rule_compliance.get(rule) == "Needs Review")
                total = yes_count + no_count + review_count
                
                if total > 0:
                    print(f"  {rule}: {yes_count} Yes, {no_count} No, {review_count} Review (of {total} features)")
        
        print(f"\nOutput files:")
        print(f"  Visualization: {viz_path}")
        print(f"  Detailed report: {report_path}")
        
        cleanup = input("\nDelete converted PNG images? (y/n): ").strip().lower()
        if cleanup == 'y':
            for page_data in document_analysis["pages"].values():
                try:
                    os.remove(page_data["image_path"])
                    print(f"  Deleted: {os.path.basename(page_data['image_path'])}")
                except:
                    pass
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

def example_usage():
    """Example usage with a sample PDF"""
    pdf_path = r"D:\casting\input\Connector Casting Input.pdf"
    
    if os.path.exists(pdf_path):
        print("Running example analysis...")
        document_analysis = analyze_pdf_document(pdf_path)
        report_path, viz_path = save_comprehensive_report(document_analysis)
        print(f"Example analysis complete:")
        print(f"  Report: {report_path}")
        print(f"  Visualization: {viz_path}")
    else:
        print(f"Example PDF not found: {pdf_path}")

if __name__ == "__main__":
    main()