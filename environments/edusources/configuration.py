REPOSITORY = "017973353230.dkr.ecr.eu-central-1.amazonaws.com"
REPOSITORY_AWS_PROFILE = "pol-prod"


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
