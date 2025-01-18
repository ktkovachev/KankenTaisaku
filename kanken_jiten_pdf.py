from typing import Iterable
import fitz
import os
from io import BytesIO
from pathlib import Path
from PIL import Image
from pytesseract import image_to_osd, TesseractError
from tqdm import tqdm


# All pages will have exactly 1 image, as that's how the PDF was generated when I created it.
def get_image(pdf: Path) -> Image.Image:
    with fitz.open(pdf) as f:
        page_num = 0
        page = f.load_page(page_num)
        image_info = page.get_images(full=True)[0]
        xref = image_info[0]
        base_image = f.extract_image(xref)
        image_bytes = base_image["image"]
        b = BytesIO(image_bytes)
        image = Image.open(b)
        return image


def get_images_from_dir(directory: Path):
    for file in tqdm(sorted(directory.glob("*.pdf"))):
        yield get_image(file)


def output_images(in_dir: Path, out_dir: Path):
    out_dir.mkdir(exist_ok=True, parents=True)  # Ensure output path exists

    for i, img in enumerate(get_images_from_dir(in_dir)):
        img.save(out_dir / f"{i}.{img.format}")


def process_images(img_dir: Path):
    for img_file in tqdm(sorted(img_dir.glob("*"), key=lambda n: int(n.stem))):
        img = Image.open(img_file)
        changes_made = False

        # # Dimensions check: obviated by OSD step below
        # if img.height > img.width:
        #     img = img.rotate(90, expand=True)  # Ensure landscape
        #     changes_made = True

        # Tesseract-based orientation check
        try:
            osd = image_to_osd(img, output_type="dict")
            if osd["rotate"] > 0:
                img = img.rotate(osd["rotate"], expand=True)  # Flip to be upright
                changes_made = True
        except TesseractError:
            # May occur, but we don't really care
            # I noticed this happens if the page lacks enough detail (DPI?) to
            # be OSDed.
            pass

        if changes_made:
            img.save(img_file)

        img.close()


def compile_pdf(files: Iterable[Path], out_dir: Path, name: str = "漢検漢字辞典.pdf"):
    out_dir.mkdir(exist_ok=True, parents=True)  # Ensure output path exists

    doc = fitz.open()  # PDF with the pictures

    # Source: https://pymupdf.readthedocs.io/en/latest/recipes-images.html#how-to-make-one-pdf-of-all-your-pictures-or-files
    for f in files:
        img = fitz.open(f)  # open pic as document
        rect = img[0].rect  # pic dimension
        pdfbytes = img.convert_to_pdf()  # make a PDF stream
        img.close()  # no longer needed
        imgPDF = fitz.open("pdf", pdfbytes)  # open stream as PDF
        page = doc.new_page(
            width=rect.width,  # new page with ...
            height=rect.height,
        )  # pic dimension
        page.show_pdf_page(rect, imgPDF, 0)  # image fills the page

    out_path = out_dir / name
    doc.save(out_path)


# Using my custom file layout, not really meant to be portable
def compile_pdf_auto(out_dir: Path):
    honbun = lambda x: Path("build/pdf/honbun") / f"{x}.JPEG"
    index = lambda x: Path("build/pdf/indices") / f"{x}.JPEG"
    extra = lambda x: Path("build/pdf/extra") / f"{x}.JPEG"
    order = (
        [honbun(x) for x in range(9)]
        + [index(x) for x in range(113)]
        + [honbun(x) for x in range(9, 825)]
        + [extra(x) for x in range(58)]
    )
    compile_pdf(tqdm(order), out_dir)


def renumber_files(out_dir: Path):
    for i, old_name in enumerate(sorted(out_dir.glob("*"), key=lambda n: int(n.stem))):
        new_name = old_name.with_stem(str(i))
        print(old_name, new_name)
        os.rename(old_name, new_name)


def main():
    import sys
    import argparse

    main = argparse.ArgumentParser()
    main.add_argument("action", choices=["extract", "process", "renumber", "compile"])
    args = main.parse_args(sys.argv[1:2])

    if args.action == "extract":
        extract = argparse.ArgumentParser()
        extract.add_argument("--in-dir", "-i", metavar="in_dir", required=True)
        extract.add_argument("--out-dir", "-o", metavar="out_dir", required=True)
        args = extract.parse_args(sys.argv[2:])
        in_dir = Path(args.in_dir)
        out_dir = Path(args.out_dir)
        output_images(in_dir, out_dir)
    elif args.action == "process":
        process = argparse.ArgumentParser()
        process.add_argument("--img-dir", "-i", metavar="img_dir", required=True)
        args = process.parse_args(sys.argv[2:])
        img_dir = Path(args.img_dir)
        process_images(img_dir)
    elif args.action == "renumber":
        renumber = argparse.ArgumentParser()
        renumber.add_argument("--in-dir", "-i", required=True, metavar="in_dir")
        args = renumber.parse_args(sys.argv[2:])
        in_dir = Path(args.in_dir)
        renumber_files(in_dir)
    elif args.action == "compile":
        compile = argparse.ArgumentParser()
        compile.add_argument("files", nargs="*")
        compile.add_argument("--out-dir", "-o", default="build/pdf", metavar="out_dir")
        args = compile.parse_args(sys.argv[2:])
        out_dir = Path(args.out_dir)
        if len(args.files) == 0:
            compile_pdf_auto(out_dir)
        else:
            paths = map(Path, args.files)
            compile_pdf(paths, out_dir)
    else:
        exit(1)


if __name__ == "__main__":
    main()
