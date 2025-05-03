import json
import ezodf
import math
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color

# --- HEX → Lab ---
def hex_to_lab(hex_code):
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    srgb = sRGBColor(r, g, b)
    return convert_color(srgb, LabColor)

# --- ΔE76 (CIELAB simple) ---
def delta_e_cielab(lab1, lab2):
    return math.sqrt(
        (lab1.lab_l - lab2.lab_l) ** 2 +
        (lab1.lab_a - lab2.lab_a) ** 2 +
        (lab1.lab_b - lab2.lab_b) ** 2
    )

# --- Données d'entrée ---
with open("message.txt", "r", encoding="utf-8") as f:
    message_data = json.load(f)

with open("armor_data.json", "r", encoding="utf-8") as f:
    armor_data = json.load(f)

# --- Entêtes ---
rows = [("HEX", "COLOR", "CLOSEST COLOR", "CLOSEST HEX", "CLOSEST", "PIECE", "", "ΔE (CIELAB)")]

# --- Mapping des pièces ---
type_mapping = {
    "VELVET_TOP_HAT": "Top Hat",
    "CASHMERE_JACKET": "Jacket",
    "SATIN_TROUSERS": "Trousers",
    "OXFORD_SHOES": "Shoes"
}

# --- Traitement des couleurs ---
for item in message_data:
    input_hex = item["itemData"]["hex"].lstrip("#").upper()
    lab_input = hex_to_lab(input_hex)

    closest = None
    min_delta = float("inf")
    for ref in armor_data:
        ref_hex = ref["color"].lstrip("#").upper()
        lab_ref = hex_to_lab(ref_hex)
        delta = delta_e_cielab(lab_input, lab_ref)
        if delta < min_delta:
            min_delta = delta
            closest = {
                "name": ref["name"],
                "hex": ref_hex,
                "color": ref["color"],
                "delta": delta
            }

    # Récupérer la pièce (ajustement ici)
    piece = type_mapping.get(item["itemData"]["itemId"], "Unknown")

    # Ligne : HEX | COLOR | CLOSEST COLOR | CLOSEST HEX | CLOSEST | PIECE | "" | ΔE
    rows.append((input_hex, "", "", closest["hex"], closest["name"], piece, "", round(closest["delta"], 2)))

# --- Génération ODS ---
doc = ezodf.newdoc(doctype="ods", filename="SeymourSweat.ods")
sheet = ezodf.Sheet("Palette ΔE", size=(len(rows), len(rows[0])))
doc.sheets += sheet

for r, row in enumerate(rows):
    for c, val in enumerate(row):
        sheet[r, c].set_value(val)

doc.save()
print("Fichier 'palette_cielab_formaté_v4.ods' généré avec succès.")
