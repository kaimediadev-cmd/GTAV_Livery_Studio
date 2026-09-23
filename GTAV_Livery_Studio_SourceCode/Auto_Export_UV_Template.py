# ==============================================================================
# GTA V Auto UV Livery Template Generator (Universal Smart Filter)
# Tu dong trich xuat UVMap 1 (Livery Decal) chuan 4K sieu sach cho MOI LOAI XE GTA V
# Ho tro ca xe nguyen ban (Rockstar) lan xe mod tu GTA5-Mods (ZModeler / Sollumz)
# ==============================================================================

import bpy
import addon_utils
import sys
import os
import shutil
import tempfile
import math

sys.path.append(r"C:\Users\KAI Media\AppData\Roaming\Python\Python313\site-packages")
from PIL import Image, ImageDraw

addon_utils.enable("Sollumz", default_set=True)

def is_valid_polygon(poly_uvs):
    """Kiem tra xem polygon co chua dinh di thuong, bi ghim vao goc hoac tran vien khong."""
    for u, v in poly_uvs:
        # Nam ngoai vung UV hop le [0, 1]
        if u < -0.005 or u > 1.005 or v < -0.005 or v > 1.005:
            return False
        # Bi ghim chat vao 4 goc canvas do khong duoc unwrap UV
        if (abs(u) < 0.02 and abs(v) < 0.02) or \
           (abs(u) < 0.02 and abs(v - 1.0) < 0.02) or \
           (abs(u - 1.0) < 0.02 and abs(v) < 0.02) or \
           (abs(u - 1.0) < 0.02 and abs(v - 1.0) < 0.02):
            return False
    return True

