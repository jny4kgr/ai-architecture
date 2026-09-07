"""
朝霞市浜崎3丁目 2号棟 (ランドスタイル) — 実行図PDFから起こしたパラメトリック3Dモデル
実行: /Applications/Blender.app/Contents/MacOS/Blender -b -P build_house.py -- [--render] [--samples N]
座標系: X=東(+), Y=北(+), Z=上。原点 = 本体西壁×南壁の交点(GL)。単位 m。
寸法根拠: 平面詳細図1-3F(1/50)・立面図(1/100)・求積図。910モジュール。
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

# ---------- 図面から読んだ寸法 ----------
X0, X1 = 0.0, 9.555          # 本体 西壁〜東壁 (壁芯)
Y0, Y1 = 0.0, 4.550          # 本体 南壁〜北壁
GX0 = -0.910                 # ガレージ西面 (本体より910張出し)
GL, FL1, FL2, FL3 = 0.0, 0.561, 3.321, 6.121   # 1FL=GL+561, 階高 2,760 / 2,800
EAVE = 8.735                 # 3階軒高
RIDGE = 9.972                # 最高高さ (北側)
SLOPE = (RIDGE - EAVE) / (Y1 - Y0)   # 片流れ 北高・南低
WT = 0.15                    # 外壁厚
IT = 0.10                    # 間仕切り厚
SLAB = 0.25                  # 床厚
HANDRAIL = 1.10

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DO_RENDER = "--render" in argv
SAMPLES = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 96
ONLY_CAM = argv[argv.index("--cam") + 1] if "--cam" in argv else None
DO_ANIM = "--animate" in argv                      # ルームツアー動画 (Eevee 連番PNG)
ANIM_TEST = "--anim-test" in argv                  # 各ショットの始点・終点だけ
ONLY_SHOT = argv[argv.index("--shot") + 1] if "--shot" in argv else None
FPS = 24
DUSK = "--dusk" in argv                             # 夕景 (低い太陽 + 室内灯 + 外構照明)
SUFFIX = "_夕景" if DUSK else ""

# ---------- 初期化 ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'

def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    return c

# ---------- マテリアル ----------
def mat(name, color, rough=0.6, metal=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if alpha < 1:
        bsdf.inputs["Alpha"].default_value = alpha
        bsdf.inputs["Roughness"].default_value = 0.05
        bsdf.inputs["Specular IOR Level"].default_value = 0.8
        m.surface_render_method = 'BLENDED'
        m.use_transparency_overlap = True
    return m

def _nodes(m):
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return nt, bsdf, tc

def siding_mat(name, color, groove_pitch=0.455, ridge_pitch=0.03, rough=0.65, along='z'):
    """横張りサイディング: 働き幅ごとの目地 + 細かい木目状リッジ + 色ムラ。Object座標で貼るので継ぎ目が出ない"""
    m = mat(name, color, rough); nt, bsdf, tc = _nodes(m)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    axis = {"x": 0, "y": 1, "z": 2}[along]
    def wave(pitch, prof):
        w = nt.nodes.new("ShaderNodeTexWave"); w.wave_type = 'BANDS'; w.bands_direction = 'X'; w.wave_profile = prof
        w.inputs["Scale"].default_value = 1.0 / pitch
        comb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(sep.outputs[axis], comb.inputs[0])
        nt.links.new(comb.outputs[0], w.inputs["Vector"]); return w
    g = wave(groove_pitch, 'SAW'); r = wave(ridge_pitch, 'SIN')
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[1].position = 0.06
    nt.links.new(g.outputs["Fac"], ramp.inputs["Fac"])
    mixh = nt.nodes.new("ShaderNodeMath"); mixh.operation = 'MULTIPLY_ADD'
    nt.links.new(ramp.outputs["Color"], mixh.inputs[0]); mixh.inputs[1].default_value = 1.0
    nt.links.new(r.outputs["Fac"], mixh.inputs[2])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.02
    nt.links.new(mixh.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 3.0; noise.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.inputs["Factor"].default_value = 0.12
    mix.inputs[6].default_value = (*color, 1); mix.inputs[7].default_value = (*[c * 0.75 for c in color], 1)
    nt.links.new(noise.outputs["Fac"], mix.inputs["Factor"]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    dark = nt.nodes.new("ShaderNodeMix"); dark.data_type = 'RGBA'
    nt.links.new(ramp.outputs["Color"], dark.inputs["Factor"]); dark.inputs[6].default_value = (*[c * 0.45 for c in color], 1)
    nt.links.new(mix.outputs[2], dark.inputs[7]); nt.links.new(dark.outputs[2], bsdf.inputs["Base Color"])
    return m

def noise_mat(name, color, rough=0.9, scale=40.0, strength=0.3, detail=6, variation=0.25, color2=None):
    """砂利・アスファルト・コンクリート用: ノイズで色ムラ + バンプ"""
    m = mat(name, color, rough); nt, bsdf, tc = _nodes(m)
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = scale; noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.7
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (*color, 1); mix.inputs[7].default_value = (*(color2 or [c * (1 - variation) for c in color]), 1)
    nt.links.new(noise.outputs["Fac"], mix.inputs["Factor"]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = strength
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def gravel_mat(name):
    m = mat(name, (0.55, 0.52, 0.47), 0.95); nt, bsdf, tc = _nodes(m)
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 60.0; vor.inputs["Randomness"].default_value = 1.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.62, 0.60, 0.55, 1); ramp.color_ramp.elements[1].color = (0.38, 0.36, 0.33, 1)
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6; bump.inputs["Distance"].default_value = 0.01
    nt.links.new(vor.outputs["Distance"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m

M = {
 "siding_gray":  siding_mat("A_ブリーレリーブMGグレー", (0.40, 0.41, 0.43)),   # ニチハ モエンサイディングM14 横張り
 "siding_white": siding_mat("B_ルスコミュール調MGホワイト", (0.88, 0.87, 0.84), groove_pitch=0.455, ridge_pitch=0.05),
 "wood_brown":   siding_mat("C_ヴィンテージウッドMGブラウン", (0.30, 0.19, 0.11), groove_pitch=0.15, ridge_pitch=0.01, rough=0.55),
 "roof":         siding_mat("屋根_コロニアルNM-9567", (0.09, 0.09, 0.10), groove_pitch=0.18, ridge_pitch=0.02, rough=0.55, along='y'),
 "glass":        mat("ガラス_Low-E", (0.80, 0.90, 0.92), alpha=0.25),
 "frame":        mat("サッシ_ブラック", (0.05, 0.05, 0.05), 0.4, 0.3),
 "concrete":     noise_mat("土間コンクリート", (0.60, 0.60, 0.58), 0.85, scale=25, strength=0.15, variation=0.15),
 "asphalt":      noise_mat("道路_アスファルト", (0.20, 0.20, 0.21), 0.95, scale=120, strength=0.35, variation=0.5),
 "ground":       gravel_mat("敷地_砂利"),
 "sidewalk":     noise_mat("歩道_ILB", (0.55, 0.53, 0.50), 0.9, scale=30, strength=0.2, variation=0.2),
 "line":         mat("白線", (0.85, 0.85, 0.82), 0.6),
 "neighbor":     noise_mat("隣家_外壁", (0.80, 0.77, 0.70), 0.8, scale=8, strength=0.1, variation=0.1),
 "neighbor2":    noise_mat("隣家_外壁2", (0.58, 0.55, 0.52), 0.8, scale=8, strength=0.1, variation=0.1),
 "neighbor_roof": mat("隣家_屋根", (0.22, 0.14, 0.12), 0.6),
 "neighbor_glass": mat("隣家_ガラス", (0.30, 0.36, 0.42), 0.2, 0.3),
 "leaf":         mat("葉", (0.16, 0.32, 0.10), 0.8),
 "leaf2":        mat("葉_明", (0.30, 0.45, 0.16), 0.8),
 "lawn":         noise_mat("芝", (0.22, 0.38, 0.14), 0.95, scale=60, strength=0.3, variation=0.35),
 "shrub":        mat("低木", (0.14, 0.30, 0.10), 0.85),
 "trunk":        mat("幹", (0.25, 0.18, 0.12), 0.9),
 "metal":        mat("金物_シルバー", (0.70, 0.70, 0.72), 0.35, 0.8),
 "fascia":       mat("破風_ホワイト", (0.92, 0.92, 0.90), 0.5),
 "emit_warm":    mat("発光_電球色", (1.0, 0.85, 0.6), 0.5),
 "emit_off":     mat("器具_消灯", (0.85, 0.85, 0.85), 0.5),
 "interior":     mat("内装_白クロス", (0.92, 0.91, 0.88), 0.8),
 "floor":        mat("フローリング", (0.72, 0.58, 0.40), 0.5),
 "shutter":      mat("ガレージシャッター_ダスクグレー", (0.30, 0.31, 0.33), 0.5, 0.4),
 "rail":         mat("手摺_ホワイト", (0.95, 0.95, 0.95), 0.4),
 "fence":        mat("CB塀", (0.70, 0.70, 0.68), 0.9),
}

# ---------- プリミティブ ----------
def box(name, x0, x1, y0, y1, z0, z1, material, collection="建物"):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = ((x1 - x0), (y1 - y0), (z1 - z0))
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    for c in o.users_collection: c.objects.unlink(o)
    coll(collection).objects.link(o)
    return o

def cut(target, x0, x1, y0, y1, z0, z1):
    """target から直方体をブーリアン減算"""
    c = box("_cut", x0, x1, y0, y1, z0, z1, M["frame"], "_cutters")
    mod = target.modifiers.new("cut", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = c
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(c)

def window(wall, axis, pos, a0, a1, z0, z1, depth=WT):
    """壁に開口を開け、サッシ枠+ガラスを入れる。axis='x' なら壁面が x=pos (南北に延びる壁)。"""
    f = 0.05
    if axis == 'x':
        cut(wall, pos - depth, pos + depth, a0, a1, z0, z1)
        fr = box("サッシ", pos - 0.03, pos + 0.03, a0, a1, z0, z1, M["frame"], "開口")
        cut(fr, pos - 0.1, pos + 0.1, a0 + f, a1 - f, z0 + f, z1 - f)
        box("ガラス", pos - 0.005, pos + 0.005, a0 + f, a1 - f, z0 + f, z1 - f, M["glass"], "開口")
        out = -1 if pos <= X0 + 0.5 else 1
        box("水切り", pos + out * 0.03, pos + out * 0.09, a0 - 0.02, a1 + 0.02, z0 - 0.04, z0 + 0.01, M["metal"], "開口")
        if a1 - a0 > 1.0: box("召し合わせ", pos - 0.02, pos + 0.02, (a0 + a1) / 2 - 0.02, (a0 + a1) / 2 + 0.02, z0, z1, M["frame"], "開口")
    else:
        cut(wall, a0, a1, pos - depth, pos + depth, z0, z1)
        fr = box("サッシ", a0, a1, pos - 0.03, pos + 0.03, z0, z1, M["frame"], "開口")
        cut(fr, a0 + f, a1 - f, pos - 0.1, pos + 0.1, z0 + f, z1 - f)
        box("ガラス", a0 + f, a1 - f, pos - 0.005, pos + 0.005, z0 + f, z1 - f, M["glass"], "開口")
        out = -1 if pos <= Y0 + 0.01 else 1          # 外側の向き
        box("水切り", a0 - 0.02, a1 + 0.02, pos + out * 0.03, pos + out * 0.09, z0 - 0.04, z0 + 0.01, M["metal"], "開口")
        if a1 - a0 > 1.0: box("召し合わせ", (a0 + a1) / 2 - 0.02, (a0 + a1) / 2 + 0.02, pos - 0.02, pos + 0.02, z0, z1, M["frame"], "開口")

def wall_x(name, x, y0, y1, z0, z1, material, t=WT):   # 南北に延びる壁 (面は x=一定)
    return box(name, x - t / 2, x + t / 2, y0, y1, z0, z1, material)
def wall_y(name, y, x0, x1, z0, z1, material, t=WT):   # 東西に延びる壁
    return box(name, x0, x1, y - t / 2, y + t / 2, z0, z1, material)

def prism(name, pts_xyz, vec, material, collection="建物"):
    """任意多角形を vec 方向に押し出した立体"""
    me = bpy.data.meshes.new(name); o = bpy.data.objects.new(name, me); coll(collection).objects.link(o)
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new(p) for p in pts_xyz])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)], vec=vec)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    return o

def sloped_slab(name, x0, x1, y0, y1, z_at, thick, material):
    return prism(name, [(x0, y0, z_at(y0)), (x1, y0, z_at(y0)), (x1, y1, z_at(y1)), (x0, y1, z_at(y1))],
                 (0, 0, thick), material)

# =====================================================================
# 敷地・道路
# =====================================================================
LOT_W, LOT_D = 14.55, 5.67       # 隣地境界線 14.55 / 道路境界 5.67
lot_x0 = GX0 - 4.30              # ガレージ前 土間 4,299
lot_y0 = -0.53                   # 南側 隣地境界まで 528
lot_x1, lot_y1 = lot_x0 + LOT_W, lot_y0 + LOT_D
ROAD_W, SW_W = 10.6, 3.75        # 道路幅員 / 歩道
road_x1 = lot_x0; road_x0 = road_x1 - ROAD_W

def cylinder(name, x, y, z0, z1, r, material, collection="建物"):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2), vertices=16)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(material)
    for c in o.users_collection: c.objects.unlink(o)
    coll(collection).objects.link(o); return o

def tree(x, y, h=4.5, crown=1.8):
    cylinder("街路樹_幹", x, y, 0, h * 0.55, 0.09, M["trunk"], "外構")
    for i, (dx, dy, dz, r) in enumerate([(0, 0, 0, 1.0), (0.5, 0.2, 0.35, 0.75), (-0.45, -0.3, 0.3, 0.7), (0.1, -0.5, 0.55, 0.65), (-0.2, 0.45, 0.6, 0.6)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r * crown / 1.0 * 0.9, location=(x + dx, y + dy, h * 0.55 + dz + crown * 0.6))
        o = bpy.context.active_object; o.name = "街路樹_葉"; o.data.materials.append(M["leaf"])
        bpy.ops.object.shade_smooth()
        for c in o.users_collection: c.objects.unlink(o)
        coll("外構").objects.link(o)

# 地面・道路・歩道・敷地
box("地面", lot_x0 - 800, lot_x0 + 800, lot_y0 - 800, lot_y0 + 800, -0.3, -0.06, M["ground"], "敷地")
box("道路", road_x0, road_x1, lot_y0 - 40, lot_y1 + 40, -0.06, 0.0, M["asphalt"], "敷地")
box("歩道_対面", road_x0 - SW_W, road_x0, lot_y0 - 40, lot_y1 + 40, -0.06, 0.12, M["sidewalk"], "敷地")
box("縁石_対面", road_x0 - 0.15, road_x0, lot_y0 - 40, lot_y1 + 40, -0.06, 0.14, M["concrete"], "敷地")
box("側溝_手前", road_x1 - 0.35, road_x1, lot_y0 - 40, lot_y1 + 40, -0.06, 0.01, M["concrete"], "敷地")
for yy in range(-40, 41, 8):
    box("側溝蓋目地", road_x1 - 0.35, road_x1, lot_y0 + yy - 0.01, lot_y0 + yy + 0.01, 0.005, 0.015, M["frame"], "敷地")
box("白線_外側", road_x1 - 0.55, road_x1 - 0.40, lot_y0 - 40, lot_y1 + 40, 0.0, 0.003, M["line"], "敷地")
box("白線_対面", road_x0 + 0.15, road_x0 + 0.30, lot_y0 - 40, lot_y1 + 40, 0.0, 0.003, M["line"], "敷地")
for yy in range(-40, 41, 10):      # センターライン (破線)
    box("白線_中央", (road_x0 + road_x1) / 2 - 0.075, (road_x0 + road_x1) / 2 + 0.075, lot_y0 + yy, lot_y0 + yy + 5, 0.0, 0.003, M["line"], "敷地")
box("敷地_砂利", lot_x0, lot_x1, lot_y0, lot_y1, -0.06, 0.0, M["ground"], "敷地")
box("土間コンクリート", lot_x0, GX0 + 0.05, Y0 - 0.2, Y1 + 0.35, 0.0, 0.03, M["concrete"], "敷地")
for xx in [lot_x0 + 1.4, lot_x0 + 2.8]:     # 土間の目地
    box("土間目地", xx - 0.008, xx + 0.008, Y0 - 0.2, Y1 + 0.35, 0.025, 0.031, M["frame"], "敷地")
box("土間目地", lot_x0, GX0 + 0.05, 1.35 - 0.008, 1.35 + 0.008, 0.025, 0.031, M["frame"], "敷地")
box("砂利_建物周り", X0 - 0.05, lot_x1, lot_y0, lot_y1, 0.0, 0.05, M["ground"], "敷地")
cut(bpy.data.objects["砂利_建物周り"], X0 - 1, X1 + 0.08, Y0 - 0.08, Y1 + 0.08, -1, 1)
# CB塀 + メッシュフェンス (北・南・東)  天端 +400 / フェンス H600〜800
for nm, (xa, xb, ya, yb) in {"北": (lot_x0 + 0.3, lot_x1, lot_y1 - 0.12, lot_y1),
                             "南": (lot_x0 + 0.3, lot_x1, lot_y0, lot_y0 + 0.12),
                             "東": (lot_x1 - 0.12, lot_x1, lot_y0, lot_y1)}.items():
    box("CB塀_" + nm, xa, xb, ya, yb, -0.05, 0.40, M["concrete"], "外構")
    if nm == "東":
        for yy in [ya + i * 1.0 for i in range(int((yb - ya) / 1.0) + 1)]:
            box("フェンス支柱", xa + 0.03, xa + 0.07, yy - 0.02, yy + 0.02, 0.40, 1.20, M["frame"], "外構")
        box("フェンス上桟", xa + 0.03, xa + 0.07, ya, yb, 1.16, 1.20, M["frame"], "外構")
        box("フェンス下桟", xa + 0.03, xa + 0.07, ya, yb, 0.42, 0.46, M["frame"], "外構")
    else:
        for xx in [xa + i * 1.0 for i in range(int((xb - xa) / 1.0) + 1)]:
            box("フェンス支柱", xx - 0.02, xx + 0.02, ya + 0.03, ya + 0.07, 0.40, 1.00, M["frame"], "外構")
        box("フェンス上桟", xa, xb, ya + 0.03, ya + 0.07, 0.96, 1.00, M["frame"], "外構")
        box("フェンス下桟", xa, xb, ya + 0.03, ya + 0.07, 0.42, 0.46, M["frame"], "外構")
# ---------- 周辺環境: 隣家なし・芝地に株立ちの樹木と低木 ----------
def slender_tree(x, y, h=4.2, mtl=None, seed=0):
    """株立ち風: 細い幹3本 + 縦長の葉の塊"""
    import random; rnd = random.Random(seed)
    for i in range(3):
        dx, dy = rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15)
        cylinder("樹木_幹", x + dx, y + dy, 0, h * 0.7, 0.035, M["trunk"], "外構")
    for i in range(7):
        r = rnd.uniform(0.45, 0.75); dz = rnd.uniform(h * 0.45, h * 0.95); dx, dy = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(x + dx, y + dy, dz))
        o = bpy.context.active_object; o.name = "樹木_葉"; o.scale = (1, 1, 1.4); o.data.materials.append(mtl or M["leaf"])
        bpy.ops.object.shade_smooth()
        for c in o.users_collection: c.objects.unlink(o)
        coll("外構").objects.link(o)

def shrub(x, y, r=0.35, seed=0):
    import random; rnd = random.Random(seed)
    for i in range(3):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r * rnd.uniform(0.7, 1.0),
                                              location=(x + rnd.uniform(-r, r) * 0.6, y + rnd.uniform(-r, r) * 0.6, r * 0.6))
        o = bpy.context.active_object; o.name = "低木"; o.data.materials.append(M["shrub"]); bpy.ops.object.shade_smooth()
        for c in o.users_collection: c.objects.unlink(o)
        coll("外構").objects.link(o)

# 遠景は芝 (敷地外・道路の向こうも)
box("芝_北", lot_x0 - 60, lot_x0 + 60, lot_y1 + 0.02, lot_y1 + 60, -0.05, 0.0, M["lawn"], "敷地")
box("芝_南", lot_x0 - 60, lot_x0 + 60, lot_y0 - 60, lot_y0 - 0.02, -0.05, 0.0, M["lawn"], "敷地")
box("芝_東", lot_x1 + 0.02, lot_x1 + 60, lot_y0, lot_y1, -0.05, 0.0, M["lawn"], "敷地")
box("芝_向かい", road_x0 - SW_W - 60, road_x0 - SW_W, lot_y0 - 60, lot_y1 + 60, -0.05, 0.0, M["lawn"], "敷地")
# 敷地内: ポーチ北側の植栽枡 と 道路沿いの低木
box("植栽枡", lot_x0 + 0.3, lot_x0 + 1.3, Y1 + 0.35, lot_y1 - 0.15, 0.0, 0.12, M["concrete"], "外構")
for i, xx in enumerate([lot_x0 + 1.9, lot_x0 + 2.6, lot_x0 + 3.3]):
    shrub(xx, Y1 + 0.55, r=0.28, seed=i)
# 敷地外: 北・南・向かいに株立ちを散らす (隣家の代わり)
# 樹木は置かない (2026-09-06 指示)。低木のみ
for i in range(3):
    shrub(lot_x0 + 0.8, Y1 + 0.55 + i * 0.5, r=0.26, seed=90 + i)
for i in range(-6, 8):
    shrub(road_x0 - SW_W - 0.6, lot_y0 + i * 2.2, r=0.4, seed=50 + i)
# 電柱

# =====================================================================
# 基礎・床
# =====================================================================
fnd = box("基礎", X0 - 0.08, X1 + 0.08, Y0 - 0.08, Y1 + 0.08, GL, FL1 - 0.03, M["concrete"])
cut(fnd, GX0 - 1, 6.825 - WT, Y0 - 1, 2.730, GL - 1, FL1 + 1)          # 車庫部は土間
box("車庫土間", GX0, 6.825, Y0, 2.730, GL, GL + 0.10, M["concrete"])
box("ポーチ床", GX0, X0, 2.730, Y1, GL, FL1 - 0.02, M["concrete"])
box("ポーチ階段", GX0 - 0.9, GX0, 2.9, Y1, GL, FL1 * 0.5, M["concrete"])
box("1F床_納戸", 6.825 - WT, X1, Y0, Y1, FL1 - 0.02, FL1, M["floor"])
box("1F床_玄関側", X0, 6.825, 2.730, Y1, FL1 - 0.02, FL1, M["floor"])
f2 = box("2F床", GX0 - 0.09, X1, Y0, Y1, FL2 - SLAB, FL2, M["floor"])    # 西へ張出し = ガレージ天井 + バルコニー
cut(f2, X0 - 1, 2.275, 3.640, Y1 + 1, FL2 - 1, FL2 + 1)                    # 2F北西 下屋部は床なし
f3 = box("3F床", 0.455 - 1.0, X1, Y0, Y1, FL3 - SLAB, FL3, M["floor"])
cut(f3, -2, 4.095, 3.640, Y1 + 1, FL3 - 1, FL3 + 1)                        # 3F北西 下屋
box("1F天井", X0, X1, Y0, Y1, FL2 - SLAB - 0.01, FL2 - SLAB, M["interior"])
box("2F天井", X0, X1, Y0, Y1, FL3 - SLAB - 0.01, FL3 - SLAB, M["interior"])
box("車庫天井_木", GX0, 6.825, Y0, 2.730, FL2 - SLAB - 0.01, FL2 - SLAB, M["wood_brown"])

# =====================================================================
# 1F 外壁 (車庫 + 玄関 + 納戸)
# =====================================================================
z0, z1 = GL + 0.10, FL2 - SLAB
w_s1 = wall_y("1F南壁", Y0, GX0, X1, z0, z1, M["siding_gray"])
w_e1 = wall_x("1F東壁", X1, Y0, Y1, z0, z1, M["siding_gray"])
w_n1 = wall_y("1F北壁", Y1, X0, X1, z0, z1, M["siding_white"])
w_w1g = wall_x("1F西壁_車庫", GX0, Y0, 2.730, z0, z1, M["siding_gray"])
w_w1e = wall_x("1F西壁_玄関", X0, 2.730, Y1, z0, z1, M["siding_white"])
w_gn = wall_y("1F車庫北壁", 2.730, GX0, 6.825, z0, z1, M["siding_white"])    # ポーチ側は外壁
# ガレージシャッター開口 W2,480 × H2,500 (電動 LIXIL ダスクグレー) — 開いた状態
sy0 = (Y0 + 2.730) / 2 - 1.24
cut(w_w1g, GX0 - 1, GX0 + 1, sy0, sy0 + 2.48, GL, GL + 0.10 + 2.50)
box("ガレージシャッターBOX", GX0 - 0.02, GX0 + 0.35, sy0, sy0 + 2.48, GL + 0.10 + 2.15, GL + 0.10 + 2.50, M["shutter"])
box("ガレージ内壁_木", GX0 + WT / 2, GX0 + WT / 2 + 0.01, Y0 + WT / 2, 2.730 - WT / 2, GL + 0.1, FL2 - SLAB, M["wood_brown"])
# 玄関ドア (西面・ポーチから)
cut(w_w1e, X0 - 1, X0 + 1, 3.30, 4.20, FL1, FL1 + 2.20)
door = box("玄関ドア_開", X0 + 0.03, X0 + 0.93, 4.14, 4.20, FL1, FL1 + 2.20, M["wood_brown"], "開口")
cut(door, X0 + 0.13, X0 + 0.33, 3, 5, FL1 + 0.4, FL1 + 1.9)
box("玄関ドアガラス", X0 + 0.13, X0 + 0.33, 4.165, 4.175, FL1 + 0.4, FL1 + 1.9, M["glass"], "開口")
# 1F窓 (図面の開口番号に対応・寸法はサッシ呼称から)
window(w_s1, 'y', Y0, 7.6, 8.7, FL1 + 1.5, FL1 + 2.0)      # (5) 高所用ヨコスベリ 11405 納戸南
window(w_s1, 'y', Y0, 3.0, 4.6, FL1 + 1.45, FL1 + 1.95)    # (7) 高所用ヨコスベリ 16505 車庫南
window(w_e1, 'x', X1, 1.6, 3.25, FL1 + 0.9, FL1 + 1.8)     # (4) 引き違い 16509 納戸東
window(w_gn, 'y', 2.730, 4.0, 5.65, FL1 + 0.9, FL1 + 1.8)  # (6) 引き違い 16520 車庫北
window(w_n1, 'y', Y1, 5.7, 6.4, FL1 + 0.9, FL1 + 1.6)      # (3) タテスベリ 02607 トイレ
window(w_n1, 'y', Y1, 4.1, 4.7, FL1 + 1.0, FL1 + 1.7)      # (2) 引き違い 06007 階段
window(w_n1, 'y', Y1, 1.5, 2.1, FL1 + 1.7, FL1 + 2.2)      # (1) 高所用 06005 玄関
# 1F 間仕切り
for name, x, ya, yb in [("玄関-収納", 1.365, 2.730, Y1), ("収納-階段", 2.730, 2.730, Y1),
                        ("階段-階段下", 3.640, 2.730, Y1), ("階段下-トイレ", 4.550, 2.730, Y1),
                        ("トイレ-クローゼット", 5.460, 2.730, Y1), ("車庫-納戸", 6.825, Y0, Y1)]:
    wall_x("1F間仕切_" + name, x, ya, yb, FL1, FL2 - SLAB, M["interior"], IT)

# =====================================================================
# 2F 外壁 (LDK・水回り・バルコニー西)  北西 2.275×0.910 は下屋
# =====================================================================
z0, z1 = FL2, FL3 - SLAB
w_s2 = wall_y("2F南壁", Y0, X0, X1, z0, z1, M["siding_gray"])
w_e2 = wall_x("2F東壁", X1, Y0, Y1, z0, z1, M["siding_gray"])
w_n2 = wall_y("2F北壁", Y1, 2.275, X1, z0, z1, M["siding_white"])
w_n2b = wall_y("2F北壁_下屋側", 3.640, X0, 2.275, z0, z1, M["siding_white"])
w_w2 = wall_x("2F西壁", X0, Y0, 3.640, z0, z1, M["siding_white"])
w_w2b = wall_x("2F西壁_下屋側", 2.275, 3.640, Y1, z0, z1, M["siding_white"])
window(w_w2, 'x', X0, 0.90, 3.41, FL2, FL2 + 1.80)                  # (18) 引き違い 25118 バルコニー出入
window(w_s2, 'y', Y0, 0.70, 2.35, FL2 + 1.60, FL2 + 2.10)          # (17) 高所用ヨコスベリ 16505
window(w_s2, 'y', Y0, 3.10, 4.29, FL2 + 0.95, FL2 + 1.85)          # (16) 引き違い 11909
window(w_s2, 'y', Y0, 5.60, 5.95, FL2 + 1.0, FL2 + 1.9)            # (15) タテスベリ 03609
window(w_s2, 'y', Y0, 7.90, 8.50, FL2 + 1.1, FL2 + 1.8)            # (14) 引き違い 06007 UB
window(w_n2, 'y', Y1, 2.40, 3.00, FL2 + 1.1, FL2 + 1.8)            # (9) 引き違い 06007 物入
window(w_n2, 'y', Y1, 4.40, 5.00, FL2 + 1.1, FL2 + 1.8)            # (10) 06007 階段
window(w_n2, 'y', Y1, 6.10, 6.45, FL2 + 1.1, FL2 + 1.8)            # (11) タテスベリ 03607 廊下
window(w_n2, 'y', Y1, 7.10, 7.45, FL2 + 1.1, FL2 + 1.8)            # (12) 03607 トイレ
window(w_e2, 'x', X1, 2.5, 2.85, FL2 + 1.1, FL2 + 1.8)             # (13) タテスベリ 03607 洗面
wall_x("2F間仕切_LDK-水回り", 7.735, Y0, 3.640, FL2, FL3 - SLAB, M["interior"], IT)
wall_y("2F間仕切_LDK-北", 3.640, 2.275, X1, FL2, FL3 - SLAB, M["interior"], IT)
wall_y("2F間仕切_UB-洗面", 1.820, 7.735, X1, FL2, FL3 - SLAB, M["interior"], IT)
wall_x("2F間仕切_物入-階段", 3.640, 3.640, Y1, FL2, FL3 - SLAB, M["interior"], IT)
wall_x("2F間仕切_階段-トイレ", 6.825, 3.640, Y1, FL2, FL3 - SLAB, M["interior"], IT)
# 2F キッチン (フラット対面プラン W2,590×D970 壁付) とダイニングの当たり
M["kitchen"] = mat("キッチン_ダークグレー", (0.18, 0.18, 0.19), 0.35)
box("キッチンカウンター", 7.735 - IT/2 - 0.97, 7.735 - IT/2, 0.95, 0.95 + 2.59, FL2, FL2 + 0.85, M["kitchen"], "家具")
box("キッチン吊戸棚", 7.735 - IT/2 - 0.35, 7.735 - IT/2, 0.95, 0.95 + 2.59, FL2 + 1.55, FL2 + 2.25, M["interior"], "家具")
box("ダイニングテーブル", 4.6, 6.1, 1.2, 2.0, FL2 + 0.68, FL2 + 0.72, M["wood_brown"], "家具")
for (tx, ty) in [(4.7, 1.3), (6.0, 1.3), (4.7, 1.9), (6.0, 1.9)]:
    box("テーブル脚", tx - 0.03, tx + 0.03, ty - 0.03, ty + 0.03, FL2, FL2 + 0.68, M["wood_brown"], "家具")
# 2F バルコニー (西・全長 / 先端 1,000) 手摺壁 H1,100 + 笠木
box("2Fバルコニー手摺_西", -1.0 - 0.06, -1.0 + 0.06, Y0 - 0.06, Y1 + 0.06, FL2, FL2 + HANDRAIL, M["siding_white"])
box("2Fバルコニー手摺_南", -1.0, X0, Y0 - 0.06, Y0 + 0.06, FL2, FL2 + HANDRAIL, M["siding_white"])
box("2Fバルコニー手摺_北", -1.0, X0, Y1 - 0.06, Y1 + 0.06, FL2, FL2 + HANDRAIL, M["siding_white"])
k = box("2Fバルコニー笠木", -1.0 - 0.08, X0, Y0 - 0.08, Y1 + 0.08, FL2 + HANDRAIL, FL2 + HANDRAIL + 0.04, M["rail"])
cut(k, -1.0 + 0.08, X0 + 1, Y0 + 0.08, Y1 - 0.08, FL2, FL2 + 2)
box("1F下屋屋根", X0 - 0.1, 2.275 + 0.05, 3.640, Y1 + 0.1, FL2 - 0.05, FL2 + 0.05, M["roof"])

# =====================================================================
# 3F 外壁 (洋室A/B/C)  西壁は 455 セットバック、北西 4.095×0.910 下屋、南東バルコニー 2.730×0.910
# =====================================================================
z0, z1 = FL3, EAVE
X3 = 0.455
w_s3 = wall_y("3F南壁", Y0, X3, 6.825, z0, z1, M["siding_gray"])
w_s3b = wall_y("3F南壁_洋室A", 0.910, 6.825, X1, z0, z1, M["siding_gray"])          # バルコニー奥
w_e3 = wall_x("3F東壁", X1, 0.910, Y1, z0, z1, M["siding_gray"])
w_n3 = wall_y("3F北壁", Y1, 4.095, X1, z0, z1, M["siding_white"])
w_n3b = wall_y("3F北壁_下屋側", 3.640, X3, 4.095, z0, z1, M["siding_white"])
w_w3 = wall_x("3F西壁", X3, Y0, 3.640, z0, z1, M["siding_white"])
w_w3b = wall_x("3F西壁_下屋側", 4.095, 3.640, Y1, z0, z1, M["siding_white"])
window(w_w3, 'x', X3, 1.0, 2.65, FL3, FL3 + 1.80)                   # (26) 引き違い 16518 洋室C→バルコニー
window(w_s3, 'y', Y0, 1.0, 2.2, FL3 + 1.5, FL3 + 2.0)               # (25) 高所用 11905
window(w_s3, 'y', Y0, 3.6, 4.75, FL3 + 0.9, FL3 + 1.8)              # (24) 引き違い 11409 洋室B
window(w_s3b, 'y', 0.910, 7.2, 8.7, FL3, FL3 + 1.80)                # (23) 引き違い 15018 洋室A→バルコニー
window(w_e3, 'x', X1, 2.0, 3.65, FL3 + 1.5, FL3 + 2.0)              # (22) 高所用 16505 洋室A東
window(w_n3, 'y', Y1, 7.4, 8.0, FL3 + 1.0, FL3 + 1.9)               # (19) 06009 洋室A北
window(w_n3, 'y', Y1, 4.6, 5.2, FL3 + 1.1, FL3 + 1.8)               # (20) 06007 階段
window(w_n3, 'y', Y1, 5.6, 6.8, FL3 + 1.5, FL3 + 2.0)               # (21) 高所用 11905
wall_x("3F間仕切_洋室C-B", 3.185, Y0, 3.640, FL3, EAVE, M["interior"], IT)
wall_x("3F間仕切_B-クローゼット", 5.915, Y0, 2.730, FL3, EAVE, M["interior"], IT)
wall_y("3F間仕切_洋室B北", 2.730, 3.185, 6.825, FL3, EAVE, M["interior"], IT)
wall_x("3F間仕切_クローゼット-洋室A", 6.825, 0.910, Y1, FL3, EAVE, M["interior"], IT)
wall_y("3F間仕切_廊下-北", 3.640, 4.095, 6.825, FL3, EAVE, M["interior"], IT)

# ---------- ルームツアー用: カメラが通る間仕切りにドア開口 (H2,000) ----------
def door(wall_name, axis, pos, a0, a1, z0):
    cut(bpy.data.objects[wall_name], *( (pos - 0.2, pos + 0.2, a0, a1, z0, z0 + 2.0) if axis == 'x'
                                       else (a0, a1, pos - 0.2, pos + 0.2, z0, z0 + 2.0) ))
door("1F間仕切_玄関-収納", 'x', 1.365, 3.05, 3.85, FL1)     # 玄関→ホール
door("1F間仕切_収納-階段", 'x', 2.730, 3.05, 3.85, FL1)     # ホール→階段
door("2F間仕切_LDK-北", 'y', 3.640, 4.60, 5.40, FL2)         # 階段ホール→LDK
door("3F間仕切_クローゼット-洋室A", 'x', 6.825, 2.75, 3.55, FL3)  # 廊下→洋室A
door("3F間仕切_洋室B北", 'y', 2.730, 4.20, 5.00, FL3)      # 廊下→洋室B
door("3F間仕切_洋室C-B", 'x', 3.185, 1.40, 2.20, FL3)

# ---------- 家具の当たり (生活感は後で作り込む) ----------
M["fabric"] = mat("ファブリック_グレー", (0.45, 0.45, 0.47), 0.9)
M["bedding"] = mat("寝具_ホワイト", (0.93, 0.93, 0.92), 0.9)
box("ソファ座面", 0.9, 2.8, 0.55, 1.45, FL2, FL2 + 0.42, M["fabric"], "家具")
box("ソファ背", 0.9, 2.8, 0.55, 0.75, FL2 + 0.42, FL2 + 0.85, M["fabric"], "家具")
box("TVボード", 0.9, 2.8, 3.30, 3.30 + 0.40, FL2, FL2 + 0.45, M["wood_brown"], "家具")
box("TV", 1.3, 2.4, 3.36, 3.40, FL2 + 0.55, FL2 + 1.20, M["frame"], "家具")
box("ラグ", 0.8, 3.2, 0.9, 3.0, FL2, FL2 + 0.02, M["bedding"], "家具")
for nm, (bx0, bx1, by0, by1) in {"ベッド_洋室A": (7.3, 8.7, 2.9, 4.4), "ベッド_洋室B": (3.4, 4.4, 1.5, 3.5), "ベッド_洋室C": (0.7, 1.7, 1.2, 3.2)}.items():
    box(nm + "_台", bx0, bx1, by0, by1, FL3, FL3 + 0.30, M["wood_brown"], "家具")
    box(nm + "_マット", bx0 + 0.03, bx1 - 0.03, by0 + 0.03, by1 - 0.03, FL3 + 0.30, FL3 + 0.50, M["bedding"], "家具")

# ---------- 天井の面光源 (Eevee 内観用) ----------
def ceiling_light(name, x, y, z, power=120, size=0.6):
    bpy.ops.object.light_add(type='AREA', location=(x, y, z))
    l = bpy.context.active_object; l.name = name
    l.data.energy = power; l.data.size = size; l.data.color = (1.0, 0.95, 0.88)
    for c in l.users_collection: c.objects.unlink(l)
    coll("照明").objects.link(l)
ceiling_light("灯_車庫", 2.5, 1.4, FL2 - SLAB - 0.05, 200, 1.0)
ceiling_light("灯_玄関ホール", 1.8, 3.6, FL2 - SLAB - 0.05, 80)
ceiling_light("灯_LDK西", 2.5, 2.0, FL3 - SLAB - 0.05, 150, 0.8)
ceiling_light("灯_LDK東", 5.5, 2.0, FL3 - SLAB - 0.05, 150, 0.8)
ceiling_light("灯_廊下3F", 5.5, 2.4, EAVE - 0.05, 60)
ceiling_light("灯_洋室A", 8.2, 2.7, EAVE - 0.05, 120, 0.8)
ceiling_light("灯_洋室B", 4.5, 1.8, EAVE - 0.05, 80)
# 3F 西バルコニー (先端 1,000 / 洋室C前) と 南東バルコニー
BX = X3 - 1.0
box("3Fバルコニー手摺_西", BX - 0.06, BX + 0.06, Y0 - 0.06, 3.640 + 0.06, FL3, FL3 + HANDRAIL, M["siding_white"])
box("3Fバルコニー手摺_南", BX, X3, Y0 - 0.06, Y0 + 0.06, FL3, FL3 + HANDRAIL, M["siding_white"])
box("3Fバルコニー手摺_北", BX, X3, 3.640 - 0.06, 3.640 + 0.06, FL3, FL3 + HANDRAIL, M["siding_white"])
box("3Fバルコニー手摺_SE南", 6.825, X1 + 0.06, Y0 - 0.06, Y0 + 0.06, FL3, FL3 + HANDRAIL, M["siding_gray"])
box("3Fバルコニー手摺_SE東", X1 - 0.06, X1 + 0.06, Y0, 0.910, FL3, FL3 + HANDRAIL, M["siding_gray"])
box("3Fバルコニー手摺_SE西", 6.825 - 0.06, 6.825 + 0.06, Y0, 0.910, FL3, FL3 + HANDRAIL, M["siding_gray"])
box("2F下屋屋根", X0 - 0.1, 4.095 + 0.05, 3.640, Y1 + 0.1, FL3 - 0.05, FL3 + 0.05, M["roof"])
box("2F下屋屋根_西", X0 - 0.1, X3, Y0, 3.640, FL3 - 0.05, FL3 + 0.05, M["roof"])  # 3F西セットバック上

# =====================================================================
# 屋根 (片流れ 北高・南低)  軒の出 ~250
# =====================================================================
zroof = lambda y: EAVE + SLOPE * (y - Y0)
sloped_slab("屋根_西", X3 - 0.25, 4.095, Y0 - 0.25, 3.640 + 0.25, zroof, 0.18, M["roof"])
sloped_slab("屋根_東", 4.095, X1 + 0.25, Y0 - 0.25, Y1 + 0.25, zroof, 0.18, M["roof"])
# 妻壁の三角部分 (北側が高い)
prism("3F西妻壁", [(X3 - WT/2, Y0, EAVE), (X3 - WT/2, 3.640, EAVE), (X3 - WT/2, 3.640, zroof(3.640))], (WT, 0, 0), M["siding_white"])
prism("3F東妻壁", [(X1 - WT/2, Y0, EAVE), (X1 - WT/2, Y1, EAVE), (X1 - WT/2, Y1, zroof(Y1))], (WT, 0, 0), M["siding_gray"])
prism("3F下屋側妻壁", [(4.095 - WT/2, 3.640, EAVE), (4.095 - WT/2, Y1, EAVE), (4.095 - WT/2, Y1, zroof(Y1))], (WT, 0, 0), M["siding_white"])
wall_y("3F北壁_屋根下", Y1, 4.095, X1, EAVE, zroof(Y1), M["siding_white"])
wall_y("3F北壁_下屋側_屋根下", 3.640, X3, 4.095, EAVE, zroof(3.640), M["siding_white"])

# ---------- 外観ディテール: 破風・鼻隠し・樋・水切り・給湯器・ポスト・庇 ----------
box("鼻隠し_南", X3 - 0.27, X1 + 0.27, Y0 - 0.27, Y0 - 0.23, zroof(Y0 - 0.25) - 0.02, zroof(Y0 - 0.25) + 0.20, M["fascia"])
box("鼻隠し_北", 4.095, X1 + 0.27, Y1 + 0.23, Y1 + 0.27, zroof(Y1 + 0.25) - 0.02, zroof(Y1 + 0.25) + 0.20, M["fascia"])
box("鼻隠し_北_下屋側", X3 - 0.27, 4.095, 3.640 + 0.23, 3.640 + 0.27, zroof(3.640 + 0.25) - 0.02, zroof(3.640 + 0.25) + 0.20, M["fascia"])
for nm, x, y0_, y1_ in [("破風_西", X3 - 0.25, Y0 - 0.25, 3.640 + 0.25), ("破風_東", X1 + 0.25, Y0 - 0.25, Y1 + 0.25), ("破風_中", 4.095, 3.640 + 0.25, Y1 + 0.25)]:
    prism(nm, [(x - 0.02, y0_, zroof(y0_) - 0.02), (x - 0.02, y1_, zroof(y1_) - 0.02), (x - 0.02, y1_, zroof(y1_) + 0.20), (x - 0.02, y0_, zroof(y0_) + 0.20)], (0.04, 0, 0), M["fascia"])
# 軒樋 (南の軒先) と 竪樋
box("軒樋_南", X3 - 0.27, X1 + 0.27, Y0 - 0.33, Y0 - 0.27, zroof(Y0 - 0.25) - 0.02, zroof(Y0 - 0.25) + 0.10, M["metal"])
for nm, x, y in [("竪樋_南西", X3 + 0.10, Y0 - 0.10), ("竪樋_南東", X1 - 0.10, Y0 - 0.10)]:
    cylinder(nm, x, y, 0.15, zroof(Y0 - 0.25), 0.035, M["metal"])
cylinder("竪樋_2Fバルコニー", -1.0 + 0.08, Y1 - 0.10, 0.15, FL2, 0.03, M["metal"])
# 幕板/水切り: 各階の境
for z in [FL2 - SLAB - 0.02, FL3 - SLAB - 0.02]:
    box("胴差水切り_南", GX0 - 0.02 if z < FL2 else X0 - 0.02, X1 + 0.02, Y0 - WT / 2 - 0.03, Y0 - WT / 2 + 0.01, z, z + 0.04, M["metal"])
    box("胴差水切り_東", X1 + WT / 2 - 0.01, X1 + WT / 2 + 0.03, Y0 - 0.02, Y1 + 0.02, z, z + 0.04, M["metal"])
box("土台水切り_南", GX0 - 0.02, X1 + 0.02, Y0 - WT / 2 - 0.03, Y0 - WT / 2 + 0.01, GL + 0.10, GL + 0.14, M["metal"])
box("土台水切り_東", X1 + WT / 2 - 0.01, X1 + WT / 2 + 0.03, Y0 - 0.02, Y1 + 0.02, GL + 0.10, GL + 0.14, M["metal"])
# 給湯器 (東側・配置図) / ポスト (ポーチ・フェイサスFF ステンシルバー) / 玄関庇の下面(木)
box("給湯器", X1 + WT / 2 + 0.02, X1 + WT / 2 + 0.30, 0.55, 1.05, 0.35, 1.05, M["metal"])
box("ポスト", X0 - 0.15, X0 + 0.02, 2.95, 3.30, FL1 + 0.55, FL1 + 0.95, M["metal"])
box("ポーチ天井_木", GX0, X0, 2.730 + WT / 2, Y1, FL2 - SLAB - 0.012, FL2 - SLAB - 0.002, M["wood_brown"])
box("玄関ステップ照明", X0 - 0.05, X0 + 0.02, 4.30, 4.45, FL1 + 1.9, FL1 + 2.1, M["metal"])
# バルコニー笠木 (3F 2箇所)
k3 = box("3Fバルコニー笠木", BX - 0.08, X3, Y0 - 0.08, 3.640 + 0.08, FL3 + HANDRAIL, FL3 + HANDRAIL + 0.04, M["rail"])
cut(k3, BX + 0.08, X3 + 1, Y0 + 0.08, 3.640 - 0.08, FL3, FL3 + 2)
k4 = box("3Fバルコニー笠木_SE", 6.825 - 0.08, X1 + 0.08, Y0 - 0.08, 0.910, FL3 + HANDRAIL, FL3 + HANDRAIL + 0.04, M["rail"])
cut(k4, 6.825 + 0.08, X1 - 0.08, Y0 + 0.08, 0.910 + 1, FL3, FL3 + 2)

# ---------- 外壁の内側面を内装仕上げに (車庫内は木目) ----------
def line_interior(wall, inward):
    me = wall.data
    me.materials.append(M["interior"]); me.materials.append(M["wood_brown"])
    i_int, i_wood = len(me.materials) - 2, len(me.materials) - 1
    for poly in me.polygons:
        if poly.normal.dot(inward) > 0.9:
            c = poly.center
            in_garage = (c.z < FL2 - SLAB) and (c.x < 6.825 - 0.05) and (c.y < 2.730 + 0.05)
            poly.material_index = i_wood if in_garage else i_int
INWARD = {"南壁": (0, 1, 0), "北壁": (0, -1, 0), "東壁": (-1, 0, 0), "西壁": (1, 0, 0), "車庫北壁": (0, -1, 0)}
for o in list(coll("建物").objects):
    if o.type != 'MESH' or "間仕切" in o.name or "妻壁" in o.name or "屋根下" in o.name or "バルコニー" in o.name: continue
    for key, vec in INWARD.items():
        if key in o.name:
            line_interior(o, Vector(vec)); break
# 間仕切りの車庫側 (車庫-納戸 壁の西面) も木目
w = bpy.data.objects["1F間仕切_車庫-納戸"]; w.data.materials.append(M["wood_brown"])
for poly in w.data.polygons:
    if poly.normal.x < -0.9 and poly.center.y < 2.730: poly.material_index = len(w.data.materials) - 1

# =====================================================================
# 照明・カメラ・レンダー設定
# =====================================================================
# 照明: 太陽ランプ + 単色の空 (Blender 5.2 の物理空は露出が読みにくいので予測可能な構成にする)
bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
sun = bpy.context.active_object; sun.name = "太陽"
sun.data.energy = 4.5
sun.data.angle = math.radians(1.0)
sun.rotation_euler = (math.radians(38), 0, math.radians(-115))   # 南西上空 (新座・9月 14時ごろの近似)
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]; bg.inputs["Strength"].default_value = 0.9
tcw = nt.nodes.new("ShaderNodeTexCoord"); sepw = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tcw.outputs["Generated"], sepw.inputs[0])
mapw = nt.nodes.new("ShaderNodeMapRange"); mapw.inputs["From Min"].default_value = -0.05; mapw.inputs["From Max"].default_value = 0.6
nt.links.new(sepw.outputs["Z"], mapw.inputs["Value"])
rampw = nt.nodes.new("ShaderNodeValToRGB")
rampw.color_ramp.elements[0].color = (0.80, 0.84, 0.88, 1)     # 地平線: 白っぽい
rampw.color_ramp.elements[1].color = (0.28, 0.48, 0.85, 1)     # 天頂: 青
e = rampw.color_ramp.elements.new(0.35); e.color = (0.55, 0.70, 0.92, 1)
nt.links.new(mapw.outputs[0], rampw.inputs["Fac"]); nt.links.new(rampw.outputs["Color"], bg.inputs["Color"])

def spot(name, loc, target, power, angle=60, color=(1.0, 0.85, 0.65), size=0.1):
    bpy.ops.object.light_add(type='SPOT', location=loc)
    l = bpy.context.active_object; l.name = name
    l.data.energy = power; l.data.spot_size = math.radians(angle); l.data.spot_blend = 0.6; l.data.color = color; l.data.shadow_soft_size = size
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    for c in l.users_collection: c.objects.unlink(l)
    coll("外構照明").objects.link(l); return l

# 外構照明: ポーチのダウンライト / 植栽枡のアップライト / ガレージ内 / 2Fバルコニー下のダウンライト
spot("DL_ポーチ", (X0 - 0.45, 3.75, FL2 - SLAB - 0.03), (X0 - 0.45, 3.75, 0), 250, 100)
spot("UP_植栽", (lot_x0 + 0.8, Y1 + 0.3, 0.15), (lot_x0 + 0.8, Y1 + 0.75, 1.5), 150, 60)
spot("UP_外壁_北西", (X0 - 0.6, Y1 + 0.25, 0.15), (X0 - 0.2, Y1 + 0.1, 7.0), 600, 40)
spot("UP_外壁_南西", (GX0 - 0.6, Y0 - 0.25, 0.15), (GX0 - 0.2, Y0 - 0.1, 7.0), 600, 40)
spot("DL_バルコニー下_1", (GX0 - 0.5, 0.6, FL2 - SLAB - 0.03), (GX0 - 0.5, 0.6, 0), 200, 100)
spot("DL_バルコニー下_2", (GX0 - 0.5, 2.1, FL2 - SLAB - 0.03), (GX0 - 0.5, 2.1, 0), 200, 100)
# 追加の外構・建物照明 (夜景用)
def point(name, loc, power, color=(1.0, 0.85, 0.62), radius=0.05):
    bpy.ops.object.light_add(type='POINT', location=loc)
    l = bpy.context.active_object; l.name = name; l.data.energy = power; l.data.color = color; l.data.shadow_soft_size = radius
    for c in l.users_collection: c.objects.unlink(l)
    coll("外構照明").objects.link(l); return l
def fixture(name, x0, x1, y0, y1, z0, z1):
    """器具本体 (夜は発光・昼は白)"""
    return box(name, x0, x1, y0, y1, z0, z1, M["emit_warm"] if DUSK else M["emit_off"], "外構")
# 玄関ブラケット (ポーチ壁) / 車庫の天井DL 2灯 / 外壁アップライト 追加 2灯 (バルコニー壁を洗う) / フットライト 3灯
fixture("ブラケット_玄関", X0 - 0.10, X0 - 0.02, 3.05, 3.20, FL1 + 1.85, FL1 + 2.05)
point("PT_ブラケット_玄関", (X0 - 0.15, 3.12, FL1 + 1.95), 60)
for yy in (0.8, 2.0):
    fixture("DL_車庫器具", 2.5 - 0.06, 2.5 + 0.06, yy - 0.06, yy + 0.06, FL2 - SLAB - 0.02, FL2 - SLAB - 0.005)
    spot("DL_車庫", (2.5, yy, FL2 - SLAB - 0.03), (2.5, yy, 0), 300, 110)
for yy in (0.9, 3.6):
    fixture("DL_バルコニー下器具", GX0 - 0.55, GX0 - 0.45, yy - 0.05, yy + 0.05, FL2 - SLAB - 0.02, FL2 - SLAB - 0.005)
spot("UP_バルコニー_2F", (GX0 - 1.6, 1.4, 0.15), (GX0 - 1.0, 1.4, FL2 + 0.8), 500, 35, size=0.15)
spot("UP_バルコニー_3F北", (X0 - 1.9, 3.9, 0.15), (X0 - 0.5, 3.9, FL3 + 0.8), 400, 30, size=0.15)
for i, yy in enumerate((Y1 + 0.5, Y1 + 0.85, Y1 + 1.2)):
    cylinder(f"フットライト{i}", lot_x0 + 1.4, yy, 0.12, 0.42, 0.03, M["frame"], "外構")
    fixture(f"フットライト{i}_灯", lot_x0 + 1.4 - 0.035, lot_x0 + 1.4 + 0.035, yy - 0.035, yy + 0.035, 0.36, 0.42)
    point(f"PT_フットライト{i}", (lot_x0 + 1.4, yy, 0.40), 12, radius=0.03).data.use_shadow = False
# 3F バルコニーの壁付け灯 / 給湯器脇は無し
fixture("ブラケット_3Fバルコニー", X3 - 0.08, X3 - 0.02, 3.0, 3.15, FL3 + 2.0, FL3 + 2.15)
point("PT_3Fバルコニー", (X3 - 0.15, 3.07, FL3 + 2.05), 40)

for l in coll("外構照明").objects: l.hide_render = not DUSK
for l in coll("照明").objects:  l.hide_render = not DUSK          # 室内灯は夕景のときだけ
if DUSK:
    # ブルーアワー: 残光は弱く、空は濃紺。主役は建物の灯り
    sun.data.energy = 0.25; sun.data.color = (0.65, 0.72, 1.0); sun.data.angle = math.radians(8)   # 空からの青い環境光相当
    sun.rotation_euler = (math.radians(60), 0, math.radians(-100))
    bg.inputs["Strength"].default_value = 0.10
    rampw.color_ramp.elements[0].color = (0.70, 0.42, 0.28, 1)       # 地平線: 残光の橙 (弱)
    rampw.color_ramp.elements[1].color = (0.02, 0.04, 0.12, 1)       # 天頂: 濃紺
    rampw.color_ramp.elements[2].color = (0.10, 0.12, 0.30, 1)
    mapw.inputs["From Max"].default_value = 0.35
    for l in coll("照明").objects: l.data.energy *= 2.5
    M["glass"].node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.5
    # 発光器具
    em = M["emit_warm"].node_tree.nodes["Principled BSDF"]
    em.inputs["Emission Color"].default_value = (1.0, 0.80, 0.55, 1); em.inputs["Emission Strength"].default_value = 25
    # 濡れたような土間・道路 (反射で灯りが映る)
    for key in ("concrete", "asphalt"):
        M[key].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.30
        M[key].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.7

def add_camera(name, loc, target, lens=28):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object; cam.name = name
    cam.data.lens = lens; cam.data.clip_end = 500
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return cam

cams = [
 add_camera("Cam_南西_外観", (-13.0, -4.8, 1.7), (2.5, 2.0, 4.2), 26),
 add_camera("Cam_道路_北西", (-13.0, 9.5, 1.7), (2.5, 2.2, 4.2), 26),
 add_camera("Cam_ガレージ正面", (-11.5, 1.6, 1.5), (3.0, 1.6, 3.4), 30),
 add_camera("Cam_俯瞰_南東", (17, -11, 11), (4.3, 2.3, 4.0), 32),
 add_camera("Cam_LDK内観", (0.9, 0.7, FL2 + 1.5), (7.2, 2.6, FL2 + 1.2), 20),
]
scene.camera = cams[0]

scene.render.engine = 'CYCLES'
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280; scene.render.resolution_y = 720
if "--preview" in argv: scene.render.resolution_percentage = 50
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
EXPOSURE_EXT, EXPOSURE_INT = (0.4, -0.6) if DUSK else (-0.3, 1.8)
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
    print("GPU devices:", [(d.name, d.type) for d in prefs.devices])
except Exception as e:
    print("GPU setup failed, CPU fallback:", e)

if "_cutters" in bpy.data.collections:
    bpy.data.collections.remove(bpy.data.collections["_cutters"])

blend_path = os.path.join(OUT_DIR, "浜崎2号棟.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("SAVED", blend_path, "objects:", len(bpy.data.objects))

if DO_RENDER:
    for cam in cams:
        if ONLY_CAM and cam.name != ONLY_CAM: continue
        scene.camera = cam
        scene.view_settings.exposure = EXPOSURE_INT if "内観" in cam.name else EXPOSURE_EXT
        scene.render.filepath = os.path.join(OUT_DIR, "render" + ("_preview" if "--preview" in argv else ""), cam.name + SUFFIX + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)


# =====================================================================
# ルームツアー (--animate): 外観一周 → 1F → 2F → 3F   20秒 @24fps
# =====================================================================
CX, CY = 4.3, 2.3   # 建物中心
def orbit(theta_deg, r=17.0, z=5.0):
    t = math.radians(theta_deg); return (CX + r * math.cos(t), CY + r * math.sin(t), z)

SHOTS = [
 # name, seconds, lens, exposure, camera keys [(t秒, loc)], target keys [(t秒, loc)]
 ("01_外観一周", 6.0, 30, EXPOSURE_EXT,
    [(0, (-13.0, 10.0, 1.8)), (6.0, (-13.0, -6.0, 1.8))],
    [(0, (2.5, 2.2, 4.2)), (6.0, (2.5, 2.0, 4.2))]),
 ("02_1F車庫", 2.0, 24, 0.6,
    [(0, (-4.5, 1.4, 1.4)), (2.0, (1.5, 1.4, 1.4))],
    [(0, (4.0, 1.4, 1.3)), (2.0, (6.0, 2.0, 1.3))]),
 ("03_1F玄関", 2.0, 22, 0.7,
    [(0, (-0.7, 3.5, FL1 + 1.45)), (2.0, (1.2, 3.45, FL1 + 1.45))],
    [(0, (3.0, 3.45, FL1 + 1.3)), (2.0, (4.5, 3.45, FL1 + 1.2))]),
 ("04_2F_LDK", 5.0, 20, 0.6,
    [(0, (-0.75, 2.15, FL2 + 1.5)), (2.0, (1.2, 2.1, FL2 + 1.5)), (5.0, (3.6, 2.0, FL2 + 1.45))],
    [(0, (5.0, 2.2, FL2 + 1.1)), (3.0, (7.2, 2.3, FL2 + 1.0)), (5.0, (7.4, 1.6, FL2 + 0.9))]),
 ("05_3F_洋室A", 5.0, 20, 0.6,
    [(0, (3.9, 3.15, FL3 + 1.5)), (2.5, (6.6, 3.15, FL3 + 1.5)), (5.0, (7.3, 3.0, FL3 + 1.45))],
    [(0, (9.0, 3.15, FL3 + 1.2)), (2.5, (9.0, 3.4, FL3 + 1.0)), (5.0, (8.2, 0.6, FL3 + 1.0))]),
]

def build_shot(name, seconds, lens, exposure, cam_keys, tgt_keys):
    n = int(round(seconds * FPS))
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=tgt_keys[0][1])
    tgt = bpy.context.active_object; tgt.name = "Target_" + name
    bpy.ops.object.camera_add(location=cam_keys[0][1])
    cam = bpy.context.active_object; cam.name = "Shot_" + name
    cam.data.lens = lens; cam.data.clip_start = 0.05; cam.data.clip_end = 500
    con = cam.constraints.new('TRACK_TO'); con.target = tgt
    con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
    for t, loc in cam_keys:
        cam.location = loc; cam.keyframe_insert("location", frame=1 + int(round(t * FPS)))
    for t, loc in tgt_keys:
        tgt.location = loc; tgt.keyframe_insert("location", frame=1 + int(round(t * FPS)))
    for o in (cam, tgt):
        for fc in o.animation_data.action.fcurves if hasattr(o.animation_data.action, "fcurves") else []:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    for c in cam.users_collection: c.objects.unlink(cam)
    for c in tgt.users_collection: c.objects.unlink(tgt)
    coll("ルームツアー").objects.link(cam); coll("ルームツアー").objects.link(tgt)
    cam["frames"] = n; cam["exposure"] = exposure if not DUSK or exposure == EXPOSURE_EXT else EXPOSURE_INT
    return cam, n

shot_cams = [build_shot(*sh) for sh in SHOTS]
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

if DO_ANIM:
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 16
    scene.eevee.shadow_pool_size = '1024'
    scene.render.fps = FPS
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for (cam, n), sh in zip(shot_cams, SHOTS):
        name = sh[0]
        if ONLY_SHOT and ONLY_SHOT not in name: continue
        scene.camera = cam
        scene.view_settings.exposure = cam["exposure"]
        scene.frame_start, scene.frame_end = 1, n
        scene.frame_step = (n - 1) if ANIM_TEST else 1
        scene.render.filepath = os.path.join(OUT_DIR, "render", ("anim_test" if ANIM_TEST else "anim") + SUFFIX, name, "f_")
        bpy.ops.render.render(animation=True)
        print("ANIM_DONE", name, n)
