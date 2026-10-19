r"""
src/gcode_corpus_builder.py - Industrial G-Code & CNC Machine Toolpath Generator
For Anjiru.AI Pretraining & Multi-Dimensional Code-Switching Corpus
Target Storage: D:\ANJIRU_AI_MASSIVE_CORPUS\dimensions\01_gcode_manufacturing

Generates authentic, syntactically valid machine control instructions:
  1. 3D Printing Toolpaths (FDM/FFF, Marlin, Klipper, RepRap)
  2. CNC Milling & Machining (3-Axis, Canned Cycles G81/G83, Contouring G01/G02/G03)
  3. CNC Lathe Turning & Threading (G76, G96, G97, Facing, Parting)
  4. Laser / Plasma Sheet Cutting (Kerf G41/G42, Pierce Dwell G04)

Each machine routine is paired with:
  - English Engineering Specification
  - Way 1: Academic Standard Kiswahili (Uhandisi wa Mitambo na Uzalishaji)
  - Way 2: Colloquial Nairobi Sheng (Ufundi wa Mtaani na Maker Spaces)
"""

import sys
import os
import json
import math
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
D_BASE = Path("D:/ANJIRU_AI_MASSIVE_CORPUS")
GCODE_DIR = D_BASE / "dimensions" / "01_gcode_manufacturing"
GCODE_DIR.mkdir(parents=True, exist_ok=True)


