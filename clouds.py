from utils import randbool

class Clouds:
    
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = [[0 for _ in range(w)] for _ in range(h)]

    def update(self):
        for x in range(self.h):
            for y in range(self.w):
                if randbool(1, 10):
                    self.cells[x][y] = 2 if randbool(1, 8) else 1
                else:
                    self.cells[x][y] = 0

    def export_data(self):
        return {
            "w": self.w,
            "h": self.h,
            "cells": self.cells,
        }

    def import_data(self, data):
        self.w = data.get("w", self.w)
        self.h = data.get("h", self.h)
        self.cells = data.get("cells", self.cells)
