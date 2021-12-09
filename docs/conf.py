import importlib.metadata


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
]

autoclass_content = 'both'
autodoc_member_order = 'bysource'

templates_path = ['_templates']

source_suffix = '.rst'
master_doc = 'index'

project = 'arku'
copyright = '2021, TargetAI Ltd.'
author = 'TargetAI LLC'
version = release = importlib.metadata.version('arku')

pygments_style = 'sphinx'

todo_include_todos = True

html_theme = 'alabaster'
html_theme_options = {
    'github_user': 'targetaidev',
    'github_repo': 'arku',
    'travis_button': True,
    'codecov_button': True,
    'page_width': '1200px',
    'github_banner': True,
    'github_type': 'star',
}
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'localtoc.html',
        'searchbox.html',
    ]
}
htmlhelp_basename = 'arkudoc'