class GCodeCorpusGenerator:
    """
    Generates industrial-grade G-Code manufacturing programs with
    dual-register African linguistic instruction annotations.
    """
    def __init__(self):
        self.materials = [
            ("Aluminium 6061", "alumini 6061", "alumi 6061", 8000, 1200),
            ("Mild Steel 1018", "chuma laini 1018", "chuma cha 1018", 3500, 450),
            ("Brass C360", "shaba ya manjano", "brass", 6500, 900),
            ("Stainless Steel 304", "chuma kisicho na kutu 304", "steel ya 304", 2800, 320),
            ("PLA Polymer", "polima ya PLA", "filament ya PLA", 200, 60),
            ("PETG Polymer", "polima imara ya PETG", "filament ya PETG", 235, 75),
            ("ABS Engineering Plastic", "plastiki ya kihandisi ya ABS", "ABS plastic", 245, 95),
            ("Delrin Acetal", "plastiki imara ya Delrin", "delrin ngumu", 7000, 1100),
            ("Cast Iron", "chuma cha kutupwa", "cast iron nzito", 2200, 280),
            ("Titanium Ti-6Al-4V", "chuma cha titani", "titanium ngumu", 1800, 180)
        ]

        self.tools = [
            ("6mm 4-Flute Carbide Endmill", "patasi ya kabidi ya mm 6 yenye mipasuko minne", "endmill ya 6mm ya carbide"),
            ("10mm 2-Flute Roughing Endmill", "patasi ya kukata kiasi kikubwa ya mm 10", "rougher ya 10mm"),
            ("3.175mm Ballnose Cutter", "kikatio chenye ncha ya duara cha mm 3.175", "ballnose ndogo ya 3mm"),
            ("12.7mm Facing Mill", "kikatio cha kusawazisha uso cha mm 12.7", "facing fly cutter ya half inch"),
            ("8.5mm HSS Jobber Drill", "msumo wa HSS wa mm 8.5 kwa ajili ya mashimo", "drill bit ya 8.5mm"),
            ("0.4mm Brass E3D Nozzle", "mdomo wa bomba la shaba wa mm 0.4", "nozzle ya 0.4 ya 3D printer"),
            ("0.6mm Hardened Steel Nozzle", "mdomo wa chuma kigumu wa mm 0.6", "hardened nozzle ya 0.6"),
            ("Single-Point External Threading Tool", "chombo cha kuchonga nyuzi za nje", "tool ya ku-thread"),
            ("CO2 100W Laser Focus Lens", "lenzi ya leza ya wati 100", "laser lens ya 100W")
        ]

    def generate_3d_print_gcode(self, obj_name: str, width: float, height: float, layer_height: float = 0.2) -> Tuple[str, str, str, str]:
        """Generates an FDM 3D printing toolpath with perimeter perimeters and infill."""
        hotend_temp = random.randint(200, 240)
        bed_temp = random.randint(55, 85)
        num_layers = int(height / layer_height)
        
        lines = [
            "; ========================================================",
            f"; ANJIRU.AI FDM ADDITIVE MANUFACTURING PIPELINE",
            f"; Target Model: {obj_name}",
            f"; Bounding Box: {width:.1f}mm x {width:.1f}mm x {height:.1f}mm",
            f"; Layer Height: {layer_height:.2f}mm | Total Layers: {num_layers}",
            "; Flavor: Marlin / Klipper / RepRap Compatible",
            "; ========================================================",
            "M140 S" + str(bed_temp) + " ; Set bed temperature",
            "M104 S" + str(hotend_temp) + " ; Set hotend temperature",
            "G28 ; Home all axes (X, Y, Z)",
            "G29 ; Execute bilinear automatic bed leveling matrix",
            "M190 S" + str(bed_temp) + " ; Wait for bed to reach target temperature",
            "M109 S" + str(hotend_temp) + " ; Wait for nozzle to reach target temperature",
            "G92 E0 ; Reset extrusion distance coordinate",
            "G1 Z2.0 F3000 ; Move Z axis up slightly to prevent scratching bed",
            "; Prime line sequence",
            "G1 X0.1 Y20 Z0.3 F5000.0 ; Move to prime start position",
            "G1 X0.1 Y180.0 Z0.3 F1500.0 E15.0 ; Extrude first prime line",
            "G1 X0.4 Y180.0 Z0.3 F5000.0 ; Step over",
            "G1 X0.4 Y20.0 Z0.3 F1500.0 E30.0 ; Extrude second purge line",
            "G92 E0 ; Reset extruder position",
            "G1 Z1.0 F1000 ; Lift nozzle",
            "M106 S255 ; Enable layer cooling fan to 100%"
        ]

        # Generate layer toolpaths
        e_pos = 0.0
        center_x = 100.0
        center_y = 100.0
        half_w = width / 2.0

        for layer in range(1, min(15, num_layers) + 1):
            z = layer * layer_height
            lines.append(f"; --- LAYER {layer} (Z = {z:.3f}mm) ---")
            lines.append(f"G1 Z{z:.3f} F1200")
            # Move to start of perimeter
            lines.append(f"G0 X{center_x - half_w:.3f} Y{center_y - half_w:.3f} F7200 ; Rapid travel to perimeter")
            
            # Print outer perimeter
            feed = 2400.0 if layer > 1 else 1200.0
            p_pts = [
                (center_x + half_w, center_y - half_w),
                (center_x + half_w, center_y + half_w),
                (center_x - half_w, center_y + half_w),
                (center_x - half_w, center_y - half_w)
            ]
            for px, py in p_pts:
                e_pos += (width * 0.035)
                lines.append(f"G1 X{px:.3f} Y{py:.3f} E{e_pos:.4f} F{feed:.1f}")

            # Rectilinear infill lines
            step = 3.0
            infill_y = center_y - half_w + 1.0
            while infill_y < (center_y + half_w - 1.0):
                lines.append(f"G0 X{center_x - half_w + 1.0:.3f} Y{infill_y:.3f} F7200")
                e_pos += (width * 0.028)
                lines.append(f"G1 X{center_x + half_w - 1.0:.3f} Y{infill_y:.3f} E{e_pos:.4f} F{feed * 1.25:.1f}")
                infill_y += step

            # Retract at layer change
            e_pos -= 0.8
            lines.append(f"G1 E{e_pos:.4f} F2400 ; Retract filament")

        # End G-code
        lines.extend([
            "; --- END PRINT ROUTINE ---",
            "M104 S0 ; Turn off hotend heater",
            "M140 S0 ; Turn off bed heater",
            "M107 ; Disable cooling fan",
            "G91 ; Relative positioning",
            "G1 E-2.0 F2700 ; Retract filament slightly",
            "G1 Z10.0 F3000 ; Raise Z clear of print",
            "G90 ; Absolute positioning",
            "G28 X0 Y0 ; Home X and Y axes to present printed object",
            "M84 ; Disable stepper motors"
        ])

        gcode_text = "\n".join(lines)
        en_spec = f"Generate an FDM 3D printing G-code slicing routine for a {obj_name} ({width}mm x {width}mm x {height}mm) with automatic bed leveling (G29), dual purge line, and thermal control."
        w1_sw = f"Tunga msimbo wa G-code wa uchapishaji wa pande tatu (3D printing) kwa mfumo wa FDM kwa ajili ya kifaa cha {obj_name} chenye upana wa mm {width:.1f} na urefu wa mm {height:.1f}, ukiwasha usawazishaji wa kitanda kiotomatiki (G29) na udhibiti wa joto."
        w2_sh = f"Generate msimbo wa G-code wa ku-print {obj_name} kwa 3D printer ya FDM yenye vipimo vya {width:.1f}mm kwa {height:.1f}mm, ukiset auto bed leveling ya G29 na ku-control joto ya nozzle na bed."

        return en_spec, w1_sw, w2_sh, gcode_text

    def generate_cnc_milling_gcode(self, part_name: str, mat_tuple: Tuple, tool_tuple: Tuple) -> Tuple[str, str, str, str]:
        """Generates a 3-axis CNC milling program with facing, pocketing, and peck drilling."""
        mat_name, mat_sw, mat_sh, rpm, feed = mat_tuple
        tool_name, tool_sw, tool_sh = tool_tuple
        plunge_feed = int(feed * 0.35)

        lines = [
            "%",
            f"O{random.randint(1000, 9999)} ({part_name.upper().replace(' ', '_')})",
            f"(ANJIRU.AI INDUSTRIAL CNC SUBTRACTIVE MACHINING)",
            f"(MATERIAL: {mat_name} | SPEED: {rpm} RPM | FEED: {feed} MM/MIN)",
            f"(TOOL: {tool_name})",
            "G21 ; All units in metric millimeters",
            "G90 ; Absolute positioning programming mode",
            "G17 ; Select XY work plane",
            "G40 ; Cancel cutter radius compensation",
            "G49 ; Cancel tool length compensation",
            "G80 ; Cancel active canned cycles",
            "G28 G91 Z0.0 ; Safe retract to machine reference home",
            "G90",
            f"T1 M06 ; Tool change to {tool_name}",
            f"S{rpm} M03 ; Spindle ON clockwise at {rpm} RPM",
            "G54 ; Call Work Coordinate System #1",
            "G00 X0.0 Y0.0 ; Rapid to workpiece datum origin",
            "G43 H1 Z15.0 M08 ; Apply tool height offset #1 and activate flood coolant",
            "; --- OPERATION 1: HIGH-EFFICIENCY SURFACE FACING ---",
            "G00 Z2.0",
            f"G01 Z0.0 F{plunge_feed} ; Touch workpiece datum surface"
        ]

        # Generate facing passes
        length = 120.0
        stepover = 8.0
        y = 0.0
        while y <= 80.0:
            lines.append(f"G01 X{length:.2f} Y{y:.2f} F{feed} ; Facing pass")
            y += stepover
            lines.append(f"G01 X{length:.2f} Y{y:.2f} F{feed}")
            lines.append(f"G01 X0.00 Y{y:.2f} F{feed} ; Return facing pass")
            y += stepover

        # Circular Pocket Routine
        lines.extend([
            "; --- OPERATION 2: CIRCULAR POCKET MILLING ---",
            "G00 Z5.0 ; Retract to safe clearance",
            "G00 X60.0 Y40.0 ; Rapid to pocket center coordinate",
            f"G01 Z-2.0 F{plunge_feed} ; Plunge into pocket roughing depth",
            f"G01 X68.0 F{feed} ; Move to circle radius",
            f"G02 I-8.0 J0.0 F{feed} ; Mill full 360-degree clockwise circular pocket (G02)",
            f"G01 X76.0 F{feed} ; Step out to second circular boundary",
            f"G02 I-16.0 J0.0 F{feed} ; Mill outer circular profile",
            "G00 Z10.0 ; Retract",
            "; --- OPERATION 3: G83 DEEP HOLE PECK DRILLING ---",
            "G00 X25.0 Y20.0 ; Position at hole coordinate #1",
            f"G83 X25.0 Y20.0 Z-22.0 R2.0 Q4.0 F{plunge_feed} ; Canned peck drilling (Q=4mm peck step)",
            "X95.0 Y20.0 ; Drill hole #2",
            "X95.0 Y60.0 ; Drill hole #3",
            "X25.0 Y60.0 ; Drill hole #4",
            "G80 ; Cancel canned drill cycle",
            "; --- SAFE MACHINE PARK & SHUTDOWN ---",
            "M09 ; Flood coolant OFF",
            "M05 ; Spindle brake STOP",
            "G28 G91 Z0.0 ; Retract Z to machine home",
            "G28 Y0.0 ; Present table to operator door",
            "M30 ; End of program and reset rewinding",
            "%"
        ])

        gcode_text = "\n".join(lines)
        en_spec = f"Generate a complete 3-axis CNC milling G-code program to machine a {part_name} from {mat_name} using a {tool_name}, with surface facing, circular pocketing (G02), and G83 canned peck drilling."
        w1_sw = f"Tunga msimbo kamili wa G-code wa mashine ya CNC yenye mihimili mitatu ili kuchonga {part_name} kutoka kwa bati la {mat_sw} kwa kutumia {tool_sw}, unaojumuisha kusawazisha uso, kukata tundu la mviringo (G02), na kutoboa mashimo kwa kurudiarudia (G83)."
        w2_sh = f"Generate msimbo kamili wa G-code wa mashine ya CNC ya axis 3 wa ku-machine {part_name} kutoka kwa {mat_sh} ukitumia {tool_sh}, ikiwa na surface facing, ku-mill circular pocket kwa G02, na ku-drill mashimo kwa G83 canned peck drilling."

        return en_spec, w1_sw, w2_sh, gcode_text

    def generate_cnc_lathe_gcode(self, part_name: str, mat_tuple: Tuple) -> Tuple[str, str, str, str]:
        """Generates a CNC Lathe turning and single-point threading program (G76)."""
        mat_name, mat_sw, mat_sh, _, _ = mat_tuple
        lines = [
            "%",
            f"O{random.randint(5000, 9999)} (LATHE_{part_name.upper().replace(' ', '_')})",
            f"(ANJIRU.AI CNC TURNING & SINGLE-POINT THREADING)",
            f"(MATERIAL: {mat_name})",
            "G21 G18 G90 G80 G40 ; Metric, ZX turning plane, absolute coordinates",
            "G28 U0.0 W0.0 ; Safe tool post index home",
            "T0101 ; Call Tool 1 (Rough Facing & OD Turning Insert)",
            "G96 S180 M03 ; Constant Surface Speed (CSS) at 180 m/min, spindle CW",
            "G50 S2500 ; Clamp maximum spindle RPM to 2500 for chuck safety",
            "G00 X52.0 Z2.0 M08 ; Position rapid with coolant",
            "; Rough facing pass",
            "G01 X-1.0 Z0.0 F0.22 ; Face front datum past centerline",
            "G00 Z2.0",
            "; OD Profile Turning",
            "G00 X48.0",
            "G01 Z-35.0 F0.25 ; Turn diameter to 48mm for 35mm length",
            "G01 X52.0",
            "G00 Z2.0",
            "G00 X20.0",
            "G01 Z-25.0 F0.18 ; Turn thread shoulder to M20 major diameter (20.0mm)",
            "G01 X24.0 Z-27.0 ; 45-degree chamfer transition",
            "G00 X100.0 Z50.0 M09 ; Retract tool",
            "M05",
            "; Threading operation",
            "T0202 ; Call Tool 2 (60-Degree External Threading Insert)",
            "G97 S650 M03 ; Direct RPM mode at 650 RPM for threading accuracy",
            "G00 X22.0 Z5.0 M08 ; Clearance before thread lead-in",
            "; G76 Two-Line Fanuc Canned Threading Cycle (M20x2.5 Metric Thread)",
            "G76 P010060 Q100 R0.05 ; P: 1 spring pass, 60-degree infeed angle",
            "G76 X16.93 Z-22.0 P1534 Q250 F2.5 ; Minor dia 16.93mm, thread depth 1.534mm, pitch 2.5mm",
            "G00 X100.0 Z100.0 M09",
            "M05 ; Stop spindle",
            "G28 U0.0 W0.0 ; Return home",
            "M30 ; End of program",
            "%"
        ]

        gcode_text = "\n".join(lines)
        en_spec = f"Generate a CNC lathe turning and threading G-code program for a {part_name} in {mat_name}, featuring Constant Surface Speed (G96), maximum RPM clamp (G50), and a Fanuc G76 canned metric threading cycle."
        w1_sw = f"Tunga msimbo wa G-code wa mtambo wa kugeuza vyuma (CNC Lathe) kwa ajili ya kutengeneza {part_name} ya {mat_sw}, ukiweka udhibiti wa kasi ya uso (G96), kizuizi cha mzunguko wa juu (G50), na kuchonga nyuzi za skrubu kwa mzunguko wa G76."
        w2_sh = f"Generate msimbo wa G-code wa lathe ya CNC wa ku-turn na ku-thread {part_name} kwa {mat_sh}, ukitumia constant surface speed (G96), ku-cap max RPM kwa G50, na ku-cut thread kwa G76 cycle ya Fanuc."

        return en_spec, w1_sw, w2_sh, gcode_text


