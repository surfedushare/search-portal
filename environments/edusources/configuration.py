REPOSITORY = "017973353230.dkr.ecr.eu-central-1.amazonaws.com"
REPOSITORY_AWS_PROFILE = "pol-prod"
SEARCH_FIELDS = [
    "title^2", "title.analyzed^2", "title.folded^2",
    "text", "text.analyzed", "text.folded",
    "description", "description.analyzed", "description.folded",
    "keywords", "keywords.folded",
    "authors.name.folded",
    "publishers", "publishers.folded",
    "ideas", "ideas.folded"
]


def get_project_search_mapping_properties():
    return {
        'aggregation_level': {
            'type': 'keyword'
        },
        'doi': {
            'type': 'keyword'
        },
        'material_type': {
            'type': 'keyword'
        },
        'material_types': {
            'type': 'keyword'
        },
        'educational_levels': {
            'type': 'keyword'
        },
        'lom_educational_levels': {
            'type': 'keyword'
        },
        'disciplines': {
            'type': 'keyword'
        },
        'ideas': {
            'type': 'text',
            'fields': {
                'keyword': {
                    'type': 'keyword',
                    'ignore_above': 256
                },
                'folded': {
                    'type': 'text',
                    'analyzer': 'folding'
                }
            }
        },
    }
