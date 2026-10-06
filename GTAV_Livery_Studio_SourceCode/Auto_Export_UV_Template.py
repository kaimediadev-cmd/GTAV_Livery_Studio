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

    def is_layer_valid(mesh, uv_layer):
        """Kiem tra xem mot UV layer co chua toa do hop le hay bi sup ve goc (0, 1)."""
        if not uv_layer or len(uv_layer.data) == 0:
            return False
        sample_size = min(len(uv_layer.data), 1000)
        u_vals = [uv_layer.data[i].uv[0] for i in range(sample_size)]
        v_vals = [uv_layer.data[i].uv[1] for i in range(sample_size)]
        # Neu tat ca vertex deu bi ghim vao goc (0, 1) do chua unwrap livery
        pinned = sum(1 for i in range(sample_size) if abs(u_vals[i]) < 0.02 and abs(v_vals[i] - 1.0) < 0.02)
        if pinned > sample_size * 0.95:
            return False
        # Neu bien do toa do bang 0 (tat ca diem sup ve 1 diem duy nhat)
        if (max(u_vals) - min(u_vals) < 0.005) and (max(v_vals) - min(v_vals) < 0.005):
            return False
        return True

    # Kiem tra xem tong the xe co kenh UV Livery (UVMap 1) that su khong
    has_valid_livery_channel = False
    for obj in mesh_objects:
        obj_name = obj.name.lower()
        if any(kw in obj_name for kw in ["body", "door", "boot", "bonnet", "bumper", "chassis"]):
            mesh = obj.data
            for layer in mesh.uv_layers:
                if "1" in layer.name or "livery" in layer.name.lower() or "ch1" in layer.name.lower():
                    if is_layer_valid(mesh, layer):
                        has_valid_livery_channel = True
                        break
        if has_valid_livery_channel:
            break

    use_uvmap_fallback = not has_valid_livery_channel

    if use_uvmap_fallback:
        print("[THONG BAO XE DUNG UVMAP 0] Phat hien UVMap 1 bi trong/sup ve goc (Xe chua lam kenh tem Livery GTA V).", flush=True)
        print("[THONG BAO XE DUNG UVMAP 0] Tu dong chuyen sang trich xuat UVMap 0 (Kenh van goc xe tuong tu Blender/ZMD3)...", flush=True)
    else:
        print("[THONG BAO] Phat hien kenh UVMap 1 hop le (Kenh Livery Decal chuan GTA V). Dang trich xuat...", flush=True)

    # Tinh toan bounding box neu su dung UVMap 0 o che do toa do rong (Multi-tile)
    multitile_mode = False
    scale_min_u, scale_max_u = 0.0, 1.0
    scale_min_v, scale_max_v = 0.0, 1.0
    norm_max_span = 1.0
    norm_off_u, norm_off_v = 0.0, 0.0
    norm_span_with_pad = 1.0

    if use_uvmap_fallback:
        all_body_u = []
        all_body_v = []
        for obj in mesh_objects:
            obj_name = obj.name.lower()
            if any(kw in obj_name for kw in global_skip_keywords):
                continue
            mesh = obj.data
            if not mesh.uv_layers:
                continue
            uv_layer = mesh.uv_layers[0]
            mats = mesh.materials
            for poly in mesh.polygons:
                mat = mats[poly.material_index] if poly.material_index < len(mats) else None
                mat_name = mat.name.lower() if mat else ""
                shader_name = (getattr(mat.shader_properties, "filename", "") or "").lower() if (mat and hasattr(mat, "shader_properties")) else ""
                if any(kw in mat_name for kw in ["plate", "glass", "window", "windscreen", "mirror_interior", "lightsemissive", "stitch", "interior"]):
                    continue
                is_paint = ("vehicle_paint" in shader_name) or any(pk in mat_name for pk in paint_keywords)
                if not is_paint:
                    continue
                for idx in poly.loop_indices:
                    all_body_u.append(uv_layer.data[idx].uv[0])
                    all_body_v.append(uv_layer.data[idx].uv[1])
        if all_body_u and all_body_v:
            scale_min_u, scale_max_u = min(all_body_u), max(all_body_u)
            scale_min_v, scale_max_v = min(all_body_v), max(all_body_v)
            span_u = scale_max_u - scale_min_u
            span_v = scale_max_v - scale_min_v
            # Neu toa do nam ngoai vung chuan [0, 1] hoac vuot tile
            if span_u > 1.2 or span_v > 1.2 or scale_min_u < -0.1 or scale_max_u > 1.1 or scale_min_v < -0.1 or scale_max_v > 1.1:
                multitile_mode = True
                norm_max_span = max(span_u, span_v)
                pad = 0.02 * norm_max_span
                norm_span_with_pad = norm_max_span + 2 * pad
                norm_off_u = (norm_max_span - span_u) / 2.0 + pad
                norm_off_v = (norm_max_span - span_v) / 2.0 + pad

    # Ham quet va ve duong net theo bo loc
    def extract_lines(use_material_paint_filter=True):
        lines_drawn = 0
        for obj in mesh_objects:
            obj_name_lower = obj.name.lower()
            mesh = obj.data
            if not mesh.uv_layers:
                continue

            # Chon UV Layer phu hop
            uv_layer = None
            if not use_uvmap_fallback:
                # Uu tien UVMap 1 neu hop le
                for layer in mesh.uv_layers:
                    if "1" in layer.name or "livery" in layer.name.lower() or "ch1" in layer.name.lower():
                        if is_layer_valid(mesh, layer):
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

                if not multitile_mode:
                    if not is_valid_polygon(poly_uvs):
                        continue

                n = len(poly_uvs)
                for i in range(n):
                    raw_u1, raw_v1 = poly_uvs[i]
                    raw_u2, raw_v2 = poly_uvs[(i + 1) % n]

                    if multitile_mode:
                        u1 = (raw_u1 - scale_min_u + norm_off_u) / norm_span_with_pad
                        v1 = (raw_v1 - scale_min_v + norm_off_v) / norm_span_with_pad
                        u2 = (raw_u2 - scale_min_u + norm_off_u) / norm_span_with_pad
                        v2 = (raw_v2 - scale_min_v + norm_off_v) / norm_span_with_pad

                        # Loai bo duong seam cat ngang canvas (> 40%)
                        if abs(u1 - u2) > 0.40 or abs(v1 - v2) > 0.40:
                            continue
                    else:
                        u1, v1 = raw_u1, raw_v1
                        u2, v2 = raw_u2, raw_v2

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

    # Neu xe do khong gan shader paint nao (total_lines == 0) -> Fallback che do Object Name
    if total_lines == 0:
        print("[THONG BAO] Khong tim thay shader vehicle_paint dac thu, chuyen sang che do Fallback Loc Than Vo...", flush=True)
        total_lines = extract_lines(use_material_paint_filter=False)

    print(f"[Buoc 3/4] Da trich xuat xong {total_lines} duong net UV than vo sieu sach!", flush=True)

    if total_lines < 500:
        print(f"[CANH BAO XE KHONG CO UV TEM] So duong net UV qua it ({total_lines} net). Xe nay CHUA DUOC TAC GIA UNWRAP UV TEM (Livery Map) cho than xe trong 3D model! Xe khong ho tro dan tem trong GTA V.", flush=True)
    elif use_uvmap_fallback:
        print(f"[THANH CONG UVMAP 0] Da tu dong trich xuat thanh cong {total_lines} net UV tu Kenh van goc xe (UVMap 0)!", flush=True)
    else:
        print(f"[THANH CONG] Da trich xuat thanh cong {total_lines} net UV tu Kenh Livery chuan (UVMap 1)!", flush=True)

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
