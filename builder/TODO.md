- website_page_designer.js fails.
- QWEB permisions in <div groups="grupo">
- mixins
- port data/oe.css.classes.xml
- install jingtrang
- select model from ir_model_data group by model (data from custom model)
- ir.actions: (server,report,client,actions,todo)
- https://www.cybrosys.com/blog/widgets-in-odoo
- https://github.com/Odoo-10-test/trucos_odoo/blob/master/views.md
- No workflows in v11:
#https://www.odoo.com/apps/modules/11.0/odoo_dynamic_workflow/
#https://bloopark.de/en_US/blog/the-bloopark-times-english-2/post/odoo-10-workflows-partial-removal-265#blog_content

- Fix security/ir.model.access.csv

- Fix tests

- https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#id12

- Reports: https://www.odoo.com/documentation/11.0/reference/reports.html

- Actions: (Only Window actions are working): https://www.odoo.com/documentation/11.0/reference/actions.html

- Controllers

- https://apps.odoo.com/apps/modules/11.0/genial_selection_widget/

- Add documentation links in each view.

- fields_view_get

- copy_data

- dynamic select

- View content are divided in fields and button, create a content with lines and order (attr,invisible,class,string,name....)

- boton para crear dominios (selecionamos el modelo, despues el field, operación, valor)

- Update FIELD_WIDGETS_ALL from demo.odoo.com

- Add buton to create report -> Wizard -> Model + View + Action

- Add button to create wizard -> Wizard -> Model + View + Action

- Snippets

- Implement Ecommerce like Controller

- odoo shell: odoo shell --db_host db -w odoo -r odoo -d odoo_11_db_builder

- Implement this: https://github.com/cdr/code-server

- mixin (https://es.slideshare.net/ElnAnnaJnasdttir/odoo-experience-2018-inherit-from-these-10-mixins-to-empower-your-app):
    - mail.thread (discuss,send mail)
    - mail.activity.mixin (schedule activity)
    - rating.mixin (customer satisfation)
    - utm.mixin (track campaigns and mediums)
    - portal
    - website.published (Manage document publication)
    - website.seo.metadata (Promote pages)

- https://www.cybrosys.com/blog/fields-and-parameters-in-odoo (selection_add)

- class odoo.fields.Reference
- class odoo.fields.Many2oneReference:
    res_model_id = fields.Many2one(
        'ir.model', 'Document Model',
        index=True, ondelete='cascade', required=True)
    res_model = fields.Char(
        'Related Document Model',
        index=True, related='res_model_id.model', compute_sudo=True, store=True, readonly=True)
    res_id = fields.Many2oneReference(string='Related Document ID', index=True, required=True, model_field='res_model')
    res_name = fields.Char(
        'Document Name', compute='_compute_res_name', compute_sudo=True, store=True,
        help="Display name of the related document.", readonly=True)

- FIELD_WIDGETS_ALL: (https://www.cybrosys.com/blog/widgets-in-odoo)
    .add('abstract', AbstractField)
    .add('input', basic_fields.InputField)
    .add('integer', basic_fields.FieldInteger)
    .add('boolean', basic_fields.FieldBoolean)
    .add('date', basic_fields.FieldDate)
    .add('datetime', basic_fields.FieldDateTime)
    .add('daterange', basic_fields.FieldDateRange)
    .add('domain', basic_fields.FieldDomain)
    .add('text', basic_fields.FieldText)
    .add('list.text', basic_fields.ListFieldText)
    .add('html', basic_fields.FieldText)
    .add('float', basic_fields.FieldFloat)
    .add('char', basic_fields.FieldChar)
    .add('link_button', basic_fields.LinkButton)
    .add('handle', basic_fields.HandleWidget)
    .add('email', basic_fields.FieldEmail)
    .add('phone', basic_fields.FieldPhone)
    .add('url', basic_fields.UrlWidget)
    .add('CopyClipboardText', basic_fields.TextCopyClipboard)
    .add('CopyClipboardChar', basic_fields.CharCopyClipboard)
    .add('image', basic_fields.FieldBinaryImage)
    .add('kanban.image', basic_fields.KanbanFieldBinaryImage)
    .add('binary', basic_fields.FieldBinaryFile)
    .add('pdf_viewer', basic_fields.FieldPdfViewer)
    .add('monetary', basic_fields.FieldMonetary)
    .add('percentage', basic_fields.FieldPercentage)
    .add('priority', basic_fields.PriorityWidget)
    .add('attachment_image', basic_fields.AttachmentImage)
    .add('label_selection', basic_fields.LabelSelection)
    .add('kanban_label_selection', basic_fields.LabelSelection) // deprecated, use label_selection
    .add('state_selection', basic_fields.StateSelectionWidget)
    .add('kanban_state_selection', basic_fields.StateSelectionWidget) // deprecated, use state_selection
    .add('boolean_favorite', basic_fields.FavoriteWidget)
    .add('boolean_toggle', basic_fields.BooleanToggle)
    .add('statinfo', basic_fields.StatInfo)
    .add('percentpie', basic_fields.FieldPercentPie)
    .add('float_time', basic_fields.FieldFloatTime)
    .add('float_factor', basic_fields.FieldFloatFactor)
    .add('float_toggle', basic_fields.FieldFloatToggle)
    .add('progressbar', basic_fields.FieldProgressBar)
    .add('toggle_button', basic_fields.FieldToggleBoolean)
    .add('dashboard_graph', basic_fields.JournalDashboardGraph)
    .add('ace', basic_fields.AceEditor)
    .add('color', basic_fields.FieldColor)
    .add('many2one_reference', basic_fields.FieldInteger);
    .add('selection', relational_fields.FieldSelection)
    .add('radio', relational_fields.FieldRadio)
    .add('selection_badge', relational_fields.FieldSelectionBadge)
    .add('many2one', relational_fields.FieldMany2One)
    .add('many2one_barcode', relational_fields.Many2oneBarcode)
    .add('list.many2one', relational_fields.ListFieldMany2One)
    .add('kanban.many2one', relational_fields.KanbanFieldMany2One)
    .add('many2many', relational_fields.FieldMany2Many)
    .add('many2many_binary', relational_fields.FieldMany2ManyBinaryMultiFiles)
    .add('many2many_tags', relational_fields.FieldMany2ManyTags)
    .add('many2many_tags_avatar', relational_fields.FieldMany2ManyTagsAvatar)
    .add('form.many2many_tags', relational_fields.FormFieldMany2ManyTags)
    .add('kanban.many2many_tags', relational_fields.KanbanFieldMany2ManyTags)
    .add('many2many_checkboxes', relational_fields.FieldMany2ManyCheckBoxes)
    .add('one2many', relational_fields.FieldOne2Many)
    .add('statusbar', relational_fields.FieldStatus)
    .add('reference', relational_fields.FieldReference)
    .add('font', relational_fields.FieldSelectionFont);
    .add('timezone_mismatch', special_fields.FieldTimezoneMismatch)
    .add('report_layout', special_fields.FieldReportLayout);

