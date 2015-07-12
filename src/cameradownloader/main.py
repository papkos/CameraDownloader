import argparse
import datetime as dt
from pathlib import Path
import shutil
from PIL import Image

__author__ = 'Ákos Pap'

EXIF_DT = 0x0132  # from PIL.ExifTags.TAGS

FILENAME_PATTERN = '{date}_{num}.{ext}'


def handle_existing_dst_dir(dst_dir: Path):
    """
    Hook to handle when the destination directory already exists.

    @type dst_dir: Path
    @param dst_dir: The directory that was not created because it already existed.
    """
    print("Destination directory already exists!")


def mkdir_silent(d: Path):
    """
    Silently creates the directory and all missing parents, or passes if it already exists.

    @type d: Path
    @param d: The path to the directory to create.
    @return: The path itself.
    """
    try:
        d.mkdir(parents=True)
    except FileExistsError:
        pass
    return d


def check_src_dir(d: Path) -> bool:
    """
    Checks whether the source directory passes some tests.

    @type d: Path
    @param d: The path to the directory to check.
    @return: True only if the directory passes all tests, False otherwise.
    """
    checks = [
        d.exists(),
        d.is_dir(),
    ]
    return all(checks)


def iglob(pattern: str) -> str:
    """
    Modifies the GLOB pattern to be case-insensitive by replacing each alphabetic character 'c' with '[cC]'.
    Source: http://stackoverflow.com/a/10886685/1119508

    @type pattern: str
    @param pattern: The pattern to make case-insensitive.
    @return: The case-insensitive glob pattern.
    """
    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
    return ''.join(either(c) for c in pattern)


def parse_args():
    description = "Copy digital camera photos to a destination directory, while sorting them to folders " \
                  "based on their creation date. Also rename them so that the new file name contains " \
                  "the date and the unique number of the image."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--src', required=True, help='The source directory that will be (recursively)'
                                                           ' searched for image files.')
    parser.add_argument('-d', '--dst', required=True, help='The destination directory that will contain '
                                                           'date-named directories of photos.')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    dst_dir = Path(args.dst)
    try:
        dst_dir.mkdir(parents=True)
    except FileExistsError:
        handle_existing_dst_dir(dst_dir)

    src_dir = Path(args.src).resolve()
    check_src_dir(src_dir)

    images = src_dir.rglob(iglob('*.jpg'))
    # videos = src_dir.rglob(iglob('*.mov'))

    for image_name in images:
        image = Image.open(str(image_name))
        image_dt = image._getexif()[EXIF_DT]
        image_dt = dt.datetime.strptime(image_dt, '%Y:%m:%d %H:%M:%S')

        num = image_name.stem.split('_')[-1]

        filename = FILENAME_PATTERN.format(
            date=image_dt.strftime('%Y%m%d'),
            num=num,
            ext=image_name.suffix.lower()[1:],  # remove '.' from the beginning of the extension
        )

        date_dir = (dst_dir / Path(image_dt.strftime('%Y%m%d')))
        mkdir_silent(date_dir)
        dst = (date_dir / Path(filename))

        with image_name.open(mode='rb') as source_file:
            with dst.open(mode='wb') as destination_file:
                shutil.copyfileobj(source_file, destination_file)
                print("Copied %s." % dst.name)
    print("Done.")


if __name__ == '__main__':
    main()
