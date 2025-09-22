from datetime import datetime
from libs.easy_llm.utils.print_style import PrintStyle

add_view = PrintStyle(background_color='green')
update_view = PrintStyle(background_color='palevioletred')


class BaseMsg:
    role_map = {
        'HumanMsg': 'user',
        'AIMsg': 'assistant',
        'SystemMsg': 'system',
        'SummaryMsg': 'user',
    }

    def __init__(self, content, create_time=None):
        if create_time is None:
            create_time = datetime.now()
        self.create_time = create_time
        self.content = content
        self.json = {'role': self.role_map[self.__class__.__name__], 'content': f"{self.content}"}
        self.prefix = ' '  # 标识符。标识数据的变动。
        self.old = ''  # 保留更新前的数据。

    def set_prefix(self, prefix):
        self.prefix = prefix  # 给print使用

    def __repr__(self):
        return f"""{self.__class__.__name__}({self.content})"""

    def update(self, text: str):
        """
        更新content前，将的content存储在old，因此只能显示对象最新的一次改动。
        """
        if text == self.content:
            print(f"warning:update text same old text: {text}")
            return
        self.set_prefix('~')
        self.old = self.content
        self.content = text


class MsgList(list):
    """
    实现一次增删改查的git风格显示。
    使用with关键字查看一次修改的历史记录。
    with msg_list:
        msg_list.delete_middle(1, 1)
    """

    def __init__(self, *msgs, name="MsgList", git_mode=True):
        super().__init__(msgs)
        self.name = name
        self._copy = None
        self.msg_view = ''
        self.git_mode = git_mode

    @staticmethod
    def get_temp_list(old_lines, new_lines):
        # 计算长度差异并填充较短的列表
        temp_old_lines = old_lines.copy()
        temp_new_lines = new_lines.copy()
        diff = len(old_lines) - len(new_lines)
        if diff > 0:
            temp_new_lines.extend([""] * diff)  # 填充 new_lines
        elif diff < 0:
            temp_old_lines.extend([""] * -diff)  # 填充 old_lines
        return temp_old_lines, temp_new_lines

    def display_add(self, new_lines, msg_index, msg):
        self.msg_view += add_view.get_styled_text(f"{msg_index}: {msg.__class__.__name__}(\n")
        for row, line in enumerate(new_lines, start=1):
            self.msg_view += add_view.get_styled_text(f"+{row}: {line}\n")
        self.msg_view += add_view.get_styled_text(')\n')

    def display_update(self, old_lines, new_lines, msg_index, msg):
        self.msg_view += f"{msg_index}: {msg.__class__.__name__}(\n"
        temp_old_lines, temp_new_lines = self.get_temp_list(old_lines, new_lines)
        temp_red = ""
        temp_green = ""
        for row, (old_line, new_line) in enumerate(zip(temp_old_lines, temp_new_lines), start=1):

            if old_line == new_line:
                if temp_red:
                    self.msg_view += temp_red
                    temp_red = ""
                if temp_green:
                    self.msg_view += temp_green
                    temp_green = ""
                self.msg_view += f" {row}: {new_line}\n"

            else:
                if old_line:
                    temp_red += update_view.get_styled_text(
                        f"-{row}: {old_line}\n")
                if new_line:
                    temp_green += add_view.get_styled_text(f"+{row}: {new_line}\n")
        self.msg_view += f"{temp_red}{temp_green}"
        self.msg_view += ')\n'

    def display_stable(self, new_lines, msg_index, msg):
        self.msg_view += f"{msg_index}: {msg.__class__.__name__}(\n"
        for row, line in enumerate(new_lines, start=1):
            self.msg_view += f" {row}: {line}\n"
        self.msg_view += ')\n'

    def display_delete(self, new_lines, msg_index, msg):
        self.msg_view += update_view.get_styled_text(f"{msg_index}: {msg.__class__.__name__}(\n")
        for row, line in enumerate(new_lines, start=1):
            self.msg_view += update_view.get_styled_text(f"-{row}: {line}\n")
        self.msg_view += update_view.get_styled_text(')\n')

    def display_body(self):
        """
        基于msg对象的前缀来决定如何显示
        """
        if not self.git_mode:
            for msg_index, msg in enumerate(self):
                new_lines = str(msg.content).splitlines()
                self.display_stable(new_lines, msg_index, msg)
            return self.msg_view

        msg_objs = self._copy if self._copy else self
        for msg_index, msg in enumerate(msg_objs):
            old_lines = str(msg.old).splitlines()
            new_lines = str(msg.content).splitlines()
            if msg.prefix == "+":
                self.display_add(new_lines, msg_index, msg)
                msg.prefix = " "
            elif msg.prefix == "-":
                self.display_delete(new_lines, msg_index, msg)
                msg.prefix = " "
                self._copy = None
            elif msg.prefix == "~":
                self.display_update(old_lines, new_lines, msg_index, msg)
                msg.prefix = " "
            else:
                self.display_stable(new_lines, msg_index, msg)
        return self.msg_view

    def __repr__(self):
        name = self.name
        if len(self) == 0:
            return f"{name}(empty)"
        counts = f"(total={len(self)},human={self.human_count()},ai={self.ai_count()}):"
        body = self.display_body()
        self.msg_view = ''
        return f"{name}{counts}\n{body}"

    def append(self, item):
        item.set_prefix("+")
        if self._copy:
            self._copy.append(item)
        super().append(item)

    def insert(self, index, item):
        item.set_prefix("+")
        if self._copy:
            self._copy.insert(index, item)
        super().insert(index, item)

    def extend(self, items):
        for item in items:
            item.set_prefix("+")
        if self._copy:
            self._copy.extend(items)
        super().extend(items)

    def delete_middle(self, keep_start, keep_end):
        """
        保留中间部分。
        每次调用该方法：
            1.创建一个新的MsgList 保存在self._copy
            2.self._copy不进行真正的删除，而是添加一个前缀"-"
            3.对self执行删除操作
            4.返回self
        如果self._copy存在，repr根据self._copy显示删除操作：
        问题：
            1.delete操作之后有其他操作时，该操作不会显示。(fixed)
            2.无法显示连续两次delete操作 (fixed)

        :param keep_start: 保留前n个数据
        :param keep_end: 保留后n个数据
        """
        if keep_start < 1 or keep_end < 1:
            raise ValueError("keep_start and keep_end must be >= 1.")
        if not self._copy:
            self._copy = self[:]  # 浅拷贝
        for item in self._copy[keep_start:-keep_end]:
            item.set_prefix("-")
        delete_objs = self[keep_start:-keep_end]
        for i in delete_objs:  # 删除引用，只有_copy指向含有"-"前缀的对象
            super().remove(i)
        return MsgList(*delete_objs)

    def pop(self, index=-1):
        if not self._copy:
            self._copy = self[:]  # 浅拷贝
        self._copy[index].set_prefix("-")
        item = super().pop(index)
        return item

    def human_count(self):
        return len([msg for msg in self if msg.type == 'human'])

    def ai_count(self):
        return len([msg for msg in self if msg.type == 'ai'])

    def to_json(self):
        return [i.json for i in self]

    def __enter__(self):
        self.__repr__()
        return self

    def __exit__(self, *args):
        print(self)


class HumanMsg(BaseMsg):
    type = 'human'


class AIMsg(BaseMsg):
    type = 'ai'


class SystemMsg(BaseMsg):
    type = 'system'


class SummaryMsg(HumanMsg):
    type = 'summary'


if __name__ == '__main__':
    msg_list = MsgList(AIMsg(content='''text1'''), AIMsg(content='''text2'''), AIMsg(content='''text3'''),
                       AIMsg(content='''text4'''), git_mode=True, name='MIYA')
    with msg_list:
        msg_list.delete_middle(1, 1)
    # with msg_list:
        msg_list.insert(0, SystemMsg(content='''text0'''))
    # with msg_list:
        msg_list.pop(0)
    # with msg_list:
        msg_list.append(SystemMsg(content='''text5'''))
    # with msg_list:
        msg_list.extend([SystemMsg(content='''text6'''), SystemMsg(content='''text7''')])
    # with msg_list:
        msg_list.delete_middle(1, 2)
    # with msg_list:
        res = msg_list.pop(0)
        # print(res.json)
    print(msg_list.to_json())
