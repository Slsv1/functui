import mkdocs.config
import mkdocs.config.base
import mkdocs.config.config_options
import mkdocs.plugins

class MyPluginConfig(mkdocs.config.base.Config):
    foo = mkdocs.config.config_options.Type(str, default='a default value')
    bar = mkdocs.config.config_options.Type(int, default=0)
    baz = mkdocs.config.config_options.Type(bool, default=True)

class MyPlugin(mkdocs.plugins.BasePlugin[MyPluginConfig]):
    def on_config(self, config, **kwargs):
        print("hej")

        return config
