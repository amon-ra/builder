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
