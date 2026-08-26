from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
cover = Image.open(
    r"C:\Users\Mstavo\.cursor\projects\c-Users-Mstavo-Desktop-Ai-Financial-Analytics-System\assets\c__Users_Mstavo_AppData_Roaming_Cursor_User_workspaceStorage_03401c363242a55a7fd9d28c32bb388e_images_image-7be558e3-a436-40f6-942d-8a3ae6770787.png"
)
toc = Image.open(
    r"C:\Users\Mstavo\.cursor\projects\c-Users-Mstavo-Desktop-Ai-Financial-Analytics-System\assets\c__Users_Mstavo_AppData_Roaming_Cursor_User_workspaceStorage_03401c363242a55a7fd9d28c32bb388e_images_image-0435f296-4ed9-4341-bf5c-96361cd62e54.png"
)
print("cover", cover.size, "toc", toc.size)

cw, ch = cover.size
cover_logo = cover.crop((int(cw * 0.04), int(ch * 0.03), int(cw * 0.42), int(ch * 0.14)))
cover_logo.save(ROOT / "duracapital_logo_cover_crop.png")

hero = cover.crop((int(cw * 0.05), int(ch * 0.28), int(cw * 0.95), int(ch * 0.72)))
hero.save(ROOT / "cover_hero.png")

tw, th = toc.size
toc_logo = toc.crop((int(tw * 0.62), int(th * 0.02), int(tw * 0.97), int(th * 0.12)))
toc_logo.save(ROOT / "duracapital_logo_header_crop.png")
print("saved", list(ROOT.glob("*.png")))
