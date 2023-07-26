import re
import sys
import click
import shutil

from loguru  import logger
from pathlib import Path
from typing  import List

class Obsidian:
    '''
    在这个正则表达式片段 [^\]]+ 中，它可以被解释为：
    
    [^]：匹配除了右方括号 ] 之外的任意字符。
    +：表示匹配前面的模式（[^]）一次或多次。
    因此，[^\]]+ 将匹配一个或多个不是右方括号 ] 的连续字符。
    '''
    pattern = r'!\[\[([^\]]+)\]\]'
    @staticmethod
    def replace_img_link_fmt_and_copy(obsi_content_lines: List[str], obsip: Path, blogp: Path):
        '''
        src_dir:
            The directory which obsidian file locate 
        '''
        assert obsip.exists()
        assert blogp.exists()

        src_dir = obsip.parent
        dst_dir = blogp.parent

        assert src_dir.is_dir()
        assert dst_dir.is_dir()

        for idx, line in enumerate(obsi_content_lines):
            # obs图片格式        :![[Pasted image 20230725144646.png]]
            # hexo中所用的图片格式 :![](afl-forkserver-maneuver/mydraw.png)    afl-forkserver-maneuver是文件名字
            if line.strip().startswith("![["):
                picname = str(re.findall(Obsidian.pattern, line)[0])

                blog_article_name_nosuf = blogp.name.split(".")[0] # make "自我介绍.md" to "自我介绍"
                new_picname = picname.replace(" ", "-")
                obsi_content_lines[idx] = f"![]({blog_article_name_nosuf}/{new_picname})"
                logger.info(f"writeback with {obsi_content_lines[idx]}")


                org_picture: Path = src_dir / "attachments" / picname
                dst_pic_dir: Path = dst_dir / blog_article_name_nosuf
                assert org_picture.is_file()
                assert dst_pic_dir.is_dir()
                # -------------- actually change -------------------
                logger.info(f"copy {org_picture} to {dst_pic_dir / new_picname}")
                shutil.copy2(org_picture, dst_pic_dir / new_picname)

        with open(blogp, "a", encoding="utf-8") as blogf:
            blogf.writelines(obsi_content_lines)
        
        logger.info("Done")


@click.command()
@click.option('--fr', '-f', required=True, type=Path, help='Path from obsidian file.')
@click.option('--to', '-t', required=True, type=Path, help='Path to blog file.')
def main(fr: Path, to: Path):
    logger.info(f'copy {fr} to {to}')
    if not fr.exists():
        logger.error(f"fr {fr} not exist")
        sys.exit(1)
    if not to.exists():
        logger.error(f"to {to} not exist")
        sys.exit(1)
    
    obsi_content_lines = []
    with open(fr, "r", encoding="utf-8") as obsif:
        obsi_content_lines = obsif.readlines()
        Obsidian.replace_img_link_fmt_and_copy(
            obsi_content_lines,
            fr,
            to
        )

# py .\o2b.py -f F:\Sync\Inbox\自我介绍.md -t F:\BlogSite\hexo\source\_posts\test-for-script.md
if __name__ == '__main__':
    main()


