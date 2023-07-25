import sys
import jinja2
import pkgutil

from .app import App
from .wrapper import DictWrapper
from . import yaml



class Base:
    def __init__(self,
                 app: App,
                 name: str = None,
                 filename: str = None,
                 template: str = None):
        self.app = app
        self.kind = type(self).__name__
        self.name = name or app.name + "-" + self.kind.lower()
        self.filename = filename or self.name + ".yaml"
        self.template = template or self.kind + ".yaml"

        self.__parsed = yaml.parser.load(self.render())
        self.yaml = DictWrapper(self.__parsed)

    def kreate(self) -> None:
        print("kreating "+self.filename)
        with open(self.app.target_dir + "/" + self.filename, 'wb') as f:
            yaml.parser.dump(self.__parsed, f)

    def annotate(self, name: str, val: str) -> None:
        if not self.yaml.metadata.has_key("annotations"):
            self.yaml.metadata.add("annotations", {})
        self.yaml.metadata.annotations.add(name, val)

    def add_label(self, name: str, val: str) -> None:
        if not self.yaml.metadata.has_key("labels"):
            self.yaml.metadata.add("labels", {})
        self.yaml.metadata.labels.add(name, val)

    def render(self, outfile=None):
        template_data = pkgutil.get_data(self.app.template_package.__package__,
                                         self.template).decode('utf-8')
        tmpl = jinja2.Template(
            template_data,
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True)
        vars = {
            "app": self.app,
            "vars": self.app.vars,
            "config": self.app.config,
            "my": self,
        }
        self._add_jinja_vars(vars)
        if outfile:
            tmpl.stream(vars).dump(outfile)
        else:
            return tmpl.render(vars)

    def _add_jinja_vars(self, vars):
        pass

## see: https://towardsdatascience.com/what-is-lazy-evaluation-in-python-9efb1d3bfed0
#def lazy_property(fn):
#    attr_name = '_lazy_' + fn.__name__
#
#    @property
#    def _lazy_property(self):
#        if not hasattr(self, attr_name):
#            setattr(self, attr_name, fn(self))
#        return getattr(self, attr_name)
#    return _lazy_property
#    @lazy_property
#    def yaml(self):
#        # Only parse yaml when needed
#        #print("yaml property is parsed for "+self.name)
#        self.__parsed = self.__yaml.load(self.render())
#        return DictWrapper(self.__parsed)