#%%
class NestedArray:
    def __init__(self, data, is_int):
        self.data = data
        self.is_int = is_int
    
    def __repr__(self):
        return "[" + ", ".join([d.__repr__() for d in self.data]) + "]"
    
    @classmethod
    def construct(cls, data):
        data_prep = [d if isinstance(d, int) else NestedArray.construct(d) for d in data]
        is_int = [isinstance(d, int) for d in data]
        return NestedArray(data_prep, is_int)
    
    def can_expand(self):
        if isinstance(self.data[-1], int) and self.data[-1] == 0:
            return False
        return True
    
    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return False
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True
    
    def have_proper_prefix(self, other) -> bool:
        if len(self.data) <= len(other.data):
            return False
        for i in range(len(other.data)):
            if not self.data[i] == other.data[i]:
                return False
        return True
    
    def get_prefix(self):
        return [NestedArray(self.data[0:i], self.is_int[0:i]) for i in range(len(self.data) + 1)]
    
    def is_regular(self):
        for i in range(len(self.data)):
            if self.is_int[i]:
                if self.data[i] == 0:
                    continue
                int_regular = False
                for j in range(i):
                    if not self.is_int[j]:
                        continue
                    if self.data[j] == self.data[i] - 1:
                        int_regular = True
                if not int_regular:
                    return False
            else:
                if not self.data[i].is_regular():
                    return False
                if self.data[i] == NestedArray.construct([0]):
                    continue
                list_regular = False
                for j in range(i):
                    if self.is_int[j]:
                        continue
                    if self.data[j].data == self.data[i].data[:-1]:
                        list_regular = True
                if not list_regular:
                    return False
        return True
    
    def make_regular(self):
        new_data = []
        new_is_int = []
        if not self.is_int[0]:
            new_data.append(0)
            new_is_int.append(True)

        for i in range(len(self.data)):
            if self.is_int[i]:
                if self.data[i] == 0:
                    new_data.append(0)
                    new_is_int.append(True)
                    continue
                lower_int_max = -1
                for j in range(len(new_data)):
                    if not new_is_int[j]:
                        continue
                    if new_data[j] < self.data[i]:
                        lower_int_max = max(new_data[j], lower_int_max)
                for j in range(lower_int_max + 1, self.data[i] + 1):
                    new_data.append(j)
                    new_is_int.append(True)
            else:
                current_term = self.data[i].make_regular()
                prefixes = current_term.get_prefix()
                if current_term == NestedArray.construct([0]):
                    new_data.append(current_term)
                    new_is_int.append(False)
                    continue
                max_prefix_idx = 0
                for j in range(len(new_data)):
                    if new_is_int[j]:
                        continue
                    if current_term.have_proper_prefix(new_data[j]):
                        max_prefix_idx = max(len(new_data[j].data), max_prefix_idx)
                for j in range(max_prefix_idx + 1, len(current_term.data) + 1):
                    new_data.append(prefixes[j])
                    new_is_int.append(False)
        return NestedArray(new_data, new_is_int)
    
    def can_expand(self):
        if not self.is_int[-1]:
            return True
        if self.data[-1] != 0:
            return True
        return False
    
    def expand(self, n):
        #[0, 1] -> [0, 0, 0, ...]
        #[0, 1, 1] -> [0, 1, 0, 1, 0, 1, ...]
        #[0, 1, 2] -> [0, 1, 1, 1, ...]
        #[0, [0]] -> [0, 1, 2, 3, ...]
        #[0, [0], 1] -> [0, [0], 0, [0]]
        #[0, [0], [0]] -> [0, [0], 1, [0], 2, [0], 3, [0], ...]
        #[0, [0], [0, 0]] -> [0, [0], [0], ...]
        #[0, [0], [0, 0], [0, 0]] -> [0, [0], [0, 0], [0], [0, 0], ...]
        #[0, [0], [0, 0], [0, 0, 0]] -> [0, [0], [0, 0], [0, 0], ...]
        #[0, [0], [0, 1]] -> [0, [0], [0, ..., 0]] ~ [0, [0], [0, 0], [0, 0, 0], ...]
        #[0, [0], [0, [0]]] -> [0, [0], [0, 1, 2, 3, ...]] ~ ...

        #[0, [0], [0, [0]], [0, [0]]] -> [0, [0], [0, 0], [0, 1, 2, 3, ...]]

        new_data = []
        new_is_int = []

        if self.is_int[-1]:
            end_idx = len(self.data) - 1
            begin_idx = 0
            for i in range(len(self.data) - 2, -1, -1):
                if not self.is_int[i]:
                    continue
                if self.data[i] == self.data[-1] - 1:
                    begin_idx = i
                    break
            new_data = self.data[0:begin_idx]
            new_is_int = self.is_int[0:begin_idx]
            for i in range(n + 1):
                for j in range(begin_idx, end_idx):
                    new_data.append(self.data[j])
                    new_is_int.append(self.is_int[j])
        elif self.data[-1] == NestedArray.construct([0]):
            end_idx = len(self.data) - 1
            begin_idx = 0
            for i in range(len(self.data) - 2, -1, -1):
                if self.is_int[i]:
                    begin_idx = i
            new_data = self.data[0:begin_idx]
            new_is_int = self.is_int[0:begin_idx]
            for i in range(n + 1):
                new_data.append(self.data[begin_idx] + i)
                new_is_int.append(True)
                for j in range(begin_idx + 1, end_idx):
                    new_data.append(self.data[j])
                    new_is_int.append(self.is_int[j])
        elif not self.data[-1].can_expand():
            end_idx = len(self.data) - 1
            begin_idx = 0
            for i in range(len(self.data) - 2, -1, -1):
                if self.is_int[i]:
                    continue
                if self.data[i].data == self.data[-1].data[:-1]:
                    begin_idx = i
                    break
            new_data = self.data[0:begin_idx]
            new_is_int = self.is_int[0:begin_idx]
            for i in range(n + 1):
                for j in range(begin_idx, end_idx):
                    new_data.append(self.data[j])
                    new_is_int.append(self.is_int[j])
        else:
            final_term = self.data[-1].expand(n)
            new_data = self.data[:-1]
            new_is_int = self.is_int[:-1]
            new_data.append(final_term)
            new_is_int.append(False)

        return NestedArray(new_data, new_is_int).make_regular()
            


# %%
print(NestedArray.construct([0, [0], [0, [0]], [0, [0], [0, [0]]]]).make_regular().expand(5))