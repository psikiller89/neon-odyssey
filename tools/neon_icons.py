#!/usr/bin/env python3
"""Generate neon sci-fi icons (Font Awesome Free glyphs, CC BY 4.0) and assign them to item and spell sources."""
import glob, os, re, sys, yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FA = os.environ.get("FA_DIR", os.path.expanduser("~/work/fa/package"))
OUT = os.path.join(ROOT, "icons", "neon")
MOD = "modules/neon-odyssey/icons/neon"
S = 512

CODES = dict((m.group(1), chr(int(m.group(2), 16))) for m in
             re.finditer(r'\.fa-([a-z0-9-]+)\s*\{\s*--fa:\s*"\\([0-9a-f]+)', open(f"{FA}/css/all.css").read()))
FONT = ImageFont.truetype(f"{FA}/webfonts/fa-solid-900.ttf", 250)

PAL = {
    "pink": ("#ff2e97", "#ff9a3c"), "cyan": ("#2de2ff", "#7b5cff"), "yellow": ("#ffd31a", "#ff7a2f"),
    "orange": ("#ff7a2f", "#ff2e97"), "green": ("#3dff8f", "#1fb7ff"), "violet": ("#c45cff", "#ff2e97"),
    "red": ("#ff3b3b", "#ffb02e"), "teal": ("#2dffd5", "#2d8cff"), "lime": ("#b6ff2e", "#2dffb0"),
    "blue": ("#4d8bff", "#2de2ff"),
}

def grad(c1, c2, size):
    a, b = Image.new("RGB", size, c1), Image.new("RGB", size, c2)
    m = Image.linear_gradient("L").resize(size)
    return Image.composite(b, a, m)

def shape_mask(round_):
    m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
    if round_: d.ellipse((20, 20, S - 20, S - 20), fill=255)
    else: d.rounded_rectangle((20, 20, S - 20, S - 20), radius=70, fill=255)
    return m

def render(glyph, pal, round_):
    c1, c2 = PAL[pal]
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    mask = shape_mask(round_)
    bg = Image.radial_gradient("L").resize((S, S))
    bg = Image.merge("RGB", [bg.point(lambda v: int(30 - v * 24 / 255)), bg.point(lambda v: int(12 - v * 9 / 255)), bg.point(lambda v: int(60 - v * 45 / 255))])
    grid = ImageDraw.Draw(bg)
    for i in range(0, S, 32):
        grid.line((i, 0, i, S), fill=(40, 22, 80)); grid.line((0, i, S, i), fill=(40, 22, 80))
    img.paste(bg, (0, 0), mask)
    # glyph
    gm = Image.new("L", (S, S), 0); gd = ImageDraw.Draw(gm)
    if glyph == "blade":
        gd.polygon([(370, 100), (412, 100), (412, 142), (232, 322), (190, 280)], fill=255)
        gd.polygon([(150, 262), (172, 240), (272, 340), (250, 362)], fill=255)
        gd.polygon([(196, 316), (216, 336), (150, 402), (130, 382)], fill=255)
        gd.ellipse((106, 384, 146, 424), fill=255)
    else:
        ch = CODES[glyph]
        l, t, r, b = gd.textbbox((0, 0), ch, font=FONT)
        gd.text(((S - (r - l)) / 2 - l, (S - (b - t)) / 2 - t), ch, font=FONT, fill=255)
    glow = Image.new("RGBA", (S, S), c1); glow.putalpha(gm.filter(ImageFilter.GaussianBlur(18)))
    img = Image.alpha_composite(img, glow); img = Image.alpha_composite(img, glow)
    fill = grad(c1, c2, (S, S)).convert("RGBA"); fill.putalpha(gm)
    img = Image.alpha_composite(img, fill)
    # border
    ring = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(17)))
    bglow = Image.new("RGBA", (S, S), c1); bglow.putalpha(ring.filter(ImageFilter.GaussianBlur(10)))
    border = grad(c1, c2, (S, S)).convert("RGBA"); border.putalpha(ring)
    img = Image.alpha_composite(Image.alpha_composite(img, bglow), border)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0)); out.paste(img, (0, 0), ImageChops.lighter(mask, bglow.getchannel("A")))
    return out.resize((256, 256), Image.LANCZOS)

def first(name, rules, default):
    n = name.lower()
    for keys, val in rules:
        if any(k in n for k in keys.split("|")) and (val[0] in CODES or val[0] == "blade"): return val
    return default

