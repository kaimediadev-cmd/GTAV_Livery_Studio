# ==============================================================================
# GTA V Auto UV Livery Template Generator (Universal)
# Tu dong trich xuat UVMap 1 (Livery Decal) chuan 4K sieu sach cho MOI LOAI XE GTA V
# ==============================================================================

import bpy
import addon_utils
import sys
import os
import shutil
import tempfile
import math

# Load thu vien Pillow
sys.path.append(r"C:\Users\KAI Media\AppData\Roaming\Python\Python313\site-packages")
from PIL import Image, ImageDraw

# Bat addon Sollumz
addon_utils.enable("Sollumz", default_set=True)

def generate_livery_template(target_xml_path, out_dir=None, target_size=4096, export_photoshop=True, export_preview=True):
    target_xml_path = target_xml_path.strip().strip('"').strip("'")
    target_xml_path = os.path.abspath(target_xml_path)

    # Kiem tra neu nguoi dung keo file .yft (nhi phan) thay vi .yft.xml
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

    # Thu muc xuat file anh: Uu tien out_dir truyen vao, neu khong thi luu cung thu muc voi XML
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

    # Tao thu muc tam va doi ten file de Sollumz luon import doc lap (khong bi loi merge LOD/xung dot bone)
    temp_dir = tempfile.mkdtemp(prefix="gtav_uv_")
    solo_xml_name = "vehicle_model_solo.yft.xml"
    temp_xml_path = os.path.join(temp_dir, solo_xml_name)
    shutil.copy2(target_xml_path, temp_xml_path)

    try:
        # Reset blender scene
        bpy.ops.wm.read_homefile(use_empty=True)
        
        # Import file qua Sollumz
        bpy.ops.sollumz.import_assets(
            directory=temp_dir + "\\",
            files=[{"name": solo_xml_name}]
        )
    except Exception as e:
        print(f"\n[LOI KHI IMPORT] Khong the doc du lieu xe qua Sollumz: {e}", flush=True)
        return
    finally:
        # Don dep thu muc tam
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("[Buoc 2/4] Da nap xong model xe! Dang loc tim bo phan than vo & UV Livery...", flush=True)

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

    total_lines = 0

    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.name.endswith(".col"):
            continue
            
        name_lower = obj.name.lower()
        
        # Loai bo tat ca noi that, kinh, den, gam may, oc vit de chi giu lai than vo (chassis / body / doors / bonnet / boot)
        skip_keywords = [
            "glass", "window", "windscreen", "interior", "engine", "chassis_low", 
            "wheel", "tire", "dial", "steering", "seat", "pedal", "mirror_interior",
            "exhaust", "radiator", "suspension", "brake", "rotor", "caliper",
            "light", "headlight", "taillight", "siren", "indicator", "reverse",
            "mesh_screw", "mesh_badge", "mesh_emblem", "undercarriage", "grille",
            "subframe", "susp", "axle", "shock", "spring", "muffler", "wiper",
            "plate", "license", "dummy", "col"
        ]
        
        if any(kw in name_lower for kw in skip_keywords):
            continue
            
        mesh = obj.data
        if not mesh.uv_layers:
            continue
            
        # Mac dinh cua GTA V: Kenh Livery luon nam o UVMap thu 2 hoac dau tien (thuong ten la UVMap 1 hoac Channel 1)
        uv_layer = None
        for layer in mesh.uv_layers:
            if "1" in layer.name or "livery" in layer.name.lower() or "ch1" in layer.name.lower():
                uv_layer = layer
                break
                
        if not uv_layer:
            uv_layer = mesh.uv_layers[0]
            
        uv_data = uv_layer.data
        
        for poly in mesh.polygons:
            loop_indices = poly.loop_indices
            poly_uvs = [uv_data[i].uv for i in loop_indices]
            
            # 1. Kiem tra neu polygon bi thu hep ve goc (0, 0) hoac goc tren (0, 1)
            is_collapsed_origin = all(abs(u) < 0.015 and abs(v) < 0.015 for u, v in poly_uvs)
            is_collapsed_top = all(abs(u) < 0.015 and abs(v - 1.0) < 0.015 for u, v in poly_uvs)
            if is_collapsed_origin or is_collapsed_top:
                continue
                
            n = len(poly_uvs)
            for i in range(n):
                u1, v1 = poly_uvs[i]
                u2, v2 = poly_uvs[(i + 1) % n]
                
                # 2. Loai bo duong noi ve diem ghim goc (0, 0) hoac (0, 1)
                if (abs(u1) < 0.015 and abs(v1) < 0.015) or (abs(u2) < 0.015 and abs(v2) < 0.015):
                    continue
                if (abs(u1) < 0.015 and abs(v1 - 1.0) < 0.015) or (abs(u2) < 0.015 and abs(v2 - 1.0) < 0.015):
                    continue
                    
                # 3. Loai bo duong cat xuyen qua canvas do Seam Wrapping (vet cat ngang doc do cuon mep UV)
                # Trong khong gian UV [0, 1], mot canh tam giac than xe khong bao gio dai qua 38% chieu rong/dai
                if abs(u1 - u2) > 0.38 or abs(v1 - v2) > 0.38:
                    continue
                    
                # Toa do pixel tren anh 1:1
                x1 = int(u1 * size)
                y1 = int((1.0 - v1) * size)
                x2 = int(u2 * size)
                y2 = int((1.0 - v2) * size)
                
                # Chi ve cac canh nam trong khung hinh 1:1
                if max(x1, x2) >= 0 and min(x1, x2) <= size and max(y1, y2) >= 0 and min(y1, y2) <= size:
                    p1 = (x1, y1)
                    p2 = (x2, y2)
                    if draw_dark:
                        draw_dark.line([p1, p2], fill=(0, 240, 255, 230), width=1)
                    if draw_trans:
                        draw_trans.line([p1, p2], fill=(255, 255, 255, 220), width=1)
                    total_lines += 1

    print(f"[Buoc 3/4] Da trich xuat xong {total_lines} duong net UV than vo!", flush=True)
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