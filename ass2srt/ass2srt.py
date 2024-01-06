import re
import sys


class Ass2srt:
    def __init__(self, filename, encoding="utf-8"):
        self.filename = filename
        self.encoding = encoding
        self.load(filename=filename,
                  encoding=encoding)

    def output_name(self, tag=None):
        outputfile = self.filename[0:-4]
        if tag:
            outputfile = outputfile+"."+tag
        return outputfile+".srt"

    def load(self, filename=None, encoding=None):
        if filename is None:
            filename = self.filename

        if encoding is None:
            encoding = self.encoding

        with open(file=filename, mode="r", encoding=encoding) as f:
            data = f.readlines()

        self.nodes = []
        for line in data:
            if line.startswith("Dialogue"):
                line = line.lstrip("Dialogue:")
                #  split at commas, unless in bracktes, eg  {\fad(500,500)}{\be35}樱律联萌站 bbs.ylbud.com
                #  note that perhaps it would be better to split at commas, unless in curley brackets
                node = _split_ignoring_parentheses(line, delimiter=',')

                assert len(node) == 10

                node[1] = timefmt(node[1])
                node[2] = timefmt(node[2])

                # Extract contents within curly brackets
                bracket_contents = re.findall(r'\{(.*?)\}', node[9])
                # Remove everything within curly brackets from node[9] using bracket_contents
                for content in bracket_contents:
                    node[9] = node[9].replace("{" + content + "}", "")

                node[9] = re.sub(r'\\N', "\n", node[9])

                node.append(bracket_contents)

                self.nodes.append(node)
                # print(f"{node[1]}-->{node[2]}:{node[9]}\n")

    def to_srt(self, name=None, encoding=None, line=0, tag=None):
        if name is None:
            name = self.output_name(tag=tag)
        if encoding is None:
            encoding = self.encoding
        with open(file=name, mode="w", encoding=encoding) as f:
            index = 1
            for node in self.nodes:
                f.writelines(f"{index}\n")
                f.writelines(f"{node[1]} --> {node[2]}\n")
                if line == 1:
                    text = node[9].split("\n")[0]
                elif line == 2:
                    tmp = node[9].split("\n")
                    if len(tmp) > 1:
                        text = tmp[1]
                else:
                    text = node[9]
                f.writelines(f"{text}\n\n")
                index += 1
            # print(f"字幕转换完成:{self.filename}-->{name}")

    def __str__(self):
        return f"文件名:{self.filename}\n合计{len(self.nodes)}条字幕\n"



def _split_ignoring_parentheses(s, delimiter=','):
    splits = []
    last_split = 0
    stack = []  # Stack to keep track of the types of open parentheses

    # Define pairs of parentheses including half-width and full-width characters
    parentheses_pairs = [
        "()", "（）",  # Regular and full-width round brackets
        "[]", "［］",  # Regular and full-width square brackets
        "{}", "【】",  # Curly and full-width fancy brackets
        "<>", "〈〉", "＜＞"  # Regular, full-width, and fancy angle brackets
    ]
    open_paren = "".join([pair[0] for pair in parentheses_pairs])
    close_paren = "".join([pair[1] for pair in parentheses_pairs])
    pairs = dict(zip(open_paren, close_paren))

    for i, char in enumerate(s):
        if char in open_paren:
            stack.append(pairs[char])  # Push the corresponding closing parenthesis
        elif char in close_paren:
            if stack and char == stack[-1]:  # If it's the correct closing type
                stack.pop()
            else:
                # Handle mismatched or unbalanced parentheses here if needed
                pass
        elif char == delimiter and not stack:  # If it's a comma and no open parentheses
            splits.append(s[last_split:i])
            last_split = i + 1

    splits.append(s[last_split:])  # Add the last segment
    return splits


def timefmt(strt):
    strt = strt.replace(".", ",")
    return f"{strt}0"


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help=".ass file to convert")
    parser.add_argument("-s", "--suffix", default="zh", choices=["zh", "en", "fr", "de"],
                        help="add suffix to subtitles name")
    parser.add_argument("-l", "--line", type=int,
                        choices=[0, 1, 2], default=0, help="keep double subtitles")
    parser.add_argument("-i", "--info", action="store_true",
                        help="display subtitles infomation")
    parser.add_argument("-o", "--out", help="output file name")

    args = parser.parse_args()

    if args.file is None:
        parser.print_help()

    app = Ass2srt(args.file)
    if args.info:
        print(app)
        sys.exit()

    line = 0
    if args.line:
        line = args.line

    app.to_srt(name=args.out, line=line, tag=args.suffix)


if __name__ == "__main__":
    main()
