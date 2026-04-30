from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = _('Remove current image')
    initial_text = _('Current product image')
    input_text = _('Choose replacement image')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'
