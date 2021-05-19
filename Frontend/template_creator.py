import os
import yaml


class CTemplateCreator:

    SourceFile = '{}/Frontend/templates/template.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

    Document = None

    def read_template(self):
        # Check if file exists
        if not os.path.exists(self.SourceFile):
            raise ValueError('{} file not found'.format(self.SourceFile))
        # Read template
        with open(self.SourceFile, 'r') as file:
            self.Document = yaml.safe_load(file)