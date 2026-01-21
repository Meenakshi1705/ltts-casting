# casting_config.py
# Configuration file for casting design analysis

# Material properties for customized recommendations
MATERIAL_PROPERTIES = {
    "Gray Cast Iron": {
        "min_wall_thickness": 3.0,
        "draft_angle": 1.5,
        "shrinkage": 1.0,
        "fillet_ratio": 0.25,
        "complexity": "High"
    },
    "Aluminum A356": {
        "min_wall_thickness": 2.5,
        "draft_angle": 1.0,
        "shrinkage": 1.2,
        "fillet_ratio": 0.2,
        "complexity": "Medium"
    },
    "Bronze": {
        "min_wall_thickness": 2.0,
        "draft_angle": 1.0,
        "shrinkage": 1.5,
        "fillet_ratio": 0.2,
        "complexity": "Medium"
    },
    "Steel": {
        "min_wall_thickness": 4.0,
        "draft_angle": 2.0,
        "shrinkage": 2.0,
        "fillet_ratio": 0.3,
        "complexity": "High"
    }
}

# Process recommendations based on volume
PROCESS_RECOMMENDATIONS = {
    "low": {"max": 100, "processes": ["Sand Casting", "Investment Casting"]},
    "medium": {"max": 10000, "processes": ["Investment Casting", "Permanent Mold"]},
    "high": {"max": 1000000, "processes": ["Die Casting", "Permanent Mold"]}
}

# Casting type options
CASTING_TYPES = [
    "Bracket Casting", "Housing Casting", "Connector Casting", 
    "Valve Body", "Pump Housing", "Engine Block", "Transmission Case",
    "Automotive Component", "Aerospace Component", "Industrial Component"
]

def get_material_guidance(material):
    """Get material-specific guidance for AI evaluation"""
    guidance = {
        "Gray Cast Iron": "Focus on thick sections (>3mm), draft angles (1.5°), and feeding paths. Gray iron is forgiving but requires good feeding.",
        "Aluminum A356": "Check for thin walls (>2.5mm), sharp corners (add fillets), and gas porosity risks. Aluminum requires degassing considerations.",
        "Bronze": "Evaluate fine details and thin sections (>2mm). Bronze allows complex geometry but watch for shrinkage.",
        "Steel": "Assess heavy sections (>4mm), high shrinkage (2%), and feeding requirements. Steel needs robust feeding systems."
    }
    return guidance.get(material, "Apply standard casting design principles.")

def get_volume_guidance(volume):
    """Get volume-specific guidance for AI evaluation"""
    if volume <= 100:
        return "Low volume production - sand casting typical. Focus on design flexibility and prototype considerations."
    elif volume <= 10000:
        return "Medium volume production - investment casting typical. Balance design complexity with tooling costs."
    else:
        return "High volume production - die casting typical. Emphasize tight tolerances, draft angles, and production efficiency."

