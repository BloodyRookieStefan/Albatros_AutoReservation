import os
import yaml

class CTemplateCreator:

    SourceFile = '{}//template.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

    def read_template(self):
        # Check if file exists
        if not os.path.exists(self.SourceFile):
            raise ValueError('{} file not found'.format(self.SourceFile))
        # Read template
        with open(self.SourceFile, 'r') as file:
            document = yaml.safe_load(file)
        return document
