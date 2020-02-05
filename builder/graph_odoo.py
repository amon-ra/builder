    @api.model
    def graph_get(self, id, model, node_obj, conn_obj, src_node, des_node, label, scale):
        def rec_name(rec):
            return (rec.name if 'name' in rec else
                    rec.x_name if 'x_name' in rec else
                    None)

        nodes = []
        nodes_name = []
        transitions = []
        start = []
        tres = {}
        labels = {}
        no_ancester = []
        blank_nodes = []

        Model = self.env[model]
        Node = self.env[node_obj]

        for model_key, model_value in Model._fields.items():
            if model_value.type == 'one2many':
                if model_value.comodel_name == node_obj:
                    _Node_Field = model_key
                    _Model_Field = model_value.inverse_name
                for node_key, node_value in Node._fields.items():
                    if node_value.type == 'one2many':
                        if node_value.comodel_name == conn_obj:
                             # _Source_Field = "Incoming Arrows" (connected via des_node)
                            if node_value.inverse_name == des_node:
                                _Source_Field = node_key
                             # _Destination_Field = "Outgoing Arrows" (connected via src_node)
                            if node_value.inverse_name == src_node:
                                _Destination_Field = node_key

        record = Model.browse(id)
        for line in record[_Node_Field]:
            if line[_Source_Field] or line[_Destination_Field]:
                nodes_name.append((line.id, rec_name(line)))
                nodes.append(line.id)
            else:
                blank_nodes.append({'id': line.id, 'name': rec_name(line)})

            if 'flow_start' in line and line.flow_start:
                start.append(line.id)
            elif not line[_Source_Field]:
                no_ancester.append(line.id)

            for t in line[_Destination_Field]:
                transitions.append((line.id, t[des_node].id))
                tres[str(t['id'])] = (line.id, t[des_node].id)
                label_string = ""
                if label:
                    for lbl in safe_eval(label):
                        if tools.ustr(lbl) in t and tools.ustr(t[lbl]) == 'False':
                            label_string += ' '
                        else:
                            label_string = label_string + " " + tools.ustr(t[lbl])
                labels[str(t['id'])] = (line.id, label_string)

        g = graph(nodes, transitions, no_ancester)
        g.process(start)
        g.scale(*scale)
        result = g.result_get()
        results = {}
        for node_id, node_name in nodes_name:
            results[str(node_id)] = result[node_id]
            results[str(node_id)]['name'] = node_name
        return {'nodes': results,
                'transitions': tres,
                'label': labels,
                'blank_nodes': blank_nodes,
                'node_parent_field': _Model_Field}
