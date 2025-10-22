from abc import ABC, abstractmethod
import ollama


class Image_Model(ABC):


    def __init__(self, model_name: str):

        self.model_name = model_name

    @abstractmethod
    def image_to_text(self,image):
        pass



class Visual_Ollama(Image_Model):

    def __init__(self, model_name: str):

        super().__init__(model_name)

    def image_to_text(self,image):

        result = ollama.chat(

            model= self.model_name,
            messages=[
                {
                    'content': 'Describe this image:',
                    'images': [image]
                }
	        ]
        )

        return result['message']['content']

    