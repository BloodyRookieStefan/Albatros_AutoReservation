import os
import yaml


class CTemplateCreator:

    SourceFile = '{}/Frontend/templates/template.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    TargetFile = '{}/Backend/settings.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

    CourseLayout = '{}/Backend/latestCourseLayout.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

    Document = None

    def read_template(self):
        # Check if file exists
        if not os.path.exists(self.SourceFile):
            raise ValueError('{} file not found'.format(self.SourceFile))
        # Read template
        with open(self.SourceFile, 'r') as file:
            self.Document = yaml.safe_load(file)

    def save_template(self):
        # Delete old one
        if os.path.exists(self.TargetFile):
            os.remove(self.TargetFile)

        with open(self.TargetFile, 'w') as file:
            yaml.dump(self.Document, file, default_flow_style=False)

    def read_course_layout(self):
        # Check if file exists
        if not os.path.exists(self.CourseLayout):
            return []
        # Read template
        with open(self.CourseLayout, 'r') as file:
            return yaml.safe_load(file)
















if __name__ == '__main__':
    debug = CTemplateCreator()
    debug.create_new_settings_file()