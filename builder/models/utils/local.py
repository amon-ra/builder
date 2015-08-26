import posixpath, os
import logging

_logger = logging.getLogger(__name__)


class LocalDir(object):
    def __init__(self, jinja_env=None):
        self.jinja_env = jinja_env
        self.default_dir = '/vagrant/custom/addons'

    def write_template(self, filename, template, d, overwrite, **kwargs):
        if not self.jinja_env:
            raise ValueError('Jinja2 Environment is not set')
        self.write(filename, self.jinja_env.get_template(template).render(d),overwrite, **kwargs)

    def write(self, filename, content, overwrite, **kwargs):

        if overwrite is False and os.path.exists(filename):
            _logger.warning("File {} exists and is not overwrited ({}).".format(filename,overwrite))
        else:
            try:
                os.makedirs(os.path.dirname(filename))
            except Exception as e:
                _logger.debug("ERROR creating directories, already created or failed permisions for file".format(filename))
            try:
                with open(filename, "w") as f:
                    f.write(content)
            except:
                _logger.error("Error creating file: {}".format(filename))


class ModuleLocalFile(object):
    def __init__(self, zip_file, module):
        self.zip_file = zip_file
        self.module = module

    def write_template(self, filename, template, d, **kwargs):
        self.zip_file.write_template(posixpath.join(self.module.dest_dir, self.module.name, filename), template, d,
                                     self.module.overwrite, **kwargs)

    def write(self, filename, content, **kwargs):
        self.zip_file.write(posixpath.join(self.module.dest_dir, self.module.name, filename), content,
                            self.module.overwrite,  **kwargs)
