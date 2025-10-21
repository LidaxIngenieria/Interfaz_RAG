from abc import ABC, abstractmethod


class Image_Model(ABC):


    def __init__(self, model_name: str):

        self.model_name = model_name


    