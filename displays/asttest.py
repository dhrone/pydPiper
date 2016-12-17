import ast
def str_node(node):
	if isinstance(node, ast.AST):
		fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
		rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
		return rv + ')'
	else:
		return repr(node)
def ast_visit(node, level=0):
	print('  ' * level + str_node(node))
	for field, value in ast.iter_fields(node):
		if isinstance(value, list):
			for item in value:
				if isinstance(item, ast.AST):
					ast_visit(item, level=level+1)
		elif isinstance(value, ast.AST):
			ast_visit(value, level=level+1)