def generate_livery_template(target_xml_path, out_dir=None, target_size=4096, export_photoshop=True, export_preview=True):
    target_xml_path = target_xml_path.strip().strip('"').strip("'")
    target_xml_path = os.path.abspath(target_xml_path)

    if target_xml_path.lower().endswith(".yft") and not target_xml_path.lower().endswith(".yft.xml"):
        potential_xml = target_xml_path + ".xml"
        if os.path.exists(potential_xml):
            target_xml_path = potential_xml
        else:
            print(f"\n[LOI] Day la file .yft nhi phan chua duoc giai ma sang XML: {target_xml_path}", flush=True)
            return

    if not os.path.exists(target_xml_path):
        print(f"\n[LOI] Khong tim thay file: {target_xml_path}\n", flush=True)
        return

    if out_dir and os.path.isdir(out_dir):
        xml_dir = os.path.abspath(out_dir)
    else:
        xml_dir = os.path.dirname(target_xml_path)

    base_name = os.path.basename(target_xml_path)
    clean_name = base_name.replace(".yft.xml", "").replace(".xml", "").replace(".yft", "")
    
    print(f"\n=======================================================", flush=True)
    print(f" >>> BAT DAU XU LY XE: {clean_name}", flush=True)
    print(f" >>> File XML: {target_xml_path}", flush=True)
    print(f" >>> Thu muc luu anh: {xml_dir}", flush=True)
    print(f" >>> Do phan giai: {target_size} x {target_size} (1:1)", flush=True)
    print(f"=======================================================", flush=True)

    print("\n[Buoc 1/4] Dang khoi tao va nap model 3D xe vao bo nho (cho khoang 15-20s)...", flush=True)

    temp_dir = tempfile.mkdtemp(prefix="gtav_uv_")
    solo_xml_name = "vehicle_model_solo.yft.xml"
    temp_xml_path = os.path.join(temp_dir, solo_xml_name)
    shutil.copy2(target_xml_path, temp_xml_path)

    try:
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.sollumz.import_assets(
            directory=temp_dir + "\\",
            files=[{"name": solo_xml_name}]
        )
    except Exception as e:
        print(f"\n[LOI KHI IMPORT] Khong the doc du lieu xe qua Sollumz: {e}", flush=True)
        return
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("[Buoc 2/4] Da nap xong model xe! Dang ap dung thuat toan loc Shader & UV Livery...", flush=True)

    size = int(target_size)
    
    img_dark = None
    draw_dark = None
    if export_preview:
        img_dark = Image.new("RGBA", (size, size), (20, 20, 20, 255))
        draw_dark = ImageDraw.Draw(img_dark)

    img_trans = None
    draw_trans = None
    if export_photoshop:
        img_trans = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw_trans = ImageDraw.Draw(img_trans)

    # Danh sach tu khoa loai tru tuyet doi o cap do Object hoac Material
    global_skip_keywords = [
        "glass", "window", "windscreen", "interior", "engine", "chassis_low", 
        "wheel", "tire", "dial", "steering", "seat", "pedal", "mirror_interior",
        "exhaust", "radiator", "suspension", "brake", "rotor", "caliper", "hub_",
        "light", "headlight", "taillight", "siren", "indicator", "reverse",
        "mesh_screw", "mesh_badge", "mesh_emblem", "undercarriage", "grille",
        "subframe", "susp", "axle", "shock", "spring", "muffler", "wiper",
        "plate", "license", "dummy", "col", "radio", "anpr", "whelen", "hbc",
        "mcs", "prop_", "bag", "crate", "seatbelt"
    ]

    paint_keywords = [
        "[primary]", "[secondary]", "[pearlescent]", 
        "paint1", "paint2", "paint3", "paint4", 
        "paint_1", "paint_2", "paint_3", "paint_4",
        "[paint", "body_d", "vehicle_paint", "livery", "liveries"
    ]

    # Thu thap mesh hop le
    mesh_objects = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith(".col")]

    # Ham quet va ve duong net theo bo loc
    def extract_lines(use_material_paint_filter=True):
        lines_drawn = 0
        for obj in mesh_objects:
            obj_name_lower = obj.name.lower()
            mesh = obj.data
            if not mesh.uv_layers:
                continue

            # Uu tien UVMap 1 (Livery Channel), neu khong co thi lay UVMap 0
            uv_layer = None
            for layer in mesh.uv_layers:
                if "1" in layer.name or "livery" in layer.name.lower() or "ch1" in layer.name.lower():
                    uv_layer = layer
                    break
            if not uv_layer:
                uv_layer = mesh.uv_layers[0]

            uv_data = uv_layer.data
            mats = mesh.materials

            for poly in mesh.polygons:
                # Kiem tra vat lieu cua polygon
                mat = mats[poly.material_index] if poly.material_index < len(mats) else None
                mat_name = mat.name.lower() if mat else ""
                shader_name = (getattr(mat.shader_properties, "filename", "") or "").lower() if (mat and hasattr(mat, "shader_properties")) else ""

                # Bo qua bien so xe, kinh, den, noi that
                if any(kw in mat_name for kw in ["plate", "glass", "window", "windscreen", "mirror_interior", "lightsemissive"]):
                    continue

                if use_material_paint_filter:
                    # Loc chinh xac cac polygon su dung shader son xe hoac co tag paint / livery
                    is_paint_shader = "vehicle_paint" in shader_name
                    is_paint_name = any(pk in mat_name for pk in paint_keywords)
                    if not (is_paint_shader or is_paint_name):
                        continue
                else:
                    # Che do fallback theo ten Object neu xe khong dung chuan shader
                    if any(kw in obj_name_lower for kw in global_skip_keywords):
                        continue

                poly_uvs = [uv_data[i].uv for i in poly.loop_indices]
                if not is_valid_polygon(poly_uvs):
                    continue

                n = len(poly_uvs)
                for i in range(n):
                    u1, v1 = poly_uvs[i]
                    u2, v2 = poly_uvs[(i + 1) % n]

                    # Loai bo duong seam wrapping cat ngang doc canvas (> 38%)
                    if abs(u1 - u2) > 0.38 or abs(v1 - v2) > 0.38:
                        continue

                    x1 = int(u1 * size)
                    y1 = int((1.0 - v1) * size)
                    x2 = int(u2 * size)
                    y2 = int((1.0 - v2) * size)

                    if max(x1, x2) >= 0 and min(x1, x2) <= size and max(y1, y2) >= 0 and min(y1, y2) <= size:
                        p1 = (x1, y1)
                        p2 = (x2, y2)
                        if draw_dark:
                            draw_dark.line([p1, p2], fill=(0, 240, 255, 230), width=1)
                        if draw_trans:
                            draw_trans.line([p1, p2], fill=(255, 255, 255, 220), width=1)
                        lines_drawn += 1

        return lines_drawn

    # Chay che do uu tien: Loc theo Shader / Paint Material (Chat luong cao nhat, sieu sach)
    total_lines = extract_lines(use_material_paint_filter=True)

    # Neu xe do khong gan shader paint nao (total_lines = 0) -> Fallback che do Object Name
    if total_lines == 0:
        print("[THONG BAO] Khong tim thay shader vehicle_paint dac thu, chuyen sang che do Fallback Loc Than Vo...", flush=True)
        total_lines = extract_lines(use_material_paint_filter=False)

    print(f"[Buoc 3/4] Da trich xuat xong {total_lines} duong net UV than vo sieu sach!", flush=True)
    print(f"[Buoc 4/4] Dang ket xuat va luu file anh {size}x{size} 1:1...", flush=True)

    out_preview = os.path.join(xml_dir, f"{clean_name}_UV_Preview.png")
    out_photoshop = os.path.join(xml_dir, f"{clean_name}_UV_Template_Photoshop.png")
    
    if img_dark:
        try:
            img_dark.save(out_preview, "PNG")
        except Exception as e:
            print(f"[CANH BAO] Khong the ghi de file preview: {e}", flush=True)
            out_preview = os.path.join(xml_dir, f"{clean_name}_UV_Preview_new.png")
            img_dark.save(out_preview, "PNG")

    if img_trans:
        try:
            img_trans.save(out_photoshop, "PNG")
        except Exception as e:
            print(f"[CANH BAO] Khong the ghi de file photoshop: {e}", flush=True)
            out_photoshop = os.path.join(xml_dir, f"{clean_name}_UV_Template_Photoshop_new.png")
            img_trans.save(out_photoshop, "PNG")
    
    print(f"\n=======================================================", flush=True)
    print(f" >>> [HOAN TAT MY MAN] Da xuat xong mau tem {size}x{size} cho xe {clean_name}!", flush=True)
    if img_dark:
        print(f" 1. Ban xem truoc (Nen toi):", flush=True)
        print(f"    -> {out_preview}", flush=True)
    if img_trans:
        print(f" 2. Ban ve tem Photoshop / Corel (Nen trong suot):", flush=True)
        print(f"    -> {out_photoshop}", flush=True)
    print(f"=======================================================\n", flush=True)

if __name__ == "__main__":
    args = sys.argv
    if "--" in args:
        idx = args.index("--")
        params = args[idx + 1:]
    else:
        params = []
        
    if not params:
        print("[HUONG DAN] Truyen it nhat mot file .yft.xml de trich xuat.", flush=True)
    else:
        target_xml = params[0]
        out_dir = params[1] if len(params) > 1 and params[1].strip() else None
        target_size = int(params[2]) if len(params) > 2 and params[2].isdigit() else 4096
        export_ps = params[3] == "1" if len(params) > 3 else True
        export_prev = params[4] == "1" if len(params) > 4 else True
        
        generate_livery_template(target_xml, out_dir, target_size, export_ps, export_prev)