ITEM_RULES = [
    ("grenade|explosive|bomb|charge|mine", ("bomb", "orange")), ("flamethrower|thermite|incendiar", ("fire-flame-curved", "red")),
    ("laser|plasma|pulse|beam|ray", ("gun", "cyan")), ("sniper|scope", ("crosshairs", "pink")),
    ("pistol|rifle|gun|carbine|cannon|scatter|blaster|smg|shotgun", ("gun", "orange")),
    ("shock|stun|taser|sap|baton|lance", ("bolt-lightning", "cyan")), ("hammer|maul|mace|flail|club", ("hammer", "pink")),
    ("blade|sword|knife|claw|glaive|axe|spear|saber|dagger|katana", ("blade", "pink")), ("fist|knuckle|gauntlet", ("hand-fist", "pink")),
    ("shield", ("shield-halved", "cyan")), ("armor|vest|suit", ("user-shield", "cyan")),
    ("goggle|glasses|visor", ("glasses", "teal")), ("mask|respirator", ("mask-face", "teal")),
    ("coat|cloth|disguise|uniform|outfit", ("shirt", "violet")),
    ("power cell|battery|cell", ("battery-full", "green")), ("med|stim|heal|antidote|pharma|surgeon", ("kit-medical", "green")),
    ("toxin|poison|venom", ("skull-crossbones", "lime")), ("chip|data|drive", ("microchip", "cyan")),
    ("deck|computer|spiking|terminal|hack", ("laptop-code", "cyan")), ("communicator|radio|jammer|signal|transmitter", ("tower-broadcast", "teal")),
    ("scanner|sensor|detector|motion", ("satellite-dish", "teal")), ("drone|bot|robot", ("robot", "cyan")),
    ("light|lamp|lighter|torch|flare", ("lightbulb", "yellow")), ("ration|food|meal", ("bowl-food", "yellow")),
    ("drink|water|canteen", ("bottle-water", "teal")), ("rope|cable|grappl|line", ("link", "violet")),
    ("lock|bypass|infiltrat|thieves", ("unlock", "violet")), ("navigation|map|surveying|compass", ("compass", "teal")),
    ("tool|kit|engineer|construction|mechanic|repair", ("screwdriver-wrench", "yellow")), ("chemist|brew|alchem|vial|flask|gas|canister", ("flask", "lime")),
    ("game", ("dice", "violet")), ("instrument|music", ("guitar", "violet")), ("pigment|paint|art", ("palette", "violet")),
    ("binocular|telescope", ("binoculars", "teal")), ("focus|crystal|orb", ("gem", "violet")), ("tent|shelter|blanket|sleeping", ("campground", "yellow")),
    ("pack|bag|locker|drum|bin|case|box|crate|container", ("box-open", "yellow")), ("bullet|shell|ammo|round", ("burst", "orange")),
]
TYPE_DEFAULT = {"weapon": ("gun", "orange"), "equipment": ("microchip", "cyan"), "consumable": ("vial", "green"),
                "container": ("box-open", "yellow"), "tool": ("screwdriver-wrench", "yellow"), "loot": ("gear", "teal")}
SPELL_RULES = [
    ("fire|flame|burn|inferno|heat|scorch|magma", ("fire-flame-curved", "red")), ("lightning|shock|storm|thunder|volt|electr", ("bolt-lightning", "cyan")),
    ("cold|ice|frost|freez|chill", ("snowflake", "blue")), ("heal|cure|restor|revive|vital|life", ("heart-pulse", "green")),
    ("teleport|dimension|step|portal|warp|blink|door", ("circle-nodes", "violet")), ("summon|spirit|conjure|familiar", ("ghost", "teal")),
    ("shield|armor|ward|protect|barrier|sanctu", ("shield-halved", "cyan")), ("eye|sight|detect|scry|see|locate|sense", ("eye", "teal")),
    ("charm|suggest|command|dominat|mind|psych|telepath|confus", ("brain", "pink")), ("invisib|vanish|blur", ("eye-slash", "violet")),
    ("death|blight|necro|wither|vampir|drain", ("skull", "lime")), ("gene|body|alter|polymorph|shape|enlarge|reduce", ("dna", "lime")),
    ("time|temporal|haste|slow|chrono", ("hourglass-half", "yellow")), ("poison|toxic|acid|spray|cloud", ("biohazard", "lime")),
    ("light|radian|sun|dawn", ("sun", "yellow")), ("dark|shadow|night", ("moon", "violet")), ("earth|quake|stone|rock|wall", ("mountain", "orange")),
    ("wind|gust|levitat|fly|feather", ("wind", "teal")), ("water|tide|wave", ("water", "blue")), ("grav|force|kinetic|push|missile|blast", ("meteor", "orange")),
    ("illusion|image|phantasm|mirror", ("masks-theater", "violet")), ("tech|machine|circuit|code|grid|hack|cyber|data", ("microchip", "cyan")),
    ("hold|bind|restrain|web|entangle|paraly", ("link", "pink")), ("fear|terror|scare", ("ghost", "pink")),
]
SCHOOL = {"abj": ("shield-halved", "cyan"), "con": ("wand-magic-sparkles", "yellow"), "div": ("eye", "teal"), "enc": ("brain", "pink"),
          "evo": ("explosion", "red"), "ill": ("masks-theater", "violet"), "nec": ("skull", "lime"), "trs": ("dna", "green")}

def main():
    os.makedirs(OUT, exist_ok=True)
    made, changed = set(), 0
    for kind in ("items", "spells"):
        for f in sorted(glob.glob(os.path.join(ROOT, "packs/_source", kind, "**/*.yml"), recursive=True)):
            text = open(f).read(); d = yaml.safe_load(text)
            if not isinstance(d, dict) or "system" not in d: continue
            if kind == "spells":
                glyph, pal = first(d["name"], SPELL_RULES, SCHOOL.get(d["system"].get("school"), ("wand-magic-sparkles", "violet"))); shape = "s"
            else:
                glyph, pal = first(d["name"], ITEM_RULES, TYPE_DEFAULT.get(d["type"], ("gear", "teal"))); shape = "i"
            key = f"{shape}-{glyph}-{pal}"
            if key not in made:
                render(glyph, pal, shape == "s").save(os.path.join(OUT, key + ".webp"), "WEBP", quality=90); made.add(key)
            img = f"{MOD}/{key}.webp"
            if d.get("img") != img:
                new = re.sub(r"(?m)^img: .*$", f"img: {img}", text, count=1)
                if new != text: open(f, "w").write(new); changed += 1
    for f in os.listdir(OUT):
        if f.endswith(".webp") and f[:-5] not in made: os.remove(os.path.join(OUT, f))
    print(f"icons: {len(made)} generated, {changed} documents updated")

if __name__ == "__main__":
    main()