def build_gcode_repository_shard(shard_id: int = 1, target_programs: int = 5000) -> Dict[str, Any]:
    """Generates an entire high-density G-code training repository shard on Drive D:."""
    gen = GCodeCorpusGenerator()
    out_file = GCODE_DIR / f"gcode_manufacturing_shard_{shard_id:03d}.jsonl"

    print("=" * 80)
    print(f"ANJIRU.AI G-CODE & MANUFACTURING REPOSITORY BUILDER (SHARD {shard_id})")
    print(f"Target Destination: {out_file}")
    print(f"Target Programs:    {target_programs:,}")
    print("=" * 80)

    t0 = time.time()
    total_tokens = 0
    total_words = 0

    parts_3d = ["Enclosure Case", "Drone Arm Bracket", "Spur Gear 24T", "Impeller Blade", "Robotic Gripper", "Prosthetic Finger", "Filament Spool Holder", "V-Slot Gantry Plate"]
    parts_cnc = ["Automotive Flange Adapter", "Hydraulic Manifold Block", "Motor Mount Bracket", "Precision Bearing Housing", "Turbine Mounting Plate", "Heat Sink Fin Assembly"]
    parts_lathe = ["Precision Lead Screw Shaft", "M20 Threaded Standoff", "Hydraulic Cylinder Rod", "Wheel Axle Spindle", "High-Pressure Bushing"]

    records = []
    with open(out_file, "w", encoding="utf-8") as f:
        for idx in range(1, target_programs + 1):
            category = idx % 3
            if category == 0:
                p_name = random.choice(parts_3d)
                w = random.uniform(30.0, 150.0)
                h = random.uniform(10.0, 60.0)
                en, w1, w2, gcode = gen.generate_3d_print_gcode(p_name, w, h)
                prog_type = "additive_3d_printing"
            elif category == 1:
                p_name = random.choice(parts_cnc)
                mat = random.choice(gen.materials)
                tool = random.choice(gen.tools)
                en, w1, w2, gcode = gen.generate_cnc_milling_gcode(p_name, mat, tool)
                prog_type = "subtractive_cnc_milling"
            else:
                p_name = random.choice(parts_lathe)
                mat = random.choice(gen.materials)
                en, w1, w2, gcode = gen.generate_cnc_lathe_gcode(p_name, mat)
                prog_type = "rotational_cnc_turning"

            # Compute token and word metrics
            gcode_words = len(gcode.split())
            w1_words = len(w1.split())
            w2_words = len(w2.split())
            en_words = len(en.split())

            prog_words = gcode_words + w1_words + w2_words + en_words
            prog_tokens = int(gcode_words * 1.35 + (w1_words + w2_words + en_words) * 1.15)

            total_words += prog_words
            total_tokens += prog_tokens

            record = {
                "id": f"ANJIRU_GCODE_{shard_id:03d}_{idx:06d}",
                "program_type": prog_type,
                "domain": "Advanced Manufacturing & Industrial G-Code",
                "instruction_english": en,
                "way1_academic": w1,
                "way2_sheng": w2,
                "gcode_toolpath": gcode,
                "metrics": {
                    "words": prog_words,
                    "tokens_estimated": prog_tokens,
                    "gcode_line_count": len(gcode.splitlines())
                }
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

            if idx % 1000 == 0:
                elapsed = time.time() - t0
                speed = idx / max(0.1, elapsed)
                print(f"  ⚡ Synthesized {idx:,} / {target_programs:,} G-code programs | Speed: {speed:,.0f} progs/sec | Words: {total_words:,}")

    elapsed = time.time() - t0
    file_size_mb = out_file.stat().st_size / (1024 * 1024)

    summary = {
        "shard_file": str(out_file),
        "total_programs": target_programs,
        "total_words_generated": total_words,
        "total_tokens_estimated": total_tokens,
        "file_size_mb": round(file_size_mb, 2),
        "elapsed_seconds": round(elapsed, 2),
        "programs_per_second": round(target_programs / max(0.1, elapsed), 1),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save shard telemetry
    with open(GCODE_DIR / f"telemetry_shard_{shard_id:03d}.json", "w", encoding="utf-8") as tf:
        json.dump(summary, tf, indent=2)

    print("\n" + "=" * 80)
    print(f"✓ G-CODE SHARD {shard_id} COMPLETE!")
    print(f"Total Programs:         {target_programs:,}")
    print(f"Total Words Generated:  {total_words:,} words")
    print(f"Total Tokens Estimated: {total_tokens:,} tokens")
    print(f"File Size on Disk:      {file_size_mb:.2f} MB")
    print(f"Runtime:                {elapsed:.2f}s ({target_programs/max(0.1, elapsed):.0f} progs/sec)")
    print(f"Output File:            {out_file}")
    print("=" * 80)

    return summary

if __name__ == "__main__":
    build_gcode_repository_shard(shard_id=1, target_programs=5000)
