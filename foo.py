from functui.classes import *
from functui.common import *

style_rule = rule_fg(Color4.RED) | rule_bold | rule_italic

# much less visual noise when defining styles inline
layout = text("foo") | styled(border, rule_fg(Color4.RED))


style_rule = StyleRule(
    fg=Color4.RED,
    bg=rgb(10, 134, 231),
    add_attrs=StyleAttr.ITALIC | StyleAttr.BOLD
    # StyleAttr is an flag which means you
    # can use | to combine muliple attributes.
)

not_italic = StyleRule(
    remove_attrs=StyleAttr.ITALIC
)