def get_recommended_action(rule, check_item, result, casting_context):
    """
    Generate customized recommended actions based on material, volume, and casting type
    """
    if result != "No":
        return ""
    
    rule_id = rule['rule_id']
    check_id = check_item['check_id']
    material = casting_context['material']
    volume = casting_context['volume']
    casting_type = casting_context['casting_type']
    
    # Get material properties for customized recommendations
    mat_props = MATERIAL_PROPERTIES.get(material, MATERIAL_PROPERTIES["Gray Cast Iron"])
    min_wall = mat_props['min_wall_thickness']
    fillet_ratio = mat_props['fillet_ratio']
    draft_angle = mat_props['draft_angle']
    
    # Base recommendations with material-specific values
    base_recommendations = {
        "R1": {
            "1.1": f"Add feeding channels or redesign to eliminate isolated heavy sections. For {material}, ensure feeding paths are ≥{min_wall*1.5:.1f}mm wide",
            "1.2": f"Provide clear section views showing wall transitions. Critical for {casting_type} to verify mold filling",
            "1.3": f"Simplify geometry or add {draft_angle}° draft angles for {material} mold filling"
        },
        "R2": {
            "2.1": f"Redesign with progressive wall thickness increase toward risers. For {material}, maintain minimum {min_wall}mm walls",
            "2.2": f"Remove reverse tapers - add {draft_angle}° draft angles in feeding direction for {material}",
            "2.3": f"Relocate heavy sections closer to riser locations. Critical for {casting_type} soundness"
        },
        "R3": {
            "3.1": f"Add fillet radii (min R = {fillet_ratio} × wall thickness = {min_wall*fillet_ratio:.1f}mm) to internal corners for {material}",
            "3.2": f"Redesign acute angles to be >90° for {material} to prevent hot spots",
            "3.3": f"Add chamfers or radii to external edges. Essential for {casting_type} mold integrity"
        },
        "R4": {
            "4.1": f"Redesign junction to have maximum 2 intersecting sections. Critical for {casting_type}",
            "4.2": f"Stagger junction locations or add relief features for {material}",
            "4.3": f"Add cored holes at unavoidable multi-section intersections in {casting_type}"
        },
        "R5": {
            "5.1": f"Redesign for uniform wall thickness (variation <30%). Maintain {min_wall}mm minimum for {material}",
            "5.2": f"Add coring or hollow out thick sections in {casting_type}",
            "5.3": f"Replace thick walls with ribbed structures for {material}"
        },
        "R6": {
            "6.1": f"Reduce inner wall thickness to 90% of outer wall thickness for {material}",
            "6.2": f"Add coring or venting to enclosed heavy inner sections in {casting_type}"
        },
        "R7": {
            "7.1": f"Add fillet radii (R = {min_wall*fillet_ratio:.1f}mm) to all re-entrant corners for {material}",
            "7.2": f"Reduce fillet size if excessive (max R = {min_wall*0.5:.1f}mm for {material})"
        },
        "R8": {
            "8.1": f"Add gradual transitions between different wall thicknesses for {material}",
            "8.2": f"Eliminate step changes - use tapered transitions for {casting_type}"
        },
        "R9": {
            "9.1": f"Reduce rib thickness to 80% of adjoining wall thickness ({min_wall*0.8:.1f}mm) for {material}",
            "9.2": f"Eliminate cross-ribbing or add relief at intersections in {casting_type}",
            "9.3": f"Increase rib depth rather than thickness for stiffness in {material}"
        },
        "R10": {
            "10.1": f"Add smooth blending transitions from bosses to walls for {material}",
            "10.2": f"Eliminate isolated pads or connect to main structure in {casting_type}",
            "10.3": f"Ensure uniform boss wall thickness ({min_wall}mm) throughout for {material}"
        }
    }
    
    # Add volume-specific recommendations
    volume_suffix = ""
    if volume <= 100:
        volume_suffix = " Consider sand casting for low volume production."
    elif volume <= 10000:
        volume_suffix = " Consider investment casting for medium volume production."
    else:
        volume_suffix = " Consider die casting for high volume production - design for tight tolerances."
    
    base_rec = base_recommendations.get(rule_id, {}).get(check_id, f"Review {rule['title']} requirements for {material}")
    
    return base_rec + volume_suffix

def get_process_suggestion(volume):
    """Get suggested casting process based on production volume"""
    if volume <= 100:
        return "Sand Casting", "low"
    elif volume <= 10000:
        return "Investment Casting", "medium"
    else:
        return "Die Casting", "high"

def get_filename_components(casting_context):
    """Generate filename components for output file"""
    material_short = casting_context['material'].replace(' ', '').replace('Cast', '').replace('Iron', 'Fe')
    volume_short = f"{casting_context['volume']//1000}K" if casting_context['volume'] >= 1000 else str(casting_context['volume'])
    return material_short, volume_short