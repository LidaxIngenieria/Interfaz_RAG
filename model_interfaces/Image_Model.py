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

    def image_to_text(self,images,query):

        result = ollama.chat(

            model= self.model_name,
            messages=[
                {
                    'role': "user",
                    'content': f'Describe any information in the images that might relevant to this query from the user, IT IS IMPERATIVE THAT YOU ONLY RETURN INFORMATION CONTAINED IN THE IMAGES DONT ADD ANYTHING ELSE: {query}',
                    'images': images
                }
	        ]
        )

        return result['message']['content']

    