from . import avr_exceptions as ex


class ConfParser(object):

    def __init__(self):

        self.parts = {}
        self.replaceable_chars = "'\t\n\r"

    def parse(self, file):

        ff_id = open(file, "r")

        part_dict = None
        stack = list()
        line_num = 1

        line = ff_id.readline()
        while line != "":
            for char in self.replaceable_chars:
                line = line.replace(char, '')
                line = line.strip()

            if line.find("#") != -1:
                line = ff_id.readline()
                continue

            if len(line) > 0:
                if line.find(";") == -1:
                    if line.find("part") != -1:
                        stack.append(";")

                        if line == "part":
                            part_dict = {}
                        else:
                            spl = line.split("\"")

                            if len(spl) > 3:
                                raise ex.ConfigParserError("Invalid line "
                                                           "format in line " +
                                                           str(line_num))

                            elif len(spl) == 3:
                                parent_id = spl[1]
                                part_dict = self.parts.get(parent_id).copy()

                    elif part_dict is not None:
                        if line.find("=") != -1:
                            items = line.split("=")
                            item = items[0].strip()
                            value = str("")

                            if len(items) == 2:
                                value += items[1]
                            elif len(items) > 2:
                                raise ex.ConfigParserError("Invalid line "
                                                           "format in line " +
                                                           str(line_num))

                            while line.find(";") == -1:
                                line = ff_id.readline()
                                line = line.strip()
                                value += line + " "

                            for char in self.replaceable_chars:
                                value = value.replace(char, '')
                            value = value.replace(',', ' ')
                            value = value.replace(';', '')
                            value = value.replace('"', '')

                            if len(stack) == 1:
                                part_dict[item] = value
                            else:
                                (part_dict[stack[-1]])[item] = value

                        elif line.find("\"") != -1:
                            spl = line.split("\"")
                            param_name = spl[0]+spl[1]
                            param_name = param_name.replace(' ', '_')
                            part_dict[param_name] = {}
                            stack.append(param_name)

                        else:
                            param_name = line
                            part_dict[param_name] = {}
                            stack.append(param_name)

                elif part_dict is not None:
                    if len(line) == 1:
                        stack_top = stack.pop()

                        if stack_top == ";":
                            part_id = part_dict.get("id")
                            if part_id is None:
                                raise ex.ConfigParserError("Missed parameter "
                                                           "'id'")

                            self.parts[part_id] = part_dict
                            part_dict = None
                            stack[:] = []

                    else:
                        items = line.split("=")

                        if len(items) != 2:
                            raise ex.ConfigParserError("Invalid line format in "
                                                       "line " + str(line_num))

                        for i in range(len(items)):
                            items[i] = items[i].strip()
                            items[i] = items[i].replace(';', '')
                            items[i] = items[i].replace('"', '')

                        if len(stack) == 1:
                            part_dict[items[0]] = items[1]
                        else:
                            param_name = stack[-1]
                            (part_dict[param_name])[items[0]] = items[1]

                line_num += 1
            line = ff_id.readline()

        ff_id.close()

    def get_parts(self):
        return self.parts
