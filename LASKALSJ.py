# matrix for tracking send events of each application process
class LASKALSJ:
    def __init__(self, n):
        self.n = n
        self.matrix = []
        for i in range(n):
            self.matrix.append([0]* n)

    def set_val(self, row, col, val):
        if(row < self.n and col < self.n and val > self.matrix[row][col]):
            self.matrix[row][col] = val

    def get_val(self, row, col):
        if(row < self.n and col < self.n):
            return self.matrix[row][col]

    def fancy_print(self):
        for elem in self.matrix:
            for val in elem:
                print(val, end = " ")
            print()
        print()

    def get_matrix(self):
        return self.matrix
